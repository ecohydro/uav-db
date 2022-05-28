# %%
from mongoengine import *
from .fields import TimedeltaField
import datetime

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
    images = ListField()
    processed_log_file = StringField()
    
    meta = {
        'collection': 'flights'
    }


    
    @classmethod
    def make_flight_from_df(cls, row):
        timestamp = datetime.datetime.strptime(
                row.Timestamp, '%Y-%m-%d %H:%M:%S'
            )
        this_flight = Flight(
            timestamp = timestamp,
            date = timestamp.date(),
            model = row.Model,
            aircraft = row.Aircraft,
            PIC = row.PIC,
            site = row['Unnamed: 5'],
            location = row.Location,
            log_file = row['Log file'],
            battery = row.Battery,
            distance = row.Distance,
            max_height = row['Max Height']
        )
        hour, min, sec = [
            int(x) for x in row['Start time'].split(":")]
        this_flight.start_time = datetime.datetime(
                timestamp.year,
                timestamp.month,
                timestamp.day,
                hour, min, sec)
        hour, min, sec = [
            int(x) for x in row['End time'].split(":")]
        this_flight.end_time = datetime.datetime(
                timestamp.year,
                timestamp.month,
                timestamp.day,
                hour, min, sec)
        this_flight.duration = (this_flight.end_time - 
                                this_flight.start_time)
        this_flight.battery_level = {
            'takeoff': row.Takeoff,
            'landing': row.Landing
        }
        this_flight.Pix4D_capture = row[16]
        this_flight.image_folder = row['Image folder']
        this_flight.conditions = row.Conditions
        this_flight.purpose = row.Purpose
        this_flight.camera_model = row.Camera
        this_flight.camera_name = row.CAM
        this_flight.camera_powerup_time = None
        this_flight.notes = row.Notes
        try:
            log_file_index = int(row['LOG_FILE index'])
        except ValueError:
            log_file_index = None
            
        this_flight.log_file_index = log_file_index
        try:
            flights_index = int(row['flights index'])
        except ValueError:
            flights_index = None
        this_flight.flights_index = flights_index
        this_flight.flight_id = str(this_flight.site + '_' 
                    + this_flight.location + '_' 
                    + this_flight.start_time.isoformat())
        return this_flight


