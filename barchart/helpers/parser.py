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
			self.table_headers = self.body.html.find('table thead tr')[0].text.split('\n')[0:16]
		except IndexError:
			raise ParsingError(msg=self.body.html.text+'\n\n\nIndex error on parsing table headers, check html response above')
		if len(self.table_headers) < 16:
			raise ParsingError(msg=self.body.html.text+'\n\n\ntable headers collection is less than 16, check html response above')

	def get_table_body(self):
		"""Returns collection of table body data"""
		table_body_collection = self.body.html.find('table tbody tr')[0:]
		for row in table_body_collection:
			try:
				row_data = row.text.split('\n')[0:]
				if len(row_data) < 16:
					raise ParsingError(msg=self.body.html.text+'\n\n\ntable body collection is less than 16, check html response above')
				obj_struct = dict(zip(self.table_headers, row_data))
				self.data.append(obj_struct)
			except IndexError:
				raise ParsingError(msg=self.body.html.text+'\n\n\nIndex error on table body, check html response above')