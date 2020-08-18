"""
Simple script that pulls a collections of videos from our list of open rtsp streams.
"""
import os
from tqdm import tqdm
from time import sleep
from datetime import datetime
from csv import DictReader
from random import shuffle
from pytz import timezone
from joblib import Parallel, delayed

max_streams = None # None to get them all
num_seconds = 10 # time to clip from each stream
time_zone = timezone('America/New_York')
out_dir = 'mdot4'

if not os.path.exists(out_dir): os.mkdir(out_dir)
which_ffmpeg = '/usr/local/bin/ffmpeg' # because when I call with cron it doesn't recognize the ffmpeg command

with open('maryland.csv') as f:
	cams = [(x['OBJECTID'], x['rtsp_uri']) for x in DictReader(f)]
	shuffle(cams)
	cams = cams[:max_streams]

	def process_each(cam):
		iden, uri = cam
		if uri == 'N/A': return # can't pull from streams without rtsp, so skip
		
		out_name = datetime.now(tz=time_zone).strftime('%Y-%m-%d-%H-%M-%S') + '_' + iden + '.mp4'

		# download `num_seconds` worth of video from the stream in a new subshell
		os.system(which_ffmpeg + ' -i ' + uri + ' -acodec copy -vcodec copy -t ' +
			str(num_seconds) + ' ' + out_dir + '/' + out_name + ' &> /dev/null')

	# grab 50 videos at a time so I can get them all quicker
	Parallel(n_jobs=50)(delayed(process_each)(cam) for cam in tqdm(cams))
		