from models import order_models, payment_models
from utility_services import common_services
from schemas import user_schemas, order_schemas
from fastapi import status
import constants
import random
from sqlalchemy.orm import Session


def update_inventory(order_id, product_id, product_quantity, db: Session):
    inventory = order_models.Inventory(order_id=order_id, quantity=product_quantity, inventory_type_id=3,
                                       product_id=product_id, warehouse_id=1, order_status="ordered", created_at=common_services.get_time())
    db.merge(inventory)
    db.commit()
    # Inverntory Update start
    try:
        # product_type = db.execute(
        #     f"SELECT `inventory`.`inventory_type_id`, SUM(`inventory`.`quantity`) AS `inventory_quantity` FROM `inventory` WHERE `inventory`.`product_id` = {product_id} GROUP BY `inventory`.`inventory_type_id` ORDER BY `inventory`.`inventory_type_id` ASC")
        product_type = db.execute(f"SELECT inventory_type_id, SUM(quantity) AS inventory_quantity FROM {constants.Database_name}.inventory WHERE inventory.product_id = {product_id} GROUP BY inventory_type_id ORDER BY inventory_type_id ASC")

        total_quantity = 0
        inventory_starting = 0
        inventory_received = 0
        inventory_shipped = 0
        inventory_cancelled = 0
        for quantity_cal in product_type:
            quantity = quantity_cal['inventory_quantity']
            if quantity_cal['inventory_type_id'] == 3:
                total_quantity -= quantity
                inventory_shipped = quantity
            else:
                total_quantity += quantity
                if quantity_cal['inventory_type_id'] == 1:
                    inventory_starting = quantity
                elif quantity_cal['inventory_type_id'] == 2:
                    inventory_received = quantity
                else:
                    inventory_cancelled = quantity
        timestamp = str(common_services.get_time())
        update_query = f"UPDATE {constants.Database_name}.products_master SET `quantity` = {total_quantity},`updated_at` = '{timestamp}',`inventory_starting` = {inventory_starting},`inventory_received` = {inventory_received},`inventory_shipped` = {inventory_shipped},`inventory_cancelled` = {inventory_cancelled},`inventory_onhand` = {total_quantity} WHERE `id` = {product_id};"
        db.execute(update_query)
        db.commit()
        return True
        # Inverntory Update end
    except Exception as e:
        print(e)
        return False

def generate_ref_number(db: Session):
    ref_no = random.randint(1000, 999999)
    same_order_ref_no = db.query(order_models.Orders).filter(
        order_models.Orders.ref_number == ref_no).first()
    if same_order_ref_no:
        ref_no = random.randint(999999, 99999999)

    return ref_no


def product_details(discount_unit, req_product_price, product_qty, product_discount):
    if discount_unit == '%':
        discount_value = (req_product_price/100)*product_discount
    elif product_discount == '':
        discount_value = 0
        product_discount = 0
    else:
        discount_value = int(product_discount)
    disc_with_qty = discount_value*product_qty
    dicscount_with_qty = round(disc_with_qty, 2)

    return discount_value, dicscount_with_qty


def order_checkout_entry(checkout_details, order, ref_no, db: Session):
    checkout_id = checkout_details['id']
    order.checkout_id = checkout_id
    db.merge(order)
    db.commit()

    ref_and_checkout_ids = order_schemas.ReferenceAndCheckoutIds(ref_number = ref_no, checkout_id = checkout_id)

    result = order_schemas.InitialOrderResponse(
        status=status.HTTP_200_OK, message="Initial Order created successfully!!", data = ref_and_checkout_ids)
    return result 
