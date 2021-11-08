import requests

url = "https://api.barcodelookup.com/v3/products?barcode=8901262072052&formatted=y&key=2ppq23rl3qiilkkc0k315y1ft3ytxw"

headers = {
    'x-rapidapi-host': "barcode-lookup.p.rapidapi.com",
    # 'x-rapidapi-key': "2ppq23rl3qiilkkc0k315y1ft3ytxw"
}

response = requests.request("GET", url, headers=headers)

print(response.text)

# import os
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail

 
# message = Mail(
#     from_email='pankajspsq@gmail.com',
#     to_emails='surya.pratap.2181@gmail.com',
#     subject='Sending with Twilio SendGrid is Fun',
#     html_content='<strong>and easy to do anywhere, even with Python</strong>')
# try:
#     sg = SendGridAPIClient(os.environ.get(
#         '[REDACTED].2_Hn6KVNk0gR0qbDMqSmKD8rHRHINHtFSX6vj6HL0co'))
#     response = sg.send(message)
#     print(response.status_code)
#     print(response.body)
#     print(response.headers)
# except Exception as e:
#     print(e)