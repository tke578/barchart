from barchart.helpers.errors import ParsingError

class BaseParser:
	def __init__(self, body, spaced_headers=[]):
		self.body 				= body
		self.table_headers 		= None
		self.spaced_headers 	= spaced_headers
		self.data 				= []

	
class UOAParse(BaseParser):
	def __init__(self, body, spaced_headers):
		super(UOAParse, self).__init__(body, spaced_headers)

	def get_table_headers(self):
		"""Returns array of table header titles"""
		try: 
			table_list = self.body.find_element_by_xpath("//table/thead/tr").text.replace('\n', ' ').split(' ')[:18]
			self.table_headers = self._parsed_spaced_headers(table_list)
			#self.table_headers = self.body.find_element_by_xpath("//table/thead/tr").text.replace('\n', ' ').split(' ')[0:15]
		except IndexError:
			raise ParsingError(msg='Index error on table headers, check response')
		if len(self.table_headers) < 15:
			raise ParsingError(msg='table headers collection is less than 15, check response')

	def get_table_body(self):
		"""Returns collection of table body data"""
		#import pdb; pdb.set_trace()
		table_body_collection = self.body.find_elements_by_tag_name('table tbody tr')
		for row in table_body_collection:
			try:
				row_data = row.text.split('\n')
				if len(row_data) < 15:
					raise ParsingError(msg='table body collection is less than 15, check response')
				obj_struct = dict(zip(self.table_headers, row_data))
				self.data.append(obj_struct)
			except IndexError:
				raise ParsingError(msg='Index error on table body, check response')


	def _parsed_spaced_headers(self, table_list):
		"""Returns a list of specific concat table headers"""
		if not self.spaced_headers:
			return table_list

		headers_list = []
		i = 1
		while i <= len(table_list)-1:
			current_concat_str = table_list[i-1] + ' ' + table_list[i]
			if current_concat_str in self.spaced_headers:
				headers_list.append(current_concat_str)
				if i+1 == len(table_list)-1:
					headers_list.append(table_list[i+1])
					break
				else:
					i+= 2
			else:
				headers_list.append(table_list[i-1])
				if i+1 > len(table_list)-1:
					headers_list.append(table_list[i])
				i += 1
		return headers_list