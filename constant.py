from supplier.settings import DATABASES
database = DATABASES['default']['NAME']


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
#! Use of dictfetchall function
#  with connection.cursor() as cursor:
#     cursor.execute(f'SELECT * FROM {constant.database}.email_template where email_template.key="po_create";')
#     y = dictfetchall(cursor)
