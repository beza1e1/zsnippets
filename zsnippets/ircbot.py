# -!- encoding: utf8 -!-
import socket
import time
import logging
import asyncore
import asynchat

REALNAME='IPD Bot'
COMMANDPREFIX="!"

_COMMANDS = dict()
_LOG = logging.getLogger(__name__)
_RAW = logging.getLogger("raw")

def ChannelCommand(command, documentation="no documentation found"):
	"""A command the bot reacts to"""
	def wrapping(func):
		def new_func(chan, msg, con):
			_LOG.info("triggered command %s '%s'" % (command, msg))
			ret = func(chan, msg)
			if not ret:
				_LOG.debug("Command return no result '%s'" % ret)
				return
			for line in ret.split("\n"):
				if not line:
					continue
				irc = "NOTICE %s :%s" % (chan, line)
				_LOG.info("Reply '%s'" % irc)
				con.send_line(irc)
		_COMMANDS[command] = new_func
		new_func._documentation = documentation
		return func
	return wrapping

def _default_handler(chan, msg, con):
	_LOG.debug("Ignore '%s' in %s" % (msg, chan))

@ChannelCommand("help")
def _help(chan, msg):
	try:
		h, cmd = msg.split()
		doc = getattr(_COMMANDS[cmd], "_documentation")
		return "%s: %s" % (cmd, doc)
	except ValueError:
		def filt(cmd):
			if cmd in ("help",):
				return False
			return True
		commands = ", ".join(filter(filt,list(_COMMANDS.keys())))
		return "Available commands: %s" % (commands)

def _process_msg(chan, msg, con):
	cmd = msg.split()[0]
	if not cmd.startswith(COMMANDPREFIX):
		return
	cmd = cmd[len(COMMANDPREFIX):]
	handler = _COMMANDS.get(cmd, _default_handler)
	handler(chan, msg, con)

def _process_irc_line(line, con):
	_RAW.info(line)
	if "NOTICE" in line:
		pass # ignore
	elif line.startswith("PING"):
		assert line[5] == ':'
		sender = line[6:]
		con.send_line("PONG "+sender)
	elif " PRIVMSG " in line:
		i = line.index("PRIVMSG")
		line = line[i+7:]
		i = line.index(":")
		chan = line[:i].strip()
		msg = line[i+1:].strip()
		_process_msg(chan, msg, con)
	else:
		_LOG.debug("??? %s" % line)

_JOBS = list()

def CronJob(year=None,month=None,day=None,hour=0,minute=0):
	def wrapping(func):
		def wrapper(con):
			result = func()
			if not result:
				return
			for line in result.split("\n"):
				con.broadcast(line)
		_JOBS.append((year,month,day,hour,minute,wrapper))
		return func
	return wrapping

def _idle(con):
	for year,month,day,hour,minute,func in _JOBS:
		tm_year,tm_mon,tm_mday,tm_hour,tm_min,tm_sec,tm_wday,tm_yday,tm_isdst = time.localtime()
		if year != None   and year != tm_year:  continue
		if month != None  and month != tm_mon:  continue
		if day != None    and day != tm_mday:   continue
		if hour != None   and hour != tm_hour:  continue
		if minute != None and minute != tm_min: continue
		ldate = getattr(func,'_last_execution',None)
		ndate = (tm_year,tm_mon,tm_mday,tm_hour,tm_min)
		if ldate == ndate: continue # already called this minute
		_LOG.debug("cronjob to run: "+str(func))
		func(con)
		setattr(func,'_last_execution',ndate) # remember execution time

HOST='irc.freenode.net'
PORT=6667
REALNAME="Leeroy Jenkins"

class IRCConnection(asynchat.async_chat):
	def __init__(self, nick, realname=REALNAME, host=HOST, port=PORT):
		asynchat.async_chat.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect((host, port))
		self.host = host
		self.port = port
		self.channels = list()
		self.nick = nick
		self.name = realname
		self.set_terminator(b"\n")
		self.ibuffer = []
		self.send_line("NICK %s" % (self.nick))
		self.send_line("USER %s %s bla :%s" % (self.nick, self.host, self.name))
	def collect_incoming_data(self, data):
		"""Buffer the data"""
		self.ibuffer.append(data.decode("utf8"))
	def found_terminator(self):
		line = "".join(self.ibuffer)
		self.ibuffer = []
		_LOG.debug("recieved %s" % line[:-1])
		_process_irc_line(line, self)
	def join(self, channel):
		assert channel.startswith("#")
		self.send_line("JOIN %s" % channel)
		_LOG.info("joined %s" % channel)
		self.channels.append(channel)
	def quit(self):
		self.send_line("QUIT :Look behind you, a three-headed monkey!")
		_LOG.info("quitting")
	def send_line(self, line):
		_LOG.debug("send '%s'" % line)
		self.push(bytes(line+"\n", 'utf8'))
	def flush(self):
		_LOG.warn("flush?")
	def broadcast(self, line):
		for channel in self.channels:
			self.send_line("NOTICE %s :%s" % (channel, line))
	def loop(self):
		"""main (asyncore) loop"""
		try:
			while True:
				asyncore.loop(count=1)
				_idle(self)
		except KeyboardInterrupt:
			self.quit()
			asyncore.loop(count=1)

# vim: noexpandtab
