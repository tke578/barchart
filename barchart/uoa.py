import json
import csv
import time
from datetime import datetime
from requests_html import HTMLSession
from user_agent import generate_user_agent
from barchart.helpers.errors import InvalidTimeoutValue, HttpErrors, ParsingError, InvalidUserAgentValue
from barchart.helpers.pagination import Pagination
from barchart.helpers.parser import UOAParse
from barchart.helpers.async_request import AsyncRequest

UOA_BASE_URL = 'https://www.barchart.com/options/unusual-activity/stocks'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36 Edg/89.0.774.68'

class UOA:
	def __init__(self, timeout=100, user_agent=USER_AGENT):
		self.timeout 			= timeout
		self.user_agent  		= user_agent
		self._total_records 	= None
		self._records_per_page  = None
		self._pages_to_paginate = None
		self.data 				= []
		self._report 			= self._generate_report()

	@property
	def timeout(self):
		return self._timeout

	@timeout.setter
	def timeout(self, data):
		if not data or type(data) is not int: 
			raise InvalidTimeoutValue(data)
		self._timeout = data

	@property
	def user_agent(self):
		return self._user_agent

	@user_agent.setter
	def user_agent(self, data):
		if not data or type(data) is not str:
			raise InvalidUserAgentValue(data)
		self._user_agent = data

	def _generate_report(self):
		init_req = self._initial_request()

	def _initial_request(self):
		session = HTMLSession(browser_args=["--no-sandbox", f'--user-agent=self.user_agent'])
		initial_response = session.get(UOA_BASE_URL)

		HttpErrors.handle_errors(initial_response)
		HttpErrors.handle_render_errors(initial_response.html.render, timeout=self.timeout)
		self._parse_pagination(initial_response)
		
		parser = UOAParse(initial_response)
		parser.get_table_headers()
		parser.get_table_body()
		self.data = parser.data

		if self._has_pagination():
			async_req = AsyncRequest(UOA_BASE_URL, self._pages_to_paginate, parser_type=UOAParse, user_agent=self.user_agent)
			async_req.run()
			self.data.extend(async_req.data)

	def _parse_pagination(self, response):
		parse_pag = Pagination(response)
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








			














