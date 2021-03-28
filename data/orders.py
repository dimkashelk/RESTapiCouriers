import sqlalchemy
from .db_session import SqlAlchemyBase


class Order(SqlAlchemyBase):
    __tablename__ = 'orders'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    weight = sqlalchemy.Column(sqlalchemy.FLOAT, default=0)
    region = sqlalchemy.Column(sqlalchemy.INT, default=0)
    delivery_hours = sqlalchemy.Column(sqlalchemy.JSON, default='')
    active = sqlalchemy.Column(sqlalchemy.INT, default=0)
    delivered = sqlalchemy.Column(sqlalchemy.VARCHAR, default='')
    assign_time = sqlalchemy.Column(sqlalchemy.VARCHAR, default='')
