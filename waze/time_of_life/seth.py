# Standard Imports
import json
from io import BytesIO, StringIO
import datetime
import timeit

# 3rd-party Imports
import pycurl
from pprint import pprint # optional
from timeit import default_timer as timer

VERBOSE = True

AGE_LIMIT_MINUTES = 15  # Limit in minutes

POLYGONS = {
	'california': '-124.374000,42.040000;-119.980000,41.975000;-119.804000,38.864000;-113.652000,34.279000;-114.355000,32.666000;-119.760000,32.518000;-123.847000,36.887000;-124.770000,41.120000;-124.374000,42.040000;-124.374000,42.040000', 
	'texas_group': '-102.12890625,40.04443758460856;-103.1396484375,37.020098201368114;-109.13818359375,37.03763967977139;-109.13818359375,31.147006308556566;-103.99658203125,28.786918085420226;-96.94335937499999,25.24469595130604;-93.36181640625,30.334953881988564;-93.55957031249999,31.952162238024975;-94.72412109375,40.06125658140474;-102.12890625,40.04443758460856',
	'florida_group': '-88.209228515625,35.016500995886005;-88.65966796875,29.79298413547051;-82.7984619140625,24.292033766081378;-79.903564453125,24.816653556469955;-78.53302001953125,33.863573814253485;-79.67010498046875,34.813803317113155;-80.6781005859375,34.82282272723702;-80.96923828125,35.16482750605027;-82.408447265625,35.22767235493586;-88.209228515625,35.016500995886005',
	'new_york_group': '-73.89747619628905,40.994410999439516;-74.11857604980469,40.52528265385008;-73.01513671875,40.60144147645398;-69.4720458984375,41.24270715552139;-66.566162109375,44.574817404670306;-68.291015625,48.085418575511966;-71.004638671875,46.263442671779885;-79.552001953125,43.45291889355465;-79.815673828125,42.00848901572399;-73.89747619628905,40.994410999439516',
	'washington_group': '-124.815673828125,49.009050809382046;-124.55749511718749,41.9921602333763;-120.00915527343749,41.98603585974727;-120.01190185546875,38.9914373369788;-114.65881347656249,34.99850370014629;-114.82910156249999,32.46806060917602;-109.6875,30.86451022625836;-95.284423828125,39.99395569397331;-97.14660644531249,49.01985919086641;-124.815673828125,49.009050809382046',
	'pennsylvania_group': '-80.52978515625,42.32606244456202;-80.782470703125,39.90973623453719;-79.47509765625,39.2492708462234;-75.56396484375,37.59682400108367;-73.95996093749999,40.01078714046552;-74.1796875,41.1455697310095;-75.30029296875,41.983994270935625;-79.7607421875,41.983994270935625;-79.7607421875,42.52069952914966;-80.52978515625,42.32606244456202',
	'north_carolina_group': '-90.263671875,35.04798673426734;-80.9033203125,35.10193405724606;-77.27783203125,33.17434155100208;-73.883056640625,36.12900165569652;-78.1787109375,39.825413103424786;-80.79345703125,39.977120098439634;-82.7490234375,38.41055825094609;-84.96826171874999,39.13006024213511;-89.2529296875,37.055177106660814;-90.263671875,35.04798673426734',
	'minnesota_group': '-88.099365234375,35.04798673426734;-90.3076171875,38.54816542304656;-90.087890625,41.902277040963696;-92.548828125,44.68427737181225;-89.47265625,47.96050238891509;-94.8779296875,49.410973199695846;-98.349609375,48.980216985374994;-94.0869140625,28.93124697186731;-88.582763671875,28.632746799225856;-88.099365234375,35.04798673426734',
	'illinois_group': '-89.45068359374999,48.03401915864286;-92.28515625,47.025206001585396;-93.33984375,45.49094569262732;-90.59326171875,42.50450285299051;-91.62597656249999,40.39676430557203;-88.76953125,36.27970720524017;-87.25341796875,41.80407814427234;-83.056640625,41.60722821271717;-82.33154296875,45.84410779560204;-89.45068359374999,48.03401915864286',
	'ohio_group': '-87.839,41.826;-80.281,42.461;-80.303,39.374;-82.742,38.071;-88.345,37.672;-87.839,41.826'
}

WAZE_URL = "https://na-georss.waze.com/rtserver/web/TGeoRSS?tk=ccp_partner&ccp_partner_name=Banjo,%20Inc.&format=JSON&types=alerts&polygon="

# Standard colors
SUCCESS='\033[0;32m' 		# Green
WARNING='\033[0;33m' 		# Yellow
ERROR='\033[0;31m' 			# Red
INFO='\033[01;34m' 			# Blue
UNIQUE='\033[00;35m'		# Light Purple
CASUAL='\033[02;37m'		# Grey
DEBUG1='\033[00;36m'		# Light Blue
DEBUG2='\033[02;36m'		# Teal
RESET='\033[0m' 			# Back to Default


class NationalWazeConnector():

	def __init__(self, *args, **kwargs):
		# Time Variables
		self.start = timer()
		self.timestamp = datetime.datetime.now()
		self.file_timestamp = self.timestamp.strftime('%Y-%m-%d-%H%M')
		self.cutoff = self.timestamp - datetime.timedelta(minutes=AGE_LIMIT_MINUTES)
		self.cutoff_milliseconds = int(self.cutoff.timestamp() * 1000)

		# Counter Variables
		self.grand_total = 0
		self.total_signals = 0
		self.total_too_old = 0
		self.total_weather = 0
		self.total_regions = 0
		self.total_latency = 0

		# Outputs
		if VERBOSE:
			# Formatting for highlighting problems and succcesses... Sleep deprived solution
			self.warning_check = lambda v : f'{CASUAL}{v}{RESET}' if v is 0 else f'{WARNING}{v}{RESET}' # 0 is good
			self.success_check = lambda v : f'{CASUAL}{v}{RESET}' if v is 0 else f'{SUCCESS}{v}{RESET}'  # more than 0 is good
			self.delay_check = lambda v : f'{CASUAL}{v}{RESET}' if v < 2 else f'{WARNING}{v} seconds {RESET}'  # less than 2 is good
			self.runtime_check = lambda a,b : f'{CASUAL}{a}{RESET}' if a < (2 * b)  else f'{WARNING}{a} seconds {RESET}'  # less than 2 * y is good

			# Outputs
			print(f'{INFO}Starting the National Waze Connector with Verbose messages{RESET}\n')
			print(f'{INFO}Basic Times Variables{RESET}')
			print(f'{DEBUG1}Timestamp:{RESET} \t\t{CASUAL}{self.timestamp}{RESET}')
			print(f'{DEBUG1}file_timestamp:{RESET} \t{CASUAL}{self.file_timestamp}{RESET}')
			print(f'{DEBUG1}cutoff:{RESET} \t\t{CASUAL}{self.cutoff}{RESET}')
			print(f'{DEBUG1}cutoff_milliseconds:{RESET} \t{CASUAL}{self.cutoff_milliseconds}{RESET}\n')

	def main(self):

		for key, value in POLYGONS.items():
			start = timer()
			self.get_signals(key, value)

			if VERBOSE:
				latency = timer() - start
				print(f'{DEBUG1}latency:{RESET} \t{self.delay_check(latency)}') #  Time in seconds


		if VERBOSE:
			print(f'{DEBUG2}----------------------------------------{RESET}')
			print(f'{SUCCESS}SUCCESS:{RESET} Finished gathering results for all regions')
			print(f'{DEBUG2}========================================{RESET}')
			print(f'{INFO}Final Results for Signals within the last {AGE_LIMIT_MINUTES} minutes{RESET}')
			print(f'{DEBUG1}Total Regions:{RESET} \t{CASUAL}{self.total_regions}{RESET}')
			print(f'{DEBUG1}Grand Total:{RESET} \t{INFO}{self.grand_total}{RESET}')
			print(f'{DEBUG1}Total Signals:{RESET} \t{self.success_check(self.total_signals)}')
			print(f'{DEBUG1}Total Too Old:{RESET} \t{self.warning_check(self.total_too_old)}')
			print(f'{DEBUG1}Total Weather:{RESET} \t{self.warning_check(self.total_weather)}')
			runtime = timer() - self.start
			print(f'{DEBUG1}Total Runtime:{RESET} \t{self.runtime_check(runtime, self.total_regions)}\n')


	def get_signals(self, region, polygon):

		# Counts
		self.total = 0
		self.signals = 0
		self.too_old = 0
		self.weather = 0

		# Set up the curl
		curl = pycurl.Curl()
		raw_object = BytesIO()

		# Set URL value
		curl.setopt(curl.URL, f'{WAZE_URL}{polygon}')

		# Write bytes that are utf-8 encoded
		curl.setopt(curl.WRITEDATA, raw_object)
		# curl.setopt(pycurl.HTTPHEADER, ['Accept: application/json'])

		# Perform a file transfer 
		curl.perform() 

		# print(json.loads(raw_data))

		# End curl session
		curl.close()

		# Store the raw data
		raw_data = raw_object.getvalue()
		raw_file = open(f'/Users/pavelkomarov/Desktop/output/raw/{self.file_timestamp}_{region}.json', 'wb')
		raw_file.write(raw_data) 

		# Convert the raw data to a dictionary
		json_data = json.loads(raw_object.getvalue())

		# pprint(json_data['alerts'])

		# Filter out the junk
		self.filtered_json = {'alerts': []}
		for alert in json_data['alerts']:
			self.filter_alert(alert, region)

		# pprint(filtered_json)

		# Save the filtered data to a file
		filtered_file = open(f'/Users/pavelkomarov/Desktop/output/filtered/{self.file_timestamp}_{region}.json', "w")
		filtered_file.write(json.dumps(self.filtered_json))

		# Update the totals
		self.grand_total = self.grand_total + self.total 
		self.total_signals = self.total_signals + self.signals 
		self.total_too_old = self.total_too_old + self.too_old
		self.total_weather = self.total_weather + self.weather
		self.total_regions = self.total_regions + 1

		# Output the stats
		if VERBOSE:
			print(f'{DEBUG2}----------------------------------------{RESET}')
			print(f'{DEBUG1}Region:{RESET} \t{INFO}{region}{RESET}')
			print(f'{DEBUG1}Total:{RESET}  \t{CASUAL}{self.total}{RESET}')
			print(f'{DEBUG1}Signals:{RESET} \t{self.success_check(self.signals)}')
			print(f'{DEBUG1}Too Old:{RESET} \t{self.warning_check(self.too_old)}')
			print(f'{DEBUG1}Weather:{RESET} \t{self.warning_check(self.weather)}')

	def filter_alert(self, alert, region):

		self.total = self.total + 1
		waze_type = alert.get('type')
		waze_subtype = alert.get('subtype')

		if alert.get('pubMillis') < self.cutoff_milliseconds:
			# This does not fit in the alloted time frame 
			self.too_old = self.too_old + 1
		elif waze_type == 'WEATHERHAZARD' and waze_subtype == "":
			# This is a weather signal and used
			self.weather = self.weather + 1
		else:
			# Congratulations you have good signal
			self.filtered_json['alerts'].append(alert)
			self.signals = self.signals + 1


if __name__ == '__main__':
    NationalWazeConnector().main()

