import json
import asyncio
import  pyppeteer
from user_agent import generate_user_agent
from requests_html import AsyncHTMLSession
from barchart.helpers.parser import UOAParse
from barchart.helpers.errors import HttpErrors, TimeoutError, MissingParserType

class AsyncRequest:
	def __init__(self, base_url, number_of_requests, timeout=1000, parser_type=None, user_agent=None):
		self.base_url   		= base_url
		self.number_of_requests = number_of_requests
		self.parser_type 		= parser_type
		self.timeout			= timeout
		self.user_agent         = user_agent
		self.data				= []

	@property
	def parser_type(self):
		return self._parser_type

	@parser_type.setter
	def parser_type(self, data):
		if not data: 
			raise MissingParserType
		self._parser_type = data
	
	async def make_requests(self, url):
		session = AsyncHTMLSession(browser_args=["--no-sandbox", f'--user-agent=self.user_agent'])
		response = await session.get(url)
		HttpErrors.handle_errors(response)
		try:
			response_url = await response.html.arender(timeout=self.timeout, script=self.js_script())
		except pyppeteer.errors.TimeoutError:
			raise TimeoutError

		if self._is_unique_page_request(response.html.url, response_url):
			parser = self.parser_type(response)
			parser.get_table_headers()
			parser.get_table_body()
			self.data.extend(parser.data)

		await session.close()

	async def main(self):
		"""Runs subsequent requests after the initial request"""
		for i in range(2, self.number_of_requests+2):
			url = self.base_url +f'/?page={i}'
			await self.make_requests(url)

	def js_script(self):
		"""Gets the web page url by javascript"""
		script = """
			() => { return window.location.href }
		"""
		return script

	def _is_unique_page_request(self, request_url, response_url):
		"""Barchart will redirect requests if a query params is invalid"""
		return request_url == response_url


	def run(self):
		run_async = asyncio.get_event_loop()
		run_async.run_until_complete(self.main())

