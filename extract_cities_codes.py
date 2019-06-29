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
	#{'name':'Hong Kong','id':294217},
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
	#{'name':'Singapore','id':294265},
	{'name':'Brazil','id':294280},
	{'name':'New Zealand','id':255104},
]



def get_country_page(country_id=None,page=None):
	url = 'https://www.tripadvisor.com/Attractions-g%s-oa%s' % (str(country_id),str(page))

	path = 'raw/cities/%s' % country_name
    
	if not os.path.exists(path):
		os.makedirs(path)

	file_name = '%s/%s.html' % (path,str(page))

	if not os.path.exists(file_name):

				# Tripadvisor rate limits at 500 GET requests, sleep randomly between 60 and 600s
		if counter % sleep_limit == 0:
			nap_time = random.randint(60,600)
			print '\n%s#######################\n Taking a nap for %ss ..\n#######################\n %s' % (colors.white, str(nap_time),colors.reset)
			time.sleep(nap_time)

		global counter

		counter +=1

		try:
		    res = requests.request("GET",url)
		    html = res.text

		except ValueError:
		    print( 'ERROR: ' + str(res))
		    sys.exit(0)


		f = open(file_name, 'w')
		f.write(html)
		f.close()

	else:
		f = open(file_name, "r")
		html = f.read()

	return html




def city_exists(city_id=None,country_id=None):
	sql = 'SELECT city_geo_id FROM city WHERE city_geo_id=%s AND country_geo_id=%s AND status=1' % (city_id,country_id)
	sql_result = db.execute(sql)
	
	#print 'result: %s len: %s' % (str(sql_result),str(len(sql_result)))
	
	if len(sql_result) == 1:
		print '%s Already in DB, skipping: %s %s' % (colors.white,colors.reset, str(city_id))
		return True
	else:
		return False



def get_max_page(html=None):
	
	result = re.findall('(?!class="paging taLnk ">)(\d+)(?=</a>)',html)
	print str(result)
	max = 0
	for i in range(len(result)):
		if int(result[i]) > max:
			max = int(result[i])

	print 'max pages: %s' % str(max)
	return max


def extract_city_codes():
	# Lets extract all the city names and store them in a database
	for country in countries:
		country_id = country['id']
		country_name = country['name']
		page = 20
		count = 1

		path = 'raw/cities/%s' % (country_name)
		file_list = os.listdir(path)

		for file in file_list:
			if file == '.DS_Store':
				continue
			file_name = path + '/' + file
			f = open(file_name, "r")
			html = f.read()

			print '%sopening file:%s %s' % (colors.white,colors.reset,file_name)
			parsed_html = BeautifulSoup(html)
			geo_list = parsed_html.body.find('ul', attrs={'class':'geoList'}).find_all('li')
			
			for item in geo_list:
				#print item
				city_name = item.a.get_text().replace(' attractions','')
				region_name = item.span.get_text()
				city_url = item.a.get('href')
				city_id = re.findall('g([0-9]+)+',city_url)[0]

				if not city_exists(city_id=city_id,country_id=country_id):
					print '%sSaving%s - region_name: %s city_name: %s city_id: %s city_url: %s' % (colors.white,colors.reset,region_name,city_name,str(city_id),city_url)

					_row = {
						 'city_name': UnicodeDammit(city_name).unicode_markup,
						 'region_name': UnicodeDammit(region_name).unicode_markup,
						 'country_name': UnicodeDammit(country_name).unicode_markup,
						 'country_geo_id':country_id,
						 'city_geo_id':city_id,
						 'listing_url': city_url,
						 'status': 1,
						 'city_tcreate' :timestamp
					    }

				   	#print json.dumps(_row,indent=4)

					result = db.insert(tablename='city', row=_row, update=False)
	 

# ====
# Main
# ====

# Lets extract all the cities from the countries to a local file


for country in countries:
	country_id = country['id']
	country_name = country['name']

	page = 20
	count = 1

	html = get_country_page(country_id=country_id,page=page)
	max_page = get_max_page(html=html)

	i = 0
	for i in range(max_page - 1):
		print '%sExtracting:%s %s -> %s of %s' % (colors.white,colors.reset,country_name,str(i),str(max_page-1))
		html = get_country_page(country_id=country_id,page=page)
		page += 50

	
extract_city_codes()
sys.exit(0)