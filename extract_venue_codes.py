#!/usr/bin/env python
import json, time, requests, sys,sqlite3, random, re, os,lxml
from sqlite3 import Error
from sql_dict import DataBase
from datetime import datetime
try: 
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup
from bs4 import UnicodeDammit

reload(sys)  
sys.setdefaultencoding('utf8')
class colors:
    green = '\033[1;32;40m'
    red = '\033[1;31;40m'
    reset = '\033[0m'
    grey = '\033[1;30;40m'
    white = '\033[1;39;40m'


timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

db = DataBase(filename='sqlite/tripadvisor2.sqlite')

# limit
sleep_limit = 500
counter = 1

countries = [
	{'name':'United States','id':191},
	
	{'name':'China','id':294211},
	{'name':'Canada','id':153339},
	{'name':'Taiwan','id':293910},
	{'name':'Ireland','id':186591},
	{'name':'Austria','id':190410},
	{'name':'South Korea','id':294196},
	##{'name':'Hong Kong','id':294217},
	{'name':'Germany','id':187275},
	{'name':'Netherlands','id':188553},
	{'name':'Belgium','id':188634},
	{'name':'Finland','id':189896},
	{'name':'Japan','id':294232},
	{'name':'France','id':187070},

	{'name':'United Kingdom','id':186216},
	{'name':'Switzerland','id':188045},
	{'name':'Israel','id':293977},
	{'name':'Sweden','id':189806},
	{'name':'Australia','id':255055},
	{'name':'Norway','id':190455},
	{'name':'Denmark','id':189512},
	{'name':'United Arab Emirates','id':294012},
	##{'name':'Singapore','id':294265},
	{'name':'Brazil','id':294280},
	{'name':'New Zealand','id':255104},
]


def get_cities(country_id=None):
	sql = 'SELECT city_geo_id,city_name,region_name FROM city WHERE country_geo_id=%s AND status=1' % (country_id)
	sql_result = db.execute(sql)
	return sql_result

def get_venues(city_id=None,country_id=None,country_name=None,region_name=None,city_name=None):

	path = 'raw/venues/%s' % country_name
    
	if not os.path.exists(path):
		os.makedirs(path)

	file_name = '%s/%s-%s-%s.html' % (path,region_name.replace('/','+'),city_name.replace('/','+'),str(city_id))
	url = 'https://www.tripadvisor.com/Attractions-g%s-Activities-c56-t208' % str(city_id)

	if not os.path.isfile(file_name):

		try:
		    res = requests.request("GET",url)
		    html = res.text

		except ValueError:
		    print( 'ERROR: ' + str(res))
		    sys.exit(0)


		f = open(file_name, 'w')
		f.write(html)
		f.close()
		return True
	else:
		print 'already exists: %s' % url
		return False


for country in countries:
	country_id = country['id']
	country_name = country['name']

	print 'grabbing cities for country: %s' % country_name	
	cities = get_cities(country_id=country_id)

	#print json.dumps(cities,indent=4)

	for city in cities:
		city_name = city['city_name']
		city_id = city['city_geo_id']
		region_name = city['region_name']

		print '#%s Extracting: %s -> %s -> %s' % (str(counter),country_name,region_name,city_name)

		result = get_venues(city_id=city_id,country_id=country_id,country_name=country_name,region_name=region_name,city_name=city_name)
		
		if result:
			counter+=1

		if counter % sleep_limit == 0:
			nap_time = random.randint(60,600)
			print '\n%s#######################\n Taking a nap for %ss ..\n#######################\n %s' % (colors.white, str(nap_time),colors.reset)
			time.sleep(nap_time)

sys.exit(0)