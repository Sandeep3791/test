import requests
import json
from wayrem_admin.models import CustomerDevice, CustomerNotification, Settings

from wayrem_admin.models_orders import StatusMaster, Orders


class FirebaseLibrary:

    FIREBASE_URL = "https://fcm.googleapis.com/fcm/send"

    FIREBASE_TEST_SERVER_TOKEN = "AAAALwoMdv8:APA91bE5_J7NSGt7fTRNW7NGh1udC_B0se-By0Z3onj1nEM_bzWf-lyUUCrc9yBb4U8H6qWHie9nM1yRlqbit33FbaKds6FWGhtC6OIsqc0g0Yk7qTNSPKrLYCAw2HiINoW4KuGi30uG"

    serverToken = FIREBASE_TEST_SERVER_TOKEN

    def push_notification_in_firebase(self, data):
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'key=' + self.serverToken,
            }
            body = {
                'notification': {'title': data.get("title"),
                                 'body': data.get("message")
                                 },
                'to': data.get("device_token"),
                'priority': 'high',
                "data": {
                    "order_id": data.get("order_id"),
                }
            }
            response = requests.post(
                self.FIREBASE_URL, headers=headers, data=json.dumps(body))
            print("sent successfully!!")
        except:
            print("Failed!!")

        return response

    def status_to_msg(self, status_id):
        switcher = {
            1: "notification_app_order_received",
            2: "notification_app_order_preparing",
            3: "notification_app_order_pickup",
            4: "notification_app_order_delivering",
            5: "notification_app_order_delivered",
        }
        return switcher.get(status_id, None)

    def send_notify(self, order_id, order_status):
        try:
            status = StatusMaster.objects.get(id=order_status)
            notify_title = status.name
            notify_msg = status.description
            order_data = Orders.objects.get(id=order_id)
            customer_id = order_data.customer
            devices = CustomerDevice.objects.filter(customer=customer_id)
            setting_key = self.status_to_msg(order_status)
            setting_msg = Settings.objects.get(key=setting_key)
            values = {
                'ref_no': order_data.ref_number
            }
            message = setting_msg.value.format(**values)
            print(devices)
            if not devices:
                return "No device found!!"
            else:
                for device in devices:
                    device_token = device.device_id
                    notf = {
                        "title": notify_title,
                        "message": message,
                        "device_token": device_token,
                        "order_id": order_id
                    }
                    self.push_notification_in_firebase(notf)
                notification_store = CustomerNotification(
                    customer=customer_id, order=order_data, title=notify_title, message=f"Your Order {order_data.ref_number} is {notify_msg}!")
                notification_store.save()
        except:
            print("something missing")
            print(order_id)
            print(order_status)
        return "Successfull!!"
