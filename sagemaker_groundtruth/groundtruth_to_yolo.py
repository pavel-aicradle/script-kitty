
# For bounding-box jobs, Sagemaker gives back results in s3://.../job_name/manifests/output/output.manifest
# But the format isn't the same as that we are used to training and testing on, so do a little conversion.

# Yolo assumes you have a couple directories, one holding image, the other holding one .txt per image
# (with the same name as the corresponding picture). The .txts contain bounding boxes in format:
# class x y width height
# where x y width and height are all in [0,1] relative to the image's size and x and y are the *center*
# of the bounding box

import json
import os

job_name = 'mdot-9000'
out_dir = 'yolo'

if not os.path.exists(out_dir): os.mkdir(out_dir)

for line in open('output.manifest'):
	record = json.loads(line)

	try:
		name = record['source-ref'].split('/')[-1]
		imwidth = record[job_name]['image_size'][0]['width']
		imheight = record[job_name]['image_size'][0]['height']

		with open(out_dir + '/' + name[:-3]+'txt', 'w+') as f:
			for bbox in record[job_name]['annotations']: # format: {"class_id":0,"width":13,"top":164,"height":13,"left":194}
				# relative width and height
				w_yolo = bbox['width']/imwidth
				h_yolo = bbox['height']/imheight
				# x and y are *center*, so that's (left + bbox width/2)/imwidth = left/imwidth + w_yolo/2
				x_yolo = bbox['left']/imwidth + w_yolo/2
				y_yolo = bbox['top']/imheight + h_yolo/2

				f.write(str(bbox['class_id']) + ' ' + str(x_yolo) + ' ' + str(y_yolo) + ' ' + str(w_yolo)
					+ ' ' + str(h_yolo) + '\n')
	except:
		print(record)