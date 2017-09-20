#This file will contain the python class used to check LAR data using the edits as described in the HMDA FIG
#This class should be able to return a list of row fail counts for each S/V edit for each file passed to the class.
#The return should be JSON formatted data, written to a file?
#input to the class will be a pandas dataframe
from collections import OrderedDict
from io import StringIO
import pandas as pd

class rules_engine(object):
	"""docstring for ClassName"""
	def __init__(self, lar_schema, ts_schema, path="../edits_files/", data_file="passes_all.txt"):
		#lar and TS field names (load from schema names?)
		self.lar_field_names = list(lar_schema.field)
		self.ts_field_names = list(ts_schema.field)
		self.ts_df, self.lar_df= self.split_ts_row(path=path, data_file=data_file)
		self.state_codes = {'WA':'53', 'WI':'55', 'WV':'54', 'FL':'12', 'WY':'56', 'NH':'33', 'NJ':'34', 'NM':'33', 'NC':'37', 'ND':'38', 'NE':'31', 'NY':'36', 'RI':'44', 'NV':'32', 'CO':'08', 'CA':'06', 'GA':'13', 'CT':'09', 'OK':'40', 'OH':'39',
							'KS':'20', 'SC':'45', 'KY':'21', 'OR':'41', 'SD':'46', 'DE':'10', 'HI':'15', 'PR':'43', 'TX':'48', 'LA':'22', 'TN':'47', 'PA':'42', 'VA':'51', 'VI':'78', 'AK':'02', 'AL':'01', 'AR':'05', 'VT':'50', 'IL':'17', 'IN':'18',
							'IA':'19', 'AZ':'04', 'ID':'16', 'ME':'23', 'MD':'24', 'MA':'25', 'UT':'49', 'MO':'29', 'MN':'27', 'MI':'26', 'MT':'30', 'MS':'29', 'DC':'11'}
		self.results = {}
	#Helper Functions
	def update_results(self, edit_name="", edit_field_results={},  row_type="", row_ids=None, fail_count=None):
		"""Updates the results dictionary by adding a sub-dictionary for the edit, any associated fields, and the result of the edit test.
		edit name is the name of the edit, edit field results is a dict containing field names as keys and pass/fail as values, row type is LAR or TS, 
		row ids contains a list of all rows failing the test"""
		self.results[edit_name] = OrderedDict({})
		self.results[edit_name]["row_type"] = row_type
		if row_ids is not None:
			self.results[edit_name]["fail_ids"] = row_ids
		for field in edit_field_results.keys():
			self.results[edit_name][field] = edit_field_results[field]
			if fail_count is not None:
				self.results[edit_name]["fail_count"] = fail_count

	def split_ts_row(self, path="../edits_files/", data_file="passes_all.txt"):
		"""This function makes a separate data frame for the TS and LAR portions of a file and returns each as a dataframe."""
		with open(path+data_file, 'r') as infile:
			ts_row = infile.readline().strip("\n")
			ts_data = []
			ts_data.append(ts_row.split("|"))
			lar_rows = infile.readlines()
			lar_data = [line.strip("\n").split("|") for line in lar_rows]
			ts_df = pd.DataFrame(data=ts_data, dtype=object, columns=self.ts_field_names)
			lar_df  = pd.DataFrame(data=lar_data, dtype=object, columns=self.lar_field_names)
		return ts_df, lar_df

	#Edit Rules from FIG
	def s300(self):
		"""1) The first row of your file must begin with a 1; and 2) Any subsequent rows must begin with a 2."""
		result = {}
		if self.ts_df.get_value(0,"record_id") != "1":
			result["record_id_ts"] = "failed"
		else:
			result["record_id_ts"] = "passed"
		count = 0 #initialize count of fail rows
		failed_rows = [] #initialize list of failed rows
		for index, row in self.lar_df.iterrows():
			if self.lar_df.get_value(index, "record_id")!="2":
				count+=1
				result["record_id_lar"] = "failed"
				failed_rows.append(self.lar_df.get_value(index, "uli"))
			else:
				result["record_id_lar"] = "passed"
		self.update_results(edit_name="s300", edit_field_results=result, row_type="TS/LAR", row_ids=failed_rows, fail_count=count)

	def s301(self):
		"""The LEI in this row does not match the reported LEI in the transmittal sheet (the first row of your file). Please update your file accordingly."""
		result = {}
		failed_rows = []
		count = 0
		for index, row in self.lar_df.iterrows():
			if self.lar_df.get_value(index, "lei") != self.ts_df.get_value(0, "lei"):
				count+=1
				result["LEI"] = "failed"
				failed_rows.append(self.lar_df.get_value(index, "uli")) #add failed row ULI to list of failed rows
			else:
				result["LEI"] = "passed"
		self.update_results(edit_name="s301", edit_field_results=result, row_type="LAR", row_ids=failed_rows, fail_count=count)

	def v600(self):
		"""1) The required format for LEI is alphanumeric with 20 characters, and it cannot be left blank."""
		result= {}
		failed_rows = []
		count = 0 #initialize fail count
		for index, row in self.lar_df.iterrows():
			if self.lar_df.get_value(index, "lei") == "" or len(self.lar_df.get_value(index, "lei"))!=20:
				count +=1
				result["LEI"] = "failed"
				failed_rows.append(self.lar_df.get_value(index, "ULI")) #append failed LEI value to list of fails
			else:
				result["LEI"] = "passed"
		self.update_results(edit_name="v600", edit_field_results=result, row_type="LAR", row_ids=failed_rows, fail_count=count)

	def s302(self, year="2018"):
		""" The reported Calendar Year does not match the filing year indicated at the start of the filing."""
		result={}
		if self.ts_df.get_value(0, "calendar_year") !=year:
			result["calendar_year"] = "failed"
		else:
			result["calendar_year"] = "passed"
		self.update_results(edit_name="s302", edit_field_results=result, row_type="TS")

	def s304(self):
		"""The reported Total Number of Entries Contained in Submission does not match the total number of LARs in the HMDA file."""
		result={}
		if self.ts_df.get_value(0, "lar_entries") != str(len(self.lar_df)):
			result["lar_entries"] = "failed"
		else:
			result["lar_entries"] = "passed"
		self.update_results(edit_name="s304", edit_field_results=result, row_type="TS/LAR")

	def v601(self):
		"""The following data fields are required, and cannot be left blank. A blank value(s) was provided.
		1) Financial Institution Name;
		2) Contact Person's Name;
		3) Contact Person's E-mail Address;
		4) Contact Person's Office Street Address;
		5) Contact Person's Office City"""
		result = {}
		fields = ["contact_name", "contact_tel", "contact_street_address", "office_city", "contact_email"]
		for field in fields:
			if self.ts_df.get_value(0, field) == "":
				result[field] = "failed"
			else:
				result[field] = "passed"
		self.update_results(edit_name="v601", edit_field_results=result, row_type="TS")

	def v602(self):
		"""An invalid Calendar Quarter was reported. 1) Calendar Quarter must equal 4, and cannot be left blank."""
		result = {}
		if self.ts_df.get_value(0, "calendar_quarter") != "4":
			result["calendar_quarter"] = "failed"
		else:
			result["calendar_quarter"] = "passed"
		self.update_results(edit_name="v602", edit_field_results=result, row_type="TS")

	def v603(self):
		"""An invalid Contact Person's Telephone Number was provided.
		1) The required format for the Contact Person's Telephone Number is 999-999-9999, and it cannot be left blank."""
		result = {}
		tel = self.ts_df.get_value(0, "contact_tel")
		tel2 = tel.replace("-", "")
		if tel == "" or len(tel) != 12 or tel2.isdigit() == False: #invalid telephone format provided
			result["contact_tel"] = "failed"
		else: #valid telephone format provided
			result["contact_tel"] = "passed"
		self.update_results(edit_name="v603", edit_field_results=result, row_type="TS")

	def v604(self):
		"""V604 An invalid Contact Person's Office State was provided. Please review the information below and update your file accordingly.
			1) Contact Person's Office State must be a two letter state code, and cannot be left blank."""
		result = {}
		#office code is not valid for US states or territories
		if self.ts_df.get_value(0, "office_state") not in self.state_codes.keys():
			result["office_state"] = "failed"
		#office code is valid for US states or territories
		else:
			result["office_state"] = "passed"
		self.update_results(edit_name="v604", edit_field_results=result, row_type="TS")

	def v605(self):
		"""V605 An invalid Contact Person's ZIP Code was provided. Please review the information below and update your file accordingly.
			1) The required format for the Contact Person's ZIP Code is 12345-1010 or 12345, and it cannot be left blank."""
		result = {}
		#office zip is not valid format
		if len(self.ts_df.get_value(0, "office_zip")) not in (5, 10) or self.ts_df.get_value(0, "office_zip").replace("-","").isdigit==False:
			result["office_zip"] = "failed"
		#offize zip is valid format
		else:
			result["office_zip"] = "passed"
		self.update_results(edit_name="v605", edit_field_results=result, row_type="TS")

	def v606(self):
		"""The reported Total Number of Entries Contained in Submission is not in the valid format.
		1) The required format for the Total Number of Entries Contained in Submission is a whole number that is greater than zero, and it cannot be left blank."""
		result = {}
		if self.ts_df.get_value(0, "lar_entries")=="" or int(self.ts_df.get_value(0, "lar_entries")) < 1 or self.ts_df.get_value(0, "lar_entries").isdigit()==False:
			result["lar_entries"] = "failed"
		else:
			result["lar_entries"] = "passed"
		self.update_results(edit_name="v606", edit_field_results=result, row_type="TS")

	def v607(self):
		"""An invalid Federal Taxpayer Identification Number was provided.
		1) The required format for the Federal Taxpayer Identification Number is 99-9999999, and it cannot be left blank."""
		result = {}
		if len(self.ts_df.get_value(0, "tax_id")) != 10 or self.ts_df.get_value(0, "tax_id").replace("-","").isdigit() == False:
			result["tax_id"] = "failed"
		else:
			result["tax_id"] = "passed"
		self.update_results(edit_name="v607", edit_field_results=result, row_type="TS")

	def s305(self):
		"""A duplicate transaction has been reported. No transaction can be an exact duplicate in a LAR file."""
		result = {}
		failed_rows = []
		count = 0
		#dupe_row = self.lar_df.iloc[0:1] #create dupe row for testing
		#test_df = pd.concat([self.lar_df, dupe_row]) #merge dupe row into dataframe
		duplicate_df = self.lar_df[self.lar_df.duplicated(keep=False)==True] #pull frame of duplicates
		if len(duplicate_df) > 0:
			result["all"] = "failed"
			for index, row in duplicate_df.iterrows():
				count +=1
				failed_rows.append(row["uli"]) #list duplicate rows by ULI
			self.update_results(edit_name="s305", edit_field_results=result, row_type="LAR", row_ids=failed_rows, fail_count=count)
		else:
			result["all"] = "passed"
			self.update_results(edit_name="s305", edit_field_results=result, row_type="LAR")

	def v608(self):
		"""V608 A ULI with an invalid format was provided.
		1) The required format for ULI is alphanumeric with at least 23 characters and up to 45 characters, and it cannot be left blank."""
		result = {}
		failed_rows = []
		count = 0
		#if length not between 23 and 45 or if ULI is blank
		#get subset of LAR dataframe that fails ULI conditions
		uli_df = self.lar_df[((self.lar_df.uli.map(lambda x: len(x))!=23)&(self.lar_df.uli.map(lambda x: len(x))!=45))|(self.lar_df.uli=="")]
		if len(uli_df) > 0:
			count = len(uli_df)
			result["ULI"] = "failed"
			for index, row in uli_df.iterrows():
				failed_rows.append(row["uli"])
			self.update_results(edit_name="v608", edit_field_results=result, row_type="LAR", row_ids=failed_rows, fail_count=count)
		else:
			result["ULI"] = "passed"
			self.update_results(edit_name="v608", edit_field_results=result, row_type="LAR")
	"""
	
	
	V609 An invalid ULI was reported. Please review the information below and update your file accordingly.
	1) Based on the check digit calculation, the ULI contains a transcription error.

	V610 An invalid data field was reported. Please review the information below and update your file accordingly.
	1) Application Date must be either a valid date using YYYYMMDD format or NA, and cannot be left blank.
	2) If Action Taken equals 6, then Application Date must be NA, and the reverse must be true.

	V611 An invalid Loan Type was reported. Please review the information below and update your file accordingly.
	1) Loan Type must equal 1, 2, 3, or 4, and cannot be left blank.

	V612 An invalid Loan Purpose was reported. Please review the information below and update your file accordingly.
	1) Loan Purpose must equal 1, 2, 31, 32, 4, or 5 and cannot be left blank.
	2) If Preapproval equals 1, then Loan Purpose must equal 1.

	V613 An invalid Preapproval data field was provided. Please review the information below and update your file accordingly.
	1) Preapproval must equal 1 or 2, and cannot be left blank.
	2) If Action Taken equals 7 or 8, then Preapproval must equal 1.
	3) If Action Taken equals 3, 4, 5 or 6, then Preapproval must equal 2.
	4) If Preapproval equals 1, then Action Taken must equal 1, 2, 7 or 8.

	V614 An invalid Preapproval was provided. Please review the information below and update your file accordingly.
	1) If Loan Purpose equals 2, 4, 31, 32, or 5, then Preapproval must equal 2.
	2) If Multifamily Affordable Units is a number, then Preapproval must equal 2.
	3) If Reverse Mortgage equals 1, then Preapproval must equal 2.
	4) If Open-End Line of Credit equals 1, then Preapproval must equal 2.

	V615 An invalid Construction Method was reported. Please review the information below and update your file accordingly.
	1) Construction Method must equal 1 or 2, and cannot be left blank.
	2) If Manufactured Home Land Property Interest equals 1, 2, 3 or 4, then Construction Method must equal 2.
	3) If Manufactured Home Secured Property Type equals 1 or 2 then Construction Method must equal 2.
	"""