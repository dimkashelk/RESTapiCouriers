import sqlalchemy
from .db_session import SqlAlchemyBase


class Couriers(SqlAlchemyBase):
    __tablename__ = 'couriers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    type = sqlalchemy.Column(sqlalchemy.String, default='')
    regions = sqlalchemy.Column(sqlalchemy.String, default='')
    working_hours = sqlalchemy.Column(sqlalchemy.String, default='')
    orders = sqlalchemy.Column(sqlalchemy.String, default='')
    earnings = sqlalchemy.Column(sqlalchemy.String, default=0)
