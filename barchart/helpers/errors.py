import  pyppeteer


class HttpErrors:

	def handle_errors(response):
		if response.status_code in [200, 201]:
			return
		elif 400 <= response.status_code < 500:
			raise HttpClientError(response.status_code, response.url)
		elif  500 <= response.status_code < 600:
			raise HttpServerError(response.status_code, response.url)

	def handle_render_errors(render_func, **kwargs):
		try:
			render_func(**kwargs)
		except pyppeteer.errors.TimeoutError:
			raise TimeoutError(msg='Timeout exceeded, try increasing the timeout value.')


class InvalidTimeoutValue(Exception):
	"""Raise when timeout value is invalid"""
	def __init__(self, val):
		super(InvalidTimeoutValue, self).__init__(f'Timeout value cannot be empty and/or less than 1: {val}')

class TimeoutError(Exception):
	"""Raise on timeout"""
	def __init__(self, msg=''):
		super(TimeoutError, self).__init__(msg)

class HttpClientError(Exception):
	"""Raise on client error exception"""
	def __init__(self, status_code, url):
		super(HttpClientError, self).__init__(f'Client Error while fetching {url} with status code {status_code}')

class HttpServerError(Exception):
	"""Raise on server error exception"""
	def __init__(self, status_code, url):
		super(HttpServerError, self).__init__(f'Server Error while fetching {url} with status code {status_code}')

class ParsingError(Exception):
	"""Raises when parsing table heading and body"""
	def __init__(self, msg=''):
		super(ParsingError, self).__init__(f'Parsing error: {msg}')

class MissingParserType(Exception):
	"""Raise when missing parser class"""
	def __init__(self):
		super(MissingParserType, self).__init__()