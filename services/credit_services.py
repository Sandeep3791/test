from sqlalchemy import desc
from schemas import user_schemas, credit_schemas
from models import credit_models, order_models
from sqlalchemy.orm import Session
from fastapi import status
from datetime import date, datetime


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
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No user credits found!")
        return common_msg


def get_credits_txn(customer_id, dues, db: Session):
    if dues == True:
        user_data = db.query(credit_models.CreditTransactionsLog).filter(credit_models.CreditTransactionsLog.customer_id == customer_id,
                                                                         credit_models.CreditTransactionsLog.payment_status == False).order_by(desc(credit_models.CreditTransactionsLog.id)).all()
        txn_list = []
        if user_data:
            for data in user_data:
                user_oder_data = db.query(order_models.Orders).filter(
                    order_models.Orders.id == data.order_id).first()
                credit_data = credit_schemas.ResponseCustomerCreditsTxn(id=data.id, credit_amount=data.credit_amount, available=data.available, credit_date=str(
                    data.credit_date), due_date=str(data.due_date), payment_status=data.payment_status, order_ref_no=user_oder_data.ref_number)
                txn_list.append(credit_data)
            response = credit_schemas.ResponseCustomerCreditsTxnFinal(
                status=status.HTTP_200_OK, message="User Credit Dues!", data=txn_list)
            return response
        else:
            common_msg = user_schemas.ResponseCommonMessage(
                status=status.HTTP_404_NOT_FOUND, message="No user credit dues found!")
            return common_msg
    else:
        user_data = db.query(credit_models.CreditTransactionsLog).filter(
            credit_models.CreditTransactionsLog.customer_id == customer_id).order_by(desc(credit_models.CreditTransactionsLog.id)).all()

        txn_list = []
        if user_data:
            for data in user_data:
                user_oder_data = db.query(order_models.Orders).filter(
                    order_models.Orders.id == data.order_id).first()
                credit_data = credit_schemas.ResponseCustomerCreditsTxn(id=data.id, credit_amount=data.credit_amount, available=data.available, credit_date=str(
                    data.credit_date), due_date=str(data.due_date), payment_status=data.payment_status, order_ref_no=user_oder_data.ref_number)
                txn_list.append(credit_data)
            response = credit_schemas.ResponseCustomerCreditsTxnFinal(
                status=status.HTTP_200_OK, message="User Credit Transactions!", data=txn_list)
            return response
        else:
            common_msg = user_schemas.ResponseCommonMessage(
                status=status.HTTP_404_NOT_FOUND, message="No user credits transactions found!")
            return common_msg


def get_overdue_credits(customer_id, db: Session):
    present_date = datetime.now()
    user_data = db.query(credit_models.CreditManagement).filter(
        credit_models.CreditManagement.customer_id == customer_id).first()

    if user_data:
        credit_data = db.query(credit_models.CreditTransactionsLog).filter(
            credit_models.CreditTransactionsLog.customer_id == customer_id).order_by(desc(credit_models.CreditTransactionsLog.id)).all()
        due_credit_data = None
        for i in credit_data:
            credit_due_date = i.due_date
            user_oder_data = db.query(order_models.Orders).filter(
                order_models.Orders.id == i.order_id).first()
            if present_date > credit_due_date:
                due_credit_data = credit_schemas.ResponseCustomerCreditsTxn(id=i.id, credit_amount=i.credit_amount, available=i.available, credit_date=str(
                    i.credit_date), due_date=str(i.due_date), payment_status=i.payment_status, order_ref_no=user_oder_data.ref_number)
        response = credit_schemas.ResponseCustomerCreditDue(
            status=status.HTTP_200_OK, message="User Overdue Credit Info!", data=due_credit_data)
        return response
    else:
        common_msg = user_schemas.ResponseCommonMessage(
            status=status.HTTP_404_NOT_FOUND, message="No user credits found!")
        return common_msg
