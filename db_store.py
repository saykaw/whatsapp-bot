import firebase_admin
from firebase_admin import credentials, firestore

class Database:
    def __init__(self):
        #Check Credentials JSON File path
        self.cred = credentials.Certificate("../Conversational_Bot/whatsapp-api-93771-firebase-adminsdk.json")
        firebase_admin.initialize_app(self.cred)
        self.db = firestore.client()

    def init_user(self,wa_id, chat_id=None, phone: str=None, name=None):
        doc_ref = self.db.collection("testing").document(wa_id)
        if not doc_ref.get().exists:
            data = {
                "whatsApp_id": wa_id,
                "id": chat_id,
                "phone": phone,
                "name": name,
                "messages": [],
            }
            self.db.collection("testing").document(wa_id).set(data)

        return self.db.collection("testing").document(wa_id)

    def payload(self, name: str, text, time):
        msg = {
            f"{name}": str(text),
            "timestamp": time
        }
        return msg

    def add_convo(self, ref, msg):
        ref.update({"messages": firestore.ArrayUnion([msg])})