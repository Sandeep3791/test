from django.template.loader import get_template
from wayrem.settings import BASE_DIR
import pandas as pd
from django.db import connection
from django.http import HttpResponse
from pyvirtualdisplay import Display
import pdfkit
from pymysql import connect
from wayrem.settings import DATABASES
from django.http import HttpResponse
from io import BytesIO
import pandas as pd
import pandas.io.sql as sql


def generate_pdf(query_string, template_name, file_name):
    query = query_string
    df = pd.read_sql_query(
        query, connection)
    df.to_html(
        f'{BASE_DIR}/wayrem_admin/templates/{template_name}')
    template = get_template(f'{template_name}')
    html = template.render({'persons': query})
    options = {
        'page-size': 'Letter',
        'encoding': "UTF-8",
    }
    display = Display(visible=0, size=(1024, 768))
    try:
        display.start()
        pdf = pdfkit.from_string(html, False, options)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename = {file_name}'
    finally:
        display.stop()
    return response


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
