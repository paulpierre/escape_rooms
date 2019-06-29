#!/usr/bin/env python
import json, time, sys,sqlite3, re, os,lxml, threading
from sqlite3 import Error
from sql_dict import DataBase
from datetime import datetime
try: 
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup
from bs4 import UnicodeDammit

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
	{'name':'Brazil','id':294280},
	{'name':'New Zealand','id':255104},
]



def listing_has_venue(html):

	parsed_html = BeautifulSoup(html,features='lxml')
	
	find_negative1 = parsed_html.body.find('div', attrs={'id':'broadening_sorry'})
	find_negative2 = parsed_html.body.find('h1',attrs={'id':'HEADING'})

	#print type(find_negative1)
	#print type(find_negative2)

	if find_negative2 is not None and 'Room Escape Games in ' in find_negative2.text:
		print '%sListing contains valid venues! %s' % (colors.green,colors.reset)
		return True

	elif find_negative1 is not None and "Sorry, we couldn't find any Things to do that match" in find_negative1.text:
		print '%sListing contains no valid venues%s' % (colors.red,colors.reset)
		return False
	elif find_negative2 is not None and 'Things to Do in ' in find_negative2.text:
		print '%sListing contains no valid venues%s' % (colors.red,colors.reset)
		return False

	else:
		print '%sListing contains no valid venues%s' % (colors.red,colors.reset)

		return False


def process_file(file):
	if file == '.DS_Store':
		return False
	fname_array = file.split('-')
	region_name = fname_array[0]
	city_id = str(fname_array[len(fname_array) - 1]).replace('.html','')
	city_name = fname_array[1]

	file_name = path + '/' + file

	print 'Parsing file: %s' % file_name
	print '#%s - %s -> %s -> %s' % (str(counter),country_name,region_name,city_name)
	f = open(file_name, "r")
	html = f.read()

	is_venue = listing_has_venue(html)

	if not is_venue:
		return False

	parsed_html = BeautifulSoup(html,features='lxml')


	list_html = parsed_html.body.find('div', attrs={'id':'FILTERED_LIST'}).find_all('div',attrs={'class':'attraction_element'})


	for item in list_html:

		venue_name = item.find('a').text
		venue_url = item.find('a').get('href')
		venue_id = re.findall('d([0-9]+)+',venue_url)[0]


		print '%svenue%s - name: %s url: %s venue_id: %s' % (colors.white,colors.reset,venue_name,venue_url,str(venue_id))

		_row = {
			 'venue_name':UnicodeDammit(venue_name).unicode_markup,
			 'venue_id':venue_id,
			 'venue_url': venue_url,
			 'city_geo_id':city_id,
			 'region_name': UnicodeDammit(region_name).unicode_markup,
			 'city_name': UnicodeDammit(city_name).unicode_markup,
			 'country_name': UnicodeDammit(country_name).unicode_markup,
			 'country_geo_id':country_id,
			 'status': 1,
 			 'venue_tmodified' :timestamp,
			 'venue_tcreate' :timestamp
		    }

	   	#print json.dumps(_row,indent=4)

		result = db.insert(tablename='venue', row=_row, update=False)
		global counter
		counter +=1

if __name__ == '__main__':

	for country in countries:

		country_id = country['id']
		country_name = country['name']

		path = 'raw/venues/%s' % (country_name)
		file_list = os.listdir(path)
		for file in file_list:
			process_file(file)
