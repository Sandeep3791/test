import requests
import json
from wayrem_admin.models import CustomerDevice, CustomerNotification, Settings

from wayrem_admin.models_orders import StatusMaster, Orders


class FirebaseLibrary:

    FIREBASE_URL = "https://fcm.googleapis.com/fcm/send"

    FIREBASE_TEST_SERVER_TOKEN = "AAAAZrpCwE0:APA91bGdD6gOGnDqIWPd-n3kt9C3zZARqWwCQsDcP_oBYT9Y_u5t4hrOETSzpH6bR6c2aUrAvg1OH908Gv-z5FVjGeYykjyLy4QtOvH7NBTIuFFdbjWCSyQzhK5cQPe_sbc22lCf8zDW"

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
                    "recurrent": data.get("grocery_id")
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
            23: "notification_app_recurrent_order_pending"
        }
        return switcher.get(status_id, None)

    def send_notify(self, order_id, order_status, grocery_id=None):
        try:
            status = StatusMaster.objects.get(id=order_status)
            notify_title = status.name
            notify_msg = status.description
            order_data = Orders.objects.get(id=order_id)
            customer_id = order_data.customer
            devices = CustomerDevice.objects.filter(
                customer=customer_id, is_active=True)
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
                        "order_id": order_id,
                        "grocery_id": grocery_id
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
