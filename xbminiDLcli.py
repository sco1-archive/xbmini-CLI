import platform
import re
from pathlib import Path

import win32api


def getXBMdrives():
    myOS = platform.system()
    if myOS == 'Windows':
        # Pull list of drive letters
        drives = win32api.GetLogicalDriveStrings()
        drives = [drivestr for drivestr in drives.split('\000') if drivestr]
        
        # Associate drive names with drive
        drivenames = {drive:win32api.GetVolumeInformation(drive)[0] for drive in drives}
        
        xbminidrives = [Path(drive) for drive in drivenames if re.match('X\d+D\d+', drivenames[drive])]
    else:
        # TODO: Add OSX support, then Linux (if different from OSX)
        raise NotImplementedError

    return xbminidrives