# Snafu: Snake Functions - Lambda Authenticator

import hmac
import hashlib
import base64
import os.path
import configparser
import binascii

def hmacsha256(secret, msg):
	return hmac.new(secret, msg=msg, digestmod=hashlib.sha256).digest()

def authorise(flaskrequest):
	auth = flaskrequest.headers.get("Authorization")
	host = flaskrequest.headers.get("Host")
	amzdate = flaskrequest.headers.get("X-Amz-Date")
	if not auth or not host or not amzdate:
		return False

	path = flaskrequest.path
	method = flaskrequest.method

	auth = auth.split(" ")
	if len(auth) != 4:
		return False

	algo, cred, sh, sig = auth
	if algo != "AWS4-HMAC-SHA256":
		return False

	cred = cred.split("=")
	sh = sh.split("=")
	sig = sig.split("=")
	if len(cred) != 2 or len(sh) != 2 or len(sig) != 2:
		return False
	if cred[0] != "Credential" or sh[0] != "SignedHeaders" or sig[0] != "Signature":
		return False
	cred = cred[1][:-1]
	sh = sh[1][:-1]
	sig = sig[1]

	cred = cred.split("/")
	if len(cred) != 5:
		return False
	keyid, date, region, service, request = cred

	c = configparser.ConfigParser()
	try:
		accdb = os.path.expanduser("~/.snafu-accounts")
		if os.getenv("HOME") == "/":
			accdb = "/root/.snafu-accounts"
		c.read(accdb)
	except:
		return False
	sections = c.sections()
	secretkey = None
	for section in sections:
		ckeyid = c.get(section, "access_key_id")
		if ckeyid == keyid:
			secretkey = c.get(section, "secret_access_key")
			break
	if not secretkey:
		return False

	enc = "utf-8"

	b_secretkey = bytes("AWS4" + secretkey, enc)
	b_date = bytes(date, enc)
	b_region = bytes(region, enc)
	b_service = bytes(service, enc)
	b_request = bytes(request, enc)

	ch = ""
	ch += "host:{}".format(host) + "\n"
	ch += "x-amz-date:{}".format(amzdate) + "\n"

	# FIXME: check existing sh for required fields
	#sh = "host" + ";" + "x-amz-date"

	payload = flaskrequest.data
	hp = hashlib.sha256(payload).hexdigest()

	cr = ""
	cr += method + "\n"
	cr += path + "\n"
	cr += "" + "\n"
	cr += ch + "\n"
	cr += sh + "\n"
	cr += hp

	hcr = base64.b16encode(hashlib.sha256(bytes(cr, "utf-8")).digest()).decode("utf-8").lower()

	sts = ""
	sts += algo + "\n"
	sts += amzdate + "\n"
	sts += "{}/{}/{}/{}".format(date, region, service, request) + "\n"
	sts += hcr

	b_string = bytes(sts, enc)

	dig_dk = hmacsha256(b_secretkey, b_date)
	dig_drk = hmacsha256(dig_dk, b_region)
	dig_drsk = hmacsha256(dig_drk, b_service)
	dig_sk = hmacsha256(dig_drsk, b_request)

	dig_sig = hmacsha256(dig_sk, b_string)

	signature = binascii.hexlify(dig_sig).decode("utf-8")

	#print("SIGNATURE", signature)
	#print("MATCH    ", sig)

	#return True
	return keyid
