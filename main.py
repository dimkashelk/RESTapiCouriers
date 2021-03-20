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


if __name__ == '__main__':
    app.run(port=8080)
