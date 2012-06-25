
import ConfigParser
import sys

config = ConfigParser.ConfigParser()

if len(sys.argv) > 1:
	config.read(sys.argv[1])
	prog = (sys.argv[1].split('/')[-1]).split('.')[0]
else:
	print "Usage: python code.py /location/of/systemd/conf_file"

def add_description():
	if check_for("Unit", "Description"):
		print "Short-Description: " + config.get("Unit", "Description")

def add_runlevels():
	if check_for("Install", "WantedBy"):
			runlevel = config.get("Install", "WantedBy")
			if runlevel == "multi-user.target":
				print "Default-Start:\t2 3 4"
				print "Default-Stop:\t0 1 6"
				return 4

			elif runlevel == "graphical.target":
				print "Default-Start:\t2 3 4 5"
				print "Default-Stop:\t0 1 6??"
				return 5

# Not sure about basic.target & rescue.target : 
# check once - https://fedoraproject.org/wiki/User:Johannbg/QA/Systemd/Systemd.special

			elif runlevel == "basic.target":
				print "Default-Start:\t1"
				print "Default-Stop:\t??"
				return 1

			elif runlevel == "rescue.target":
				print "Default-Start:\t1"
				return 1

			else:
				return

def add_required_service():
	required_str = "Required-Start:\t"
	remote_fs_flag = True
	syslog_flag = True
	network_flag = True
	local_fs_flag = True
	rpcbind_flag = True
	options = ['After', 'Requires']

	for option in options:
		if check_for("Unit", option):
			after_services_str = config.get("Unit", option)
			for unit in after_services_str.split(" "):
				if unit == "syslog.target" and syslog_flag:
					required_str = required_str + "$syslog "
					syslog_flag = False
				elif (unit == "remote-fs.target" or unit == 
					"proc-fs-nfsd.mount" or unit == 
					"var-lib-nfs-rpc_pipefs.mount") and remote_fs_flag:
					required_str = required_str + "$remote_fs "
					remote_fs_flag = False
				elif unit == "network.target" and network_flag:
					required_str = required_str + "$network "
					network_flag = False
				elif unit == "local_fs.target" and local_fs_flag:
					required_str = required_str + "$local_fs "
					local_fs_flag = False
				elif unit == "rpcbind.service" and rpcbind_flag:
					required_str = required_str + "$portmap"
					rpcbind_flag = False
		else:
			break

	print required_str

def add_should_service():
	should_str = "Should-Start:\t"
	remote_fs_flag = True
	syslog_flag = True
	network_flag = True
	local_fs_flag = True
	rpcbind_flag = True
	options = ['Wants']
	for option in options:
		if check_for("Unit", option):
			after_services_str = config.get("Unit", option)
			for unit in after_services_str.split(" "):
				if unit == "syslog.target" and syslog_flag:
					should_str = should_str + "$syslog "
					syslog_flag = False
				elif (unit == "remote-fs.target" or unit == 
					"proc-fs-nfsd.mount" or unit == 
					"var-lib-nfs-rpc_pipefs.mount") and remote_fs_flag:
					should_str = should_str + "$remote_fs "
					remote_fs_flag = False
				elif unit == "network.target" and network_flag:
					should_str = should_str + "$network "
					network_flag = False
				elif unit == "local_fs.target" and local_fs_flag:
					should_str = should_str + "$local_fs "
					local_fs_flag = False
				elif unit == "rpcbind.service" and rpcbind_flag:
					should_str = should_str + "$portmap"
					rpcbind_flag = False
		else:
			break
	print should_str

def check_env_file(Environment_file):
	print "if test -f " + Environment_file + "; then\n\t. " + Environment_file + "\nfi\n"
															
def check_for(service, option):
	try:
		config.get(service, option)
		return 1
	except:
		return 0

def build_LSB_header(): #add more arguments here
	print "### BEGIN INIT INFO"
# Call functions here for Provides, Required-Start, Required-Stop,
# Default-Start, Default-Stop, Short-Description and Description. Don't know
# whether we can get all the info for this from the "Unit" Section alone.

	add_description()
	add_required_service()
	add_should_service()
	add_runlevels()
	print "### END INIT INFO"

def build_start():
	print "start() {\necho -n \"Starting $prog: \""

	if check_for("Service", "ExecStartPre"):
		print config.get("Service", "ExecStartPre")
		
	if check_for("Service", "ExecStart"):
		print config.get("Service", "ExecStart")

	if check_for("Service", "ExecStartPost"):
		print config.get("Service", "ExecStartPost")

	print "}\n"

def build_stop():
	print "stop() {\necho -n \"Stopping $prog: \""

	if check_for("Service", "ExecStop"):
		print config.get("Service", "ExecStop")

	if check_for("Service", "ExecStopPost"):
		print config.get("Service", "ExecStopPost")	
	print "}\n"
	
def build_reload():
	print "reload () {\necho -n \"Reloading $prog: \""
	if check_for("Service", "ExecReload"):
		print config.get("Service", "ExecReload")
	print "}\n"

def build_default_params():
# This file is included to comply with lsb guidelines.
	print "\n. /lib/lsb/init-functions\n"
	print "prog=" + prog

	if check_for("Service", "EnvironmentFile"):
		check_env_file(config.get("Service", "EnvironmentFile"));

	if check_for("Service", "PIDFile"):
		print "pidfile=${PIDFILE-" + config.get("Service", "PIDFile")

	print

def build_call_arguments():
# check for status
	print """case "$1" in"""
	print "\tstart)\n\t\tstart\n\t\t;;"
	print "\tstop)\n\t\tstop\n\t\t;;"
	print "\treload)\n\t\treload\n\t\t;;"
	print "\trestart)\n\t\tstop\n\tstart\n\t\t;;"
	print "\t* )\n\t\techo $\"Usage: $prog {start|stop|reload|restart|status}\""
	print "esac\n"


for section in config.sections():
#	print section
	if  section == "Unit" :
		build_LSB_header();
	if  section == "Service" :
		build_default_params()

# The build_{start,stop,reload} functions will be called irrespective of the
# existence of Exec{Start,Stop,Reload} options. This is to ensure that all the
# basic call exists(even if they have no operation).

build_start()
build_stop()
build_reload()
build_call_arguments()
