
import ConfigParser, sys

config = ConfigParser.ConfigParser()

if len(sys.argv) > 1:
	config.read(sys.argv[1])
else:
	print "Usage: python code.py /location/of/systemd/conf_file"

def add_description():
	if check_for("Unit", "Description"):
		print "Short-Description: "+ config.get("Unit", "Description")
	
def add_runlevels():
	if check_for("Install", "WantedBy"):
		runlevel = config.get("Install", "WantedBy")
		if runlevel == "multi-user.target":
			print "Default-Start:\t2 3 4"
			print "Default-Stop:"
		
		elif runlevel == "graphical.target":
			print "Default-Start:\t2 3 4 5"
			print "Default-Stop:\t??"
		
		#Not sure about basic.target & rescue.target
		elif runlevel == "basic.target":
			print "Default-Start:\t1"
			print "Default-Stop:\t??"	
			
		elif runlevel == "rescue.target":
			print "Default-Start:\t1"
			
		else:
			return
			
def add_required_service():
	if check_for("Unit", "After"):
		after_services_str = config.get("Unit", "After")
		required_str = "Required-Start:\t"
		for service in  after_services_str.split(" "):
			if service == "syslog.target":
				required_str = required_str + "$syslog "
			elif service == "remote-fs.target":
				required_str = required_str + "$remote_fs "
			else:
				break
			
		print required_str

def check_env_file(Environment_file):
	print "if test -f " + Environment_file + "; then\n\t. " + Environment_file + "\nfi\n"
	
def check_for(service, option):	
	try:
		config.get(service,option)
		return 1
	except:
		return 0
	
def build_LSB_header(): #add more arguments here
	print "### BEGIN INIT INFO"
# Call functions here for Provides, Required-Start, Required-Stop, Default-Start, Default-Stop, Short-Description and Description
# Don't know whether we can get all the info for this from the "Unit" Section alone....check this...
	add_description()
	add_required_service()
	add_runlevels()
	print "### END INIT INFO"

def build_start():
	print "start() {"
# Call functions here to check for ExecStartPre, post and all other options
	if check_for("Service","ExecStartPre"):
		print config.get("Service", "ExecStartPre")
	
	print config.get("Service", "ExecStart")
	
	if check_for("Service","ExecStartPost"):
		print config.get("Service", "ExecStartPost")
	
	print "}\n"

def build_stop():
	print "stop() {"
# Call functions here to check for options
	print config.get("Service", "ExecStop")
	
	if check_for("Service","ExecStopPost"):
		print config.get("Service", "ExecStopPost")
		
	print "}\n"
	
def build_reload():
	print "reload () {"
	print config.get("Service", "ExecReload")
	print "}\n"

# Similarly we would have build_restart(), build_reload(), build_status() and so on...

for section in config.sections():
		if section == "Unit":
			build_LSB_header();

		if section == "Service":
			print "\nset -e\n"
			check_env_file(config.get(section,"EnvironmentFile"));
			for option in config.options(section):
				if option == "execstart":
					build_start()
				elif option == "execstop":
					build_stop()
				elif option == "execreload":
					build_reload()