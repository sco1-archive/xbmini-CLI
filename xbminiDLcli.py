import platform
import logging
import time
import re

import click
from pathlib import Path

# Platform specific imports
myOS = platform.system().lower()
if myOS.startswith('win'):
    import win32api
elif myOS == 'darwin':
    from os import listdir

# Force UTC Timestamps
# From the logging cookbook: https://docs.python.org/3/howto/logging-cookbook.html
class UTCFormatter(logging.Formatter):
    converter = time.gmtime

logformat = r'%(asctime)s %(levelname)s:%(module)s:%(message)s'
dateformat = r'%Y-%m-%d %H:%M:%S'
logging.basicConfig(filename='./log/xbminiCLI.log', filemode='a', level=logging.DEBUG, 
                    format=logformat, datefmt=dateformat
                    )

@click.command()
@click.option('--date', prompt=True, help='Drop Date [str:YYYYMMDD]')
@click.option('--location', prompt=True, help='Drop Location [str]')
@click.option('--systemname', prompt=True, help='Parachute System Name [str]')
@click.option('--auw', prompt=True, help='System All Up Weight, lb [float]')
@click.option('--nloggers', prompt=True, help='Number of XBM loggers [int]')
def main(date, location, systemname, auw, nloggers):
    pass

def getXBMdrives():
    # Define XBM volume name regex
    xbmregex = 'X\d+D\d+'

    if myOS.startswith('win'):
        # Pull list of drive letters
        drives = win32api.GetLogicalDriveStrings()
        drives = [drivestr for drivestr in drives.split('\000') if drivestr]
        
        # Associate drive names with drive
        drivenames = {}
        for drive in drives:
            try:
                drivenames[drive] = win32api.GetVolumeInformation(drive)[0]
            except win32api.error as err:
                if err.args[0] == 21:
                    logging.debug(f"{drive} not ready, ignoring...")
                else:
                    raise err
                
        xbminidrives = [Path(drive) for drive in drivenames if re.match(xbmregex, drivenames[drive])]
    elif myOS == 'darwin':
        volumenames = listdir('/Volumes')
        xbminidrives = [Path(volume) for volume in volumenames if re.match(xbmregex, volume)]
    else:
        # TODO: Add Linux (if different from OSX)
        raise NotImplementedError(f"OS '{myOS}' not supported")

    return xbminidrives

if __name__ == "__main__":
    main()