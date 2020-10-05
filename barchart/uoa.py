import json
import csv
from datetime import datetime
#from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from user_agent import generate_user_agent
from barchart.helpers.errors import InvalidWebDriverPathValue, InvalidTimeoutValue, HttpErrors, ParsingError
from barchart.helpers.pagination import Pagination
from barchart.helpers.parser import UOAParse
from barchart.helpers.async_request import AsyncRequest

UOA_BASE_URL = 'https://www.barchart.com/options/unusual-activity/stocks'

class UOA:
	def __init__(self, webdriver_path=None, timeout=100):
		self.webdriver_path 	= webdriver_path
		self.timeout 			= timeout
		self._total_records 	= None
		self._records_per_page  = None
		self._pages_to_paginate = None
		self.data 				= []
		self._report 			= self._generate_report()

	@property
	def webdriver_path(self):
		return self._webdriver_path

	@webdriver_path.setter
	def webdriver_path(self, data):
		if not data or type(data) is not str: 
			raise InvalidWebDriverPathValue(data)
		self._webdriver_path = data

	@property
	def timeout(self):
		return self._timeout

	@timeout.setter
	def timeout(self, data):
		if not data or type(data) is not int: 
			raise InvalidTimeoutValue(data)
		self._timeout = data
	

	def _generate_report(self):
		init_req = self._initial_request()

	def _initial_request(self):
		options = Options()
		options.headless = True
		browser = webdriver.Firefox(options=options, executable_path=self.webdriver_path)
		browser.get(UOA_BASE_URL)
		#session = HTMLSession()
		#initial_response = session.get(UOA_BASE_URL, headers={'User-Agent': generate_user_agent()})
		# HttpErrors.handle_errors(initial_response)
		# HttpErrors.handle_render_errors(initial_response.html.render, timeout=self.timeout)
		try:
			self._parse_table_headers_body(browser)
			self._parse_pagination(browser)
		finally:
			browser.quit()
		# import pdb; pdb.set_trace()
			#self._parse_pagination(browser)
		#parser = UOAParse(initial_response)
		#parser.get_table_headers()
		#parser.get_table_body()
		#self.data = parser.data

		# if self._has_pagination():
		# 	async_req = AsyncRequest(UOA_BASE_URL, self._pages_to_paginate, parser_type=UOAParse)
		# 	async_req.run()
		# 	self.data.extend(async_req.data)

	def _parse_table_headers_body(self, browser):
		WebDriverWait(browser,10).until(EC.presence_of_element_located((By.XPATH, '//table/thead/tr')))
		parser = UOAParse(browser, spaced_headers=['Exp Date', 'Open Int', 'Last Trade'])
		parser.get_table_headers()
		parser.get_table_body()
		self.data = parser.data

	def _parse_pagination(self, browser):
		WebDriverWait(browser,10).until(EC.presence_of_element_located((By.CLASS_NAME, 'pagination-info')))
		parse_pag = Pagination(browser)
		parse_pag.get_pagination()
		parse_pag.calculate_pages_to_paginate()
		self._total_records 	= parse_pag.total_records
		self._records_per_page 	= parse_pag.per_page
		self._pages_to_paginate = parse_pag.pages_needed_to_paginate

	def _has_pagination(self):
		return bool(self._total_records) and bool(self._records_per_page) and bool(self._pages_to_paginate)

	def to_csv(self):
		keys = self.data[0].keys()
		file_name = datetime.now().strftime("%m%d%Y") + '_UOA'
		with open(file_name+'.csv', 'w', newline='')  as file:
		    dict_writer = csv.DictWriter(file, keys)
		    dict_writer.writeheader()
		    dict_writer.writerows(self.data)








			














