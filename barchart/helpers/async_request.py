import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from user_agent import generate_user_agent
from barchart.helpers.parser import UOAParse
from barchart.helpers.errors import HttpErrors, TimeoutError, MissingParserType

class AsyncRequest:
	def __init__(self, base_url, number_of_requests, webdriver_path=None, parser_type=None):
		self.webdriver_path 	= webdriver_path
		self.base_url   		= base_url
		self.number_of_requests = number_of_requests
		self.parser_type 		= parser_type
		self.data				= []

	@property
	def parser_type(self):
		return self._parser_type

	@parser_type.setter
	def parser_type(self, data):
		if not data: 
			raise MissingParserType
		self._parser_type = data
	
	def make_requests(self, url):
		profile = webdriver.FirefoxProfile()
		profile.set_preference("general.useragent.override", generate_user_agent())
		options = Options()
		options.headless = True
		browser = webdriver.Firefox(options=options, executable_path=self.webdriver_path)
		try:
			browser.get(url)
			if self._is_valid_page_request(url, browser.current_url):
				WebDriverWait(browser,10).until(EC.presence_of_element_located((By.XPATH, '//table/thead/tr')))
				parser = self.parser_type(browser)
				parser.get_table_headers()
				parser.get_table_body()
				
				self.data.extend(parser.data)
		finally:
			browser.quit()

	def main(self):
		"""Runs subsequent requests after the initial request"""
		for i in range(2, self.number_of_requests+2):
			url = self.base_url +f'?page={i}'
			self.make_requests(url)


	def _is_valid_page_request(self, request_url, response_url):
		"""Barchart will redirect requests if a query params is invalid"""
		return request_url == response_url


	def run(self):
		self.main()