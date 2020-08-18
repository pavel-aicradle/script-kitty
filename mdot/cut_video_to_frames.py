

import os
from tqdm import tqdm
from random import random
from joblib import Parallel, delayed
from multiprocessing import current_process
from time import sleep
from subprocess import Popen

p_include = 0.1 # probability of inclusion
vids_dir = 'mdot1'
out_dir = 'mdot_random_frames1'


if not os.path.exists(out_dir): os.mkdir(out_dir)


def process_each(f):
	temp = 'temp'# + str(current_process()._identity[0])
	os.mkdir(temp)

	proc = Popen(['ffmpeg -i ' + vids_dir + '/' + f + ' -vf fps=0.5 ' + temp + '/' + f[:-4] + '_%03d.jpg &> /dev/null'], shell=True) # convert to frames
	proc.wait()

	for frame in os.listdir(temp):
		#if '_13.' in f: print(frame) # should print 5 entries
		if random() <= p_include: # include frames with probability = p_include
			os.system('mv ' + temp + '/' + frame + ' ' + out_dir + '/' + frame) # move to the out_dir if selected

	os.system('rm -rf ' + temp) # clean up


Parallel(n_jobs=1)(delayed(process_each)(f) for f in tqdm(os.listdir(vids_dir)))