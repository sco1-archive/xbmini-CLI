# xbmini DL CLI
Command Line Tool for downloading log files from the [GCDC HAM](http://www.gcdataconcepts.com/ham.html)

```
$ python xbminiDLcli.py --outpathbase "~/Path/To/Desktop"
Date: 20170711
Location: Quonset
Systemname: T-11
Auw: 350
Nloggers: 1

Press any key to download logger #1 ...
Polling for XBM devices ...

Found 1 XBM(s)
Downloading Log 10 of 10 ██████████████████████████| 139.85it/s
```

## Option Flags
### `--outpathbase:pathlib.Path`
Base Output Directory

Defaults to current directory (`'.'`) if not explicitly set

### `--date:str`
Drop Date, YYYYMMDD

Prompts user if not explicitly set

### `--location:str`
Drop Location

Prompts user if not explicitly set

### `--systemname:str`
Parachute System Name

Prompts user if not explicitly set

### `--auw:float`
System All Up Weight (AUW), generally pounds

Prompts user if not explicitly set

### `--nloggers:int`
Number of XBM loggers

Prompts user if not explicitly set

### `--timeout:int`
Device Polling Timeout, seconds

Used when searching for connected XBM devices.

Defaults to 5 seconds if not explicitly set

### `--help`
Show the help message and exit

## Notes
On Windows devices, BitLocker prevents querying volume info from locked drives. These drives are ignored by the CLI.

When polling for devices to download logs, if multiple drives are connected the CLI will download only from the first drive detected and ignore the remainder.

## Logging
Local debug logging is provided by [Python's `logging` package](https://docs.python.org/3/library/logging.html) to `./log`