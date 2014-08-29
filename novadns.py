#!/usr/bin/python

import ConfigParser
import sys
import time
import signal
from novaclient.v1_1 import client
from jinja2 import Environment, FileSystemLoader

VERSION = 0.2
NOVADNS_HOME = "/etc/novadns"
CONFIG_FILE = NOVADNS_HOME + "/novadns.conf"
OSCOMPUTE_ERROR = 0

class Server:

	def __init__(self, name, ip):
		self.name = name
		self.ip   = ip

class Novadns:

	def __init__(self, user, password, tenant, auth_url, wait_time):
		self.user      = user
		self.password  = password
		self.tenant    = tenant
		self.auth_url  = auth_url
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
	global NOVADNS_HOME
	env = Environment(loader=FileSystemLoader(NOVADNS_HOME))
	return env.get_template('novadns.template')

def run():
	global OSCOMPUTE_ERROR
	novadns = getConfig()

	if novadns:
		nt = getCompute(novadns.user, novadns.password, novadns.tenant, novadns.auth_url)
		print "DEBUG: nova wait time is " + str(novadns.wait_time) + " seconds"
	else:
		print "ERROR: Novadns object could not be created, exiting..."
		sys.exit(1)

	while True:
		# FIXME: Ugly

		if OSCOMPUTE_ERROR >= 5:
			break

		# Get the list of nova servers
		nova_servers = nt.servers.list()

		all_servers = []
		for nova_server in nova_servers:
			ip = None
			try:
				# The network, in this example 'cybera' will likely be different in
				# your openstack environment.
				ip = nova_server.networks['cybera'][0]
			except:
				pass

			# We've actually had times when a server in openstack is active but
			# has no ip address.
			if ip and nova_server.status == 'ACTIVE':
				new_server = Server(nova_server.name, ip)
				all_servers.append(new_server)

		# Create the template
		template = getTemplate()
		output = template.render(servers=all_servers)

		# Write the template to /etc/hosts
		print "DEBUG: Writing to /etc/hosts..."
		try:
			with open("/etc/hosts", "wb") as fh:
				fh.write(output)
		except:
			print 'ERROR: Writing to /etc/hosts failed...'
			OSCOMPUTE_ERROR = OSCOMPUTE_ERROR + 1

		# Sleep for a weak daemon, why upstart is not that bad :)
		time.sleep(novadns.wait_time)


	# Too many errors
	print "ERROR: Maximum errors reached, exiting..."
	sys.exit(0)

if __name__ == '__main__':

   signal.signal(signal.SIGINT, exitGracefully)
   run()
