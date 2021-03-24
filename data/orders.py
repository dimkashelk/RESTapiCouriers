import sqlalchemy
from .db_session import SqlAlchemyBase


class Order(SqlAlchemyBase):
    __tablename__ = 'orders'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    weight = sqlalchemy.Column(sqlalchemy.Float, default=0)
    region = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    delivery_hours = sqlalchemy.Column(sqlalchemy.String, default='')
    active = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    delivered = sqlalchemy.Column(sqlalchemy.String, default='')
    assign_time = sqlalchemy.Column(sqlalchemy.String, default='')
