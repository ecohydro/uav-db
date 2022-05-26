from mongoengine import *
import os
from exifpy import exifread

class Image(Document):
    file = StringField(required=True)
    metadata = DictField()
    is_init = BooleanField(default=False)
    image_format = StringField()
    coords = DictField()
    altitidue = FloatField()
    timestamp = DateTimeField()

    def get_metadata(self):
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
        file = self.file
        fd = open(file, 'rb')
        # Read header tags
        tags = exifread.process_file(fd)
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
        metadata['SubSecDateTime'] = metadata.get('DateTime') + '.' + str(int(metadata.get('SubSecTime')))
        self.metadata=metadata
    