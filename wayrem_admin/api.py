# import requests   [REDACTED].wJUoHtkX0wRjj9g1xk6G_tNlrWqoST7PlW8gH7OnyF8

# url = "https://api.barcodelookup.com/v3/products?barcode=8901262072052&formatted=y&key=2ppq23rl3qiilkkc0k315y1ft3ytxw"

# headers = {
#     'x-rapidapi-host': "barcode-lookup.p.rapidapi.com",
#     # 'x-rapidapi-key': "2ppq23rl3qiilkkc0k315y1ft3ytxw"
# }

# response = requests.request("GET", url, headers=headers)


# print(response.text)


import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

message = Mail(
    from_email='wayrem@hotmail.com',
    to_emails=('surya.pratap.2181@gmail.com', 'pankajspsq@gmail.com'),
    subject='Sending with Twilio SendGrid is Fun',
    html_content='<strong>and easy to do anywhere, even with Python</strong>')
try:
    sg = SendGridAPIClient(
        '[REDACTED].3HFHrgCCN81kEee5n_LCmeZbm8GrAVOXU1lClP5S_vI')
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e)
    print(e.body)
    # print(e.message)
