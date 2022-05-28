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


def clear_db(collection='Flight'):
    if collection == 'Flight':
        for flight in Flight.objects:
            flight.delete()
        return len(Flight.objects)

# %%

clear_db()
[Flight.make_flight_from_df(row).save() 
    for index, row in df.iterrows()]

print("A total of {} Flight obj"ects written to db".format(
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
df.head()
# %%
import random
from models.image import Image

### Let's do images now.
image_dir = '/Users/kellycaylor/Remotes/forge/waves-dangermond/UAV/Level00'
image_list_file = '/Users/kellycaylor/Documents/dev/uav-db/image_lists/all_tif_images.txt'

with open(image_list_file, 'r') as f:
    image_list = f.read().splitlines()
    
image_list_full = [image_dir + image[1:] for image in image_list]

image = random.sample(image_list_full,1)


# %%
