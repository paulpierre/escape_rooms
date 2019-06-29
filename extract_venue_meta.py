#!/usr/bin/env python
import json, time, requests, sys,sqlite3, random, re, os,lxml,base64
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

#{'name':'Singapore','id':294265},
#{'name':'Hong Kong','id':294217},

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

def process_venue(html,venue_id=None,venue_url=None):
	# what we need to extract:
	# venue_img, venue_email, venue_phone, venue_street_address,venue_locality, venue_postal_code, venue_cost, venue_rating, venue_review_count, status = 2

	parsed_html = BeautifulSoup(html,features='lxml')

	meta_data = parsed_html.head.find('script',attrs={'type':'application/ld+json'}).text

	venue_img = ''
	venue_rating = ''
	venue_review_count = ''
	venue_locality = ''
	venue_postal_code = ''
	venue_region = ''
	venue_street_address = ''
	venue_lat = 0.0
	venue_long = 0.0
	venue_email = ''
	venue_website = ''
	venue_phone = ''


	if meta_data:
		meta_data = json.loads(meta_data)
		venue_img = meta_data['image']
	
		if 'aggregateRating' in meta_data:
			venue_rating =  meta_data['aggregateRating']['ratingValue']
			venue_review_count =  meta_data['aggregateRating']['reviewCount']
	
		venue_locality = UnicodeDammit(meta_data['address']['addressLocality']).unicode_markup
		venue_postal_code = UnicodeDammit(meta_data['address']['postalCode']).unicode_markup
		venue_region = UnicodeDammit(meta_data['address']['addressRegion']).unicode_markup
		venue_street_address = UnicodeDammit(meta_data['address']['streetAddress']).unicode_markup

	_email = parsed_html.body.find('div',attrs={'class':'detail_section email'})

	if _email:
		_email = _email.find('span',attrs={'class':'taLnk'}).get('onclick').replace('placementEvCall(\'taplc_location_detail_contact_card_ar_responsive_0\', \'handlers.trackEmailClick\', event, this, \'','').replace('\');','')
		venue_email = base64.b64decode(_email).split('_')[1]

	_site =  parsed_html.body.find('div',attrs={'class':'detail_section website'})
	if _site:
		_site = _site.find('span',attrs={'class':'taLnk'}).get('onclick').replace('placementEvCall(\'taplc_location_detail_contact_card_ar_responsive_0\', \'handlers.trackWebsiteClick\', event, this, \'','').replace('\');','')
		venue_website = venue_street_address = UnicodeDammit(base64.b64decode(_site).split('_')[1]).unicode_markup

	_phone = parsed_html.body.find('div',attrs={'class':'detail_section phone'})
	if _phone:
		venue_phone = _phone.text
	
	_long = parsed_html.body.find('input',attrs={'id':'TYPEAHEAD_LATITUDE'}).get('value')
	if _long:
		venue_long = _long

	_lat = parsed_html.body.find('input',attrs={'id':'TYPEAHEAD_LONGITUDE'}).get('value')
	if _lat:
		venue_lat = _lat

	#print json.dumps(meta_data,indent=4)

	"""
	_row = {
		'id':primary_key,
		'venue_img': venue_img,
		'venue_website': venue_website,
		'venue_phone' : venue_phone,
		'venue_street_address': venue_street_address,
		'venue_locality':venue_locality,
		'venue_postal_code':venue_postal_code,
		'venue_rating':venue_rating,
		'venue_review_count':venue_review_count,
		'venue_long':venue_long,
		'venue_lat':venue_lat,
		'status':2,
		'venue_tcreate':timestamp,
		'venue_tmodified':timestamp
    }
    """
    #'venue_region': venue_region,
   	print '#%s - website: %s locale: %s rating: %s reviews: %s' % (counter,venue_website, venue_locality,venue_rating,venue_review_count)

	venue_url = venue_url.replace('https://www.tripadvisor.com','')
	sql = ("""UPDATE venue SET
				venue_img = "%s",
				venue_website = "%s",
				venue_phone = "%s",
				venue_street_address = "%s",
				venue_locality = "%s",
				venue_postal_code = "%s",
				venue_rating = "%s",
				venue_review_count = "%s",
				venue_long = "%s",
				venue_lat = "%s",
				status = 2,
				venue_tcreate = "%s",
				venue_tmodified = "%s"

			WHERE venue_id = %s AND venue_url = "%s";
			""") % (venue_img,venue_website,venue_phone,venue_street_address,venue_locality,venue_postal_code,venue_rating,venue_review_count,venue_long,venue_lat,timestamp,timestamp,venue_id,venue_url)


	result = db.execute(sql)
	return result


def get_venue_list_by_geo(country_id):
	#https://www.tripadvisor.com/Attraction_Review-g42604-d10783074
	#sql = 'SELECT id,country_geo_id,venue_id,venue_url FROM venue WHERE country_geo_id=%s AND status=1' % (str(country_id))
	sql = 'SELECT DISTINCT venue_id, venue_url FROM venue WHERE country_geo_id=%s AND status=1' % (str(country_id))
	sql_result = db.execute(sql)
	return sql_result


for country in countries:

	country_id = country['id']
	country_name = country['name']

	result = get_venue_list_by_geo(country_id)

	for venue in result:

		venue_id = venue['venue_id']
		venue_url = 'https://www.tripadvisor.com' + venue['venue_url']

		try:
		    res = requests.request("GET",venue_url)
		    html = res.text

		except ValueError:
		    print( 'ERROR: %s') % str(venue_url)
		    sys.exit(0)


		result = process_venue(html,venue_id=venue_id,venue_url=venue_url)

		counter +=1
	
		if counter % sleep_limit == 0:
			nap_time = random.randint(60,600)
			print '\n%s#######################\n Taking a nap for %ss ..\n#######################\n %s' % (colors.white, str(nap_time),colors.reset)
			time.sleep(nap_time)



sys.exit(0)