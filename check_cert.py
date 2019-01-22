import requests
import time
import OpenSSL
import sys
import ssl, socket
from urlparse import urlparse
from datetime import datetime


headers = {"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"}

def get_final_domain(domain_name):
	return requests.get(domain_name, headers=headers, timeout=10).url

def check_cert_exp(domain_name):
	cert=ssl.get_server_certificate((domain_name, 443))
	x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
	t = str(x509.get_notAfter()[:8])
	dt = datetime.strptime(t, '%Y%m%d') - datetime.now()
	return dt.days


def check_response_time(domain_name):
	start = time.time()
	data = requests.get(domain_name, headers=headers)
	if not data.ok:
		return {"status": "not ok"}
	total_time = round(time.time() - start, 2)
	return {"time": total_time, "status": "ok"}

def check_all(domain_name):
	domain_name_1 = urlparse(domain_name)
	details = {"domain_name": domain_name_1.netloc}
	data = check_response_time(domain_name)
	if data["status"] == "ok":
		details["status"] = "ok"
		details["time"] = data["time"]

	if data["status"] == "ok" and domain_name_1.scheme == "https":
		details["days"] = check_cert_exp(domain_name_1.netloc)

	return details


def print_f(data):
	if data["status"] == "not ok":
		print data['domain_name'] + ", Not up"
	elif data["status"] == "ok" and "days" in data:
		print data['domain_name'] + ",OK," + str(data['time']) + "sec," + str(data['days'])
	else:
		print data['domain_name'] + ",OK," + str(data['time']) + "sec"



if __name__ == "__main__":
	file_name = sys.argv[1]
	with open(file_name) as f:
		for url in f:
			data = check_all(get_final_domain(url))
			print_f(data)