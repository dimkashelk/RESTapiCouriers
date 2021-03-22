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
            current_courier.working_hours = ';'.join(courier["working_hours"])
            self.session.add(current_courier)
            self.commit()

    def get_courier(self, courier_id):
        return self.session.query(couriers.Couriers).filter(
            couriers.Couriers.id == courier_id).first()

    def set_args_courier(self, courier_id, args):
        current_courier = self.get_courier(courier_id)
        for i in args.keys():
            if i == 'courier_type':
                current_courier.type = args[i]
            elif i == 'regions':
                current_courier.regions = ';'.join(map(str, args[i]))
            elif i == 'working_hours':
                current_courier.working_hours = ';'.join(map(str, args[i]))
            self.commit()
        return current_courier

    def commit(self):
        self.session.commit()

    def to_dict(self, courier_id, type="CourierItem"):
        current_courier = self.get_courier(courier_id)
        res = {"courier_id": current_courier.id,
               "courier_type": current_courier.type}
        if current_courier.regions == '':
            res['regions'] = []
        else:
            res['regions'] = list(map(int, current_courier.regions.split(';')))
        if current_courier.working_hours == '':
            res['working_hours'] = []
        else:
            res['working_hours'] = list(current_courier.working_hours.split(';'))
        if type == "CourierGetResponse":
            # TODO: rating
            res['rating'] = 0
            res['earnings'] = current_courier.earnings
        return res

    def get_count_couriers(self):
        dop = self.session.query(couriers.Couriers).order_by(couriers.Couriers.id.desc()).first()
        if dop is None:
            return 0
        return dop.id
