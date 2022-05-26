# %%
from mongoengine import *
from .fields import TimedeltaField

class Flight(Document):
    
    flight_id = StringField(unique=True)
    timestamp = DateTimeField()
    date = DateField()
    aircraft = StringField()
    model = StringField()
    PIC = StringField()
    site = StringField()
    location = StringField()
    start_time = DateTimeField()
    end_time = DateTimeField()
    flight_time = TimedeltaField()
    distance = FloatField()
    max_height = FloatField()
    battery = StringField()
    batt_level = DictField()
    log_file = StringField()
    Pix4D_capture = StringField()
    image_folder = StringField()
    conditions = StringField()
    purpose = StringField()
    camera_model = StringField()
    camera_name = StringField()
    camera_powerup_time = DateTimeField()
    notes = StringField()
    log_file_index = IntField()
    flights_index = IntField()
    flight_area = PolygonField()
    flight_origin = PointField()
    meta = {
        'collection': 'flights'
    }



