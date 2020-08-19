import json
import csv
from datetime import datetime
from requests_html import HTMLSession
from user_agent import generate_user_agent
from barchart.helpers.errors import InvalidTimeoutValue, HttpErrors, ParsingError
from barchart.helpers.pagination import Pagination
from barchart.helpers.parser import UOAParse
from barchart.helpers.async_request import AsyncRequest

UOA_BASE_URL = 'https://www.barchart.com/options/unusual-activity/stocks'
# UOA_BASE_URL = 'https://www.barchart.com/options/naked-puts'

class UOA:
	def __init__(self, timeout=100):
		self.timeout 			= timeout
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
	

	def _generate_report(self):
		init_req = self._initial_request()

	def _initial_request(self):
		session = HTMLSession()
		initial_response = session.get(UOA_BASE_URL, headers={'User-Agent': generate_user_agent()})
		HttpErrors.handle_errors(initial_response)
		HttpErrors.handle_render_errors(initial_response.html.render, timeout=self.timeout)

		self._parse_pagination(initial_response)
		parser = UOAParse(initial_response)
		parser.get_table_headers()
		parser.get_table_body()
		self.data = parser.data

		if self._has_pagination():
			async_req = AsyncRequest(UOA_BASE_URL, self._pages_to_paginate, parser_type=UOAParse)
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








			














