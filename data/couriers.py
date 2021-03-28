import sqlalchemy
from .db_session import SqlAlchemyBase


class Couriers(SqlAlchemyBase):
    __tablename__ = 'couriers'

    id = sqlalchemy.Column(sqlalchemy.INT, primary_key=True)
    type = sqlalchemy.Column(sqlalchemy.VARCHAR, default='')
    regions = sqlalchemy.Column(sqlalchemy.JSON)
    working_hours = sqlalchemy.Column(sqlalchemy.JSON)
    orders = sqlalchemy.Column(sqlalchemy.JSON)
    earnings = sqlalchemy.Column(sqlalchemy.BIGINT, default=0)
    assign_time = sqlalchemy.Column(sqlalchemy.VARCHAR, default='')
