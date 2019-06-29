#!/usr/bin/env python
import json, time, requests, sys,sqlite3, random
from sqlite3 import Error
from sql_dict import DataBase
from datetime import datetime
from bs4 import UnicodeDammit

reload(sys)  
sys.setdefaultencoding('utf8')
class colors:
    green = '\033[1;32;40m'
    red = '\033[1;31;40m'
    reset = '\033[0m'
    grey = '\033[1;30;40m'
    white = '\033[1;39;40m'



db = DataBase(filename='sqlite/tripadvisor.sqlite')



def city_in_db(city_name=None,state_name=None,country_name=None):
	sql = 'SELECT city_id FROM city WHERE city_name="%s" AND state="%s" AND country="%s" AND status=1' % (city_name,state_name,country_name)
	sql_result = db.execute(sql)
	
	#print 'result: %s len: %s' % (str(sql_result),str(len(sql_result)))
	
	if len(sql_result) == 1:
		print '%s Already in DB, skipping %s' % (colors.white,colors.reset)
		return True
	else:
		return False

def get_tripadvisor_geo_id(query):
	url = 'https://www.tripadvisor.com/TypeAheadJson?action=API&types=geo&filter=&legacy_format=true&urlList=false&strictParent=true&query=%s&max=10&name_depth=1&details=true&rescue=true&uiOrigin=Tourism_geopicker&source=Tourism_geopicker&startTime=%s' % (query,time.time())

	try:
	    res = requests.request("GET",url)
	    o = json.loads(res.text)

	except ValueError:
	    print( 'ERROR: ' + str(res))
	    sys.exit(0)

	return o

def process_city(data,city_name=None,country_name=None,state_name=None):
	try:


		timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		for o in data:

			status = 0
			ta_id = None
			ta_name = None
			ta_full_name = None
			ta_parent_name = None
			ta_parent_place_type = None
			ta_grandparent_name = None
			ta_place_type = None
			ta_parent_ids = None
			ta_grandparent_id = None
			ta_url = None
			ta_geo_name = None
			ta_document_id = None
			if 'details' in o and 'parent_name' in o['details']:
				parent_name = UnicodeDammit(o['details']['parent_name']).unicode_markup.lower()

			#city_name.lower() in o['name'].encode('utf-8').strip().lower() or state_name.lower() in o['name'].encode('utf-8').strip().lower()) and
			if 'name' in o and 'details' in o and 'parent_name' in o['details'] and  parent_name == country_name.lower():
				status = 1
				"""
				ta_id = o['value']
				ta_name = str(o['details']['name'].decode('utf-8').strip().replace("'", "\'"))
				ta_full_name = str(o['name'].decode('utf-8').strip().replace("'", "\'"))
				ta_parent_name =str(o['details']['parent_name'].decode('utf-8').strip().replace("'", "\'"))
				ta_parent_place_type = o['details']['parent_place_type']
				ta_grandparent_name = str(o['details']['grandparent_name'].decode('utf-8').strip().replace("'", "\'"))
				ta_place_type = o['details']['placetype']
				ta_parent_ids = ','.join(str(x) for x in o['details']['parent_ids'])
				ta_grandparent_id = o['details']['grandparent_id']
				ta_url = o['url'].decode('utf-8').strip()
				ta_geo_name = str(o['details']['geo_name'].decode('utf-8').strip().replace("'", "\'"))
				ta_document_id = o['document_id']
				"""
				ta_id = o['value']
				ta_name = UnicodeDammit(o['details']['name']).unicode_markup
				ta_full_name = UnicodeDammit(o['name']).unicode_markup
				ta_parent_name = UnicodeDammit(o['details']['parent_name']).unicode_markup
				ta_parent_place_type = o['details']['parent_place_type']
				ta_grandparent_name = UnicodeDammit(o['details']['grandparent_name']).unicode_markup
				ta_place_type = o['details']['placetype']
				ta_parent_ids = ','.join(str(x) for x in o['details']['parent_ids'])
				ta_grandparent_id = o['details']['grandparent_id']
				ta_url = o['url']
				ta_geo_name = UnicodeDammit(o['details']['geo_name']).unicode_markup
				ta_document_id = o['document_id']

			else:
				status = 0

			_row = {
				 'city_name': UnicodeDammit(city_name).unicode_markup,
				 'state': UnicodeDammit(state_name).unicode_markup,
				 'country': UnicodeDammit(country_name).unicode_markup,
				 'status':status,
				 'tripadvisor_id':ta_id,
				 'tripadvisor_name':ta_name,
				 'tripadvisor_full_name':ta_full_name,
				 'tripadvisor_parent_name':ta_parent_name,
				 'tripadvisor_parent_place_type':ta_parent_place_type,
				 'tripadvisor_grandparent_name':ta_grandparent_name,
				 'tripadvisor_place_type':ta_place_type,
				 'tripadvisor_parent_ids':ta_parent_ids,
				 'tripadvisor_grandparent_id' :ta_grandparent_id,
				 'tripadvisor_url':ta_url,
				 'tripadvisor_geo_name':ta_geo_name,
				 'tripadvisor_document_id':ta_document_id,
				 'city_tcreate' :timestamp
			    }

		   	print json.dumps(_row,indent=4)

			result = db.insert(tablename='city', row=_row, update=False)

			if status == 1:
				return True

	except Error as e:
		print '%sError processing: %s %s' % (colors.red,colors.reset,json.dumps(data,indent=4))

f = open('json/countries_final.json','r')
city_data = json.loads(f.read())

print '[ Countries ]\n============='

# show the stats
for country in city_data:
	count = 1
	if 'states' in country:
		for state in country['states']:
				count +=len(state['cities'])
	
	print '%s (%s)' % (str((country['countryName'])),str(count))


#total count
count = 1
count_limit = 5
for country in city_data:
	country_name = UnicodeDammit(country['countryName']).unicode_markup
	print '\n\nSorting country %s\n----------------------------------' % (country_name)

	if 'states' in country:

		for state in country['states']:
			state_name = UnicodeDammit(state['stateName']).unicode_markup
			city_count = 1
			for city in state['cities']:
				city_name = UnicodeDammit(city['cityName']).unicode_markup.replace('City of ','')
				print '#%s %s -> %s (%s of %s)' % (str(count),str(state_name),str(city_name),str(city_count),len(state['cities']))
				
				if city_in_db(city_name=city_name,state_name=state_name,country_name=country_name):
					continue

				city_count += 1

				count +=1

				# lets take a nap for a minute since TA rate limits us
				if count % 900 == 0:
					nap_time = random.randint(60,600)
					print '\n%s#######################\n Taking a nap for %ss ..\n#######################\n %s' % (colors.white, str(nap_time),colors.reset)

					time.sleep(nap_time)				
				
    			# Lets query with city and state
				query = '%s %s' % (city_name.replace(' County','').replace('Gemeente ',''),state_name)

				o = get_tripadvisor_geo_id(query)







				# If we get no results, lets just try the city name
				if len(o) == 1 and 'See all results for' in o[0]['name']:
				
					print 'No results found for %s -> %s -> %s' % (country_name,state_name,city_name) 
					print 'Trying different query'

					query = '%s' % (city_name.replace(' County','').replace('Gemeente ',''))

					o = get_tripadvisor_geo_id(query)

					result = process_city(o,city_name=city_name,country_name=country_name,state_name=state_name)

					if result:
						print '%sFound city!%s - %s -> %s -> %s' % (colors.green,colors.reset,country_name,state_name,city_name)
					else:
						print '%sCity not found%s - %s -> %s -> %s' % (colors.red,colors.reset,country_name,state_name,city_name)
						print 'data: %s' % str(o)

				# We have results
				else:
					result = process_city(o,city_name=city_name,country_name=country_name,state_name=state_name)

					# We successfully found the right city
					if result:
						print '%sFound city!%s - %s -> %s -> %s' % (colors.green,colors.reset,country_name,state_name,city_name)
					
					# If we didn't, letry just try with just the city
					else:
						print '%sCity not found%s - %s -> %s -> %s' % (colors.red,colors.reset,country_name,state_name,city_name)
						print 'Trying different query'

						query = '%s' % (city_name.replace(' County','').replace('Gemeente ',''))

						o = get_tripadvisor_geo_id(query)

						result = process_city(o,city_name=city_name,country_name=country_name,state_name=state_name)

						if result:
							print '%sFound city!%s - %s -> %s -> %s' % (colors.green,colors.reset,country_name,state_name,city_name)
						else:
							print '%sCity not found%s - %s -> %s -> %s' % (colors.red,colors.reset,country_name,state_name,city_name)
							print 'data: %s' % str(o)

				#if count == count_limit:
				#	print 'Hit limit, quitting!'
				#	sys.exit(0)
			


sys.exit(0)





# Input State, city
# in result look for country

