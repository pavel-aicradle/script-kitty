
import json
import os

infile = '5.json'
w = 1280
h = 720


record = json.load(open(infile))

with open(infile[:-4] + 'csv', 'w+') as f: # output file
	f.write("frame_id,xmin,ymin,xmax,ymax,object_name,object_confidence,x_centroid,y_centroid\n")

	for frame in record['tracking-annotations']:
		frame_id = frame['frame-no']

		for bbox in frame['annotations']:
			xmin = bbox['left']/w
			ymin = bbox['top']/h
			xmax = xmin + bbox['width']/w
			ymax = ymin + bbox['height']/h
			object_name = bbox['object-name']
			object_confidence = '1' if 'occluded' in bbox['label-category-attributes'] and \
				bbox['label-category-attributes']['occluded'] == "no" else '0'
			x_centroid = (xmin + xmax)/2
			y_centroid = (ymin + ymax)/2

			for n in [xmin, ymin, xmax, ymax]: # sanity check to make sure my w and h aren't wrong
				assert 0 <= n <= 1

			f.write(','.join([frame_id, str(xmin), str(ymin), str(xmax), str(ymax),
				object_name, object_confidence, str(x_centroid), str(y_centroid)]) + '\n')

