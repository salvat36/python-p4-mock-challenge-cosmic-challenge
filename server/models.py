from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
  "ix": "ix_%(column_0_label)s",
  "uq": "uq_%(table_name)s_%(column_0_name)s",
  "ck": "ck_%(table_name)s_%(constraint_name)s",
  "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
  "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)

class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.String)
    nearest_star = db.Column(db.String)
    image = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    missions = db.relationship('Mission', back_populates='planet')

    scientists = association_proxy('missions', 'planet')

    def __repr__(self):
        return f'<Planet {self.id}: {self.name}>'

class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    field_of_study = db.Column(db.String)
    avatar = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default= db.func.now())
    updated_at = db.Column(db.DateTime, onupdate= db.func.now())

    missions = db.relationship('Mission', back_populates='scientist')

    planets = association_proxy('missions', 'scientist')

    @validates('name')
    def validate(self, key, name):
        if not name or name in [scientist.name for scientist in Scientist.query.all()]:
            raise ValueError('Must have a name and must be unique')
        return name
    
    @validates('field_of_study')
    def validate(self, key, field_of_study):
        if not field_of_study:
            raise ValueError("must have a field_of_study")
        return field_of_study
        

    def __repr__(self):
        return f'<Scientist {self.id}: {self.name}>'

class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'))
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    planet = db.relationship('Planet', back_populates='missions')
    scientist = db.relationship('Scientist', back_populates='missions')

    @validates('name')
    def validate_name(self, key, name):
        if not name:
            raise ValueError('must include a name') 
        return name
    
    @validates('scientist')
    def validate_scientist(self, key, scientist):
        if not scientist or scientist in [mission.scientist for mission in Mission.query.all()]:
            raise ValueError('must include a scientist who has not been on this mission previously') 
        return scientist
    
    @validates('planet')
    def validate_planet(self, key, planet):
        if not planet:
            raise ValueError('must include a planet') 
        return planet
    


# add any models you may need. 