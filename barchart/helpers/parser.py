from barchart.helpers.errors import ParsingError

class BaseParser:
	def __init__(self, body):
		self.body 				= body
		self.table_headers 		= None
		self.data 				= []

	
class UOAParse(BaseParser):
	def __init__(self, body):
		super(UOAParse, self).__init__(body)

	def get_table_headers(self):
		"""Returns array of table header titles"""
		try: 
			self.table_headers = self.body.html.find('table thead tr')[0].text.split('\n')[0:15]
		except IndexError:
			raise ParsingError(msg='Index error on table headers, check response')
		if len(self.table_headers) < 15:
			raise ParsingError(msg='table headers collection is less than 15, check response')

	def get_table_body(self):
		"""Returns collection of table body data"""
		table_body_collection = self.body.html.find('table tbody tr')[0:]
		for row in table_body_collection:
			try:
				row_data = row.text.split('\n')[0:]
				if len(row_data) < 15:
					raise ParsingError(msg='table body collection is less than 15, check response')
				obj_struct = dict(zip(self.table_headers, row_data))
				self.data.append(obj_struct)
			except IndexError:
				raise ParsingError(msg='Index error on table body, check response')