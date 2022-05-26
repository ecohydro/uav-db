# %%
from mongoengine import *
connect(db='uav_test')

# %%
import pandas as pd
log_file = "MicaSense-Flight Log.csv"
dir = "/Users/kellycaylor/Documents/dev/uav-db"
flight_log = dir + "/flight_logs/" + log_file
print("\nlog: ",flight_log)
df = pd.read_csv(flight_log)

# %%
import datetime
from models.flight import Flight
def make_flight_from_df(row):
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

def clear_db(collection='Flight'):
    if collection == 'Flight':
        for flight in Flight.objects:
            flight.delete()
        return len(Flight.objects)

# %%

clear_db()
for i in range(len(df)):
    flight = make_flight_from_df(df.iloc[i])
    if flight:
        flight.save()

print("A total of {} Flight objects written to db".format(
    len(Flight.objects)
))
# %%
# Pull all the flight data out of the database and into a pandas dataframe:

df = pd.DataFrame([flight.to_mongo().to_dict() for flight in Flight.objects])
df.head()
# %%
# Slightly slower loads... 
import json
df = pd.DataFrame([json.loads(flight.to_json()) for flight in Flight.objects])  
