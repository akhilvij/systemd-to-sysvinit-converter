
import ConfigParser
import sys

def parser_init():
	global config
	config = ConfigParser.ConfigParser()
	if len(sys.argv) > 1:
		if not config.read(sys.argv[1]):
			print "Unable to parse file", sys.argv[1]
			return;
		global prog
		prog = (sys.argv[1].split('/')[-1]).split('.')[0]
	else:
		print "Usage: python code.py /location/of/systemd/conf_file"

def add_description():
	if config.has_option("Unit", "Description"):
		print "Short-Description: " + config.get("Unit", "Description")

def add_runlevels():
	if config.has_option("Install", "WantedBy"):
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
		if config.has_option("Unit", option):
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
		if config.has_option("Unit", option):
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
	
""" This functions is used to check the return value of every command executed
in the init script. The syntax is simple.
Usage:	
	bash_check_for_success("start", return_value)
This means that the command in concern was execute during script's start()
action. In this way, this functions knows what error message to print and
what value to return to signify success or failure.

"""

def bash_check_for_success(action, r_val=1):
	print "\tif [ $? -ne 0 ]; then"
	print "\t\techo \"Unable to " + action + " $prog\"\n\t\texit " + str(r_val)
	print "\tfi"
	

def build_start():
	print "start() {\n\techo - n \"Starting $prog: \""

	if config.has_option("Service", "ExecStartPre"):
		start_pre_list = config.get("Service", "ExecStartPre").split(';')
		for start_pre in start_pre_list:
			print "\tstart_daemon " + start_pre
			bash_check_for_success("start")
		
	if config.has_option("Service", "ExecStart"):
		exec_start = config.get("Service", "ExecStart")
		if config.has_option("Service", "PIDFile"):
			print "\tstart_daemon " + "-p $PIDFILE " + exec_start
		else:
			print "\tstart_daemon " + exec_start
		bash_check_for_success("start")

	if config.has_option("Service", "ExecStartPost"):
		start_post_list = config.get("Service", "ExecStartPost")
		for start_post in start_post_list:
			print "\tstart_daemon " + start_post
			bash_check_for_success("start")

	print "}\n"

'''
The behaviour of build_stop is based on the option "killmode"
	=> control-group - This is the default. In this case, the ExecStop is
	executed first and then rest of the processes are killed.
	=> process - Only the main process is killed.
	=> none - The ExecStop command is run and no process is killed.
	
	Since, we don't have the concept of control group in sysV, we simply run
	ExecStop and kill all the remaining processes. The signal for killing is
	derived from "KillSignal" option.

'''

def build_stop():
	print "stop() {\n\techo -n \"Stopping $prog: \""
	
	if config.has_option("Service", "ExecStop"):
		print "\t", config.get("Service", "ExecStop")
	
	else:
		if config.has_option("Service", "ExecStart"):
			prog_path = config.get("Service", "ExecStart").split(" ")[0]
		if config.has_option("Service", "PIDFile"):
			if config.has_option("Service", "KillSignal"):
				print "\tkillproc -p $PIDFILE -s",
				print config.get("Service", "KillSignal"), prog_path
			else:
				print "\tkillproc -p $PIDFILE ", prog_path
		else:
			if config.has_option("Service", "KillSignal"):
				print "\tkillproc -s", config.get("Service", "KillSignal"),
				print prog_path
		bash_check_for_success("stop")

	if config.has_option("Service", "ExecStartPost"):
		print "\t", config.get("Service", "ExecStartPost")
	print "}\n"
	
""" This functions generates the reload() bash function. Here is how it works:
	- If ExecReload statement already exists then it'll be executed.
	- If there is no ExecReload then we need to find the service's PID. For 
	that, the function checks for pidfile and call "pidofproc -p $PIDFILE" 
	else it'll find the service's executable through ExecStart and execute 
	"pidofproc /path/to/executable". Since, ExecStart is mandatory for every
	service, obtaining path is easy and reliable.

"""

def build_reload():
	print "reload () {\n\techo -n \"Reloading $prog: \""
	if config.has_option("Service", "ExecReload"):
		print "\t", config.get("Service", "ExecReload")
		
	else:
		if config.has_option("Service", "PIDFile"):
			print "\tPID = pidofproc -p $PIDFILE"
		elif config.has_option("Service", "ExecStart"):
			exec_path = config.get("Service", "ExecStart").split(" ")[0]
			print "\tPID = pidofproc ", exec_path
		else:
			print "}\n"
		print "\tif [ $PID -eq 1 -o $PID -eq 2 -o $PID -eq 3 ] then"
		print "\t\techo \"Unable to Reload - Service is not running\"" 
		print "\tkill -HUP $PID"
	print "}\n"

def build_default_params():
# This file is included to comply with lsb guidelines.
	print "\n. /lib/lsb/init-functions\n"
	print "prog=" + prog

	if config.has_option("Service", "EnvironmentFile"):
		check_env_file(config.get("Service", "EnvironmentFile"));

	if config.has_option("Service", "PIDFile"):
		print "PIDFILE=${PIDFILE-" + config.get("Service", "PIDFile")
	
	if config.has_option("Service", "KillMode"):
		print "SIG=" + config.get("Service", "KillMode")

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

# The build_{start,stop,reload} functions will be called irrespective of the
# existence of Exec{Start,Stop,Reload} options. This is to ensure that all the
# basic call exists(even if they have no operation).

parser_init()
build_LSB_header()
build_default_params()
build_start()
build_stop()
build_reload()
build_call_arguments()
