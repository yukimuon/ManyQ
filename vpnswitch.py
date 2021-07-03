import os, sys, subprocess, json, argparse, signal
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired
import random
from datetime import datetime

TIMEOUT = 15

def runcmdsafe(binfile):
	b_stdout, b_stderr, b_exitcode = runcmd(binfile)
	
	return b_stdout, b_stderr, b_exitcode

def runcmd(cmd):
	#executed = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
	#stdout, stderr = executed.communicate()
	#return stdout, stderr, executed.returncode
	stdout, stderr = None, None
	if os.name != 'nt':
		cmd = "exec " + cmd
	with Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True) as process:
		try:
			stdout, stderr = process.communicate(timeout=TIMEOUT)
		except TimeoutExpired:
			if os.name == 'nt':
				Popen("TASKKILL /F /PID {pid} /T".format(pid=process.pid))
			else:
				process.kill()
				exit()
	return stdout, stderr, process.returncode

import time


def mozillavpn(interval):
	t = int(time.time())
	while True:
		try:
			if int(time.time())-t>interval:
				t = int(time.time())
				res = str(runcmd("mozillavpn servers")[0])
				s = res.split()
				servers = [i.replace("\\n","") for i in s if "-wireguard" in i]
				server = random.choice(servers)
				runcmd("mozillavpn deactivate")[0]
				runcmd(f"mozillavpn select {server}")[0]
				runcmd("mozillavpn activate")[0]
				print("Switched:",datetime.now().time().strftime("%H:%M:%S"),res)
			time.sleep(1)
		except:
			pass

def protonvpn(interval):
	t = int(time.time())
	while True:
		try:
			if int(time.time())-t>interval:
 				t = int(time.time())
				runcmd("protonvpn c -r")[0]
				print("Switched:",datetime.now().time().strftime("%H:%M:%S"),res)
			time.sleep(1)
		except:
			pass

def vpnsel(vpn,interval):
	if 'mozilla' in vpn:
		mozillavpn(interval)
	elif 'proton' in vpn:
		protonvpn(interval)
	else:
		print("VPN not started")
        assert 1==-1

