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
        user_data = db.query(credit_models.CreditTransactionsLog).filter(credit_models.CreditTransactionsLog.customer_id == customer_id,
                                                                         credit_models.CreditTransactionsLog.payment_status == False).order_by(desc(credit_models.CreditTransactionsLog.id)).all()
        txn_list = []
        if user_data:
            for data in user_data:
                paid_credit_data = db.query(credit_models.CreditTransactionsLog).filter(
                    credit_models.CreditTransactionsLog.credit_id == data.id, credit_models.CreditTransactionsLog.payment_status == True).first()
                if not paid_credit_data:
                    user_oder_data = db.query(order_models.Orders).filter(
                        order_models.Orders.id == data.order_id).first()
                    present_date = datetime.now()
                    if present_date > data.due_date:
                        is_due = False
                    else:
                        is_due = True
                    credit_data = credit_schemas.ResponseCustomerCreditsTxn(id=data.id, credit_amount=data.credit_amount, available=data.available, credit_date=str(
                        data.credit_date), due_date=str(data.due_date), payment_status=data.payment_status, order_ref_no=user_oder_data.ref_number, valid_date=is_due, is_refund = data.is_refund)
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
        txn_list = []
        if user_data:
            for data in user_data:
                user_oder_data = db.query(order_models.Orders).filter(
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
                    data.credit_date), due_date=str(data.due_date), payment_status=data.payment_status, order_ref_no=user_oder_data.ref_number, valid_date=is_due, paid_date=str(data.paid_date), 
                    paid_amount=data.paid_amount, paid_credit_id=data.credit_id, is_refund = data.is_refund)

                txn_list.append(credit_data)
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
            credit_models.CreditTransactionsLog.customer_id == customer_id, credit_models.CreditTransactionsLog.payment_status == False).order_by(desc(credit_models.CreditTransactionsLog.id)).all()
        due_credit_data = None
        for i in unpaid_credit_data:
            paid_credit_data = db.query(credit_models.CreditTransactionsLog).filter(
                credit_models.CreditTransactionsLog.credit_id == i.id, credit_models.CreditTransactionsLog.payment_status == True).first()
            if not paid_credit_data:
                credit_due_date = i.due_date
                user_oder_data = db.query(order_models.Orders).filter(
                    order_models.Orders.id == i.order_id).first()
                if present_date > credit_due_date:
                    due_credit_data = credit_schemas.ResponseCustomerCreditsTxn(id=i.id, credit_amount=i.credit_amount, available=i.available, credit_date=str(
                        i.credit_date), due_date=str(i.due_date), payment_status=i.payment_status, order_ref_no=user_oder_data.ref_number, is_refund = i.is_refund)
        response = credit_schemas.ResponseCustomerCreditDue(
            status=status.HTTP_200_OK, message="User Overdue Credit Info!", data=due_credit_data)
        return response
    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No user credits found!")
        return common_msg


def pay_overdue_credits(request, db: Session):
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
        for i in request.credit_dues_ids:
            exist_credit_info = db.query(credit_models.CreditTransactionsLog).filter(
                credit_models.CreditTransactionsLog.credit_id == i, credit_models.CreditTransactionsLog.payment_status == True).first()
            if not exist_credit_info:
                credit_info = db.query(credit_models.CreditTransactionsLog).filter(
                    credit_models.CreditTransactionsLog.id == i, credit_models.CreditTransactionsLog.payment_status == False).first()
                present_date = common_services.get_time()
                amount_to_paid = credit_info.credit_amount
                available_limit = credit_info.available
                exist_credit_date = credit_info.credit_date
                exist_due_date = credit_info.due_date

                if credit_info:
                    if request.amount >= amount_to_paid:
                        new_available_limit = available_limit + amount_to_paid
                        paid_data = credit_models.CreditTransactionsLog(credit_date=exist_credit_date, due_date=exist_due_date, credit_id=i, paid_date=present_date,
                                                                        paid_amount=amount_to_paid, payment_status=True, order_id=credit_info.order_id, customer_id=request.customer_id, available=new_available_limit)
                        db.merge(paid_data)
                        db.commit()
                        user_Credit_data = db.query(credit_models.CreditManagement).filter(
                            credit_models.CreditManagement.customer_id == request.customer_id).first()
                        user_Credit_data.available = new_available_limit
                        db.merge(user_Credit_data)
                        db.commit()

            else:
                response = user_schemas.ResponseCommonMessage(
                    status=status.HTTP_400_BAD_REQUEST, message="Dues for this ids are already paid!!")
                return response
        data = credit_schemas.CreditDuesResponse(total_amount=request.amount, date=str(
            present_date), customer_id=request.customer_id)
        data2 = credit_schemas.FinalDuesPayResponse(
            status=status.HTTP_200_OK, message="credit paid successfully!", data=data)
        return data2

    else:
        response = user_schemas.ResponseCommonMessage(
            status=status.HTTP_424_FAILED_DEPENDENCY, message="Please provide credit id's!!")
        return response


def user_credit_request(request, db: Session, background_tasks: BackgroundTasks,confirm):
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
                f"SELECT email FROM {constants.Database_name}.users_master where role_id in (SELECT role_id FROM {constants.Database_name}.role_permissions where function_id = (SELECT id FROM {constants.Database_name}.function_master where codename = 'credits.assign_customer')) ")

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
                    message = f"You have already requested the credit for the amount of {round(credit_request_check.requested_amount)} SAR. Do you want to change to the newly requested credit amount to {request.requested_amount} SAR?"
                )
                return response
            if confirm == True:
                credit_request_check.requested_amount = request.requested_amount
                db.merge(credit_request_check)
                db.commit()
                response = user_schemas.ResponseCommonMessage(
                    status=status.HTTP_200_OK, message = f"The newly requested credit amount of {round(request.requested_amount)} SAR is saved successfully."
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
