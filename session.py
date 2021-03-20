from data import couriers, db_session


class Session:

    def __init__(self):
        db_session.global_init('db/db.db')
        self.session = db_session.create_session()

    def add_courier(self, courier):
        self.session.add(courier)

    def add_couriers(self, couriers_data):
        for courier in couriers_data:
            current_courier = couriers.Couriers()
            current_courier.id = courier["courier_id"]
            current_courier.type = courier["courier_type"]
            current_courier.regions = ';'.join(map(str, courier["regions"]))
            current_courier.regions = ';'.join(courier["working_hours"])
            self.session.add(current_courier)
            self.commit()

    def get_courier(self, courier_id):
        return self.session.query(couriers.Couriers).filter(
            couriers.Couriers.id == courier_id).first()

    def set_args_courier(self, courier_id, args):
        current_courier = self.get_courier(courier_id)
        for i in args.keys():
            eval(f'current_courier.{i} = {";".join(map(str, args[i]))}')
            self.commit()
        return current_courier

    def commit(self):
        self.session.commit()
