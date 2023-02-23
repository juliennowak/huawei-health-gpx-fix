# Huawei Health GPX fix

## Description

This is a small project containing draft pieces of code used to fix the .GPX files exported by Huawei Health application
on IOS.

Tested on Huawei Health versions:

- 13.1.1.305
- 13.1.2.305

iOS versions:

- on iOS 16.3.1

### What it fixes

- .GPX files
- Route
- Pace
- Time
- Activity type
- Elevation

### What it doesn't fix

- .TCX files
- Heart rate

## Prerequisites

- Python 3.8

## Install requirements

```shell
pip install -r requirements.txt
```

## Process

The .GPX files you want to fix must be uploaded to the `/input` folder. You can put several files in this folder, they
will all be processed.

Then, you can run the cleaning process with :

```shell
python strava.py
```

The fixed .GPX files will be available in the `/output` folder at the end of the process.
You can upload them directly on Strava : http://www.strava.com/upload/select
