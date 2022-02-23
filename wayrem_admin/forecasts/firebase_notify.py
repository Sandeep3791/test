import requests
import json


class FirebaseLibrary:

    FIREBASE_URL = "https://fcm.googleapis.com/fcm/send"

    FIREBASE_TEST_SERVER_TOKEN = "AAAALwoMdv8:APA91bE5_J7NSGt7fTRNW7NGh1udC_B0se-By0Z3onj1nEM_bzWf-lyUUCrc9yBb4U8H6qWHie9nM1yRlqbit33FbaKds6FWGhtC6OIsqc0g0Yk7qTNSPKrLYCAw2HiINoW4KuGi30uG"

    serverToken = FIREBASE_TEST_SERVER_TOKEN

    def push_notification_in_firebase(self, data):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + self.serverToken,
        }
        body = {
            'notification': {'title': data.get("title"),
                             'body': data.get("message")
                             },
            'to': data.get("device_token"),
            'priority': 'high'
        }
        response = requests.post(
            self.FIREBASE_URL, headers=headers, data=json.dumps(body))
        print("Successfull!!")

        return response

    def send_notify(self, order_id, order_status):
        notf = {
            "title": "Order placed",
            "message": f"I am groot",
            "device_token": "fMDp4PUtSiOa4pGwEpHsD9:APA91bEUHOYZcF1c3LBH-9S8NCTpY5pGZ5TmIY9cLZZtdSzj00rYHuZH07IigaQ8UjKJNaXDemL4Fjs4-0o_Yq6pvR8os-CtXbyjFQTPY_6CYS_VcSH5CLFQC3NzeqsdJe2wu_mwG5iO"
        }
        for i in range(5):
            self.push_notification_in_firebase(notf)
        return "Successfull!!"


FirebaseLibrary().send_notify(1, 2)
