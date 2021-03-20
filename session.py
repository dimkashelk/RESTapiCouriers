from data import couriers, db_session


class Session:

    def __init__(self):
        db_session.global_init('db/db.db')
        self.session = db_session.create_session()

    def insert_new_user(self, courier_id):
        user = couriers.Couriers(id=courier_id)
        self.session.add(user)
        self.session.commit()

    def get_courier(self, courier_id):
        user = self.session.query(couriers.Couriers).filter(couriers.Couriers.id == courier_id).first()
        return user

    def commit(self):
        self.session.commit()
