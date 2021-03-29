from flask import Flask, request, jsonify
from .session import Session
import logging
from datetime import time

app = Flask(__name__)

session = Session()

logging.basicConfig(level=logging.INFO, filename='app.log')


@app.errorhandler(404)
def not_found(e):
    return jsonify({"server_error": "Method not allowed"}), 404


@app.route('/couriers', methods=["POST"])
def couriers():
    """
    /couriers:
        post:
            description: 'Import couriers'
            requestBody:
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/CouriersPostRequest'
            responses:
                '201':
                    description: 'Created'
                    content:
                        application/json:
                            schema:
                                $ref: '#/components/schemas/CouriersIds'
                '400':
                    description: 'Bad request'
                    content:
                        application/json:
                            schema:
                                type: object
                                additionalProperties: true
                                properties:
                                    validation_error:
                                        $ref: '#/components/schemas/CouriersIds'
                                required:
                                  - validation_error
    :return:
    """
    data = request.json['data']
    id_couriers = []
    for courier in data:
        fields = [False, False, False, False]
        fl_time = False
        fl_region = True
        fl_courier_in_db = False
        if session.get_courier(courier["courier_id"]) is not None:
            fl_courier_in_db = True
        dop = ['courier_id', 'courier_type', 'regions', 'working_hours']
        for ind, field in enumerate(courier.keys()):
            if field in dop:
                fields[ind] = True
        no_parameter = []
        for i, v in enumerate(fields):
            if not v:
                no_parameter.append(dop[i])
        unknown_types = []
        unknown_time = []
        id_regions = []
        if type(courier['courier_id']) != int:
            unknown_types.append({'courier_id': "Courier id is not int"})
            fl_courier_in_db = False
        if type(courier['courier_type']) != str:
            unknown_types.append({'courier_type': "Courier type is not string"})
        if courier['courier_type'] not in ['foot', 'bike', 'car']:
            unknown_types.append({"courier_type_item": "Courier type is not in ['foot', 'bike', 'car']"})
        if type(courier['regions']) != list:
            unknown_types.append({"regions_type": "Regions is not list"})
            fl_region = False
        elif any([type(i) != int for i in courier['regions']]):
            unknown_types.append({"regions": "Not all regions is int"})
            fl_region = False
        if type(courier['working_hours']) != list:
            unknown_types.append({"working_hours": "Working hours is not list"})
            fl_time = True
        if not fl_time:
            for t in courier['working_hours']:
                try:
                    time(hour=int(t.split('-')[0].split(':')[0]),
                         minute=int(t.split('-')[0].split(':')[1]))
                    time(hour=int(t.split('-')[1].split(':')[0]),
                         minute=int(t.split('-')[1].split(':')[1]))
                except BaseException:
                    unknown_time.append(t)
        if fl_region:
            for r in courier['regions']:
                if r <= 0:
                    id_regions.append(r)
        fl = False
        dop = {"id": courier['courier_id']}
        if len(no_parameter) > 0:
            dop["no_parameter"] = no_parameter
            fl = True
        if len(unknown_types) > 0:
            dop["unknown_types"] = unknown_types
            fl = True
        if len(unknown_time) > 0:
            dop["unknown_time"] = unknown_time
            fl = True
        if len(id_regions) > 0:
            dop["id_regions"] = f"Not correct regions: {id_regions}"
            fl = True
        if fl_courier_in_db:
            dop["error_db"] = "Courier id in database"
            fl = True
        if fl:
            id_couriers.append(dop)
    if len(id_couriers) > 0:
        return jsonify({"validation_error": {"couriers": id_couriers}}), 400
    session.add_couriers(data)
    return jsonify({"couriers": list({"id": courier["courier_id"]} for courier in data)}), 201


@app.route('/couriers/<int:id_courier>', methods=["PATCH", "GET"])
def edit_courier(id_courier):
    """
    /couriers/{courier_id}:
        parameters:
          - in: path
            name: courier_id
            required: true
            schema:
                type: integer
        get:
            description: 'Get courier info'
            responses:
                '200':
                    description: 'OK'
                    content:
                        application/json:
                            schema:
                                $ref: '#/components/schemas/CourierGetResponse'
                '404':
                    description: 'Not found'

        patch:
            description: 'Update courier by id'
            requestBody:
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/CourierUpdateRequest'
            responses:
                '200':
                    description: 'Created'
                    content:
                        application/json:
                            schema:
                                $ref: '#/components/schemas/CourierItem'
                '400':
                    description: 'Bad request'
                '404':
                    description: 'Not found'
    :param id_courier:
    :return:
    """
    if session.get_courier(id_courier) is None:
        return jsonify({"status": "Not found"}), 404
    if request.method == "PATCH":
        data = request.json
        unknown_params = []
        unknown_meaning = ''
        unknown_regions = []
        unknown_time = []
        for key in data.keys():
            if key == 'courier_type':
                if type(data[key]) != str:
                    unknown_params.append({'courier_type': data[key]})
                    continue
                if data[key] not in ['foot', 'bike', 'car']:
                    unknown_meaning = data[key]
            elif key == 'regions':
                if type(data[key]) != list:
                    unknown_params.append({'regions': data[key]})
                    continue
                for i in data[key]:
                    if type(i) != int:
                        unknown_regions.append(i)
                    else:
                        if i <= 0:
                            unknown_regions.append(i)
            elif key == 'working_hours':
                if type(data[key]) != list:
                    unknown_params.append({'working_hours': data[key]})
                    continue
                for t in data[key]:
                    try:
                        time(hour=int(t.split('-')[0].split(':')[0]),
                             minute=int(t.split('-')[0].split(':')[1]))
                        time(hour=int(t.split('-')[1].split(':')[0]),
                             minute=int(t.split('-')[1].split(':')[1]))
                    except ValueError:
                        unknown_time.append(t)
            else:
                unknown_params.append({key: data[key]})
        if len(unknown_regions) == 0 and \
                len(unknown_time) == 0 and \
                unknown_meaning == '' and \
                len(unknown_params) == 0:
            session.set_args_courier(id_courier, data)
        else:
            dop = {"validation_error": "Bad request"}
            fl = False
            if unknown_meaning != '':
                dop['unknown_meaning'] = unknown_meaning
                fl = True
            if len(unknown_time) != 0:
                dop['unknown_time'] = unknown_time
                fl = True
            if len(unknown_params) != 0:
                dop['unknown_params'] = unknown_params
                fl = True
            if len(unknown_regions) != 0:
                dop['unknown_regions'] = unknown_regions
                fl = True
            if fl:
                return jsonify(dop), 400
        return jsonify(session.to_dict(id_courier, "CourierItem")), 200
    elif request.method == "GET":
        return jsonify(session.to_dict(id_courier, "CourierGetResponse")), 200


@app.route('/orders', methods=["POST"])
def orders():
    """
    /orders:
        post:
            description: 'Import orders'
            requestBody:
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/OrdersPostRequest'
            responses:
                '201':
                    description: 'Created'
                    content:
                        application/json:
                            schema:
                                $ref: '#/components/schemas/OrdersIds'
                '400':
                    description: 'Bad request'
                    content:
                        application/json:
                            schema:
                                type: object
                                additionalProperties: false
                                properties:
                                    validation_error:
                                        $ref: '#/components/schemas/OrdersIds'
                                required:
                                  - validation_error
    :return:
    """
    data = request.json["data"]
    id_orders = []
    for order in data:
        fields = [False, False, False, False]
        fl_order_in_db = False
        fl_time = False
        if type(order['order_id']) == int:
            if session.get_order(order['order_id']) is not None:
                fl_order_in_db = True
        dop = ['order_id', 'weight', 'region', 'delivery_hours']
        for ind, field in enumerate(order.keys()):
            if field in dop:
                fields[ind] = True
        no_parameter = []
        for i, v in enumerate(fields):
            if not v:
                no_parameter.append(dop[i])
        unknown_types = []
        unknown_time = []
        if type(order['order_id']) != int:
            unknown_types.append({'order_id': "Order id is not int"})
            fl_order_in_db = False
        if type(order['weight']) != float and type(order['weight']) != int:
            unknown_types.append({'weight': "Order weight type is not float"})
        elif not 0.01 <= order['weight'] <= 50:
            unknown_types.append({"weight": "Order weight is not in [0.01; 50]"})
        if type(order['region']) != int:
            unknown_types.append({"region_type": "Region is not int"})
        elif order['region'] <= 0:
            unknown_types.append({"region_item": "Region value is not positive"})
        if type(order['delivery_hours']) != list:
            unknown_types.append({"delivery_hours": "Delivery hours is not list"})
            fl_time = False
        if fl_time:
            for t in order['delivery_hours']:
                try:
                    time(hour=int(t.split('-')[0].split(':')[0]),
                         minute=int(t.split('-')[0].split(':')[1]))
                    time(hour=int(t.split('-')[1].split(':')[0]),
                         minute=int(t.split('-')[1].split(':')[1]))
                except BaseException:
                    unknown_time.append(t)
        fl = False
        dop = {"id": order['order_id']}
        if len(no_parameter) > 0:
            dop["no_parameter"] = no_parameter
            fl = True
        if len(unknown_types) > 0:
            dop["unknown_types"] = unknown_types
            fl = True
        if len(unknown_time) > 0:
            dop["unknown_time"] = unknown_time
            fl = True
        if fl_order_in_db:
            dop["error_db"] = "Courier id in database"
            fl = True
        if fl:
            id_orders.append(dop)
    if len(id_orders) > 0:
        return jsonify({"validation_error": {"orders": id_orders}}), 400
    if len(data) == len(set(i['order_id'] for i in data)):
        session.add_orders(data)
    else:
        return jsonify({"validation_error": {"orders": "Duplicate id's are present"}}), 400
    return jsonify({"orders": list({"id": order["order_id"]} for order in data)}), 201


@app.route('/orders/assign', methods=["POST"])
def assign():
    """
    /orders/assign:
        post:
            description: 'Assign orders to a courier by id'
            requestBody:
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/OrdersAssignPostRequest'
            responses:
                '200':
                    description: 'OK'
                    content:
                        application/json:
                            schema:
                                allOf:
                                  - $ref: '#/components/schemas/OrdersIds'
                                  - $ref: '#/components/schemas/AssignTime'
                '400':
                    description: 'Bad request'
    :return:
    """
    data = request.json
    if len(data.keys()) > 1:
        return jsonify({"validation_error": "Bad request",
                        "unknown_params": "Unknown fields are present"}), 400
    try:
        courier_id = request.json["courier_id"]
    except IndexError:
        return jsonify({"validation_error": "Bad request",
                        "unknown_params": "'courier_id' parameter is missing"}), 400
    if type(courier_id) != int:
        return jsonify({"validation_error": "Bad request",
                        "courier_id": "Courier id is not int"}), 400
    courier = session.get_courier(courier_id)
    if courier is None:
        return jsonify({"validation_error": "Bad request",
                        "courier_id": "Courier id not in database"}), 400
    orders_id = session.get_orders(courier_id)
    if len(orders_id) == 0:
        return jsonify({"orders": []}), 200
    return jsonify({"orders": [{"id": i} for i in orders_id],
                    "assign_time": courier.assign_time})


@app.route('/orders/complete', methods=["POST"])
def complete():
    """
    /orders/complete:
        post:
            description: 'Marks orders as completed'
            requestBody:
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/OrdersCompletePostRequest'
            responses:
                '200':
                    description: 'OK'
                    content:
                        application/json:
                            schema:
                                $ref: '#/components/schemas/OrdersCompletePostResponse'
                '400':
                    description: 'Bad request'
    :return:
    """
    data = request.json
    res = session.set_time_complete_order(data["courier_id"], data["order_id"], data["complete_time"])
    if res[0] == 400:
        dop = {"order_id": data["order_id"]}
        for i in res[1].keys():
            dop[i] = res[1][i]
        return jsonify(dop), 400
    return jsonify({"order_id": data["order_id"]}), 200


@app.route('/')
def main():
    return 'This is RESTapi server for second stage of selection for summer school'


if __name__ == '__main__':
    app.run(port=8080)
