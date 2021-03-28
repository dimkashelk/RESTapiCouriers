import datetime
from data import couriers, db_session, orders
from datetime import time
import json


class Session:

    def __init__(self):
        db_session.global_init('db/db.db')
        self.session = db_session.create_session()

    def add_courier(self, courier):
        self.session.add(courier)
        self.session.commit()

    def add_couriers(self, couriers_data):
        for courier in couriers_data:
            current_courier = couriers.Couriers()
            current_courier.id = courier["courier_id"]
            current_courier.type = courier["courier_type"]
            current_courier.regions = json.dumps(courier["regions"])
            current_courier.working_hours = json.dumps(courier["working_hours"])
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
        try:
            id_orders = list(map(int, current_courier.orders.split(';')))
        except Exception:
            id_orders = [current_courier.orders]
        if id_orders[0] != '':
            for i in id_orders:
                order = self.get_order(i)
                if order.delivered == '':
                    order.assign_time = ''
                    order.active = 0
                    self.session.commit()
        self.get_orders(current_courier.id)
        return current_courier

    def commit(self):
        self.session.commit()

    def to_dict(self, courier_id, type="CourierItem"):
        current_courier = self.get_courier(courier_id)
        res = {"courier_id": current_courier.id,
               "courier_type": current_courier.type,
               'regions': json.loads(current_courier.regions),
               'working_hours': json.loads(current_courier.working_hours)}
        if type == "CourierGetResponse":
            id_orders = json.loads(current_courier.orders)
            sr_times = []
            if len(id_orders) > 0:
                for i in res['regions']:
                    orders_in_current_region = list(filter(lambda x: self.get_order(x).region == i, id_orders))
                    if len(orders_in_current_region) == 0:
                        continue
                    sum_time = 0
                    count = 0
                    pr_time = self.get_order(orders_in_current_region[0]).assign_time
                    for order in orders_in_current_region:
                        order = self.get_order(order)
                        if order.delivered != '':
                            count += 1
                            sum_time += (datetime.datetime.strptime(order.delivered, '%Y-%m-%dT%H:%M:%S.%fZ') -
                                         datetime.datetime.strptime(pr_time, '%Y-%m-%dT%H:%M:%S.%fZ')).seconds
                            pr_time = order.delivered
                    if count > 0:
                        sr_times.append(sum_time / count)
                if len(sr_times) > 0:
                    res['rating'] = (60 * 60 - min(min(sr_times), 60 * 60)) / (60 * 60) * 5
            res['earnings'] = current_courier.earnings
        return res

    def get_count_couriers(self):
        dop = self.session.query(couriers.Couriers).order_by(couriers.Couriers.id.desc()).first()
        if dop is None:
            return 0
        return dop.id

    def add_orders(self, orders_data):
        for order in orders_data:
            current_order = orders.Order()
            current_order.id = order["order_id"]
            current_order.weight = order["weight"]
            current_order.region = order["region"]
            current_order.delivery_hours = json.dumps(order["delivery_hours"])
            self.session.add(current_order)
            self.session.commit()

    def get_order(self, id_order):
        return self.session.query(orders.Order).filter(orders.Order.id == id_order).first()

    def get_orders(self, id_courier):
        courier = self.get_courier(id_courier)
        max_weight = 0
        if courier.type == 'foot':
            max_weight = 10
        elif courier.type == 'bike':
            max_weight = 15
        elif courier.type == 'car':
            max_weight = 50
        id_orders = list(
            map(lambda x: x.id, self.session.query(orders.Order).filter(
                orders.Order.weight <= max_weight)))
        regions = json.loads(courier.regions)
        id_orders = list(filter(lambda x: self.get_order(x).region in regions, id_orders))
        working_hours = json.loads(courier.working_hours)
        end_orders = set()
        fl = False
        time_to_assign = datetime.datetime.utcnow().isoformat("T") + "Z"
        for t in working_hours:
            begin = time(hour=int(t.split('-')[0].split(':')[0]),
                         minute=int(t.split('-')[0].split(':')[1]))
            end = time(hour=int(t.split('-')[1].split(':')[0]),
                       minute=int(t.split('-')[1].split(':')[1]))
            for j in id_orders:
                order = self.get_order(j)
                hours = json.loads(order.delivery_hours)
                for hour in hours:
                    b = time(hour=int(hour.split('-')[0].split(':')[0]),
                             minute=int(hour.split('-')[0].split(':')[1]))
                    e = time(hour=int(hour.split('-')[1].split(':')[0]),
                             minute=int(hour.split('-')[1].split(':')[1]))
                    if begin <= b <= end and begin <= e <= end and order.delivered == '' \
                            and order.active == 0 or order.active == courier.id:
                        if order.active != courier.id:
                            fl = True
                        order = self.get_order(j)
                        order.active = courier.id
                        if order.assign_time == '':
                            order.assign_time = time_to_assign
                        self.session.commit()
                        end_orders.add(j)
        if fl:
            courier.assign_time = time_to_assign
        courier.orders = json.dumps(list(sorted(end_orders)))
        self.session.commit()
        final_orders = []
        for i in end_orders:
            order = self.get_order(i)
            if order.delivered == '':
                final_orders.append(i)
        return final_orders

    def set_time_complete_order(self, id_courier, id_order, time_complete):
        courier = self.get_courier(id_courier)
        if courier is None:
            return 400, {"courier_id": "Courier id is not found"}
        order = self.get_order(id_order)
        if order is None:
            return 400, {"order_id": "Order id is not found"}
        try:
            datetime.datetime.strptime(order.delivered, '%Y-%m-%dT%H:%M:%S.%fZ')
        except BaseException:
            return 400, {"complete_time": "Incorrect time"}
        orders = json.dumps(courier.orders)
        if order.delivered == '':
            if id_order in orders:
                order.delivered = time_complete
                if courier.type == 'foot':
                    courier.earnings = courier.earnings + 500 * 2
                elif courier.type == 'bike':
                    courier.earnings = courier.earnings + 500 * 5
                elif courier.type == 'car':
                    courier.earnings = courier.earnings + 500 * 9
                self.session.commit()
                return 200
            return 400, {"order_delivered": "The order is delivered by another courier"}
        return 400, {"order_delivered": f"The order is delivered in {order.delivered}"}
