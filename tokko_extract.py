from requests import request, session
from lxml import html
import json
import unicodecsv
import codecs

s = session()

tree = html.fromstring(s.get('http://www.tokkobroker.com/go/').text)
csrf_token = tree.cssselect('input[name=csrfmiddlewaretoken]')[0].attrib['value']

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'es-ES,es;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Length': '108',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'www.tokkobroker.com',
    'Origin': 'http://www.tokkobroker.com',
    'Referer': 'http://www.tokkobroker.com/go/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 '
                  'Safari/537.36'
}

data = {
    'csrfmiddlewaretoken': csrf_token,
    'username': 'mariano.mussi@roilands.com',
    'password': ''
}

s.post('http://www.tokkobroker.com/login/?next=/home', headers=headers, data=data)

countries_file = open('countries.csv', 'w')
regions_file = open('regions.csv', 'w')
divisions_file = open('divisions.csv', 'w')
sub_divisions_file = open('sub_divisions.csv', 'w')

countries_writer = unicodecsv.DictWriter(countries_file, lineterminator='\n', escapechar='\\',
                                         fieldnames=['id', 'name'])
countries_writer.writeheader()
regions_writer = unicodecsv.DictWriter(regions_file, lineterminator='\n', escapechar='\\',
                                       fieldnames=['country_id', 'id', 'name'])
regions_writer.writeheader()
divisions_writer = unicodecsv.DictWriter(divisions_file, lineterminator='\n', escapechar='\\',
                                         fieldnames=['country_id', 'region_id', 'id', 'name'])
divisions_writer.writeheader()
sub_divisions_writer = unicodecsv.DictWriter(sub_divisions_file, lineterminator='\n', escapechar='\\',
                                             fieldnames=['country_id', 'region_id', 'division_id', 'id', 'name'])
sub_divisions_writer.writeheader()

countries = json.loads(s.get('http://www.tokkobroker.com/locations/countries_json').text.replace('\'', '"').replace(',}', '}'))
for country_id in [c for c in countries if c not in ['selected', '0']]:
    if countries[country_id] != 'Otro':
        print countries[country_id]
        countries_writer.writerow({'id': int(country_id), 'name': countries[country_id]})
        countries_file.flush()
        regions = json.loads(s.get('http://www.tokkobroker.com/locations/regions_json?country={0}'.format(country_id))
                             .text.replace('\'', '"').replace(',}', '}'))

        for region_id in [r for r in regions if r not in ['selected', '0']]:
            print countries[country_id] + u' / ' + regions[region_id]
            regions_writer.writerow({'country_id': int(country_id), 'id': int(region_id), 'name': regions[region_id]})
            regions_file.flush()
            divisions = json.loads(s.get('http://www.tokkobroker.com/locations/divisions_json?state={0}'
                                         .format(region_id)).text.replace('\'', '"').replace(',}', '}'))

            for division_id in [d for d in divisions if d not in ['selected', '0']]:
                divisions_writer.writerow({'country_id': int(country_id), 'region_id': int(region_id),
                                           'id': int(division_id), 'name': divisions[division_id]})
                divisions_file.flush()
                sub_divisions_string = s.get('http://www.tokkobroker.com/locations/divisions_json?division={0}'
                                             .format(division_id)).text
                if sub_divisions_string:
                    sub_divisions = json.loads(sub_divisions_string.replace('\'', '"').replace(',}', '}'))

                    for sub_division_id in [sd for sd in sub_divisions if sd not in ['selected', '0']]:
                        sub_divisions_writer.writerow({'country_id': int(country_id), 'region_id': int(region_id),
                                                       'division_id': int(division_id), 'id': int(sub_division_id),
                                                       'name': sub_divisions[sub_division_id]})
                        sub_divisions_file.flush()

countries_file = open('countries.csv', 'r')
regions_file = open('regions.csv', 'r')
divisions_file = open('divisions.csv', 'r')
sub_divisions_file = open('sub_divisions.csv', 'r')

countries_reader = unicodecsv.DictReader(countries_file, lineterminator='\n', escapechar='\\',
                                         fieldnames=['id', 'name'])
countries_reader.next()
regions_reader = unicodecsv.DictReader(regions_file, lineterminator='\n', escapechar='\\',
                                       fieldnames=['country_id', 'id', 'name'])
regions_reader.next()
divisions_reader = unicodecsv.DictReader(divisions_file, lineterminator='\n', escapechar='\\',
                                         fieldnames=['country_id', 'region_id', 'id', 'name'])
divisions_reader.next()
sub_divisions_reader = unicodecsv.DictReader(sub_divisions_file, lineterminator='\n', escapechar='\\',
                                             fieldnames=['country_id', 'region_id', 'division_id', 'id', 'name'])
sub_divisions_reader.next()

countries = [c for c in countries_reader]
regions = [r for r in regions_reader]
divisions = [d for d in divisions_reader]
sub_divisions = [sd for sd in sub_divisions_reader]

script = u'update public.collaborative_crm_property\nset city_id = null, neighborhood_id = null;\n\nupdate public.' \
         u'collaborative_crm_contact\nset country_id = null, state_id = null, city_id = null, neighborhood_id = null;' \
         u'\n\nupdate collaborative_crm_branch\nset city_id = null;\n\nupdate collaborative_crm_company\nset city_id' \
         u' = null;\n\ndelete from public.collaborative_crm_neighborhood;\ndelete from public.collaborative_crm_city;' \
         u'\ndelete from public.collaborative_crm_state;\ndelete from public.collaborative_crm_country;\n\n'

for country in countries:
    script += u'insert into public.collaborative_crm_country values ({0}, \'{1}\');\n'.format(country['id'],
                                                                                              country['name'])
    print country
    for region in [r for r in regions if r['country_id'] == country['id']]:
        script += u'insert into public.collaborative_crm_state values ({0}, \'{1}\', {2});\n'.format(region['id'],
                                                                                                     region['name'],
                                                                                                     region[
                                                                                                         'country_id'])
        print region
        for division in [d for d in divisions if d['country_id'] == country['id'] and
                         d['region_id'] == region['id']]:
            script += u'insert into public.collaborative_crm_city values ({0}, \'{1}\', {2});\n'\
                .format(division['id'], division['name'], division['region_id'])
            for sub_division in [sd for sd in sub_divisions if sd['country_id'] == country['id'] and
                                 sd['region_id'] == region['id'] and sd['division_id'] == division['id']]:
                script += u'insert into public.collaborative_crm_neighborhood values ({0}, \'{1}\', {2});\n'\
                    .format(sub_division['id'], sub_division['name'], sub_division['division_id'])

codecs.open('loading_script.sql', 'w', 'utf-8').write(script)
