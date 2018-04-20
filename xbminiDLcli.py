import logging
import platform
import re
import time
from pathlib import Path

import click
from tqdm import tqdm, trange

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
@click.option('--outpathbase', type=Path, help='Base Output Directory')
@click.option('--date', type=str, prompt=True, help='Drop Date [YYYYMMDD]')
@click.option('--location', type=str, prompt=True, help='Drop Location')
@click.option('--systemname', type=str, prompt=True, help='Parachute System Name')
@click.option('--auw', type=float, prompt=True, help='System All Up Weight [lb]')
@click.option('--nloggers', type=int, prompt=True, help='Number of XBM loggers')
@click.option('--timeout', type=int, default=5, help='Device Polling Timeout (s)')
def mainCLI(outpathbase, date, location, systemname, auw, nloggers, timeout):
    if not outpathbase:
        outpathbase = Path(f"./{date} {location}/{systemname}")

    for ii in range(nloggers):
        click.pause(info=f"\nPress any key to download logger #{ii+1} ... ")
        
        retry = True
        while retry:
            xbmdrives = XBMpoll(timeout)
            if xbmdrives:
                retry = False
                click.secho(f"Found {len(xbmdrives)} XBM(s)", fg='green')
                
                # Limit file transfer to first drive found
                if len(xbmdrives) > 1:
                    click.secho(f"Processing volume '{xbmdrives[0]}', ignoring '{xbmdrives[1:]}''")
                
                sourcedrive = xbmdrives[0]
            else:
                click.secho('No logger(s) found', fg='red')
                retry = click.confirm('Retry search?')
        
        if xbmdrives:
            transferdata(sourcedrive, outpathbase, ii)

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

def XBMpoll(timeout, pollinginterval=0.5):
    click.secho('Polling for XBM devices ...', fg='green')

    pollinginterval = 0.5  # Polling interval, seconds
    loggerfound=False
    for ii in trange(0, timeout*int(1/pollinginterval), 1, bar_format='{bar}| {remaining}'):
        xbmdrives = getXBMdrives()
        if len(xbmdrives) == 0:
            time.sleep(pollinginterval)
        else:
            logging.debug(f"Found {len(xbmdrives)} XBM(s)")
            return xbmdrives
    else:
        logging.debug('No logger(s) found')

def transferdata(sourcedrive, outpathbase):
    pass

if __name__ == "__main__":
    mainCLI()
