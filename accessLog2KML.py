#!/usr/bin/python3
from cc2cn import cc2_cn
import re
import json
import ipaddress
import sys
from collections import OrderedDict
from operator import itemgetter
from urllib.request import urlopen

# everytime the program finds a new ip, it checks if it's in already_scanned_ips,
# if it's not, then add it to already_scanned_ips and add the IP to the KML file
already_scanned_ips = []

logins_by_country = {}
for iso_country_code in cc2_cn:
	country = cc2_cn[iso_country_code]
	logins_by_country[country] = 0

logins_by_asn = {}

print("""\
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
""")

def _add_ip(ip):
	ip_json =  json.loads(urlopen("https://ipinfo.io/" + ip + "/json").read().decode())
	coords = ip_json['loc'].split(',')
	# use coords[1] + ',' + coords[0] because in KML, coordinates are written in longitude,latitude format
	# instead of the commonly accepted latitude,longitude format
	country = cc2_cn[ip_json['country']]
	asn = ip_json['org']
	if not(asn in logins_by_asn.keys()):
		logins_by_asn[asn] = 1
	else:
		logins_by_asn[asn] += 1
	logins_by_country[country] += 1
	print("<Placemark>\n<name>" + ip + "</name>\n<description>Country:" + country + "<br />City:" + ip_json['city'] + '<br />Region:' + 	ip_json['region'] +  "<br /></description>\n<Point>\n<coordinates>" + coords[1] + ',' + coords[0] + "</coordinates>\n</Point>\n</Placemark>\n")

def add_ip(ip):
	if ipaddress.ip_address(ip).is_private != True and not(ip in already_scanned_ips):
		try:
			#print("FOUND IP:" + ip)
			already_scanned_ips.append(ip)
			_add_ip(ip)
		except Exception as e:
			print("<!--- " + str(e) + " ---!>")
def search_for_ips(log_file):
	log_lines = open(log_file, 'r').read().split('\n')
	for log_line in log_lines:
		ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', log_line )
		if len(ip) != 0:
			add_ip(ip[0])

search_for_ips(sys.argv[1])
print("</Document>\n</kml>")
# Make the logins_by_country and logins_by_asn statistic
# variables in order and turn them into json and then
# write them to a json file
logins_by_country = OrderedDict(sorted(logins_by_country.items(), key=itemgetter(1), reverse=True))
logins_by_country = json.dumps(logins_by_country, indent=4)
logins_by_asn = OrderedDict(sorted(logins_by_asn.items(), key=itemgetter(1), reverse=True))
logins_by_asn = json.dumps(logins_by_asn, indent=4)
open('logins_by_country.json', 'w').write(logins_by_country)
open('logins_by_asn.json', 'w').write(logins_by_asn)
