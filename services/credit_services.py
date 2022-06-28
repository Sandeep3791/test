from sqlalchemy import desc
from schemas import user_schemas, credit_schemas
from models import credit_models
from sqlalchemy.orm import Session
from fastapi import status

def get_credits(customer_id, db: Session):
    user_data = db.query(credit_models.CreditManagement).filter(credit_models.CreditManagement.customer_id == customer_id).first()
    if user_data:
        rule_id_data = db.query(credit_models.CreditSettings).filter(credit_models.CreditSettings.id == user_data.credit_rule_id).first()
        assigned_credit = rule_id_data.credit_amount
        credit_data = credit_schemas.ResponseCustomerCredits(id=user_data.id, customer_id=user_data.customer_id, used_credits=user_data.used, available_credits=user_data.available ,total_credits = assigned_credit )
        response = credit_schemas.ResponseCustomerCreditsFinal(status=status.HTTP_200_OK, message="User Credit Info!", data=credit_data)
        return response
    else:
        common_msg = user_schemas.ResponseCommonMessage(status=status.HTTP_404_NOT_FOUND, message="No user credits found!")
        return common_msg
        
def get_credits_txn(customer_id, db: Session):
    user_data = db.query(credit_models.CreditTransactionsLog).filter(credit_models.CreditTransactionsLog.customer_id == customer_id).order_by(desc(credit_models.CreditTransactionsLog.id)).all()
    txn_list = []
    if user_data:
        for data in user_data:
            credit_data = credit_schemas.ResponseCustomerCreditsTxn(id = data.id,credit_amount = data.credit_amount,available = data.available,credit_date = str(data.credit_date),due_date = str(data.due_date) )
            txn_list.append(credit_data)
        response = credit_schemas.ResponseCustomerCreditsTxnFinal(status=status.HTTP_200_OK, message="User Credit Transactions!", data=txn_list)
        return response
    else:
        common_msg = user_schemas.ResponseCommonMessage(status=status.HTTP_404_NOT_FOUND, message="No user credits transactions found!")
        return common_msg

        