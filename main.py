from flask import Flask, request, abort, jsonify, Response
from session import Session

app = Flask(__name__)

session = Session()


def check_params(req, params):
    id_couriers = []
    dop = params
    for courier in req:
        fields = [False, False, False, False]
        fl = True
        for ind, field in enumerate(courier.keys()):
            if field in dop:
                fields[ind] = True
            else:
                id_couriers.append({"id": courier["courier_id"]})
                fl = False
                break
        if fl:
            if False in fields:
                id_couriers.append({"id": courier["courier_id"]})
    return id_couriers


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
    id_couriers = check_params(data, ['courier_id', 'courier_type', 'regions', 'working_hours'])
    if len(id_couriers) > 0:
        return jsonify({"validation_error": {"couriers": id_couriers}}), 400
    session.add_couriers(data)
    return jsonify({"couriers": list({"id": courier["courier_id"]} for courier in data)}), 201


@app.route('/couriers/<int:id_courier>', methods=["PATCH"])
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
    data = request.json
    if id_courier > session.get_count_couriers():
        return jsonify({"validation_error": "there is no courier with this id"}), 400
    unknown_params = []
    for key in data.keys():
        if key not in ['courier_type', 'regions', 'working_hours']:
            unknown_params.append(key)
    if len(unknown_params) > 0:
        return jsonify({"validation_error": f"unknown params: {'; '.join(unknown_params)}"}), 400
    session.set_args_courier(id_courier, data)
    return jsonify(session.to_dict(id_courier)), 200


if __name__ == '__main__':
    app.run(port=8080)
