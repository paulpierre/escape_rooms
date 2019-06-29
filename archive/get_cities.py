#!/usr/bin/env python
import json

countries = [
'United States',
'China',
'Canada',
'Taiwan',
'Ireland',
'Austria',
'South Korea',
'Hong Kong',
'Germany',
'Netherlands',
'Belgium',
'Finland',
'Japan',
'France',
'United Kingdom',
'Switzerland',
'Israel',
'Sweden',
'Australia',
'Norway',
'Denmark',
'United Arab Emirates',
'Singapore',
'Brazil',
'New Zealand'
]
print 'Extracting %s countries' % str(len(countries))
city_export = list()
countries_found = list()

f1 = open('json/countries.json','r')
city_data = json.loads(f1.read())

for node in city_data:
	for country in countries:
		if node['name'].lower() == country.lower():
			city_export.append(node)
			countries_found.append(country)

print 'Exported %s countries' % str(len(city_export))
if len(countries_found) != len(countries):
	print 'Could not find countries: %s' % str(list(set(countries) - set(countries_found)))

f2 = open ('cities_final.json','w')
f2.write(json.dumps(city_export, indent=4))
