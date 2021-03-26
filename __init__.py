from flask import Flask, request, jsonify
from session import Session
import logging

app = Flask(__name__)

session = Session()

logging.basicConfig(level=logging.INFO, filename='app.log')


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
        fl = True
        if session.get_courier(courier["courier_id"]) is not None:
            id_couriers.append({"id": courier["courier_id"]})
            continue
        for ind, field in enumerate(courier.keys()):
            if field in ['courier_id', 'courier_type', 'regions', 'working_hours']:
                fields[ind] = True
            else:
                id_couriers.append({"id": courier["courier_id"]})
                fl = False
                break
        if fl:
            if False in fields:
                id_couriers.append({"id": courier["courier_id"]})
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
        for key in data.keys():
            if key not in ['courier_type', 'regions', 'working_hours']:
                unknown_params.append(key)
        if len(unknown_params) > 0:
            return jsonify({"validation_error": f"Bad request"}), 400
        session.set_args_courier(id_courier, data)
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
        fl = True
        if session.get_order(order['order_id']) is not None:
            id_orders.append({"id": order["order_id"]})
        for ind, field in enumerate(order.keys()):
            if field in ['order_id', 'weight', 'region', 'delivery_hours']:
                fields[ind] = True
            else:
                id_orders.append({"id": order["order_id"]})
                fl = False
                break
        if fl:
            if False in fields:
                id_orders.append({"id": order["order_id"]})
        if not 0.01 <= order['weight'] <= 50:
            id_orders.append({"id": order["order_id"]})
    if len(id_orders) > 0:
        return jsonify({"validation_error": {"orders": id_orders}}), 400
    session.add_orders(data)
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
    courier_id = request.json["courier_id"]
    courier = session.get_courier(courier_id)
    if courier is None:
        return jsonify({"validation_error": f"Bad request"}), 400
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
    return jsonify({"order_id": data["order_id"]} if res == 200 else {"complete_error": "Bad request"}), res


@app.route('/')
def main():
    return 'This is RESTapi server for second stage of selection for summer school'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
