import ast
from curses import meta
from mongoengine import *
import os
import exifread

def parse_key(key,value):
    import ast
    try:
        return key_dict[key](value) 
    except KeyError:
        try:
            return ast.literal_eval(value)
        except SyntaxError:
            return str(value)
        except ValueError:
            return str(value)


def parse_fraction(x):
    l = [float(v) for v in x.split('/')]
    if len(l) == 1:
        l.append(1)
    return float(l[0]/l[1])

def parse_datetime(x, fmt='%Y:%m:%d %H:%M:%S'):
    import datetime
    return datetime.datetime.strptime(x, fmt)

def parse_array_with_fractions(x):
    import re
    extra = re.compile('[[" \]]')
    result = extra.sub('', x).split(',')
    return [parse_fraction(i) for i in result]

def parse_array_with_ellipses(x):
    return ast.literal_eval(x)[:-1]
    
key_dict = {
    'EXIF FocalPlaneXResolution': parse_fraction,
    'EXIF FocalPlaneYResolution': parse_fraction,
    'GPS GPSAltitude': parse_fraction,
    'EXIF FocalLength': parse_fraction,
    'EXIF ExposureTime': parse_fraction,
    'EXIF FNumber': parse_fraction,
    'EXIF FocalPlaneYResolution': parse_fraction,
    'EXIF DateTimeOriginal': parse_datetime,
    'EXIF DateTimeDigitized': parse_datetime,
    'Image DateTime': parse_datetime,
    'GPS GPSLatitude': parse_array_with_fractions,
    'GPS GPSLongitude': parse_array_with_fractions,
    'Image Tag 0xC74E': parse_array_with_ellipses,
}


flir_dict = {
    'RJPEG': {
        'dt_key': 'DateTimeOriginal',
        'dt_format': '%Y:%m:%d %H:%M:%S.%f%z',
        'end_char': 6,
    },
    'TIFF': {
        'dt_key': 'SubSecDateTimeOriginal',
        'ext':'.tif',
        'dt_format': '%Y:%m:%d %H:%M:%S.%f',
        'end_char': 4,
    },
    'JPEG': {
        'dt_key': 'FileModifyDate',
        'dt_format': '%Y:%m:%d %H:%M:%S%z',  # Note: the time is local machine
        'end_char': 7,
    }
}

mica_dict = {
    'TIFF': {
        'dt_key': 'SubSecDateTime',
        'dt_format': '%Y:%m:%d %H:%M:%S.%f'
    }
}

ext_dict = {
    'TIFF' : ['tif', 'TIF', 'tiff', 'TIFF'],
    'JPEG' : ['jpg', 'JPG', 'jpeg', 'jpeg']
}

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
            [tags.update({key:parse_key(key,raw_tags[key].printable)}) for key in raw_tags.keys()]
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
            LatDMS = self.metadata['GPS GPSLatitude']
            LonDMS = self.metadata['GPS GPSLongitude']
            LatDD = LatDMS[0] + LatDMS[1]/60 + LatDMS[2]/(60*60)
            LonDD = LonDMS[0] + LonDMS[1]/60 + LonDMS[2]/(60*60)
            if self.metadata['GPS GPSLatitudeRef'] == 'S':
                LatDD *= -1
            if self.metadata['GPS GPSLongitudeRef'] == 'W':
                LonDD *= -1
            return [LonDD, LatDD]