import urllib
import urllib2
import cookielib

AUTH_URI = 'https://www.google.com/accounts/ClientLogin'
AUTH_TYPE = "HOSTED_OR_GOOGLE"
URLLIB = 'urllib2'
HTTPLIB = 'httplib2'

class App(object):
	def __new__(cls, name, base_url, auth_uri=AUTH_URI, auth_type=AUTH_TYPE, httplib=URLLIB):
		mixin = HttplibMixin if httplib == HTTPLIB else UrllibMixin
		cls = type(cls.__name__, (AppImpl, mixin), {})
		return cls(name, base_url, auth_uri, auth_type)

class AppImpl(object):
	def __init__(self, name, base_url, auth_uri, auth_type):
		self.name = name
		self.auth_uri = auth_uri
		self.base_url = base_url

		self.cookies = None
		self.key = None

		if not self.base_url.endswith('/'):
			self.base_url += '/'
		self.auth_type = auth_type

	def _getpass(self):
		from getpass import getpass
		return getpass("enter password for service \"%s\": " % (self.name,))
		self.password = password
	
	def login(self, email, password):
		if password is None:
			password = self._getpass()
		self._before_login()
		# get an AuthToken from Google accounts
		authreq_data = urllib.urlencode({
			"Email": email,
			"Passwd": password,
			"service": "ah",
			"source": self.name,
			"accountType": self.auth_type })
		auth_resp_body = self.request(self.auth_uri, data=authreq_data)
		# auth response includes several fields - we're interested in
		#  the bit after Auth=
		auth_resp_dict = dict(x.split("=") for x in auth_resp_body.split("\n") if x)
		self.key = auth_resp_dict["Auth"].strip()
		
		# now authenicate to the app in question
		serv_args = dict(auth=self.key)
		serv_args['continue'] = '/'
		full_serv_uri = self.base_url + "_ah/login?%s" % (urllib.urlencode(serv_args))
		self.request(full_serv_uri, follow_redirect=False)
		return self.key

	def logout(self):
		self._assert_logged_in()
		super(self, type(self)).logout()

	def _assert_logged_in(self):
		if self.key is None:
			raise RuntimeError("Not logged in!")

	def add_auth_key(self, params):
		"""
		Add the stored auth key to the given dictionary
		NOTE: this is generally not needed, as login()
		      installs a cookie jar that should provide
					authentication for all relevant urllib2 requests
		"""
		self._assert_logged_in()
		params = params.copy()
		params['auth'] = self.key
		return params


class AuthError(RuntimeError): pass
class HttpError(RuntimeError): pass

class AbstractHttpLibrary(object):
	def _before_login(self): pass
	def request(self, uri, data=None, follow_redirect=False): pass

class UrllibMixin(AbstractHttpLibrary):
	def _before_login(self):
		# we use a cookie to authenticate with Google App Engine
		#  by registering a cookie handler here, this will automatically store the
		#  cookie returned when we use urllib2 to open http://currentcost.appspot.com/_ah/login
		if self.cookies is not None:
			return # already installed
		self.cookies = cookielib.LWPCookieJar()
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))
		urllib2.install_opener(opener)
	
	def request(self, uri, data=None, **ignored):
		auth_req = urllib2.Request(uri, data=data)
		try:
			auth_resp = urllib2.urlopen(auth_req)
			self.foo = auth_resp
			return auth_resp.read()
		except urllib2.HTTPError, e:
			if e.getcode() == 403:
				raise AuthError()
			raise HttpError(e.getcode())
	
	def logout(self):
		self.cookies.clear()

class HttplibMixin(AbstractHttpLibrary):
	def request(self, uri, data=None, method=None,
			content_type='application/x-www-form-urlencoded', follow_redirect=False):
		import httplib2
		h = httplib2.Http()
		if not follow_redirect:
			h.follow_redirects = False
		headers = {}
		if self.cookies:
			headers['Cookie'] = self.cookies
		headers['Content-Type'] = content_type

		if not method:
			method = 'POST' if data else 'GET'

		response, body = h.request(uri, body=data, method=method, headers=headers)
		status = int(response['status'])

		if status == 200 or (follow_redirect is False and status in (300, 301, 302, 303, 307)):
			try:
				self.cookies = response['set-cookie']
			except KeyError: pass
			return body
		if status == 403:
			raise AuthError()
		else:
			raise HttpError(status)
		return body

	def logout(self):
		self.cookies = None


if __name__ == '__main__':
	name = 'test service'
	email = raw_input("testing google login. what's your email? ")
	url = raw_input("URL? e.g. http://myapp.appspot.com: ")
	app = App(name, url)
	app.login()


