import requests
import json
from wayrem_admin.models import CustomerDevice, EmailTemplateModel, Settings, User
from wayrem_admin.models import CustomerNotification

from wayrem_admin.models import StatusMaster, Orders
from wayrem_admin.services import send_email


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
                    "order_id": data.get("order_id", None),
                    "recurrent": data.get("grocery_id", None),
                    "action_type": data.get("profile_document", None)
                }
            }
            response = requests.post(
                self.FIREBASE_URL, headers=headers, data=json.dumps(body))
            print("sent successfully!!")
            return response
        except:
            print("Failed!!")

    def send_email_notification(self, order_id, order_ref, status):
        try:
            email_template = EmailTemplateModel.objects.get(
                key="order_delivery_log_notification")
            subject = email_template.subject
            body = email_template.message_format
            values = {
                "Ref#": order_ref,
                "status": status
            }
            subject = subject.format(**values)
            body_values = {
                "Ref#": order_ref,
                "status": status,
                "link": f"https://admin-stg.wayrem.com/orders/{order_id}"
            }
            body = body.format(**body_values)
            users = User.objects.filter(order_notify=True)
            for user in users:
                email = user.email
                send_email(to=email, subject=subject, body=body)
            print("email sent successfully!!")
        except:
            print("Failed!!")
        return True

    def status_to_msg(self, status_id):
        switcher = {
            1: "notification_app_order_received",
            2: "notification_app_order_preparing",
            3: "notification_app_order_pickup",
            4: "notification_app_order_delivering",
            5: "notification_app_order_delivered",
            7: "notification_app_order_payment_confirm",
            15: "notification_app_order_cancelled",
            17: "notification_app_admin_order_approved",
            18: "notification_app_admin_order_canceled",
            23: "notification_app_recurrent_order_pending",
            26: "notification_app_bank_transfer_reject",
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
            self.send_email_notification(
                order_id=order_id, order_ref=order_data.ref_number, status=notify_title)
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
                    customer=customer_id, order=order_data, title=notify_title, message=message)
                notification_store.save()
        except:
            print("something missing")
            print(order_id)
            print(order_status)
        return "Successfull!!"

    def send_firebase_notification(self, data={}, payload={}):
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
                }
            }
            body["data"].update(payload)
            response = requests.post(
                self.FIREBASE_URL, headers=headers, data=json.dumps(body))
            print("sent successfully!!")
            return response
        except:
            print("Failed!!")
