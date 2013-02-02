import syslog

syslog.openlog(facility=syslog.LOG_LOCAL0)

def log(text):
	syslog.syslog(syslog.LOG_INFO, text)

def err(text):
	syslog.syslog(syslog.LOG_ERR, text)
