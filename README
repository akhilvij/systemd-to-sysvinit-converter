This software is part of the Debian project "SysV-init file creator from systemd service files" as part of Google Summer of Code 2012.

Installation
============
This is a simple script. There is no need for installation.

Usage
=====
It takes the location of a systemd configuration file as argument.
python converter.py /location/of/systemd/conf_file

Conversion Logic
================
This document describes the conversion logic used to convert a given systemd configuration file to a SysV init script. To get a correct SysV init script, we need to extract the correct LSB header from the systemd service file. Once we have the correct LSB header, we need methods to support the default actions. According to the debian policy, an init script must support the following actions - start, stop, restart and force-reload. So, the goal is to parse the systemd configuration file, extract the sections and underlying options and one-by-one use the conversion logic to convert each option to a corresponding bash command (SysV init script is an executable bash file). This document also describes the systemd options that do not have corresponding sysV conversion. Whenever an user enters any such systemd option, he/she is warned about it. Init scripts usually are very tedious, long, complex and hard to manage but this converter produces a very basic and a clean init script and tries to reduce the existing code duplication between various init scripts. The conversion logic is describes below : 

To generate the init-script LSB header :
----------------------------------------

Required-start : This option takes as arguments boot facilities which must be available during the start of this init script. This is a hard dependency. This option is derived from the REQUIRES and AFTER systemd keywords. As per the systemd.service manpage[0], AFTER keyword should only be used to determine the boot order and the actual dependency for the Required-start should come from the REQUIRES keyword. But while testing I observed that most of the systemd service files only had the AFTER option and not the REQUIRES. Hence, I used both of them to get the mapping for Required-start.

Should-start : This option is similar to Required-start but is a weaker/soft dependency. This option is derived from the WANTS systemd keyword.

Provides : This option tells the service/boot facility provided by this init script such that when the script is run with the start argument, the specified boot facilities will be considered to be present. I use the script name as boot facility for this option.

Required-stop : This option takes as arguments boot facilities which must be available during the shut down of this service. Normally we include the same facilities here as for the Required-start keyword as stated in [1].

Should-stop : This option is similar to Required-stop but is a weaker/soft dependency. Normally we include the same facilities here as for the Should-start keyword as stated in [1].

Default-{start/stop} - These options define the run levels where the script should be started (or stopped) by default. I use the WANTEDBY option in the INSTALL section of the systemd configuration file to extract these run levels.

Short-Description - This provides a brief description of the actions of the init script. This is derived from the DESCRIPTION keyword in the UNIT section of the systemd service file.

For correct dependency tracking, which is one of our main goals, the provides, required- and should- keywords are the main ones. Once we have correct LSB headers, we can have correct dependencies between services.

Supporting various default actions :
------------------------------------
All of the SysV init scripts accept one argument, saying the action to be performed. The following actions are mandatory as per the debian policy[2] and have been implemented. Now, in order to generate generic and widely accepted scripts, I decided to follow the LSB convention[3] as much as possible. I have used the methods start_daemon(), killproc() and pidofproc() defined in /lib/lsb/init-functions for starting, stopping daemons and getting their PIDs whenever I need them. These functions allow graceful behaviour and throw lsb complaint exit codes in cases of any problem. I use these log_*_msg() methods to log or display messages. This introduces consistent output in the generated init scripts. Also the message follow the syntax defined in the debian policy[4]. Here is a list of implemented actions :

start() method :  This method is called when the generated SysV init script is called with the start argument to start the service. The command(s) to be executed are fetched from the EXECSTARTPRE, EXECSTART and EXECSTARTPOST systemd keywords. The EXECSTART keyword has to be present in every systemd service file. The fetched commands are then executed with the help of start_daemon() function. Special cases (commands prefixed with symbols <<->> and <<@>> are taken care of. 

stop() method : This method is called when the generated SysV init script is called with the stop argument to stop the service. Here, we execute the commands that are used to stop the service(s) started by the EXECSTART{*} keywords. These commands are fetched from the EXECSTOP and EXECSTOPPOST keywords. The problem here is these keywords are optional and may not be present in many systemd service files but we need to have the support for stop() action which is mandatory. In absence of EXECSTOP{*} keywords, I identify the executable path from the EXECSTART keyword and use killproc() method in the standard /lib/lsb/init-functions to kill the job. 

restart() method : This method is called when the generated SysV init script is called with the restart argument to restart the service. In order to restart, I stop the service and start it again if the service is running, else the service is started. 

reload() method : This method is called when the generated SysV init script is called with the reload argument to reload the configuration file of the service. Reload causes the configuration to be reloaded without actually stopping and restarting the service. I have implemented this method with the help of EXECRELOAD systemd keyword. If this keyword is present in the input systemd service file, then the command(s) after this keyword is executed. Note that this action is not supported by all init scripts as it is an optional action.

force-reload() method : This method is called when the generated SysV init script is called with the force-reload argument. Force-reload causes the configuration file of the service to be reloaded if the service supports reload(), otherwise the service is restarted. To check whether the service supports reloading, I check the presence of EXECRELOAD keyword in the service's systemd configuration file.

Other Systemd Functionalities converted :
-----------------------------------------

TIMEOUTSEC : This systemd keyword configures the time to wait for start-up and stop for the service. This takes a value of time (in seconds) as argument. I have a script to check whether a daemon service signals start-up completion within the above value of time. If not, then the start up is considered failed and service is stopped. If the action is stop instead of start and the service does not terminate in the time specified, then it is terminated forcibly via SIGTERM and after another delay of the specified time with SIGKILL. 

There are other systemd keywords too like ONFAILURE, ONFAILUREISOLATE etc. but these options are related to the service monitoring feature of systemd and are not useful for the generation of Sys-V init scripts. I will update this space with a thorough list of such keywords which cannot be mapped to SysV.


[0] : http://0pointer.de/public/systemd-man/systemd.service.html
[1] : http://wiki.debian.org/LSBInitScripts/
[2] : http://www.debian.org/doc/debian-policy/ch-opersys.html#s9.3.2
[3] : http://refspecs.linux-foundation.org/LSB_4.1.0/LSB-Core-generic/LSB-Core-generic/iniscrptfunc.html
[4] :  http://www.debian.org/doc/debian-policy/ch-opersys.html#s9.4
