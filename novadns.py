#!/usr/bin/python

import ConfigParser
import sys
import time
import signal
from novaclient.v1_1 import client
from jinja2 import Environment, FileSystemLoader

CONFIG_FILE="/home/centos/novadns/novadns.conf"

class Novadns:

	def __init__(self, user, password, tenant, auth_url, wait_time):
		self.user = user
		self.password = password
		self.tenant = tenant
		self.auth_url = auth_url
		self.wait_time = wait_time

def exitGracefully(signal, frame):
	print "User entered ctrl-c, exiting..."
	sys.exit(0)

def getConfig():
	global CONFIG_FILE
	settings = ConfigParser.ConfigParser()
	config = settings.read(CONFIG_FILE)
	if not config:
	    	return False

	USER = settings.get('openstack', 'user')
	PASS = settings.get('openstack', 'password')
	TENANT = settings.get('openstack', 'tenant')
	AUTH_URL = settings.get('openstack', 'auth_url')
	WAIT_TIME = int(settings.get('default', 'wait_time'))

	novadns = Novadns(USER, PASS, TENANT, AUTH_URL, WAIT_TIME)

	if novadns:
		return novadns
	else:
		return False


def getCompute(USER, PASS, TENANT, AUTH_URL):

	try:
		oscompute = client.Client(USER, PASS, TENANT, AUTH_URL, service_type="compute")
		return oscompute
	except:
		return False


def getTemplate():
	env = Environment(loader=FileSystemLoader('/home/centos/novadns'))
	return env.get_template('novadns.template')

def run():

	novadns = getConfig()

	print "DEBUG: nova wait time is " + str(novadns.wait_time) + " seconds"

	if novadns:
		nt = getCompute(novadns.user, novadns.password, novadns.tenant, novadns.auth_url)

	OSCOMPUTE_ERROR = 0

	while True:
		# This would be five total for the lifetime of the run though
		if OSCOMPUTE_ERROR >= 5:
			break
		
		try:
			servers = nt.servers.list()
			template = getTemplate()
			output = template.render(servers=servers)
			print "DEBUG: Writing to /etc/hosts..."
			with open("/etc/hosts", "wb") as fh:
				fh.write(output)

		except:
			print 'ERROR: Getting servers or writing to /etc/hosts failed...'
			OSCOMPUTE_ERROR = OSCOMPUTE_ERROR + 1

		time.sleep(novadns.wait_time)

	
	# Too many errors
	print "ERROR: Maximum errors reached, exiting..."
	sys.exit(0)

if __name__ == '__main__':

   signal.signal(signal.SIGINT, exitGracefully)
   run()
