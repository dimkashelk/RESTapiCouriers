import sqlalchemy
from .db_session import SqlAlchemyBase
import json


class Couriers(SqlAlchemyBase):
    __tablename__ = 'couriers'

    id = sqlalchemy.Column(sqlalchemy.INT, primary_key=True)
    type = sqlalchemy.Column(sqlalchemy.VARCHAR, default='')
    regions = sqlalchemy.Column(sqlalchemy.JSON, default=json.dumps({}))
    working_hours = sqlalchemy.Column(sqlalchemy.JSON, default=json.dumps({}))
    orders = sqlalchemy.Column(sqlalchemy.JSON, default=json.dumps({}))
    earnings = sqlalchemy.Column(sqlalchemy.BIGINT, default=0)
    assign_time = sqlalchemy.Column(sqlalchemy.VARCHAR, default='')
