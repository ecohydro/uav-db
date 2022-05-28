from curses import meta
from mongoengine import *
import os
import exifread
from .metadata import (
    parse_key, flir_dict, mica_dict, ext_dict
)

class Image(Document):
    
    file = StringField(required=True)
    metadata = DictField()
    is_init = BooleanField(default=False)
    image_format = StringField()
    coords = PointField()
    altitiude = FloatField()
    timestamp = DateTimeField()
    meta = {
        'collection':'images'
    }    
    
    def __init__(self, file=None):
        super(Image, self).__init__()
        self.metadata = self.get_metadata(file)
        self.file = self.metadata['SourceFile']
        self.image_format = self.metadata['FileType']
        self.coords = {
            "type": "Point",
            "coordinates" : self.get_coords()
        }
        self.altitude = self.metadata['GPS GPSAltitude']
        self.timestamp = self.metadata['Image DateTime']

    @classmethod
    def get_metadata(cls, file):
        import ast
        """
        Gets the image metadata using exifread.

        Parameters
        ----------
        file : str
            File for which metadata should be retrieved.

        Returns
        -------
        metadata : dict
            Dictionary of image metadata

        """
        # Open file
        if file:
            print("Processing metadata for {}".format(file))
            fd = open(file, 'rb')
            # Read header tags
            raw_tags = exifread.process_file(fd)
            tags = {}
            [
                tags.update(
                    {key:parse_key(key,raw_tags[key].printable)}
                    ) 
                for key in raw_tags.keys()
            ]
            metadata = {
                'SourceFile' : file,
                'FileName' : os.path.basename(file),
                'Directory' : os.path.dirname(file),
                'FileSize' : os.path.getsize(file),
                'FileModifyDate' : os.path.getmtime(file),
                'FileAccessDate' : os.path.getatime(file),
                'FileTypeExtension' : os.path.basename(file).split('.')[1],
            }
            # TODO: Convert the file modify and access datetimes to UTC (by default
            # they are in the timezone of the OS)
            # 1. Get local machine timezone.
            # 2. Convert to UTC.
            metadata['FileType'] = [k for k,v in ext_dict.items() if metadata.get('FileTypeExtension') in v][0]
            metadata.update(tags)
            try:
                metadata['SubSecDateTime'] = metadata.get('DateTime') + '.' + str(int(metadata.get('SubSecTime')))
            except TypeError:
                metadata['SubSecDateTime'] = None
            return metadata

    def get_coords(self, fmt="DMS"):
        if fmt == "DMS":
            lat_dms = self.metadata['GPS GPSLatitude']
            lon_dms = self.metadata['GPS GPSLongitude']
            lat_dd = lat_dms[0] + lat_dms[1]/60 + lat_dms[2]/(60*60)
            lon_dd = lon_dms[0] + lon_dms[1]/60 + lon_dms[2]/(60*60)
            if self.metadata['GPS GPSLatitudeRef'] == 'S':
                lat_dd *= -1
            if self.metadata['GPS GPSLongitudeRef'] == 'W':
                lon_dd *= -1
            return [lon_dd, lat_dd]
        else:
            raise ValueError("fmt {} not recognized.".format(fmt))