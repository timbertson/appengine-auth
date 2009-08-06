import urllib
import urllib2
import cookielib

AUTH_URI = 'https://www.google.com/accounts/ClientLogin'
AUTH_TYPE = "HOSTED_OR_GOOGLE"

class AuthError(RuntimeError):
	pass

class App(object):
	key = None
	def __init__(self, name, base_url, auth_uri=AUTH_URI, auth_type=AUTH_TYPE):
		self.name = name
		self.auth_uri = auth_uri
		self.base_url = base_url
		if not self.base_url.endswith('/'):
			self.base_url += '/'
		self.auth_type = auth_type

	def _install_cookie_jar(self):
		# we use a cookie to authenticate with Google App Engine
		#  by registering a cookie handler here, this will automatically store the 
		#  cookie returned when we use urllib2 to open http://currentcost.appspot.com/_ah/login
		cookiejar = cookielib.LWPCookieJar()
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
		urllib2.install_opener(opener)

	def _getpass(self):
		import getpass
		return getpass.getpass("enter password for %s:" % (self.name,))
		self.password = password
	
	def login(self, email, password):
		if password is None:
			password = self._getpass()
		self._install_cookie_jar()
		# get an AuthToken from Google accounts
		authreq_data = urllib.urlencode({
			"Email": email,
			"Passwd": password,
			"service": "ah",
			"source": self.name,
			"accountType": self.auth_type })
		auth_req = urllib2.Request(self.auth_uri, data=authreq_data)
		auth_resp = urllib2.urlopen(auth_req)
		auth_resp_body = auth_resp.read()
		# auth response includes several fields - we're interested in 
		#  the bit after Auth=
		auth_resp_dict = dict(x.split("=") for x in auth_resp_body.split("\n") if x)
		self.key = auth_resp_dict["Auth"]
		
		# now authenicate to the app in question
		serv_args = dict(auth=self.key)
		serv_args['continue'] = '/'
		full_serv_uri = app_uri + "_ah/login?%s" % (urllib.urlencode(serv_args))
		serv_req = urllib2.Request(full_serv_uri)
		serv_resp = urllib2.urlopen(serv_req)
		serv_resp_body = serv_resp.read()
		return self.key
	
	def logout(self, app_uri):
		raise StandardError("not yet implemented")

	def add_auth_key(self, dict):
		"""add the stored auth key to the given dictionary"""
		params = params.copy()
		if self.key is None:
			raise RuntimeError("Not logged in!")
		dict['auth'] = self.key

