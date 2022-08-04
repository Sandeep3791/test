from django.core.validators import MinValueValidator
from wayrem_admin.models.purchase_order import PurchaseOrder
from wayrem_admin.models.products import Products
import imp
from django.db import models
from django.utils.translation import ugettext_lazy as _
from wayrem_admin.utils.constants import *
from django.db.models import Sum


class InventoryType(models.Model):
    id = models.SmallAutoField(primary_key=True)
    type_name = models.CharField(
        max_length=50, db_collation='utf8mb4_unicode_ci')
    status = models.IntegerField(default=1)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'inventory_type'


class Inventory(models.Model):
    order_status_choices = (('ordered', 'Ordered'),
                            ('shipped', 'Shipped'), ('cancelled', 'Canceled'))
    id = models.BigAutoField(primary_key=True)
    inventory_type = models.ForeignKey('InventoryType', models.DO_NOTHING)
    quantity = models.IntegerField(
        validators=[MinValueValidator(0)], blank=False, null=False)
    product = models.ForeignKey(
        'Products', on_delete=models.CASCADE, null=True, blank=True)
    warehouse = models.ForeignKey('Warehouse', models.DO_NOTHING, null=True)
    po_id = models.IntegerField(blank=True, null=True)
    supplier_id = models.IntegerField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)
    order_status = models.CharField(
        max_length=30, blank=True, null=True, choices=order_status_choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length=1000, blank=True, null=True)

    def po_inventory_process(self, po_id):
        po_details = PurchaseOrder.objects.filter(po_id=po_id, available=True)
        for po_detail in po_details:
            po_detail_dict = {'inventory_type_id': 2, 'quantity': po_detail.product_qty, 'product_id': po_detail.product_name.id, 'warehouse_id': po_detail.product_name.warehouse.id,
                              'po_id': po_detail.id, 'supplier_id': po_detail.supplier_product.supplier_id.id, 'order_id': None, 'order_status': None}
            # print(po_detail_dict)
            self.insert_inventory(po_detail_dict)
        return 1

    def order_inventory_process(self, order_id):
        # When we place order inventory process to shipping
        from wayrem_admin.models.orders import Orders, OrderDetails
        orders = Orders.objects.filter(id=order_id).first()
        order_status = orders.status.id
        order_details = OrderDetails.objects.filter(order=order_id)
        if (order_status == ORDER_STATUS_RECEIVED) or (order_status == ORDER_STATUS_CANCELLED)  or (order_status == ORDER_CANCELLED) :
            for order_detail in order_details:
                inventory_dict = {'inventory_type_id': 3, 'quantity': order_detail.quantity, 'product_id': order_detail.product.id,
                                  'warehouse_id': order_detail.product.warehouse.id, 'po_id': None, 'supplier_id': None, 'order_id': order_id, 'order_status': order_status}
                if (order_status == ORDER_STATUS_RECEIVED):
                    inventory_dict['inventory_type_id'] = 3
                    inventory_dict['order_status'] = INVENTORY_ORDER_STATUS_ORDERED
                else:
                    inventory_dict['inventory_type_id'] = 4
                    inventory_dict['order_status'] = INVENTORY_ORDER_STATUS_CANCELLED
                self.insert_inventory(inventory_dict)
        else:
            # update inventory table
            if (order_status == ORDER_STATUS_DELIVERING):
                inventory_lists = Inventory.objects.filter(
                    order_id=order_id, inventory_type_id=3, order_status=INVENTORY_ORDER_STATUS_ORDERED)
                for inv_list in inventory_lists:
                    inv_id = inv_list.id
                    Inventory.objects.filter(id=inv_id).update(
                        order_status=INVENTORY_ORDER_STATUS_SHIPPED)
        return 1

    def insert_inventory(self, inventory_dict):
        try:
            if ('product_id' in inventory_dict) and ('quantity' in inventory_dict) and ('inventory_type_id' in inventory_dict) and ('warehouse_id' in inventory_dict):
                # inventory_dict={'inventory_type_id':1,'quantity':2,'product_id':1,'warehouse_id':1,'po_id':None,'supplier_id':None,'order_id':None,'order_status':None}
                inventory_create = Inventory(**inventory_dict)
                inventory_create.save()
                product_id = inventory_dict['product_id']
                self.update_product_quantity(product_id)
                return True
            else:
                print("missing value")
        except Exception as e:
            print(e)
            return False

    def update_product_quantity(self, product_id):
        try:
            total_quantity = 0
            inventory_starting = 0
            inventory_received = 0
            inventory_shipped = 0
            inventory_cancelled = 0
            product_type = Inventory.objects.annotate(inventory_quantity=Sum('quantity')).values(
                'inventory_type', 'inventory_quantity').filter(product=product_id).order_by('inventory_type_id')
            product_type.query.group_by = [('inventory_type')]
            for quantity_cal in product_type:
                quantity = quantity_cal['inventory_quantity']
                if quantity_cal['inventory_type'] == 3 or quantity_cal['inventory_type'] == 5:
                    total_quantity -= quantity
                    inventory_shipped = quantity
                else:
                    total_quantity += quantity
                    if quantity_cal['inventory_type'] == 1:
                        inventory_starting = quantity
                    elif quantity_cal['inventory_type'] == 2:
                        inventory_received = quantity
                    else:
                        inventory_cancelled = quantity
            Products.objects.filter(id=product_id).update(quantity=total_quantity, inventory_starting=inventory_starting, inventory_received=inventory_received,
                                                          inventory_shipped=inventory_shipped, inventory_cancelled=inventory_cancelled, inventory_onhand=total_quantity)
        except:
            print("An exception occurred")

    def update_product_inventory(self):
        product = self.product
        starting_inventory = 0
        received_inventory = 0
        shipped_inventory = 0
        for inventory in Inventory.objects.filter(product=product):
            if inventory.inventory_type == 'Starting':
                starting_inventory += inventory.quantity
            elif inventory.inventory_type == 'Received':
                received_inventory += inventory.quantity
            else:
                shipped_inventory += inventory.quantity

        inventory_onhand = (received_inventory +
                            starting_inventory)-shipped_inventory
        product.inventory_onhand = inventory_onhand if inventory_onhand >= 0 else 0
        product.inventory_received = received_inventory
        product.starting_inventory = starting_inventory
        product.inventory_shipped = shipped_inventory
        product.save()

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'inventory'
