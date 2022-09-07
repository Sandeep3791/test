import constants
from sqlalchemy import desc
from schemas import user_schemas, credit_schemas
from models import credit_models, order_models, payment_models, user_models
from sqlalchemy.orm import Session
from fastapi import status, BackgroundTasks
from datetime import date, datetime
import re
from services import payment_services
from sqlalchemy import null, or_
from utility_services import common_services
import os
import random

def get_credits(customer_id, db: Session):
    user_data = db.query(credit_models.CreditManagement).filter(
        credit_models.CreditManagement.customer_id == customer_id).first()
    if user_data:
        rule_id_data = db.query(credit_models.CreditSettings).filter(
            credit_models.CreditSettings.id == user_data.credit_rule_id).first()
        assigned_credit = rule_id_data.credit_amount
        credit_data = credit_schemas.ResponseCustomerCredits(
            id=user_data.id, customer_id=user_data.customer_id, used_credits=user_data.used, available_credits=user_data.available, total_credits=assigned_credit)
        response = credit_schemas.ResponseCustomerCreditsFinal(
            status=status.HTTP_200_OK, message="User Credit Info!", data=credit_data)
        return response
    else:
        credit_data = credit_schemas.ResponseCustomerCredits(
            id=0, customer_id=customer_id, used_credits=0, available_credits=0, total_credits=0)
        response = credit_schemas.ResponseCustomerCreditsFinal(
            status=status.HTTP_200_OK, message="User Credit not found!", data=credit_data)
        return response


def get_credits_txn(customer_id, dues, db: Session):
    if dues == True:
        user_data = db.query(credit_models.CreditTransactionsLog).filter(credit_models.CreditTransactionsLog.customer_id == customer_id,credit_models.CreditTransactionsLog.payment_status == False).order_by(desc(credit_models.CreditTransactionsLog.id)).all()
        txn_list = []
        if user_data:
            for data in user_data:
                paid_credit_data = db.query(credit_models.CreditTransactionsLog).filter(
                        credit_models.CreditTransactionsLog.credit_id == data.id, credit_models.CreditTransactionsLog.payment_status == True).first()
                
                check_credit_id = db.query(credit_models.CreditTransactionsLog).filter(
                        credit_models.CreditTransactionsLog.credit_id == data.id).first()

                if data.reference_id == None and check_credit_id == None:
                    if not paid_credit_data:
                        pending = False
                        user_order_data = db.query(order_models.Orders).filter(
                            order_models.Orders.id == data.order_id).first()
                        present_date = datetime.now()
                        if present_date > data.due_date:
                            is_due = False
                        else:
                            is_due = True
                        credit_data = credit_schemas.ResponseCustomerCreditsTxn(id=data.id, credit_amount=data.credit_amount, available=data.available, credit_date=str(
                            common_services.utc_to_tz(data.credit_date)), payment_status=data.payment_status, order_ref_no=[credit_schemas.OrdersRefNumber(order_ref_no = user_order_data.ref_number, order_amount = user_order_data.grand_total, order_due_time = str(
                            common_services.utc_to_tz(data.due_date)))], valid_date=is_due, is_refund=data.is_refund,bank_pending=pending)
                        txn_list.append(credit_data)
                elif data.reference_id != None:
                    if not paid_credit_data:
                        check_reject_payment = db.query(credit_models.CreditPaymentReference).filter(credit_models.CreditPaymentReference.id == data.reference_id).first()
                        if check_reject_payment:
                            if check_reject_payment.payment_status_id == 26:
                                payment_rejection = True
                                pending = False
                                present_date = datetime.now()
                                if present_date > data.due_date:
                                    is_due = False
                                else:
                                    is_due = True
                                rejected_orders = db.query(credit_models.CreditTransactionsLog).filter(credit_models.CreditTransactionsLog.reference_id == data.reference_id).all()
                                orders_list = []
                                total_credit_amount = 0
                                for order_var in rejected_orders:
                                    user_order_data = db.query(order_models.Orders).filter(
                                                order_models.Orders.id == order_var.order_id).first()
                                    total_credit_amount += user_order_data.grand_total
                                    orders_list.append(credit_schemas.OrdersRefNumber(order_ref_no = user_order_data.ref_number, order_amount = user_order_data.grand_total, order_due_time = str(
                                    common_services.utc_to_tz(order_var.due_date))))
                                credit_data = credit_schemas.ResponseCustomerCreditsTxn(id=data.id, credit_amount = total_credit_amount, available=data.available, credit_date=str(
                                common_services.utc_to_tz(data.credit_date)), payment_status=data.payment_status, order_ref_no=orders_list, valid_date=is_due, is_refund=data.is_refund, bank_pending=pending, bank_reject = payment_rejection, transaction_ref_id = check_reject_payment.id, transaction_ref_no = check_reject_payment.reference_no, transaction_creation_date = str(
                                    common_services.utc_to_tz(check_reject_payment.created_at)))
                                txn_list.append(credit_data)
                            
                            elif check_reject_payment.payment_status_id == 27:
                                payment_rejection = False
                                pending = True
                                present_date = datetime.now()
                                if present_date > data.due_date:
                                    is_due = False
                                else:
                                    is_due = True
                                rejected_orders = db.query(credit_models.CreditTransactionsLog).filter(credit_models.CreditTransactionsLog.reference_id == data.reference_id).all()
                                orders_list = []
                                total_credit_amount = 0
                                
                                if check_reject_payment.bank_payment_file and check_reject_payment.payment_status_id == 6:
                                    bank_docs = constants.BANK_PAYMENT_IMAGES_PATH + check_reject_payment.bank_payment_file
                                else:
                                    bank_docs = None

                                for order_var in rejected_orders:
                                    user_order_data = db.query(order_models.Orders).filter(
                                                order_models.Orders.id == order_var.order_id).first()
                                    total_credit_amount += user_order_data.grand_total
                                    orders_list.append(credit_schemas.OrdersRefNumber(order_ref_no = user_order_data.ref_number, order_amount = user_order_data.grand_total, order_due_time = str(
                                    common_services.utc_to_tz(order_var.due_date))))
                                credit_data = credit_schemas.ResponseCustomerCreditsTxn(id=data.id, credit_amount = total_credit_amount, available=data.available, credit_date=str(
                                common_services.utc_to_tz(data.credit_date)), payment_status=data.payment_status, order_ref_no=orders_list, valid_date=is_due, is_refund=data.is_refund, bank_pending=pending, bank_reject = payment_rejection, transaction_ref_id = check_reject_payment.id, transaction_creation_date = str(
                                    common_services.utc_to_tz(check_reject_payment.created_at)), bank_details = bank_docs)
                                txn_list.append(credit_data)
 
            response = credit_schemas.ResponseCustomerCreditsTxnFinal(
                status=status.HTTP_200_OK, message="User Credit Dues!", data=txn_list)
            return response
        else:
            common_msg = user_schemas.ResponseCommonMessage(
                status=status.HTTP_200_OK, message="No user credit dues found!")
            return common_msg
    else:
        user_data = db.query(credit_models.CreditTransactionsLog).filter(
            credit_models.CreditTransactionsLog.customer_id == customer_id).order_by(desc(credit_models.CreditTransactionsLog.id)).all()

        transacted_data = db.query(credit_models.CreditTransactionsLog).filter(credit_models.CreditTransactionsLog.customer_id == customer_id, credit_models.CreditTransactionsLog.payment_status == True, credit_models.CreditTransactionsLog.reference_id != None).all()
        
        txn_list = []
        if user_data:
            for data in user_data:
                bank_paid_credit = db.query(credit_models.CreditTransactionsLog).filter(credit_models.CreditTransactionsLog.id == data.id, credit_models.CreditTransactionsLog.payment_status == False,credit_models.CreditTransactionsLog.reference_id == None).first()
                if bank_paid_credit:
                    user_order_data = db.query(order_models.Orders).filter(
                        order_models.Orders.id == data.order_id).first()
                    present_date = datetime.now()
                    if data.due_date:
                        if present_date > data.due_date:
                            is_due = False
                        else:
                            is_due = True
                    else:
                        is_due = True

                    credit_data = credit_schemas.ResponseCustomerCreditsTxn(id=data.id, credit_amount=data.credit_amount, available=data.available, credit_date=str(
                        common_services.utc_to_tz(data.credit_date)), payment_status=data.payment_status, order_ref_no=[credit_schemas.OrdersRefNumber(order_ref_no = user_order_data.ref_number, order_amount = user_order_data.grand_total, order_due_time = str(common_services.utc_to_tz(data.due_date)))], valid_date=is_due, paid_date=str(common_services.utc_to_tz(data.paid_date)),
                        paid_amount=data.paid_amount, paid_credit_id=data.credit_id, is_refund=data.is_refund)

                    txn_list.append(credit_data)

        if transacted_data:
            distinct_ref_id = []
            for trans_var in transacted_data:
                if trans_var.reference_id not in distinct_ref_id:
                    distinct_ref_id.append(trans_var.reference_id)

            for ref_id_var in distinct_ref_id:
                paid_data = db.query(credit_models.CreditTransactionsLog).filter(credit_models.CreditTransactionsLog.customer_id, credit_models.CreditTransactionsLog.reference_id == ref_id_var).all()

                payment_ref_details = db.query(credit_models.CreditPaymentReference).filter(credit_models.CreditPaymentReference.id == ref_id_var).first()

                if paid_data:
                    orders_list = []
                    total_credit_amount = 0
                    for data_var in paid_data:
                        present_date = datetime.now()
                        if data_var.due_date:
                            if present_date > data_var.due_date:
                                is_due = False
                            else:
                                is_due = True
                        else:
                            is_due = True
                        order_data = db.query(order_models.Orders).filter(
                                    order_models.Orders.id == data_var.order_id).first()
                        total_credit_amount += order_data.grand_total
                        orders_list.append(credit_schemas.OrdersRefNumber(order_ref_no = order_data.ref_number, order_amount = order_data.grand_total, order_due_time = str(
                        common_services.utc_to_tz(data_var.due_date))))

                    credit_data = credit_schemas.ResponseCustomerCreditsTxn(id=data_var.id, credit_amount = total_credit_amount, available=data_var.available, credit_date=str(
                    common_services.utc_to_tz(data_var.credit_date)), payment_status=data_var.payment_status, order_ref_no=orders_list, valid_date=is_due, is_refund=data_var.is_refund, transaction_ref_id = payment_ref_details.id, transaction_ref_no = payment_ref_details.reference_no, transaction_creation_date = str(
                        common_services.utc_to_tz(payment_ref_details.created_at)))
                    txn_list.append(credit_data)

            txn_list = sorted(txn_list, key=lambda d: d.id,  reverse=True) 
            response = credit_schemas.ResponseCustomerCreditsTxnFinal(
                status=status.HTTP_200_OK, message="User Credit Transactions!", data=txn_list)
            return response
        else:
            common_msg = user_schemas.ResponseCommonMessage(
                status=status.HTTP_200_OK, message="No user credits transactions found!")
            return common_msg


def get_overdue_credits(customer_id, db: Session):
    present_date = datetime.now()
    user_data = db.query(credit_models.CreditManagement).filter(
        credit_models.CreditManagement.customer_id == customer_id).first()

    if user_data:
        unpaid_credit_data = db.query(credit_models.CreditTransactionsLog).filter(
            credit_models.CreditTransactionsLog.customer_id == customer_id, credit_models.CreditTransactionsLog.payment_status == False,credit_models.CreditTransactionsLog.credit_id==None).order_by(desc(credit_models.CreditTransactionsLog.id)).all()
        due_credit_data = None
        for i in unpaid_credit_data:
            paid_credit_data = db.query(credit_models.CreditTransactionsLog).filter(
                credit_models.CreditTransactionsLog.credit_id == i.id, credit_models.CreditTransactionsLog.payment_status == True).first()
            if not paid_credit_data:
                bank_paid_credit = db.query(credit_models.CreditTransactionsLog).filter(
                credit_models.CreditTransactionsLog.credit_id == i.id, credit_models.CreditTransactionsLog.payment_status == False).first()
                if bank_paid_credit:
                    pending = True
                else:
                    pending = False
                credit_due_date = i.due_date
                user_order_data = db.query(order_models.Orders).filter(
                    order_models.Orders.id == i.order_id).first()
                if present_date > credit_due_date:
                    due_credit_data = credit_schemas.ResponseCustomerCreditsTxn(id=i.id, credit_amount=i.credit_amount, available=i.available, credit_date=str(
                        common_services.utc_to_tz(i.credit_date)), due_date=str(common_services.utc_to_tz(i.due_date)), payment_status=i.payment_status, order_ref_no=user_order_data.ref_number, is_refund=i.is_refund,bank_pending=pending)
        response = credit_schemas.ResponseCustomerCreditDue(
            status=status.HTTP_200_OK, message="User Overdue Credit Info!", data=due_credit_data)
        return response
    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No user credits found!")
        return common_msg


def pay_overdue_credits(request, db: Session):
    reference_number = random.randint(1000, 999999)
    same_credit_ref_no = db.query(credit_models.CreditPaymentReference).filter(
        credit_models.CreditPaymentReference.reference_no == reference_number).first()
    if same_credit_ref_no:
        reference_number = random.randint(999999, 99999999)
    reference = credit_models.CreditPaymentReference(customer_id=request.customer_id,reference_no=reference_number,payment_type_id=14)
    db.merge(reference)
    db.commit()
    SUCCESS_CODES_REGEX = re.compile(r'^(000\.000\.|000\.100\.1|000\.[36])')
    SUCCESS_MANUAL_REVIEW_CODES_REGEX = re.compile(
        r'^(000\.400\.0[^3]|000\.400\.[0-1]{2}0)')
    PENDING_CHANGEABLE_SOON_CODES_REGEX = re.compile(r'^(000\.200)')
    PENDING_NOT_CHANGEABLE_SOON_CODES_REGEX = re.compile(
        r'^(800\.400\.5|100\.400\.500)')
    hyperpay_response = None
    hyperpay_response_description = None

    payment_status = payment_services.HyperPayResponseView(
        request.entityId).get_payment_status(request.checkout_id)

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

    if request.credit_dues_ids:
        reference_number_obj = db.query(credit_models.CreditPaymentReference).filter(credit_models.CreditPaymentReference.reference_no == reference_number,credit_models.CreditPaymentReference.customer_id == request.customer_id).first()
        for i in request.credit_dues_ids:
            exist_credit_info = db.query(credit_models.CreditTransactionsLog).filter(
                credit_models.CreditTransactionsLog.credit_id == i).first()
            if not exist_credit_info:
                credit_info = db.query(credit_models.CreditTransactionsLog).filter(
                    credit_models.CreditTransactionsLog.id == i, credit_models.CreditTransactionsLog.payment_status == False).first()
                present_date = common_services.get_time()
                amount_to_paid = credit_info.credit_amount
                available_limit = credit_info.available
                exist_credit_date = credit_info.credit_date
                exist_due_date = credit_info.due_date

                if credit_info:
                    if float(request.amount) >= float(amount_to_paid):
                        new_available_limit = available_limit + amount_to_paid
                        paid_data = credit_models.CreditTransactionsLog(credit_date=exist_credit_date, due_date=exist_due_date, credit_id=i, paid_date=present_date,
                                                                        paid_amount=amount_to_paid, payment_status=True, order_id=credit_info.order_id, customer_id=request.customer_id, 
                                                                        available=new_available_limit,reference_id=reference_number_obj.id)
                        db.merge(paid_data)
                        db.commit()
                        user_Credit_data = db.query(credit_models.CreditManagement).filter(
                            credit_models.CreditManagement.customer_id == request.customer_id).first()
                        available_amt = float(user_Credit_data.available)
                        user_Credit_data.available = round(
                            available_amt + float(amount_to_paid), 2)
                        db.merge(user_Credit_data)
                        db.commit()
            else:
                response = user_schemas.ResponseCommonMessage(
                    status=status.HTTP_400_BAD_REQUEST, message="Dues for this ids are already paid!!")
                return response
        data = credit_schemas.CreditDuesResponse(total_amount=request.amount, date=str(
            common_services.utc_to_tz(present_date)), customer_id=request.customer_id)
        data2 = credit_schemas.FinalDuesPayResponse(
            status=status.HTTP_200_OK, message="credit paid successfully!", data=data)
        return data2

    else:
        response = user_schemas.ResponseCommonMessage(
            status=status.HTTP_424_FAILED_DEPENDENCY, message="Please provide credit id's!!")
        return response


def upload_credit_bank_payment_image(customer_id, reference_no, image, db: Session):
    reference_number_obj = db.query(credit_models.CreditPaymentReference).filter(credit_models.CreditPaymentReference.reference_no == reference_no,credit_models.CreditPaymentReference.customer_id == customer_id).first()
    if not reference_number_obj:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Credit Reference not found")
        return common_msg

    path = os.path.abspath('.')

    image_path = os.path.join(path, 'common_folder')
    inner_image_path = os.path.join(image_path, 'customer_banks')
    filepath = image.filename
    extension = filepath.split(".")[-1]
    db_path = f"bank_payment_creditRef-{reference_no}."+extension
    stored_path = os.path.join(
        inner_image_path, db_path)

    if os.path.exists(stored_path):
        os.remove(stored_path)

    with open(os.path.join(stored_path), "wb+") as file_object:
        file_object.write(image.file.read())
        file_object.close()

    reference_number_obj.bank_payment_file = db_path
    reference_number_obj.payment_status_id = 27
    db.merge(reference_number_obj)
    db.commit()
    prfl_path = user_schemas.UploadProfiledata(path=db_path)
    common_msg = user_schemas.UploadProfile(
        status=status.HTTP_200_OK, message="success", data=prfl_path)
    return common_msg
    # try:
    #     customer_data = db.execute(
    #         f"select * from {constants.Database_name}.customer_device where customer_id = {customer_id} and is_active=True ;")

    #     setting_message = db.execute(
    #         f"select * from {constants.Database_name}.settings where settings.key = 'credit_bank_receipt_upload_notification' ;")

    #     for msg in setting_message:
    #         message = msg.value
    #         title_message = msg.display_name
    #     values = {
    #         "order_ref_no": reference_no
    #     }

    #     message = message.format(**values)

    #     if customer_data:
    #         for data in customer_data:
    #             notf = firebase_schemas.PushNotificationFirebase(
    #                 title=title_message, message=message, device_token=data.device_id, order_id=order_id)
    #             firebase_services.push_notification_in_firebase(notf)

    #         if notf:
    #             fire = firebase_models.CustomerNotification(
    #                 customer_id=customer_id, order_id=order_id, title=notf.title, message=notf.message, created_at=common_services.get_time())
    #             db.merge(fire)
    #             db.commit()
    # except Exception as e:
    #     print(e)
    # return common_msg

def user_credit_request(request, db: Session, background_tasks: BackgroundTasks, confirm):
    user_data = db.query(user_models.User).filter(
        user_models.User.id == request.customer_id).first()

    if user_data:
        credit_request_check = db.query(credit_models.UserCreditRequest).filter(
            credit_models.UserCreditRequest.customer_id == request.customer_id).first()
        if not credit_request_check:
            requested_data = credit_models.UserCreditRequest(
                customer_id=request.customer_id, requested_amount=request.requested_amount)
            db.merge(requested_data)
            db.commit()
            saved_data = credit_schemas.UserCreditResponse(
                customer_id=request.customer_id, requested_amount=request.requested_amount)
            email_query = f"SELECT * FROM {constants.Database_name}.email_template where email_template.key = 'credit_request_customer' "
            emails = db.execute(email_query)
            for email in emails:
                subject = email.subject.format(customer=user_data.first_name)
                body = email.message_format
            emails_query = db.execute(
                f"SELECT email FROM {constants.Database_name}.users_master where is_superuser=True or role_id in (SELECT role_id FROM {constants.Database_name}.role_permissions where function_id = (SELECT id FROM {constants.Database_name}.function_master where codename = 'credits.request_notification')) ")

            raw_email_data = emails_query.mappings().all()
            email_list = []
            for i in range(len(raw_email_data)):
                admin_e = raw_email_data[i].email
                email_list.append(admin_e)
            values = {
                'customer': f"{user_data.first_name} {user_data.last_name}",
                'amount': request.requested_amount
            }
            body = body.format(**values)
            for to in email_list:
                background_tasks.add_task(
                    common_services.send_otp, to, subject, body, request, db)
            result = credit_schemas.FinalUserCreditResponse(
                status=status.HTTP_200_OK, message="Your credit request has been forwarded to admin", data=saved_data)
            return result
        else:
            if confirm == False:
                response = user_schemas.ResponseCommonMessage(
                    status=status.HTTP_208_ALREADY_REPORTED,
                    message=f"You have already requested the credit for the amount of {round(credit_request_check.requested_amount)} SAR. Do you want to change to the newly requested credit amount to {round(request.requested_amount)} SAR?"
                )
                return response
            if confirm == True:
                credit_request_check.requested_amount = request.requested_amount
                db.merge(credit_request_check)
                db.commit()
                response = user_schemas.ResponseCommonMessage(
                    status=status.HTTP_200_OK, message=f"The newly requested credit amount of {round(request.requested_amount)} SAR is saved successfully."
                )
                return response
    else:
        response = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Customer id not found!!")
        return response


def check_user_credit(customer_id, db: Session):
    user_data = db.query(user_models.User).filter(
        user_models.User.id == customer_id).first()

    if user_data:
        new_user = False
        credit_exist = db.query(credit_models.CreditManagement).filter(
            credit_models.CreditManagement.customer_id == customer_id).first()
        if credit_exist:
            new_user = False
            fetched_credit = credit_schemas.CreditCheckNewUser(
                new_user=new_user)
        else:
            new_user = True
            fetched_credit = credit_schemas.CreditCheckNewUser(
                new_user=new_user)
        response = credit_schemas.CheckUserCredit(
            status=status.HTTP_200_OK, message="Successfully fetched!!", data=fetched_credit)
        return response
    else:
        response = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Customer id not found!!")
        return response



def pay_overdue_credits_ByBank(request, db: Session):
    reference_number = random.randint(1000, 999999)
    same_credit_ref_no = db.query(credit_models.CreditPaymentReference).filter(
        credit_models.CreditPaymentReference.reference_no == reference_number).first()
    if same_credit_ref_no:
        reference_number = random.randint(999999, 99999999)
    reference = credit_models.CreditPaymentReference(customer_id=request.customer_id,reference_no=reference_number,payment_type_id=12)
    db.merge(reference)
    db.commit()
    if request.credit_dues_ids:
        reference_number_obj = db.query(credit_models.CreditPaymentReference).filter(credit_models.CreditPaymentReference.reference_no == reference_number,credit_models.CreditPaymentReference.customer_id == request.customer_id).first()
        for i in request.credit_dues_ids:
            exist_credit_info = db.query(credit_models.CreditTransactionsLog).filter(
                credit_models.CreditTransactionsLog.credit_id == i).first()
            if not exist_credit_info:
                credit_info = db.query(credit_models.CreditTransactionsLog).filter(
                    credit_models.CreditTransactionsLog.id == i, credit_models.CreditTransactionsLog.payment_status == False).first()
                present_date = common_services.get_time()
                amount_to_paid = credit_info.credit_amount
                available_limit = credit_info.available
                exist_credit_date = credit_info.credit_date
                exist_due_date = credit_info.due_date

                if credit_info:
                    if float(request.amount) >= float(amount_to_paid):
                        new_available_limit = available_limit + amount_to_paid
                        paid_data = credit_models.CreditTransactionsLog(credit_date=exist_credit_date, due_date=exist_due_date, credit_id=i, paid_date=present_date,
                                                                        paid_amount=amount_to_paid, payment_status=False, order_id=credit_info.order_id, customer_id=request.customer_id, 
                                                                        available=new_available_limit, reference_id=reference_number_obj.id)
                        db.merge(paid_data)
                        db.commit()
                        user_Credit_data = db.query(credit_models.CreditManagement).filter(
                            credit_models.CreditManagement.customer_id == request.customer_id).first()
                        available_amt = float(user_Credit_data.available)
                        user_Credit_data.available = round(
                            available_amt + float(amount_to_paid), 2)
                        db.merge(user_Credit_data)
                        db.commit()
            else:
                response = user_schemas.ResponseCommonMessage(
                    status=status.HTTP_400_BAD_REQUEST, message="Dues for this ids are already paid!!")
                return response
        data = credit_schemas.CreditDuesResponse(total_amount=request.amount, date=str(
            common_services.utc_to_tz(present_date)), customer_id=request.customer_id,reference_no=reference_number)
        data2 = credit_schemas.FinalDuesPayResponse(
            status=status.HTTP_200_OK, message="credit paid successfully!", data=data)
        return data2

    else:
        response = user_schemas.ResponseCommonMessage(
            status=status.HTTP_424_FAILED_DEPENDENCY, message="Please provide credit id's!!")
        return response


def update_payment_status_id(customer_id, transation_ref_id,  db: Session):

    trans_payment_status_update = db.query(credit_models.CreditPaymentReference).filter(
        credit_models.CreditPaymentReference.customer_id == customer_id,credit_models.CreditPaymentReference. id ==  transation_ref_id).first()
    if trans_payment_status_update:
        trans_payment_status_update.payment_status_id=8

        db.merge(trans_payment_status_update)
        db.commit()

        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_200_OK, message="Payment Cancelled Successfully !")
        return common_msg

    common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="Invalid transation reference_id !")
    return common_msg 