import ast
import datetime
import re


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


def parse_key(key,value):
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
    return datetime.datetime.strptime(x, fmt)

def parse_array_with_fractions(x):
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
