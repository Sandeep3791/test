from wayrem_admin.models import Orders, ShippingLoginextNotification, OrderDetails, OrderTransactions, StatusMaster, Wallet
from wayrem_admin.forecasts.order_liberary import OrderLiberary
from datetime import timedelta, date, datetime
from django.db.models import Sum

class OrderLib:
    def update_order(self,order_id):
        order=Orders.objects.filter(id=order_id).first()
        tax_vat = OrderLiberary().get_tax_vat()
        product_total = self.calculate_price(order_id)
        sub_total = round(product_total['sub_total'], 2)
        item_margin = round(product_total['item_margin'], 2)
        total = round(product_total['total'], 2)        
        order_lat=order.order_ship_latitude
        order_long = order.order_ship_longitude
        shipping = OrderLiberary().get_shipping_value(total,order_lat,order_long)
        item_discount = round(product_total['item_discount'], 2)
        discount = round(product_total['discount'], 2)
        grand_total, tax = OrderLiberary().get_grand_total(total, tax_vat, shipping)
        currentTimeDate = datetime.now() + timedelta(days=1)
        order_date = currentTimeDate
        order_dic = {'sub_total': sub_total, 'item_discount': item_discount, 'item_margin': item_margin, 'tax': tax, 'tax_vat': tax_vat, 'shipping': shipping, 'total': total, 'discount': discount, 'grand_total': grand_total,'order_date': order_date}
        Orders.objects.filter(id=order_id).update(**order_dic)
        
        return 1
    
    def calculate_price(self,order_id):
        order_detail_list=OrderDetails.objects.filter(order_id=order_id)
        subtotal_unit_price = 0
        product_total = {}
        total_item_discount = 0
        total_item_margin = 0
        for gpl in order_detail_list:
            quantity = float(gpl.quantity)
            if quantity:
                product_subtotal = float(gpl.product.price)
                product_margin_amount = OrderLiberary().calculate_price_unit_type(
                    gpl.product.wayrem_margin, gpl.product.price, gpl.product.margin_unit)
                if gpl.product.discount is None:
                    product_discount_price = 0
                    total_price_margin = product_subtotal+product_margin_amount
                else:
                    product_discount_price = gpl.product.discount
                    total_price_margin = product_subtotal+product_margin_amount
                total_product_discount_price = OrderLiberary().calculate_price_unit_type(
                    product_discount_price, total_price_margin, gpl.product.dis_abs_percent)

                subtotal_unit_price += (product_subtotal+product_margin_amount -
                                        total_product_discount_price) * quantity
                total_item_discount += (total_product_discount_price * quantity)
                total_item_margin += (product_margin_amount * quantity)

        product_total = {'sub_total': subtotal_unit_price, 'item_margin': total_item_margin,
                         'total': subtotal_unit_price, 'item_discount': total_item_discount, 'discount': 0}
        return product_total

    def credit_to_wallet(self,order,order_tran):
        customer_id=order['customer_id']
        wallet_amount=self.wallet_total_amount(customer_id)
        grand_total=order['grand_total']
        currentDateTime = datetime.now()
        payment_type=order_tran['payment_mode_id']
        order_id=order['id']
        if float(wallet_amount) >= float(grand_total):
            total_amount= float(grand_total)
        else:
            total_amount=float(wallet_amount)
        wallet={'amount':total_amount,'payment_type_id':payment_type,'transaction_type_id':1,'order_id':order_id,'customer_id':customer_id,'created':currentDateTime}
        wallet=Wallet(**wallet)
        wallet.save()
        return 1
    
    def order_partial_payment(self,order_id):
        order=Orders.objects.filter(id=order_id).first()
        customer_id=order.customer_id
        wallet_amount=self.wallet_total_amount(customer_id)
        grand_total=order.grand_total
        if float(wallet_amount) >= float(grand_total):
            partial_payment=0
        else:
            partial_payment=float(grand_total) - float(wallet_amount)
            partial_payment=round(partial_payment,2)
        
        Orders.objects.filter(id=order_id).update(partial_payment=partial_payment)
        return 1

    def wallet_total_amount(self,customer_id):
        transaction_id=Wallet.objects.values('transaction_type_id').annotate(total_sum=Sum('amount')).filter(customer_id=customer_id)
        dr=0
        cr=0
        for tr in transaction_id:
            if tr['transaction_type_id'] == 1:
                dr=tr['total_sum']
            else:
                cr=tr['total_sum']
        total_amount=cr - dr
        if total_amount <= 0:
            return 0
        else:
            return total_amount
