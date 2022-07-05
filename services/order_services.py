import math
from services import firebase_services, payment_services
from utility_services import common_services, inventory_services
from utility_services.inventory_services import product_details, update_inventory, generate_ref_number
import os
from fastapi.encoders import jsonable_encoder
import logging
from models import user_models, order_models, firebase_models, payment_models,credit_models
from schemas import firebase_schemas, user_schemas, order_schemas, payment_schemas,credit_schemas
from fastapi import FastAPI, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
import random
import googlemaps
import datetime as DT 
from datetime import timedelta
import constants
import re
from sqlalchemy import null, or_


app = FastAPI()

logger = logging.getLogger(__name__)


def create_order(request, db: Session, background_tasks: BackgroundTasks):
    
    paid = False
    cod = False
    pending = False
    SUCCESS_CODES_REGEX = re.compile(r'^(000\.000\.|000\.100\.1|000\.[36])')
    SUCCESS_MANUAL_REVIEW_CODES_REGEX = re.compile(
        r'^(000\.400\.0[^3]|000\.400\.[0-1]{2}0)')
    PENDING_CHANGEABLE_SOON_CODES_REGEX = re.compile(r'^(000\.200)')
    PENDING_NOT_CHANGEABLE_SOON_CODES_REGEX = re.compile(
        r'^(800\.400\.5|100\.400\.500)')
    hyperpay_response = None
    hyperpay_response_description = None
    if int(request.payment_type) == 10 or int(request.payment_type) == 12:
        cod = True
    if not cod:
        # payment_status = payment_services.get_payment_status(request.checkout_id, request.entityId)
        payment_status = payment_services.HyperPayResponseView(request.entityId).get_payment_status(request.checkout_id)

        payment_check = payment_status.get("result").get("code")
        hyperpay_response = payment_status
        hyperpay_response_description = payment_status.get(
            "result").get("description")
        if re.search(PENDING_CHANGEABLE_SOON_CODES_REGEX, payment_check) or re.search(PENDING_NOT_CHANGEABLE_SOON_CODES_REGEX, payment_check) or re.search(SUCCESS_CODES_REGEX, payment_check) or re.search(SUCCESS_MANUAL_REVIEW_CODES_REGEX, payment_check):
            failed = False
        else:
            failed = True
        if failed:
            response = user_schemas.ResponseCommonMessage(
                status=status.HTTP_424_FAILED_DEPENDENCY, message="Transaction Failed!!", data=str(hyperpay_response))
            return response
        if re.search(PENDING_CHANGEABLE_SOON_CODES_REGEX, payment_check) or re.search(PENDING_NOT_CHANGEABLE_SOON_CODES_REGEX, payment_check):
            request.payment_status = 6
            pending = True
        if re.search(SUCCESS_CODES_REGEX, payment_check) or re.search(SUCCESS_MANUAL_REVIEW_CODES_REGEX, payment_check):
            paid = True
        registrationId = payment_status.get("registrationId")

        if registrationId:
            card_body = payment_status.get("card")
            card_number = card_body.get("last4Digits")

            reg_id = db.query(payment_models.CustomerCard).filter(payment_models.CustomerCard.customer_id == request.customer_id, or_(
                payment_models.CustomerCard.registration_id == registrationId, payment_models.CustomerCard.card_number == card_number)).first()

            if not reg_id:
                card_body = payment_status.get("card")
                card_number = card_body.get("last4Digits")
                expiry_month = card_body.get("expiryMonth")
                expiry_year = card_body.get("expiryYear")
                card_holder = card_body.get("holder")
                card_type = card_body.get("type")
                card_brand = payment_status.get("paymentBrand")
                save_card = payment_models.CustomerCard(customer_id=request.customer_id, registration_id=registrationId, card_number=card_number, expiry_month=expiry_month,
                                                        expiry_year=expiry_year, card_holder=card_holder, card_type=card_type, card_body=str(card_body), card_brand=card_brand)
                db.merge(save_card)
                db.commit()

    for req_product in request.products:
        product_qty = req_product.product_quantity
        product_quantity_check = db.execute(
            f"select * from {constants.Database_name}.products_master where id = {req_product.product_id};")
        for prod_qty in product_quantity_check:
            if int(prod_qty.quantity) < product_qty:
                result = user_schemas.ResponseCommonMessage(
                    status=status.HTTP_404_NOT_FOUND, message="Please check your cart some item are out of stock")
                return result

    db_user_active = db.query(user_models.User).filter(
        user_models.User.id == request.customer_id).first()

    if db_user_active.verification_status == "active":

        ref_no = random.randint(1000, 999999)
        same_order_ref_no = db.query(order_models.Orders).filter(
            order_models.Orders.ref_number == ref_no).first()
        if same_order_ref_no:
            ref_no = random.randint(999999, 99999999)
        order = order_models.Orders(
            ref_number=ref_no,
            customer_id=request.customer_id,
            status=16,
            delivery_status=1,
            sub_total=0,
            item_discount=0,
            item_margin=0,
            tax=0,
            tax_vat=0,
            discount=0,
            grand_total=0,
            shipping=0,
            total=0,
            order_shipped=0,
            order_ship_name=request.shipping_name,
            order_ship_address=request.shipping_address,
            order_billing_name=request.billing_name,
            order_billing_address=request.billing_address,
            order_city=request.city,
            order_country=request.country,
            order_ship_region=request.shipping_region,
            order_ship_landmark=request.shipping_landmark,
            order_ship_building_name=request.shipping_building_name,
            order_ship_latitude=request.shipping_latitude,
            order_ship_longitude=request. shipping_longitude,
            order_phone=request.contact,
            order_email=request.email,
            order_type=24,
            delivery_charge=request.delivery_fees,
            order_date=common_services.get_time()

        )
        db.merge(order)
        db.commit()

        order_data = db.query(order_models.Orders).filter(
            order_models.Orders.ref_number == order.ref_number).first()
        order_id = order_data.id
        sub_total_list = []
        discount_list = []
        margin_list = []
        order_view_list = []
        image_list = []
        price_list = []
        sup_name_list = []
        if not cod:
            transaction_id = payment_status.get("id")
            checkout_id = request.checkout_id
            response_body = str(payment_status)
            payment_type = payment_status.get("paymentType")
            payment_brand = payment_status.get("paymentBrand")
            amount = payment_status.get("amount")
            payment_status = payment_status.get("result").get("description")
            payment_transaction = payment_models.PaymentTransaction(order_id=order_id, transaction_id=transaction_id, checkout_id=checkout_id,
                                                                    response_body=response_body, payment_type=payment_type, payment_brand=payment_brand, amount=amount, status=payment_status)
            db.merge(payment_transaction)
            db.commit()

        for product in request.products:
            product_id = product.product_id
            product_qty = product.product_quantity
            req_product_price = product.product_price
            final_request_proce_with_qty = req_product_price*product_qty

            sub_total_list.append(final_request_proce_with_qty)

            product_data = db.execute(
                f"select * from {constants.Database_name}.products_master where id = {product_id};")
            for product1 in product_data:
                if product1.discount == None:
                    product_discount = 0
                else:
                    product_discount = float(product1.discount)
                product_price = float(product1.price)
                product_margin = float(product1.wayrem_margin)
                margin_unit = product1.margin_unit
                discount_unit = product1.dis_abs_percent
                product_SKU = product1.SKU
                product_name = product1.name

                a = product1.primary_image
                b = product1.mfr_name
                # update_img = a.split("/")[-1]
                upd_image_path = constants.IMAGES_DIR_PATH + a
                image_list.append(upd_image_path)
                sup_name_list.append(b)

            price_list.append(req_product_price)

            if discount_unit == '%':
                discount_value = (req_product_price/100)*product_discount
            elif product_discount == '':
                discount_value = 0
                product_discount = 0
            else:
                discount_value = int(product_discount)
            disc_with_qty = discount_value*product_qty
            dicscount_with_qty = round(disc_with_qty, 2)
            discount_list.append(dicscount_with_qty)

            if margin_unit == '%':
                intial_margin_value = (product_price/100) * product_margin
                margin_value = intial_margin_value
                abc = product_price + margin_value
                product_with_margin_price = round(abc, 2)
                final_product_price = (product_with_margin_price) * product_qty

            else:
                margin_value = product_margin
                final_product_price = (
                    product_price + product_margin) * product_qty
                cde = product_price + margin_value
                product_with_margin_price = round(cde, 2)
            margin_wity_qty = product_margin*product_qty
            margin_list.append(margin_wity_qty)

            if round(req_product_price, 2) > product_with_margin_price:
                data1 = order_schemas.OrderedProducts(
                    product_id=product_id, latest_price=product_with_margin_price)
                order_intial_data = db.query(order_models.Orders).filter(
                    order_models.Orders.id == order_id).first()
                db.delete(order_intial_data)
                db.commit()
                result = order_schemas.OrderResponse1(
                    status=status.HTTP_401_UNAUTHORIZED, message="Price Decreased for this product", data=data1)
                return result

            if round(req_product_price, 2) < product_with_margin_price:
                data = order_schemas.OrderedProducts(
                    product_id=product_id, latest_price=product_with_margin_price)
                order_intial_data = db.query(order_models.Orders).filter(
                    order_models.Orders.id == order_id).first()
                db.delete(order_intial_data)
                db.commit()
                result = order_schemas.OrderResponse1(
                    status=status.HTTP_401_UNAUTHORIZED, message="Price Increased for this product", data=data)
                return result

            order_details = order_models.OrderDetails(
                order_id=order_id,
                product_id=product_id,
                product_name=product_name,
                sku=product_SKU,
                price=product_price,
                discount=discount_value,
                item_margin=margin_value,
                quantity=product_qty
            )
            db.merge(order_details)
            db.commit()
            order_view_list.append(order_details)

            if paid or cod or pending:
                inventory = order_models.Inventory(
                    order_id=order_id, quantity=product_qty, inventory_type_id=3, product_id=product_id, warehouse_id=1, order_status="ordered", created_at=common_services.get_time())
                db.merge(inventory)
                db.commit()
                # Inverntory Update start
                try:
                    product_type = db.execute(
                        f"SELECT `inventory`.`inventory_type_id`, SUM(`inventory`.`quantity`) AS `inventory_quantity` FROM `inventory` WHERE `inventory`.`product_id` = {product_id} GROUP BY `inventory`.`inventory_type_id` ORDER BY `inventory`.`inventory_type_id` ASC")
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
                except Exception as e:
                    print(e)

            # Inverntory Update end
        inv_no = None
        if paid or cod:
            transaction_data = db.query(order_models.OrderTransactions).all()
            if transaction_data:
                inv_no = len(transaction_data)+1001
            else:
                inv_no = 1001
        order_transact = order_models.OrderTransactions(user_id=request.customer_id,  order_id=order_id, order_type=1,
                                                        payment_mode_id=request.payment_type, payment_status_id=request.payment_status, invoices_id=inv_no)
        db.merge(order_transact)
        db.commit()
        if paid or cod or pending:
            order_delivery_logs = order_models.OrderDeliveryLogs(
                order_id=order_id, order_status_id=1, order_status_details="Order is confirmed", user_id=1, customer_view=1, log_date=common_services.get_time())
            db.merge(order_delivery_logs)
            db.commit()

        final_sub_total = sum(sub_total_list) - sum(discount_list)
        final_discount_total = sum(discount_list)
        final_margin_total = sum(margin_list)
        final_total = final_sub_total
        vat_value = db.execute(
            f"select value from {constants.Database_name}.settings where id = 7 ;")
        for i in vat_value:
            vat_prcnt_value = int(i[0])

        final_total_with_delivery_fee = final_total+request.delivery_fees
        vat_amount = (final_total_with_delivery_fee/100)*vat_prcnt_value
        final_grand_total = final_total_with_delivery_fee + vat_amount

        order_data.sub_total = round(final_sub_total, 2)
        order_data.item_discount = round(final_discount_total, 2)
        order_data.item_margin = round(final_margin_total, 2)
        order_data.total = round(final_total, 2)
        order_data.grand_total = round(final_grand_total, 2)
        order_data.tax_vat = vat_prcnt_value
        order_data.tax = round(vat_amount, 2)
        order_data.shipping = request.delivery_fees
        order_data.is_shown = True
        db.merge(order_data)
        db.commit()
        if paid or cod or pending:
            cart_items = db.query(order_models.CustomerCart).filter(
                order_models.CustomerCart.customer_id == request.customer_id).all()
            for item in cart_items:
                db.delete(item)
                db.commit()

        user_notify = f"SELECT * FROM {constants.Database_name}.users_master where users_master.order_notify = True "
        if user_notify:
            emails = db.execute(user_notify)
            email_ids = []
            for email in emails:
                email_ids.append(email.email)
            email_query = f"SELECT * FROM {constants.Database_name}.email_template where email_template.key = 'order_placed_notification'"
            email_template = db.execute(email_query)
            subject = None
            body = None
            for template in email_template:
                subject = template.subject
                body = template.message_format
            values = {
                'order_number': ref_no,
                'link': f"{constants.global_link}/orders/{order_id}"
            }
            body = body.format(**values)
            for to in email_ids:
                background_tasks.add_task(
                    common_services.send_otp, to, subject, body, request, db)

        # for key = order_placed_customer_notification
        if paid or cod:
            invoice_link_mail = f"{constants.global_link}/orders/invoice-orders/{ref_no}"
            common_services.invoice_saver(invoice_link_mail, ref_no)
            path = os.path.abspath('.')
            invoice_path = os.path.join(
                path, f"invoice_folder/invoice_{ref_no}.pdf")
            invoice_delete = os.path.join(
                path, f"invoice_folder/invoice_{ref_no}.pdf")

            order_type_email = order.order_type
            user_mail = request.email

            returned = common_services.email_body(
                user_mail, order_id, order_view_list, image_list, order_type_email, ref_no, price_list, sup_name_list, db)

            background_tasks.add_task(
                common_services.send_otp, returned[0], returned[1], returned[2], request, db, invoice_path, invoice_delete)

        if paid or cod or pending:
            if pending:
                response = order_schemas.OrderResponse(
                    status=status.HTTP_206_PARTIAL_CONTENT, message="Order Placed Successfully")
            else:
                response = order_schemas.OrderResponse(
                    status=status.HTTP_200_OK, message="Order Placed Successfully")
            try:
                customer_data = db.execute(
                    f"select * from {constants.Database_name}.customer_device where customer_id = {request.customer_id} and is_active=True ;")
                setting_message = db.execute(
                    f"select * from {constants.Database_name}.settings where settings.key = 'notification_app_order_received' ;")
                for msg in setting_message:
                    message = msg.value
                values = {
                    "ref_no": ref_no,
                }
                message = message.format(**values)
                if customer_data:
                    for data in customer_data:
                        notf = firebase_schemas.PushNotificationFirebase(
                            title="Order placed", message=message, device_token=data.device_id, order_id=order_id)
                        firebase_services.push_notification_in_firebase(notf)

                    if notf:
                        fire = firebase_models.CustomerNotification(
                            customer_id=request.customer_id, order_id=order_id, title=notf.title, message=notf.message, created_at=common_services.get_time())
                        db.merge(fire)
                        db.commit()
            except Exception as e:
                print(e)
        else:
            data = hyperpay_response
            if not hyperpay_response_description:
                data = None
                hyperpay_response_description = "Unable to place order. Try with another card."
            response = user_schemas.ResponseCommonMessage(
                status=status.HTTP_404_NOT_FOUND, message=str(hyperpay_response_description), data=str(data))
        return response
    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="User is not approved to place the order")
        return common_msg


def initial_order(request, db: Session, background_tasks: BackgroundTasks):
    db_user_active = db.query(user_models.User).filter(
        user_models.User.id == request.customer_id).first()

    if not db_user_active:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Customer doesn't exist!!")
        return common_msg

    if db_user_active.verification_status != "active":
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="User is not approved to place the order !")
        return common_msg
    
    for product in request.products:
        product_qty = product.product_quantity
        product_quantity_check = db.execute(
            f"select * from {constants.Database_name}.products_master where id = {product.product_id} and publish = {True};")
        for prod_qty in product_quantity_check:
            if int(prod_qty.quantity) < product_qty:
                result = user_schemas.ResponseCommonMessage(
                    status=status.HTTP_404_NOT_FOUND, message="Please check your cart some item are out of stock")
                return result
            if prod_qty.discount == None:
                product_discount = 0
            else:
                product_discount = float(prod_qty.discount)
            product_price = float(prod_qty.price)
            product_margin = float(prod_qty.wayrem_margin)
            margin_unit = prod_qty.margin_unit
            discount_unit = prod_qty.dis_abs_percent

        product_id = product.product_id
        req_product_price = product.product_price
        final_request_price_with_qty = req_product_price*product_qty

        discount_value, dicscount_with_qty = product_details(discount_unit, req_product_price, product_qty, product_discount)

        if margin_unit == '%':
            intial_margin_value = (product_price/100) * product_margin
            margin_value = intial_margin_value
            abc = product_price + margin_value
            product_with_margin_price = round(abc, 2)
            final_product_price = (product_with_margin_price) * product_qty

        else:
            margin_value = product_margin
            final_product_price = (
                product_price + product_margin) * product_qty
            cde = product_price + margin_value
            product_with_margin_price = round(cde, 2)
        if round(req_product_price, 2) > product_with_margin_price or round(req_product_price, 2) < product_with_margin_price:
            data1 = order_schemas.OrderedProducts(
                product_id=product_id, latest_price=product_with_margin_price)
            increased = "Price Increased for this product"
            decreased = "Price Decreased for this product"
            message = decreased if req_product_price < product_with_margin_price else increased
            result = order_schemas.OrderResponse1(
                status=status.HTTP_401_UNAUTHORIZED, message=message, data=data1)
            return result
    
    ref_no = generate_ref_number(db)
    
    order = order_models.Orders(
        ref_number=ref_no,
        customer_id=request.customer_id,
        status=16,
        delivery_status=1,
        sub_total=0,
        item_discount=0,
        item_margin=0,
        tax=0,
        tax_vat=0,
        discount=0,
        grand_total=0,
        shipping=0,
        total=0,
        order_shipped=0,
        order_ship_name=request.shipping_name,
        order_ship_address=request.shipping_address,
        order_billing_name=request.billing_name,
        order_billing_address=request.billing_address,
        order_city=request.city,
        order_country=request.country,
        order_ship_region=request.shipping_region,
        order_ship_landmark=request.shipping_landmark,
        order_ship_building_name=request.shipping_building_name,
        order_ship_latitude=request.shipping_latitude,
        order_ship_longitude=request. shipping_longitude,
        order_phone=request.contact,
        order_email=request.email,
        order_type=24,
        delivery_charge=request.delivery_fees,
        order_date=common_services.get_time()
    )
    entityId = common_services.get_entityId(request.entityId)

    checkout_request = payment_schemas.CheckoutIdRequest(entityId = entityId, amount = request.amount, currency = 'SAR', 
                    paymentType = request.hyperpay_payment_type, customer_id = request.customer_id)
    
    user_request = jsonable_encoder(checkout_request)

    if request.registrationId:
        user_request['registrationId'] = request.registrationId
        # checkout_details = payment_services.order_checkout_id(user_request)
        checkout_details = payment_services.HyperPayResponseView(request.entityId).generate_checkout_id(user_request)

        success_code = checkout_details['result']['code']

        if success_code == '000.200.100' or success_code == '000.200.101' or success_code == '000.200.102':
            result = inventory_services.order_checkout_entry(checkout_details, order, ref_no, db)
            return result   
        else:
            # payment_services.delete_card(request.registrationId, entityId)
            payment_services.HyperPayResponseView(entityId).delete_card(request.registrationId)

            card = db.query(payment_models.CustomerCard).filter(
            payment_models.CustomerCard.registration_id == request.registrationId).first()
            if not card:
                common_msg = user_schemas.ResponseCommonMessage(
                    status=status.HTTP_404_NOT_FOUND, message="Registration id Doesn't Exist!")
                return common_msg
            db.delete(card)
            db.commit()

            common_msg = user_schemas.ResponseCommonMessage(status = status.HTTP_400_BAD_REQUEST, message = "Invalid registration id!")
            return common_msg          
        
    else:
        # checkout_details = payment_services.order_checkout_id(user_request)

        checkout_details = payment_services.HyperPayResponseView(request.entityId).generate_checkout_id(user_request)

          
        success_code = checkout_details['result']['code']

        if success_code == '000.200.100' or success_code == '000.200.101' or success_code == '000.200.102':
            result = inventory_services.order_checkout_entry(checkout_details, order, ref_no, db)
            return result 
        else:
            common_msg = user_schemas.ResponseCommonMessage(status = status.HTTP_404_NOT_FOUND, message = "Transaction Failed !")
            return common_msg


def create_order_new(request, db: Session, background_tasks: BackgroundTasks):
    
    try:
        if request.ref_number:
            db.query(order_models.Orders).filter(order_models.Orders.ref_number == request.ref_number).delete(synchronize_session = False)
            db.commit()

    except Exception as e:
        common_msg = user_schemas.ResponseCommonMessage(
                status=status.HTTP_406_NOT_ACCEPTABLE, message="Order already created !!")
        return common_msg
        
    paid = False
    cod = False
    pending = False
    credit = False
    PVC = False
    
    SUCCESS_CODES_REGEX = re.compile(r'^(000\.000\.|000\.100\.1|000\.[36])')
    SUCCESS_MANUAL_REVIEW_CODES_REGEX = re.compile(
        r'^(000\.400\.0[^3]|000\.400\.[0-1]{2}0)')
    PENDING_CHANGEABLE_SOON_CODES_REGEX = re.compile(r'^(000\.200)')
    PENDING_NOT_CHANGEABLE_SOON_CODES_REGEX = re.compile(
        r'^(800\.400\.5|100\.400\.500)')
    hyperpay_response = None
    hyperpay_response_description = None
    entityId = common_services.get_entityId(request.entityId)

    if int(request.payment_type) == 10 or int(request.payment_type) == 12:
        cod = True

    if int(request.payment_type) == 13:
        PVC = True #paying via credit

    if not cod and not PVC:
        # payment_status = payment_services.get_payment_status(request.checkout_id, entityId)
        payment_status = payment_services.HyperPayResponseView(request.entityId).get_payment_status(request.checkout_id)

        payment_check = payment_status.get("result").get("code")
        hyperpay_response = payment_status
        hyperpay_response_description = payment_status.get(
            "result").get("description")
        if re.search(PENDING_CHANGEABLE_SOON_CODES_REGEX, payment_check) or re.search(PENDING_NOT_CHANGEABLE_SOON_CODES_REGEX, payment_check) or re.search(SUCCESS_CODES_REGEX, payment_check) or re.search(SUCCESS_MANUAL_REVIEW_CODES_REGEX, payment_check):
            failed = False
        
        else:
            failed = True
        
        if failed:
            response = user_schemas.ResponseCommonMessage(
                status=status.HTTP_424_FAILED_DEPENDENCY, message="Transaction Failed!!", data=str(hyperpay_response))
            return response
        
        if re.search(PENDING_CHANGEABLE_SOON_CODES_REGEX, payment_check) or re.search(PENDING_NOT_CHANGEABLE_SOON_CODES_REGEX, payment_check):
            request.payment_status = 6
            pending = True
        
        if re.search(SUCCESS_CODES_REGEX, payment_check) or re.search(SUCCESS_MANUAL_REVIEW_CODES_REGEX, payment_check):
            paid = True
        # if payment_check == "000.100.110" or payment_check == "000.000.000" or payment_check == payment_check.startswith("000.400."):
        #     paid = True
        registrationId = payment_status.get("registrationId")
        
        if registrationId:
            card_body = payment_status.get("card")
            card_number = card_body.get("last4Digits")

            reg_id = db.query(payment_models.CustomerCard).filter(payment_models.CustomerCard.customer_id == request.customer_id, or_(
                payment_models.CustomerCard.registration_id == registrationId, payment_models.CustomerCard.card_number == card_number)).first()

            if not reg_id:
                card_body = payment_status.get("card")
                card_number = card_body.get("last4Digits")
                expiry_month = card_body.get("expiryMonth")
                expiry_year = card_body.get("expiryYear")
                card_holder = card_body.get("holder")
                card_type = card_body.get("type")
                card_brand = payment_status.get("paymentBrand")
                save_card = payment_models.CustomerCard(customer_id=request.customer_id, registration_id=registrationId, card_number=card_number, expiry_month=expiry_month,
                                                        expiry_year=expiry_year, card_holder=card_holder, card_type=card_type, card_body=str(card_body), card_brand=card_brand)
                db.merge(save_card)
                db.commit()
        # if registrationId:
        #     card_body = payment_status.get("card")
        #     card_number = card_body.get("last4Digits")
        #     expiry_month = card_body.get("expiryMonth")
        #     expiry_year = card_body.get("expiryYear")
        #     card_holder = card_body.get("holder")
        #     card_type = card_body.get("type")
        #     card_brand = payment_status.get("paymentBrand")
        #     save_card = payment_models.CustomerCard(customer_id=request.customer_id, registration_id=registrationId, card_number=card_number, expiry_month=expiry_month,
        #                                             expiry_year=expiry_year, card_holder=card_holder, card_type=card_type, card_body=str(card_body), card_brand=card_brand)
        #     db.merge(save_card)
        #     db.commit()

    for req_product in request.products:
        product_qty = req_product.product_quantity
        product_quantity_check = db.execute(
            f"select * from {constants.Database_name}.products_master where id = {req_product.product_id} and publish = {True};")
        for prod_qty in product_quantity_check:
            if int(prod_qty.quantity) < product_qty:
                result = user_schemas.ResponseCommonMessage(
                    status=status.HTTP_404_NOT_FOUND, message="Please check your cart some item are out of stock")
                return result

    db_user_active = db.query(user_models.User).filter(
        user_models.User.id == request.customer_id).first()

    if db_user_active.verification_status == "active":

        if not request.ref_number:
            ref_no = generate_ref_number(db)
            
        else:
            ref_no = request.ref_number
        order = order_models.Orders(
            ref_number=ref_no,
            customer_id=request.customer_id,
            status=16,
            delivery_status=1,
            sub_total=0,
            item_discount=0,
            item_margin=0,
            tax=0,
            tax_vat=0,
            discount=0,
            grand_total=0,
            shipping=0,
            total=0,
            order_shipped=0,
            order_ship_name=request.shipping_name,
            order_ship_address=request.shipping_address,
            order_billing_name=request.billing_name,
            order_billing_address=request.billing_address,
            order_city=request.city,
            order_country=request.country,
            order_ship_region=request.shipping_region,
            order_ship_landmark=request.shipping_landmark,
            order_ship_building_name=request.shipping_building_name,
            order_ship_latitude=request.shipping_latitude,
            order_ship_longitude=request. shipping_longitude,
            order_phone=request.contact,
            order_email=request.email,
            order_type=24,
            delivery_charge=request.delivery_fees,
            order_date=common_services.get_time()

        )
        db.merge(order)
        db.commit()

        order_data = db.query(order_models.Orders).filter(
            order_models.Orders.ref_number == order.ref_number).first()
        order_id = order_data.id
        sub_total_list = []
        discount_list = [] 
        margin_list = []
        order_view_list = []
        image_list = []
        price_list = []
        sup_name_list = []
        unit_list = []
        
        if not cod and not PVC:
            transaction_id = payment_status.get("id")
            checkout_id = request.checkout_id
            response_body = str(payment_status)
            payment_type = payment_status.get("paymentType")
            payment_brand = payment_status.get("paymentBrand")
            amount = payment_status.get("amount")
            payment_status = payment_status.get("result").get("description")
            payment_transaction = payment_models.PaymentTransaction(order_id=order_id, transaction_id=transaction_id, checkout_id=checkout_id,
                                                                    response_body=response_body, payment_type=payment_type, payment_brand=payment_brand, amount=amount, status=payment_status)
            db.merge(payment_transaction)
            db.commit()

        for product in request.products:
            product_id = product.product_id
            product_qty = product.product_quantity
            req_product_price = product.product_price
            final_request_price_with_qty = req_product_price*product_qty

            sub_total_list.append(final_request_price_with_qty)

            product_data = db.execute(
                f"select * from {constants.Database_name}.products_master where id = {product_id} and publish = {True};")
            for product1 in product_data:
                if product1.discount == None:
                    product_discount = 0
                else:
                    product_discount = float(product1.discount)
                product_price = float(product1.price)
                product_margin = float(product1.wayrem_margin)
                margin_unit = product1.margin_unit
                discount_unit = product1.dis_abs_percent
                product_SKU = product1.SKU
                product_name = product1.name

                a = product1.primary_image
                b = product1.mfr_name
                # update_img = a.split("/")[-1]
                upd_image_path = constants.IMAGES_DIR_PATH + a
                image_list.append(upd_image_path)
                sup_name_list.append(b)

                quantity_unit = product1.quantity_unit_id
                if quantity_unit == None :
                    unit_list.append(None)
                else:
                    product_quantity_unit = db.execute(f"select unit_name from {constants.Database_name}.unit_master where id = {quantity_unit}")
                    for pqu in product_quantity_unit:
                        unit_name = pqu.unit_name
                        unit_list.append(unit_name)


            price_list.append(req_product_price)
            
            discount_value, dicscount_with_qty = product_details(discount_unit, req_product_price, product_qty, product_discount)
            
            discount_list.append(dicscount_with_qty)

        
            if margin_unit == '%':
                intial_margin_value = (product_price/100) * product_margin
                margin_value = intial_margin_value
                abc = product_price + margin_value
                product_with_margin_price = round(abc, 2)
                final_product_price = (product_with_margin_price) * product_qty

            else:
                margin_value = product_margin
                final_product_price = (
                    product_price + product_margin) * product_qty
                cde = product_price + margin_value
                product_with_margin_price = round(cde, 2)
            margin_wity_qty = product_margin*product_qty
            margin_list.append(margin_wity_qty)

            if round(req_product_price, 2) > product_with_margin_price or round(req_product_price, 2) < product_with_margin_price:
                data1 = order_schemas.OrderedProducts(
                    product_id=product_id, latest_price=product_with_margin_price)
                order_intial_data = db.query(order_models.Orders).filter(
                    order_models.Orders.id == order_id).first()
                db.delete(order_intial_data)
                db.commit()
                increased = "Price Increased for this product"
                decreased = "Price Decreased for this product"
                message = decreased if req_product_price < product_with_margin_price else increased
                result = order_schemas.OrderResponse1(
                    status=status.HTTP_401_UNAUTHORIZED, message=message, data=data1)
                return result

            order_details = order_models.OrderDetails(
                order_id=order_id,
                product_id=product_id,
                product_name=product_name,
                sku=product_SKU,
                price=product_price,
                discount=discount_value,
                item_margin=margin_value,
                quantity=product_qty
            )
            db.merge(order_details)
            db.commit()
            order_view_list.append(order_details)

            if paid or cod or pending or PVC :
                update_inventory(order_id, product_id, product_qty, db)

        final_sub_total = sum(sub_total_list) - sum(discount_list)
        final_discount_total = sum(discount_list)
        final_margin_total = sum(margin_list)
        final_total = final_sub_total
        vat_value = db.execute(
            f"select value from {constants.Database_name}.settings where id = 7 ;")
        for i in vat_value:
            vat_prcnt_value = int(i[0])

        final_total_with_delivery_fee = final_total+request.delivery_fees
        vat_amount = (final_total_with_delivery_fee/100)*vat_prcnt_value
        final_grand_total = final_total_with_delivery_fee + vat_amount

        order_data.sub_total = round(final_sub_total, 2)
        order_data.item_discount = round(final_discount_total, 2)
        order_data.item_margin = round(final_margin_total, 2)
        order_data.total = round(final_total, 2)
        order_data.grand_total = round(final_grand_total, 2)
        order_data.tax_vat = vat_prcnt_value
        order_data.tax = round(vat_amount, 2)
        order_data.shipping = request.delivery_fees

        paying_price= final_grand_total
        order_id_credit = order_id
        if PVC:
            credit_data = db.query(credit_models.CreditManagement).filter(credit_models.CreditManagement.customer_id == request.customer_id).first()
            available_cr = credit_data.available

            if available_cr >= paying_price:
                updated_credit = float(available_cr - paying_price)

                credit_data.available = updated_credit
                credit_data.used += float(paying_price)
                credit_data.updated_at = common_services.get_time()
                db.merge(credit_data)
                db.commit()

                update_date = credit_data.updated_at

                credit_settings_data = db.query(credit_models.CreditSettings).filter(credit_models.CreditSettings.id == credit_data.credit_rule_id).first()
                time_in_days = credit_settings_data.time_period
                due_date = update_date + timedelta(days=time_in_days)

                    
                credit_log = credit_models.CreditTransactionsLog(customer_id = request.customer_id,order_id = order_id_credit,credit_amount = float(paying_price),available = updated_credit,credit_date = common_services.get_time(),due_date = due_date,payment_status = request.payment_status)
                db.merge(credit_log)
                db.commit()
                
                credit=True
                    # request.payment_status = updated_payment_status
            else:
                result = user_schemas.ResponseCommonMessage(status=status.HTTP_404_NOT_FOUND, message="Not enough credits available !")
                return result

        if paid or cod or pending or credit:
            order_data.is_shown = True
            db.merge(order_data)
            db.commit()

        if paid or cod or pending or credit:
            order_delivery_logs = order_models.OrderDeliveryLogs(
                order_id=order_id, order_status_id=1, order_status_details="Order is confirmed", user_id=1, customer_view=1, log_date=common_services.get_time())
            db.merge(order_delivery_logs)
            db.commit()

        inv_no = None
        if paid or cod or credit or credit:
            transaction_data = db.query(order_models.OrderTransactions).all()
            if transaction_data:
                inv_no = len(transaction_data)+1001
            else:
                inv_no = 1001
        order_transact = order_models.OrderTransactions(user_id=request.customer_id,  order_id=order_id, order_type=1,payment_mode_id=request.payment_type, payment_status_id=request.payment_status, invoices_id=inv_no)
        db.merge(order_transact)
        db.commit()

        if paid or cod or pending or credit:
            cart_items = db.query(order_models.CustomerCart).filter(
                order_models.CustomerCart.customer_id == request.customer_id).all()
            for item in cart_items:
                db.delete(item)
                db.commit()

        user_notify = f"SELECT * FROM {constants.Database_name}.users_master where users_master.order_notify = True "
        if user_notify:
            emails = db.execute(user_notify)
            email_ids = []
            for email in emails:
                email_ids.append(email.email)
            email_query = f"SELECT * FROM {constants.Database_name}.email_template where email_template.key = 'order_placed_notification'"
            email_template = db.execute(email_query)
            subject = None
            body = None
            for template in email_template:
                subject = template.subject
                body = template.message_format
            values = {
                'order_number': ref_no,
                'link': f"{constants.global_link}/orders/{order_id}"
            }
            body = body.format(**values)
            for to in email_ids:
                background_tasks.add_task(
                    common_services.send_otp, to, subject, body, request, db)

        # for key = order_placed_customer_notification
        if paid or cod or credit:
            invoice_link_mail = f"{constants.global_link}/orders/invoice-orders/{ref_no}"
            common_services.invoice_saver(invoice_link_mail, ref_no)
            path = os.path.abspath('.')
            invoice_path = os.path.join(
                path, f"invoice_folder/invoice_{ref_no}.pdf")
            invoice_delete = os.path.join(
                path, f"invoice_folder/invoice_{ref_no}.pdf")

            order_type_email = order.order_type
            user_mail = request.email

            returned = common_services.email_body(user_mail, order_id, order_view_list, image_list, order_type_email, ref_no, price_list, sup_name_list,unit_list ,db)

            background_tasks.add_task(common_services.send_otp,
                                    returned[0], returned[1], returned[2], request, db, invoice_path, invoice_delete)

        if paid or cod or pending or credit:
            data_response  = order_schemas.OrderResponseData(order_id=order_id)
            response = order_schemas.OrderResponse(status=status.HTTP_200_OK, message="Order Placed Successfully",data=data_response)
            try:
                customer_data = db.execute(
                    f"select * from {constants.Database_name}.customer_device where customer_id = {request.customer_id} and is_active=True ;")
                setting_message = db.execute(
                    f"select * from {constants.Database_name}.settings where settings.key = 'notification_app_order_received' ;")
                for msg in setting_message:
                    message = msg.value
                values = {
                    "ref_no": ref_no,
                }
                message = message.format(**values)
                if customer_data:
                    for data in customer_data:
                        notf = firebase_schemas.PushNotificationFirebase(
                            title="Order placed", message=message, device_token=data.device_id, order_id=order_id)
                        firebase_services.push_notification_in_firebase(notf)

                    if notf:
                        fire = firebase_models.CustomerNotification(
                            customer_id=request.customer_id, order_id=order_id, title=notf.title, message=notf.message, created_at=common_services.get_time())
                        db.merge(fire)
                        db.commit()
            except Exception as e:
                print(e)
        else:
            data = hyperpay_response
            if not hyperpay_response_description:
                data = None
                hyperpay_response_description = "Unable to place order. Try with another card."
            response = user_schemas.ResponseCommonMessage(
                status=status.HTTP_404_NOT_FOUND, message=str(hyperpay_response_description), data=str(data))
        return response
    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="User is not approved to place the order")
        return common_msg


def get_all_orders(offset, customer_id, db: Session):
    
    offset_int = int(offset)
    limit_value = db.execute(
        f"select value from {constants.Database_name}.settings where id = 15 ;")
    for value in limit_value:
        limit_val = int(value[0])
    orders_data = db.execute(
        f'SELECT t1.*, t2.id as transaction_id, t2.payment_mode_id, t2.payment_status_id , t2.invoices_id, t4.name as payment_mode , t3.name as payment_status FROM {constants.Database_name}.orders t1 inner join {constants.Database_name}.order_transactions t2 on t1.id = t2.order_id inner join {constants.Database_name}.status_master t3 on  t3.id = t2.payment_status_id inner join {constants.Database_name}.status_master t4 on t4.id = t2.payment_mode_id  where customer_id = {customer_id} and is_shown = true order by t1.id DESC limit {offset_int},{limit_val};')
    if orders_data.rowcount > 0:
        order_list = []
        for data in orders_data:
            order_details_data = db.execute(
                f'select * from {constants.Database_name}.order_details where order_id = {data.id}')
            order_product_list = []
            product_count = order_details_data.rowcount
            logs_list = []
            delivery_logs_data = db.execute(
                f"select m.id,m.name,m.description,d.log_date from status_master as m inner join order_delivery_logs as d ON m.id = d.order_status_id where d.order_id={data.id} and d.customer_view = 1 order by d.id ")
            for log_data in delivery_logs_data:
                log_date = str(log_data.log_date.strftime("%Y-%m-%d %H:%M:%S"))

                data_logs = order_schemas.OrderByIdDeliveryLogs(
                    id=log_data.id, status_name=log_data.name, status_description=log_data.description, log_date=log_date)
                logs_list.append(data_logs)
            last_log = []
            try:
                last_log.append(logs_list[-1])
            except:
                last_log = []
            for data2 in order_details_data:
                prod_data = db.execute(
                    f"select * from {constants.Database_name}.products_master where id = {data2.product_id}")
                for i in prod_data:
                    # quantity_unit = i.quantity_unit_id
                    # weight_unit = i.weight_unit_id
                    quantity_unit = i.quantity_unit_id if i.quantity_unit_id else 1
                    weight_unit = i.weight_unit_id if i.weight_unit_id else 1
                    if i.primary_image:
                        primary_img = i.primary_image
                        # img_name = primary_img.split("/")[-1]
                        image_path = constants.IMAGES_DIR_PATH + primary_img
                    else:
                        image_path = "null"
                    unit1 = db.execute(
                        f"select unit_name from {constants.Database_name}.unit_master where id = {quantity_unit}")
                    unit2 = db.execute(
                        f"select unit_name from {constants.Database_name}.unit_master where id = {weight_unit}")
                    prod_images = db.execute(
                        f"select image from {constants.Database_name}.product_images where product_id = {data2.product_id}")
                    image_list = []
                    for image in prod_images:
                        a = image[0]
                        # update_img = a.split("/")[-1]
                        upd_image_path = constants.IMAGES_DIR_PATH + a
                        image_list.append(upd_image_path)

                    for j in unit1:
                        for k in unit2:
                            intial_price = float(i.price)
                            wayrem_margin = i.wayrem_margin if i.wayrem_margin else 0
                            if i.margin_unit == '%':
                                margin_value = (intial_price/100) * \
                                    int(wayrem_margin)
                                updated_price = intial_price+margin_value
                            else:
                                updated_price = intial_price + \
                                    float(wayrem_margin)
                    var2 = i.id
                    result = None
                    rates = db.execute(
                        f"select * from {constants.Database_name}.product_rating where product_id= {var2}")
                    for rate in rates:
                        result = rate.rating
                    qty = int(i.quantity)
                    qty_thresold = i.outofstock_threshold
                    final_qty = qty
                    data3 = order_schemas.OrdersProducts(product_id=data2.product_id, ordered_product_quantity=data2.quantity, stock_quantity=final_qty, name=i.name, SKU=i.SKU, mfr_name=i.mfr_name, description=i.description,
                                                         quantity_unit=j[0], threshold=qty_thresold, weight=i.weight, weight_unit=k[0], price=updated_price, discount=i.discount, discount_unit=i.dis_abs_percent, primary_image=image_path, images=image_list, rating=result)
                order_product_list.append(data3)

                vat_value = db.execute(
                    f"select value from {constants.Database_name}.settings where id = 7 ;")
                for i in vat_value:
                    vat_prcnt_value = int(i[0])
                    vat_with_prcnt = str(vat_prcnt_value)
                payment_type = data.payment_mode
                payment_status = data.payment_status
                order_date = data.order_date
                date = str(order_date.strftime("%Y-%m-%d %H:%M:%S"))
                order_status = data.status

                order_type = data.order_type
                order_type_data = db.execute(
                    f"select * from {constants.Database_name}.status_master where id = {order_type}")
                for type_value in order_type_data:
                    order_value = type_value.name

            data_order = order_schemas.OrderDetails(order_id=data.id, order_ref_no=data.ref_number, sub_total=data.sub_total, item_discount=data.item_discount, tax_vat=vat_with_prcnt, total=data.total, grand_total=data.grand_total, email=data.order_email, contact=data.order_phone, country=data.order_country, city=data.order_city, billing_name=data.order_billing_name,
                                                    billing_address=data.order_billing_address, shipping_name=data.order_ship_name, shipping_address=data.order_ship_address, payment_type=payment_type, payment_status=payment_status, order_date=date, product_count=product_count, order_status=order_status, order_type=order_value, invoice_id=data.invoices_id, delivery_logs=last_log, products=order_product_list)
            order_list.append(data_order)

        data4 = order_schemas.ResponseMyOrders(
            customer_id=data.customer_id, orders=order_list)
        response = order_schemas.FinalOrderResponse(
            status=status.HTTP_200_OK, message="Orders details!", data=data4)
        return response

    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No Orders found!")
        return common_msg


def get_order_details(order_id, db: Session):
    
    orders_data = db.execute(
        f'SELECT t1.*, t2.id as transaction_id, t2.payment_mode_id,t2.bank_payment_image, t2.payment_status_id , t2.invoices_id, t4.name as payment_mode , t3.name as payment_status FROM {constants.Database_name}.orders t1 inner join {constants.Database_name}.order_transactions t2 on t1.id = t2.order_id inner join {constants.Database_name}.status_master t3 on  t3.id = t2.payment_status_id inner join {constants.Database_name}.status_master t4 on t4.id = t2.payment_mode_id  where t1.id = {order_id};')
    if orders_data.rowcount > 0:
        order_product_list = []
        order_list = []
        logs_list = []
        for data in orders_data:
            final_bank_re = None
            if data.bank_payment_image:
                final_bank_re = constants.BANK_PAYMENT_IMAGES_PATH + data.bank_payment_image
                
            order_details_data = db.execute(
                f'select * from {constants.Database_name}.order_details where order_id = {data.id}')
            for data2 in order_details_data:
                product_count = order_details_data.rowcount
                prod_data = db.execute(
                    f"select * from {constants.Database_name}.products_master where id = {data2.product_id}")
                for i in prod_data:
                    # quantity_unit = i.quantity_unit_id
                    # weight_unit = i.weight_unit_id
                    quantity_unit = i.quantity_unit_id if i.quantity_unit_id else 1
                    weight_unit = i.weight_unit_id if i.weight_unit_id else 1
                    if i.primary_image:
                        primary_img = i.primary_image
                        # img_name = primary_img.split("/")[-1]
                        image_path = constants.IMAGES_DIR_PATH + primary_img
                    else:
                        image_path = "null"
                    unit1 = db.execute(
                        f"select unit_name from {constants.Database_name}.unit_master where id = {quantity_unit}")
                    unit2 = db.execute(
                        f"select unit_name from {constants.Database_name}.unit_master where id = {weight_unit}")
                    prod_images = db.execute(
                        f"select image from {constants.Database_name}.product_images where product_id = {data2.product_id}")
                    image_list = []
                    for image in prod_images:
                        a = image[0]
                        # update_img = a.split("/")[-1]
                        upd_image_path = constants.IMAGES_DIR_PATH + a
                        image_list.append(upd_image_path)

                    for j in unit1:
                        for k in unit2:
                            intial_price = float(i.price)
                            wayrem_margin = i.wayrem_margin if i.wayrem_margin else 0
                            if i.margin_unit == '%':
                                margin_value = (intial_price/100) * \
                                    int(wayrem_margin)
                                updated_price = intial_price+margin_value
                            else:
                                updated_price = intial_price + \
                                    float(wayrem_margin)
                    var2 = i.id
                    result = None
                    rev = None
                    rat_rev = db.execute(
                        f"select * from {constants.Database_name}.rating_review where product_id = {var2} and customer_id={data.customer_id}")
                    if rat_rev:
                        for temp in rat_rev:
                            rev = temp.review
                            result = temp.rating

                    new_data = db.execute(
                        f"select * from {constants.Database_name}.order_details where order_details.order_id={order_id} and {data2.product_id} = order_details.product_id ").first()
                    intial_prc = new_data.price
                    unit_margin = new_data.item_margin
                    final_ordered_price = intial_prc + unit_margin
                    dis = new_data.discount
                    qua = new_data.quantity

                    qty = int(i.quantity)
                    qty_thresold = i.outofstock_threshold
                    final_qty = qty
                    data3 = order_schemas.OrdersProducts(product_id=data2.product_id, ordered_product_quantity=qua, stock_quantity=final_qty, name=i.name, SKU=i.SKU, mfr_name=i.mfr_name, description=i.description,
                                                         quantity_unit=j[0], threshold=qty_thresold, weight=i.weight, weight_unit=k[0], price=final_ordered_price, discount=dis, primary_image=image_path, images=image_list, rating=result, review=rev)
                order_product_list.append(data3)

                vat_value = db.execute(
                    f"select value from {constants.Database_name}.settings where id = 7 ;")
                for i in vat_value:
                    vat_prcnt_value = int(i[0])
                    vat_with_prcnt = str(vat_prcnt_value)
                payment_type = data.payment_mode
                payment_status = data.payment_status
                order_date = data.order_date
                date = str(order_date.strftime("%Y-%m-%d %H:%M:%S"))
                order_status = data.status

            delivery_logs_data = db.execute(
                f"select m.id,m.name,m.description,d.log_date from status_master as m inner join order_delivery_logs as d ON m.id = d.order_status_id where d.order_id={data.id} and d.customer_view = 1 order by d.log_date ")
            for log_data in delivery_logs_data:
                log_date = str(log_data.log_date.strftime("%Y-%m-%d %H:%M:%S"))

                data_logs = order_schemas.OrderByIdDeliveryLogs(
                    id=log_data.id, status_name=log_data.name, status_description=log_data.description, log_date=log_date)
                logs_list.append(data_logs)
            if data.delivery_charge:
                delivery_charge = data.delivery_charge
            else:
                delivery_charge = 0

            order_type = data.order_type
            order_type_data = db.execute(
                f"select * from {constants.Database_name}.status_master where id = {order_type}")
            for type_value in order_type_data:
                order_value = type_value.name

            # invoice_link = f"http://15.185.103.226/orders/invoice-order/{data.invoices_id}"
            invoice_link = None
            if data.invoices_id:
                invoice_link = f"{constants.global_link}/orders/invoice-orders/{data.ref_number}"
            
            
            data_order = order_schemas.OrderDetailsbyid(order_id=data.id, order_ref_no=data.ref_number, sub_total=data.sub_total, item_discount=data.item_discount, tax_vat=vat_with_prcnt, total=data.total, grand_total=data.grand_total, email=data.order_email, contact=data.order_phone, country=data.order_country, city=data.order_city, billing_name=data.order_billing_name,
                                                        billing_address=data.order_billing_address, shipping_name=data.order_ship_name, shipping_address=data.order_ship_address, payment_type=payment_type, payment_status=payment_status, order_date=date, product_count=product_count, order_status=order_status, order_type=order_value, invoice_id=data.invoices_id, invoice_link=invoice_link, delivery_charges=delivery_charge,
bank_receipt=final_bank_re, order_delivery_logs=logs_list, products=order_product_list)
            order_list.append(data_order)
        data4 = order_schemas.ResponseMyOrdersbyid(
            customer_id=data.customer_id, orders=order_list)

        response = order_schemas.FinalOrderResponsebyid(
            status=status.HTTP_200_OK, message="Order details!", data=data4)
        return response

    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No Orders found!")
        return common_msg


def create_recurrence_order(request, db: Session):
    
    grocery = db.query(order_models.UserGrocery).filter(order_models.UserGrocery.id ==
                                                        request.grocery_id, order_models.UserGrocery.customer_id == request.customer_id).first()
    if not grocery:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="grocery id not found for this user!")
        return common_msg
    recurrent_grocery = db.query(order_models.RecurrenceGrocery).filter(order_models.RecurrenceGrocery.grocery_id ==
                                                                        request.grocery_id, order_models.RecurrenceGrocery.customer_id == request.customer_id).first()
    if recurrent_grocery:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="This grocery is already available in your recurrent order!")
        return common_msg
    if request.recurrenttype == "":
        recurrent_id = 2
    else:
        request_days = db.execute(
            f"select * from {constants.Database_name}.recurrent_type where name = '{request.recurrenttype}' ;")
        for i in request_days:
            recurrent_type_value = int(i.value)
            recurrent_id = i.id
    if request.recurrence_startdate == "":
        recurrence_startdate = "null"
        next_recurrent_date = "null"
    else:
        recurrence_startdate1 = request.recurrence_startdate
        recurrence_startdate = datetime.strptime(
            recurrence_startdate1, '%d-%b-%y')
        next_recurrent = recurrence_startdate + \
            DT.timedelta(days=recurrent_type_value)
        next_recurrent_date = str(next_recurrent.date())

    recurrent_data = order_models.RecurrenceGrocery(customer_id=request.customer_id, grocery_id=request.grocery_id, recurrenttype=recurrent_id,
                                                    recurrence_startdate=recurrence_startdate, recurrence_nextdate=next_recurrent_date, status=request.status)
    db.merge(recurrent_data)
    db.commit()
    grocery_product_update = db.query(order_models.GroceryProducts).filter(
        order_models.GroceryProducts.grocery_id == request.grocery_id).all()
    for j in grocery_product_update:
        j.recurrence_nextdate = next_recurrent_date
        db.merge(j)
        db.commit()
    data = order_schemas.RecurrenceResponse(grocery_id=request.grocery_id, recurrenttype=request.recurrenttype,
                                            recurrence_startdate=request.recurrence_startdate, status=request.status)
    result = order_schemas.RecurrenceFinalResponse(
        status=status.HTTP_200_OK, message="recurrence order created successfully!", customer_id=request.customer_id, data=data)
    return result


def update_recurrence_order(request, db: Session):
    
    recurrent = db.query(order_models.RecurrenceGrocery).filter(
        order_models.RecurrenceGrocery.id == request.recurrent_order_id).first()
    if not recurrent:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="recurrent order id not found!")
        return common_msg

    request_days = db.execute(
        f"select * from {constants.Database_name}.recurrent_type where name = '{request.recurrenttype}' ;")
    for i in request_days:
        recurrent_type_value = int(i.value)
        recurrent_id = i.id
    recurrence_startdate1 = request.recurrence_startdate
    recurrence_startdate = datetime.strptime(recurrence_startdate1, '%d-%b-%y')
    next_recurrent = recurrence_startdate + \
        DT.timedelta(days=recurrent_type_value)
    next_recurrent_date = str(next_recurrent.date())

    recurrent.grocery_id = request.grocery_id
    recurrent.customer_id = request.customer_id
    recurrent.recurrence_startdate = recurrence_startdate
    recurrent.recurrence_nextdate = next_recurrent_date
    recurrent.recurrenttype = recurrent_id
    recurrent.status = request.status
    db.merge(recurrent)
    db.commit()

    grocery_product_update = db.query(order_models.GroceryProducts).filter(
        order_models.GroceryProducts.grocery_id == request.grocery_id).all()
    for j in grocery_product_update:
        j.recurrence_nextdate = next_recurrent_date
        db.merge(j)
        db.commit()
    data = order_schemas.RecurrenceResponse(grocery_id=request.grocery_id, recurrenttype=request.recurrenttype,
                                            recurrence_startdate=request.recurrence_startdate, status=request.status)
    result = order_schemas.RecurrenceFinalResponse(
        status=status.HTTP_200_OK, message="recurrence order Updated successfully!", customer_id=request.customer_id, data=data)
    return result


def get_all_recurrent_type(db: Session):
    
    recurrent_data = db.execute(
        f'select * from {constants.Database_name}.recurrent_type')
    cat_list = []
    for data in recurrent_data:
        res_data = order_schemas.Recurrentdata(
            recurrent_type_id=data.id, recurrent_name=data.name)
        cat_list.append(res_data)
    common_msg = order_schemas.RecurrentResponse(
        status=status.HTTP_200_OK, message="Recurrent type details", data=cat_list)
    return common_msg


def get_delivery_fees(address_id, db: Session):
    
    try:
        delivery_charge_data = db.execute(
            f"""SELECT * FROM {constants.Database_name}.settings WHERE settings.key = 'setting_vat' OR settings.key = 'delivery_fee_distance_charge' OR settings.key = 'delivery_charge_base_fee' OR settings.key = 'delivery_free_charge_after_amount' OR settings.key = 'delivery_free_charge_below_range'OR settings.key = 'shipping_rates_after_basefare' order by id ;""")
        for j in delivery_charge_data:
            if j.key == "setting_vat":
                vat_prcnt_value = float(j.value)
            if j.key == "delivery_charge_base_fee":
                basic_delivery_charge = float(j.value)
            if j.key == "delivery_free_charge_after_amount":
                free_delivery_after_amount = float(j.value)
            if j.key == "delivery_free_charge_below_range":
                free_delivery_before_range = float(j.value)
            if j.key == "delivery_fee_distance_charge":
                fixed_charge_after_range = float(j.value)
            if j.key == "shipping_rates_after_basefare":
                shipping_rates = float(j.value)
        if address_id is not None:
            customer_address = db.query(user_models.CustomerAddresses).filter(
                user_models.CustomerAddresses.id == address_id).first()
            customer_latitude = customer_address.deliveryAddress_latitude
            customer_longitude = customer_address.deliveryAddress_longitude
            warehouse_data = db.execute(
                f"select * from {constants.Database_name}.warehouse where id = 1")
            for i in warehouse_data:
                warehouse_latitude = i.latitude
                warehouse_longitude = i.longitude

            # Requires API key
            gmaps = googlemaps.Client(
                key='AIzaSyCT93vNszQ2b8JQmHqrkDTVJnjVKmHSaTc')
            origin_latitude = float(warehouse_latitude)
            origin_longitude = float(warehouse_longitude)
            destination_latitude = float(customer_latitude)
            destination_longitude = float(customer_longitude)
            distance = gmaps.distance_matrix([str(origin_latitude) + " " + str(origin_longitude)], [str(
                destination_latitude) + " " + str(destination_longitude)], mode='driving')['rows'][0]['elements'][0]
            x = distance.get("distance").get('value')
            distance_in_km = float(x/1000)

            if distance_in_km <= free_delivery_before_range:
                delivery_fees = 0
            if distance_in_km > free_delivery_before_range:
                basic_charge = basic_delivery_charge
                include_fees_after_km = fixed_charge_after_range
                y = distance_in_km/include_fees_after_km
                z = math.ceil(y)-1
                fees = (z-1)*shipping_rates
                delivery_fees = fees + basic_charge

            data1 = order_schemas.Deliveryfeedata(
                delivery_fees=delivery_fees, free_delivery_after_amount=free_delivery_after_amount, vat_value=vat_prcnt_value)
            common_msg = order_schemas.Getdeliveryfees(
                status=status.HTTP_200_OK, message="Delivery fees and vat details ", data=data1)
            return common_msg

        data1 = order_schemas.Deliveryfeedata(
            free_delivery_after_amount=free_delivery_after_amount, vat_value=vat_prcnt_value)
        common_msg = order_schemas.Getdeliveryfees(
            status=status.HTTP_200_OK, message="Delivery fees and vat details ", data=data1)
        return common_msg
    except:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Your location is not acceptable!!")
        return common_msg


def get_filters_orders(offset, customer_id, filter_id, db: Session):
    
    offset_int = int(offset)
    limit_value = db.execute(
        f"select value from {constants.Database_name}.settings where id = 15 ;")
    for value in limit_value:
        limit_val = int(value[0])
    orders_data = db.execute(
        f'SELECT t1.*, t2.id as transaction_id, t2.payment_mode_id, t2.payment_status_id , t2.invoices_id, t4.name as payment_mode , t3.name as payment_status FROM {constants.Database_name}.orders t1 inner join {constants.Database_name}.order_transactions t2 on t1.id = t2.order_id inner join {constants.Database_name}.status_master t3 on  t3.id = t2.payment_status_id inner join {constants.Database_name}.status_master t4 on t4.id = t2.payment_mode_id  where customer_id = {customer_id} and delivery_status = {filter_id} order by t1.id DESC limit {offset_int},{limit_val};')
    if orders_data.rowcount > 0:
        order_list = []
        for data in orders_data:
            order_details_data = db.execute(
                f'select * from {constants.Database_name}.order_details where order_id = {data.id}')
            order_product_list = []
            product_count = order_details_data.rowcount
            logs_list = []
            delivery_logs_data = db.execute(
                f"select m.id,m.name,m.description,d.log_date from status_master as m inner join order_delivery_logs as d ON m.id = d.order_status_id where d.order_id={data.id} and d.customer_view = 1 order by d.log_date ")
            for log_data in delivery_logs_data:
                log_date = str(log_data.log_date.strftime("%Y-%m-%d %H:%M:%S"))

                data_logs = order_schemas.OrderByIdDeliveryLogs(
                    id=log_data.id, status_name=log_data.name, status_description=log_data.description, log_date=log_date)
                logs_list.append(data_logs)
            last_log = []
            try:
                last_log.append(logs_list[-1])
            except:
                last_log = []
            for data2 in order_details_data:
                prod_data = db.execute(
                    f"select * from {constants.Database_name}.products_master where id = {data2.product_id}")
                for i in prod_data:
                    # quantity_unit = i.quantity_unit_id
                    # weight_unit = i.weight_unit_id
                    quantity_unit = i.quantity_unit_id if i.quantity_unit_id else 1
                    weight_unit = i.weight_unit_id if i.weight_unit_id else 1
                    if i.primary_image:
                        primary_img = i.primary_image
                        # img_name = primary_img.split("/")[-1]
                        image_path = constants.IMAGES_DIR_PATH + primary_img
                    else:
                        image_path = "null"
                    unit1 = db.execute(
                        f"select unit_name from {constants.Database_name}.unit_master where id = {quantity_unit}")
                    unit2 = db.execute(
                        f"select unit_name from {constants.Database_name}.unit_master where id = {weight_unit}")
                    prod_images = db.execute(
                        f"select image from {constants.Database_name}.product_images where product_id = {data2.product_id}")
                    image_list = []
                    for image in prod_images:
                        a = image[0]
                        # update_img = a.split("/")[-1]
                        upd_image_path = constants.IMAGES_DIR_PATH + a
                        image_list.append(upd_image_path)

                    for j in unit1:
                        for k in unit2:
                            intial_price = float(i.price)
                            wayrem_margin = i.wayrem_margin if i.wayrem_margin else 0
                            if i.margin_unit == '%':
                                margin_value = (intial_price/100) * \
                                    int(wayrem_margin)
                                updated_price = intial_price+margin_value
                            else:
                                updated_price = intial_price + \
                                    float(wayrem_margin)
                    var2 = i.id
                    result = None
                    rates = db.execute(
                        f"select * from {constants.Database_name}.product_rating where product_id= {var2}")
                    for rate in rates:
                        result = rate.rating

                    qty = int(i.quantity)
                    qty_thresold = i.outofstock_threshold
                    final_qty = qty
                    data3 = order_schemas.OrdersProducts(product_id=data2.product_id, ordered_product_quantity=data2.quantity, stock_quantity=final_qty, threshold=qty_thresold, name=i.name, SKU=i.SKU, mfr_name=i.mfr_name, description=i.description,
                                                         quantity_unit=j[0], weight=i.weight, weight_unit=k[0], price=updated_price, discount=i.discount, discount_unit=i.dis_abs_percent, primary_image=image_path, images=image_list, rating=result)
                order_product_list.append(data3)

                vat_value = db.execute(
                    f"select value from {constants.Database_name}.settings where id = 7 ;")
                for i in vat_value:
                    vat_prcnt_value = int(i[0])
                    vat_with_prcnt = str(vat_prcnt_value)
                payment_type = data.payment_mode
                payment_status = data.payment_status
                order_date = data.order_date
                date = str(order_date.strftime("%Y-%m-%d %H:%M:%S"))
                order_status = data.status

            order_type = data.order_type
            order_type_data = db.execute(
                f"select * from {constants.Database_name}.status_master where id = {order_type}")
            for type_value in order_type_data:
                order_value = type_value.name

            data_order = order_schemas.OrderDetails(order_id=data.id, order_ref_no=data.ref_number, sub_total=data.sub_total, item_discount=data.item_discount, tax_vat=vat_with_prcnt, total=data.total, grand_total=data.grand_total, email=data.order_email, contact=data.order_phone, country=data.order_country, city=data.order_city, billing_name=data.order_billing_name,
                                                    billing_address=data.order_billing_address, shipping_name=data.order_ship_name, shipping_address=data.order_ship_address, payment_type=payment_type, payment_status=payment_status, order_date=date, product_count=product_count, order_status=order_status, order_type=order_value, invoice_id=data.invoices_id, delivery_logs=last_log, products=order_product_list)
            order_list.append(data_order)

        data4 = order_schemas.ResponseMyOrders(
            customer_id=data.customer_id, orders=order_list)
        response = order_schemas.FinalOrderResponse(
            status=status.HTTP_200_OK, message="Orders details!", data=data4)
        return response

    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No Orders found!")
        return common_msg


def format_string(view_list, image_list):
    x = f""
    for i, j in zip(view_list, image_list):
        pro_name = i.product_name
        pro_qty = i.quantity
        pro_price = i.price
        pro_image_path = j
        x += f"""<tr>
                                            <td width="20%">
                                                <img src="{pro_image_path}" alt="" style="width:100px;height:100px;object-fit:cover;border-radius:16px" class="CToWUd a6T" tabindex="0"><div class="a6S" dir="ltr" style="opacity: 0.01; left: 299px; top: 417.109px;"><div id=":pv" class="T-I J-J5-Ji aQv T-I-ax7 L3 a5q" title="Download" role="button" tabindex="0" aria-label="Download attachment " data-tooltip-class="a1V"><div class="akn"><div class="aSK J-J5-Ji aYr"></div></div></div></div>
                                            </td>
                                            <td width="60%" style="padding-left:0.5rem">
                                                <div>
                                                    <p style="margin:0;color:#152f50">{pro_name}</p>
                                                </div>
                                                <div><span style="color:#a8a8a8;font-size:.8rem">Wayrem Supplier</span></div>
                                                <div><span style="font-weight:600;color:#152f50">{pro_price}sr</span></div>
                                            </td>
                                            <td style="min-width:100px;text-align:end">X {pro_qty}.0
    
                                            </td>
                                    </tr>
                                """
    return x
