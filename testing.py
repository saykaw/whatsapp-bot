from db_store import Database

store = Database()

doc_ref = store.init_user("123981290","82902817890","Sayali")

msg = store.payload("Sayali","It worked!!!!", "109381208")

store.add_convo(doc_ref,msg)
