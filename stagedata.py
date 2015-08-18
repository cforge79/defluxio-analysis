 # -*- coding: utf8 -*-
import pandas as pd
import freqanalysis.datatools as datatool
import numpy as np
import sys as sys
import argparse
# pip install progressbar2
import progressbar as pb
import os

cmd_parser = argparse.ArgumentParser()
cmd_parser.add_argument("datadir", help="directory containing the frequency measurements (i.e. YYYYMMDD.txt files)")
cmd_parser.add_argument("-a", "--alldata", help="Copy all data into the HDF+ file (default: off)", action="store_true")
cmd_parser.add_argument("outfile", help="HDF+ file to create")
args = cmd_parser.parse_args()

print "Slurping data from %s, writing to %s" % (args.datadir,
    args.outfile)
files = sorted(os.listdir(args.datadir))

if args.alldata:
  print "Note: will export all records."

print "Loading datasets. This might take a while."
alldata = None
with pb.ProgressBar(maxval=len(files)) as progress:
  for idx, file in enumerate(files):
    newdata = datatool.load_data_as_dataframe(os.path.join(args.datadir, file))
    if idx == 0:
      alldata = newdata
    else:
      alldata = alldata.append(newdata, ignore_index=True)
    progress.update(idx)
print "Finished reading data into memory."

print "Computing Savitzky-Golay Filter (windowlen=7, polyorder=2)"
alldata = datatool.addSavitzkyGolay(alldata)

#print "Selecting all friday data for comparison."
## select the friday 8:00 to 11:00 UTC datasets from the alldata frame
fridaydata = alldata[(alldata.weekday == 4) & (alldata.hour > 7) &
    (alldata.hour < 11)]

print "Selecting eclipse data"
eclipsedata = alldata[(alldata.unix >= 1426838400) & (alldata.unix < 1426849200)]

print "Selecting Amsterdam blackout data"
amsterdam = alldata[(alldata.unix >= 1427445400) & (alldata.unix < 1427455400)]

print "Selecting KKW Grundremmingen Schnellabschaltung 25.03.2015 data"
grundremmingen = alldata[(alldata.unix >= 1427268780) & (alldata.unix < 1427269200)]

print u"Selecting KKW Mühleberg Schnellabschaltung 06.07.2015 data"
muehleberg = alldata[(alldata.unix >= 1436173380 - 3*60) &
    (alldata.unix < 1436173380+ 10*60)]

with pd.get_store(args.outfile) as store:
  store['eclipsedata'] = eclipsedata
  store['fridaydata'] = fridaydata
  store['grundremmingen'] = grundremmingen
  store['amsterdam'] = amsterdam
  store['muehleberg'] = muehleberg
  if args.alldata:
    print "Storing also all records into the data file"
    store['alldata'] = alldata


