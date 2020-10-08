import json
import csv
from datetime import datetime
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
	def __init__(self, webdriver_path=None):
		self.webdriver_path 	= webdriver_path
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
		profile = webdriver.FirefoxProfile()
		profile.set_preference("general.useragent.override", generate_user_agent())
		options = Options()
		options.headless = True
		browser = webdriver.Firefox(firefox_profile=profile, options=options, executable_path=self.webdriver_path)
		try:
			browser.get(UOA_BASE_URL)
			self._parse_table_headers_body(browser)
			self._parse_pagination(browser)
		finally:
			browser.quit()

		if self._has_pagination():
			async_req = AsyncRequest(UOA_BASE_URL, self._pages_to_paginate, webdriver_path=self.webdriver_path, parser_type=UOAParse)
			async_req.run()
			self.data.extend(async_req.data)

	def _parse_table_headers_body(self, browser):
		WebDriverWait(browser,10).until(EC.presence_of_element_located((By.XPATH, '//table/thead/tr')))
		parser = UOAParse(browser)
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

