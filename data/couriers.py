import sqlalchemy
from .db_session import SqlAlchemyBase


class Couriers(SqlAlchemyBase):
    __tablename__ = 'couriers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    type = sqlalchemy.Column(sqlalchemy.String)
    regions = sqlalchemy.Column(sqlalchemy.String)
    working_hours = sqlalchemy.Column(sqlalchemy.String)