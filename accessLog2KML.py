#!/usr/bin/python3
from cc2cn import cc2_cn
import re
import json
import ipaddress
import sys
from urllib.request import urlopen

already_scanned_ips = []
isGettingError = False

logins_by_country = {}
for iso_country_code in cc2_cn:
	country = cc2_cn[iso_country_code]
	logins_by_country[country] = 0

print("""\
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
""")

def _add_ip(ip):
	ip_json =  json.loads(urlopen("https://ipinfo.io/" + ip + "/json").read().decode())
	coords = ip_json['loc']
	country = cc2_cn[ip_json['country']]
	logins_by_country[country] += 1
	print("<Placemark>\n<name>" + ip + "</name>\n<description>Country:" + country + "<br />City:" + ip_json['city'] + '<br />Region:' + 	ip_json['region'] +  "<br /></description>\n<Point>\n<coordinates>" + coords + "</coordinates>\n</Point>\n</Placemark>\n")

def add_ip(ip):
	if ipaddress.ip_address(ip).is_private != True and not(ip in already_scanned_ips):
		try:
			#print("FOUND IP:" + ip)
			already_scanned_ips.append(ip)
			_add_ip(ip)
		except Exception as e:
			print("<!-- " + str(e) + " --!>")
def search_for_ips(log_file):
	log_lines = open(log_file, 'r').read().split('\n')
	for log_line in log_lines:
		ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', log_line )
		if len(ip) != 0:
			add_ip(ip[0])

search_for_ips(sys.argv[1])
print("</Document>\n</kml>")
open('logins_by_country.json', 'w').write(json.dumps(logins_by_country, sort_keys=True, indent=4))
