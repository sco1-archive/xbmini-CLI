import itertools
import logging
import platform
import re
import shutil
import sys
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
        # Default to current directory
        outpathbase = Path(f".")

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
            transferdata(sourcedrive, outpathbase, ii+1)

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

def transferdata(sourcedrive, outpathbase, loggeridx):
    inpath = sourcedrive / 'GCDC'
    logpaths = inpath.glob('DATA-*.csv')

    logcountIt, logmoveIt = itertools.tee(logpaths, 2)  # Split iterator since we need it twice
    nlogs = sum(1 for _ in logcountIt)  # Get number of logs without converting to list

    logging.debug(f"Log file path: {inpath}")
    logging.debug(f"Found {nlogs} log files")
    if nlogs == 0:
        click.secho('No log files found', fg='red')
        return

    logfolderprefix = 'XBM'
    outpath = outpathbase / f"{date} {location}/{systemname}/{logfolderprefix} {loggeridx}"
    logging.debug(f"Ouput directory: {outpath}")
    if not outpath.exists():
        logging.debug("Output directory not found, creating directory (w/parents)")
        outpath.mkdir(parents=True)

    transferpbar = tqdm(logmoveIt, bar_format='Downloading Log {n_fmt} of {total_fmt} |{bar}| {rate_fmt}')
    for log in transferpbar:
        shutil.copy(log, outpath)


if len(sys.argv) == 1:
    # If called without inputs, automatically enter interactive mode
    mainCLI()
else:
    # Otherwise pass everything straight through
    mainCLI(sys.argv[1:])
