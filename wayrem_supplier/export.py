import pandas as pd
from django.http import HttpResponse
from pymysql import connect
from supplier.settings import DATABASES
from django.http import HttpResponse
from io import BytesIO
import pandas as pd
import pandas.io.sql as sql


def generate_excel(table_name, file_name):
    con = connect(user=DATABASES['default']['USER'], password=DATABASES['default']['PASSWORD'],
                  host=DATABASES['default']['HOST'], database=DATABASES['default']['NAME'])
    df = sql.read_sql(f'select * from {table_name}', con)
    print(df)
    with BytesIO() as b:
        # Use the StringIO object as the filehandle.
        writer = pd.ExcelWriter(b, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1')
        writer.save()
        # Set up the Http response.
        filename = f'{file_name}.xlsx'
        response = HttpResponse(
            b.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response
