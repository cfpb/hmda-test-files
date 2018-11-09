#This file will contain the python class used to check LAR data using the edits as described in the HMDA FIG
#This class should be able to return a list of row fail counts for each S/V edit for each file passed to the class.
#The return should be JSON formatted data, written to a file?
#input to the class will be a pandas dataframe

from collections import OrderedDict
import pandas as pd
from io import StringIO
import string
import time

from lar_generator import lar_gen #used for check digit

class rules_engine(object):
	"""docstring for ClassName"""
	def __init__(self, lar_schema=None, ts_schema=None, year=2018, cbsa_data=None):#tracts=None, counties=None, small_counties=None):
		#lar and TS field names (load from schema names?)
		self.year = year
		self.tracts = list(cbsa_data.tractFips)#tracts #instantiate valid Census tracts
		self.counties = list(cbsa_data.countyFips) #instantiate valid Census counties
		self.small_counties = cbsa_data[cbsa_data.smallCounty=="1"]#small_counties #instantiate list of small counties
		self.lar_field_names = list(lar_schema.field)
		self.ts_field_names = list(ts_schema.field)
		self.cbsa_data = cbsa_data
		#self.ts_df, self.lar_df= self.split_ts_row(data_file=data_file)
		#if data_row:
			#self.lar_df = data_row
		self.state_codes = {'WA':'53', 'WI':'55', 'WV':'54', 'FL':'12', 'WY':'56', 'NH':'33', 'NJ':'34', 'NM':'33', 'NC':'37', 'ND':'38', 'NE':'31', 'NY':'36', 'RI':'44', 'NV':'32', 'CO':'08', 'CA':'06', 'GA':'13', 'CT':'09', 'OK':'40', 'OH':'39',
							'KS':'20', 'SC':'45', 'KY':'21', 'OR':'41', 'SD':'46', 'DE':'10', 'HI':'15', 'PR':'43', 'TX':'48', 'LA':'22', 'TN':'47', 'PA':'42', 'VA':'51', 'VI':'78', 'AK':'02', 'AL':'01', 'AR':'05', 'VT':'50', 'IL':'17', 'IN':'18',
							'IA':'19', 'AZ':'04', 'ID':'16', 'ME':'23', 'MD':'24', 'MA':'25', 'UT':'49', 'MO':'29', 'MN':'27', 'MI':'26', 'MT':'30', 'MS':'29', 'DC':'11'}
		self.results = []
	#Helper Functions
	def load_lar_data(self, lar_df=None):
		"""Takes a dataframe of LAR data and stores it as a class variable."""
		self.lar_df = lar_df

	def load_ts_data(self, ts_df=None):
		"""Takes a dataframe of TS data and stores it as a class variable. TS data must be a single row."""
		self.ts_df = ts_df

	def load_data_frames(self, ts_data, lar_data):
		"""Receives dataframes for TS and LAR and writes them as object attributes"""
		self.ts_df = ts_data
		self.lar_df = lar_data

	def update_results(self, edit_name="", edit_field_results="",  row_type="", fields="", row_ids=None, fail_count=None):
		"""Updates the results dictionary by adding a sub-dictionary for the edit, any associated fields, and the result of the edit test.
		edit name is the name of the edit, edit field results is a dict containing field names as keys and pass/fail as values, row type is LAR or TS,
		row ids contains a list of all rows failing the test"""
		add_result = {}
		add_result["edit_name"] = edit_name
		add_result["row_type"] = row_type
		add_result["status"] = edit_field_results
		add_result["fields"] = fields
		if row_ids is not None:
			add_result["row_ids"] = row_ids
		if fail_count is not None:
			add_result["fail_count"] = fail_count
		self.results.append(add_result)

	def results_wrapper(self, fail_df=None, field_name=None, edit_name=None, row_type="LAR"):
		"""Helper function to create results dictionary/JSON object."""
		if len(fail_df) > 0:
			count = len(fail_df)
			result = "failed"
			if row_type == "LAR":
				failed_rows = list(fail_df.uli)
				self.update_results(edit_name=edit_name, edit_field_results=result, row_type=row_type, fields=field_name, row_ids=failed_rows, fail_count=count)
			else:
				self.update_results(edit_name=edit_name, edit_field_results=result, row_type=row_type, fields=field_name)
		else:
			result = "passed"
			self.update_results(edit_name=edit_name, edit_field_results=result, row_type=row_type, fields=field_name)

	def reset_results(self):
		"""Resets results list to empty."""
		self.results = []

	def split_ts_row(self, data_file="../edits_files/passes_all.txt"):
		"""This function makes a separate data frame for the TS and LAR portions of a file and returns each as a dataframe."""
		with open(data_file, 'r') as infile:
			ts_row = infile.readline().strip("\n")
			ts_data = []
			ts_data.append(ts_row.split("|"))
			lar_rows = infile.readlines()
			lar_data = [line.strip("\n").split("|") for line in lar_rows]
			ts_df = pd.DataFrame(data=ts_data, dtype=object, columns=self.ts_field_names)
			lar_df  = pd.DataFrame(data=lar_data, dtype=object, columns=self.lar_field_names)
		return ts_df, lar_df

	def valid_date(self, date):
		"""checks if a passed date is valid. If not returns false."""
		try:
			time.strptime(date,'%Y%m%d')
			return True
		except:
			return False

	def check_dupes(self, row, fields=[]):
		"""checks for duplicate entries in the ethnicity fields"""
		dct = {i:row[fields[i]] for i in range(len(fields))}
		#eths = {1: row["app_eth_1"], 2:row["app_eth_2"], 3:row["app_eth_3"], 4:row["app_eth_4"], 5:row["app_eth_5"]}
		result = "pass"
		for key, value in dct.items():
			for key2, value2 in dct.items():
				if not key == key2:
					if value == value2 and value2 != "":
						result = "fail"
		return result

	def check_number(self, field, min_val=None):
		"""Checks if a passed field contains only digits. Optionally a minimum value can be checked as well"""
		try:
			digit = field.replace(".","").isdigit() #check if data field is a digit
			if min_val is not None: #min_val was passed
				if digit == True and float(field) > min_val:
					return True #digit and min_val are True
				else:
					return False #digit is True, min_val is False
			else:
				return digit #no min value passed
		except:
			return False #passed value is not a number

	def compare_nums(self, row, fields=[]):
		"""Checks if field_1 is greater than field_2"""
		try:
			field_1 = float(row[fields[0]])
			field_2 = float(row[fields[1]])
			if field_1 > field_2:
				return True
			else:
				return False
		except:
			return False

	def check_counts(self, row, fields_1, fields_2, vals_1, vals_2):
		"""Checks if two sets of fields have the same count of valid entries"""
		count_1 = 0
		count_2 = 0
		for field in fields_1:
			if row[field] in vals_1:
				count_1 +=1
		for field in fields_2:
			if row[field] in vals_2:
				count_2 +=1
		if count_1 == count_2:
			return True
		else:
			return False

	#Edit Rules from FIG
	def s300_1(self):
		"""1) The first row of your file must begin with a 1;."""
		field = "record_id"
		edit_name = "s300_1"
		fail_df = self.ts_df[self.ts_df.record_id!="1"]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df, row_type="TS")

	def s300_2(self):
		"""2) Any subsequent rows [of your file] must begin with a 2."""
		field = "record_id"
		edit_name = "s300_2"
		fail_df = self.lar_df[self.lar_df.record_id!="2"]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df, row_type="LAR")

	def s301(self):
		"""The LEI in this row does not match the reported LEI in the transmittal sheet (the first row of your file). Please update your file accordingly."""
		field="LEI"
		edit_name = "s301"
		#get dataframe of LAR row fails
		#fail_df = self.lar_df[self.lar_df.lei != self.ts_df.get_value(0, "lei")]
		fail_df = self.lar_df[self.lar_df.lei!=self.ts_df.at[0,"lei"]]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df, row_type="TS")

	def v600(self):
		"""1) The required format for LEI is alphanumeric with 20 characters, and it cannot be left blank."""
		field = "LEI"
		edit_name = "v600"
		#get dataframe of failed LAR rows
		fail_df = self.lar_df[(self.lar_df.lei=="")|(self.lar_df.lei.map(lambda x: len(x))!=20)]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df, row_type="LAR")

	def s302(self):
		"""The reported Calendar Year does not match the filing year indicated at the start of the filing."""
		field = "calendar_year"
		edit_name = "s302"
		fail_df = self.ts_df[self.ts_df.calendar_year != self.year]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df, row_type="TS")

	def s304(self):
		"""The reported Total Number of Entries Contained in Submission does not match the total number of LARs in the HMDA file."""
		result={}
		#if self.ts_df.get_value(0, "lar_entries") != str(len(self.lar_df)):
		if self.ts_df.at[0,"lar_entries"]!=str(len(self.lar_df)):
			result["lar_entries"] = "failed"
		else:
			result["lar_entries"] = "passed"
		self.update_results(edit_name="s304", edit_field_results=result, row_type="TS/LAR")

	def v601_1(self):
		"""The following data fields are required, and cannot be left blank. A blank value(s) was provided.
		1) Financial Institution Name;"""
		field = "inst_name"
		edit_name = "v601_1"
		fail_df = self.ts_df[self.ts_df.inst_name == ""]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df, row_type="TS")

	def v601_2(self):
		"""The following data fields are required, and cannot be left blank. A blank value(s) was provided.
		2) Contact Person's Name"""
		field = "contact_name"
		edit_name = "v601_2"
		fail_df = self.ts_df[self.ts_df.contact_name == ""]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df, row_type="TS")

	def v601_3(self):
		"""The following data fields are required, and cannot be left blank. A blank value(s) was provided.
		3) Contact Person's E-mail Address"""
		field = "contact_email"
		edit_name = "v601_3"
		fail_df = self.ts_df[self.ts_df.contact_email == ""]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df, row_type="TS")

	def v601_4(self):
		"""The following data fields are required, and cannot be left blank. A blank value(s) was provided.
		4) Contact Person's Office Street Address"""
		field = "contact_street_address"
		edit_name = "v601_4"
		fail_df = self.ts_df[self.ts_df.contact_street_address== ""]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df, row_type="TS")

	def v601_5(self):
		"""The following data fields are required, and cannot be left blank. A blank value(s) was provided.
		5) Contact Person's Office City"""
		field = "office_city"
		edit_name = "v601_5"
		fail_df = self.ts_df[self.ts_df.office_city == ""]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df, row_type="TS")

	def v602(self):
		"""An invalid Calendar Quarter was reported. 1) Calendar Quarter must equal 4, and cannot be left blank."""
		field = "calendar_quarter"
		edit_name = "v602"
		fail_df = self.ts_df[self.ts_df.calendar_quarter!=4]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df, row_type="TS")

	def v603(self):
		"""An invalid Contact Person's Telephone Number was provided.
		1) The required format for the Contact Person's Telephone Number is 999-999-9999, and it cannot be left blank."""
		edit_name = "v603"
		field = "contact_tel"
		fail_df = self.ts_df[(self.ts_df.contact_tel.map(lambda x: len(x))!=12)|(self.ts_df.contact_tel.map(lambda x: x.replace("-","").isdigit())==False)]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df, row_type="TS")

	def v604(self):
		"""An invalid Contact Person's Office State was provided. Please review the information below and update your file accordingly.
			1) Contact Person's Office State must be a two letter state code, and cannot be left blank."""
		field = "office_state"
		edit_name = "v604"
		#office code is not valid for US states or territories
		fail_df = self.ts_df[~(self.ts_df.office_state.isin(self.state_codes.keys()))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df, row_type="TS")

	def v605(self):
		"""An invalid Contact Person's ZIP Code was provided. Please review the information below and update your file accordingly.
			1) The required format for the Contact Person's ZIP Code is 12345-1010 or 12345, and it cannot be left blank."""
		edit_name = "v605"
		field = "office_zip"
		fail_df = self.ts_df[~(self.ts_df.office_zip.map(lambda x: len(x) in (5,10)))|(self.ts_df.office_zip.map(lambda x: x.replace("-","").isdigit())==False)]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df, row_type="TS")

	def v606(self):
		"""The reported Total Number of Entries Contained in Submission is not in the valid format.
		1) The required format for the Total Number of Entries Contained in Submission is a whole number that is greater than zero, 
		and it cannot be left blank."""
		field = "lar_entries"
		edit_name = "v606"
		fail_df = self.ts_df[(self.ts_df.lar_entries.map(lambda x: self.check_number(x, min_val=0))==False)]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df, row_type="TS")

	def v607(self):
		"""An invalid Federal Taxpayer Identification Number was provided.
		1) The required format for the Federal Taxpayer Identification Number is 99-9999999, and it cannot be left blank."""
		edit_name = "v607"
		field = "tax_id"
		fail_df = self.ts_df[(self.ts_df.tax_id.map(lambda x: len(x))!=10) | (self.ts_df.tax_id.map(lambda x: x.replace("-","").isdigit())==False)]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df, row_type="TS")

	def s305(self):
		"""A duplicate transaction has been reported. No transaction can be an exact duplicate in a LAR file."""
		edit_name = "s305"
		field = "all"
		#dupe_row = self.lar_df.iloc[0:1] #create dupe row for testing
		#test_df = pd.concat([self.lar_df, dupe_row]) #merge dupe row into dataframe
		fail_df = self.lar_df[self.lar_df.duplicated(keep=False)==True] #pull frame of duplicates
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v608(self):
		"""A ULI with an invalid format was provided.
		1) The required format for ULI is alphanumeric with at least 23 characters and up to 45 characters, 
		and it cannot be left blank.
		Exempt Filers:
		If your institution is reporting a Loan/Application Number, the required format for Loan/Application Number 
		is alphanumeric with at least 1 character and no more than 22 characters, and it cannot be left blank."""

		edit_name = "v608"
		field = "ULI"
		#if length not between 23 and 45 or if ULI is blank
		#get subset of LAR dataframe that fails ULI conditions
		#check if LEI present as first 20 digits of ULI
		lei = self.lar_df.lei.iloc[0]
		#get seperate dataframes for ULI and Loan ID 
		uli_check_df = self.lar_df[(self.lar_df.uli.apply(lambda x: str(x)[:20]==lei))].copy()
		loan_id_check_df = self.lar_df[(self.lar_df.uli.apply(lambda x: str(x)[:20]!=lei))].copy()
		#filter each df for failures
		uli_fail_df = uli_check_df[(uli_check_df.uli.map(lambda x: len(x)<23))|
			(uli_check_df.uli.map(lambda x: len(x))>45)|(uli_check_df.uli=="")].copy()

		loan_id_fail_df = loan_id_check_df[(loan_id_check_df.uli=="")|
			(loan_id_check_df.uli.apply(lambda x: len(x)>22))].copy()
		#recombine dfs
		fail_df = pd.concat([uli_fail_df, loan_id_fail_df])
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v609(self):
		"""An invalid ULI was reported. Please review the information below and update your file accordingly.
		1) Based on the check digit calculation, the ULI contains a transcription error.
		This check exempts rows where the first 20 digits of the ULI are not the reported LEI.

		If ULI is not required, institution may report a loan id (similar to 2017). 
		In that situation, this edit is not applicable."""
		edit_name = "v609"
		field = "ULI"
		check_digit = lar_gen.check_digit_gen #establish check digit function alias

		#limit check digit checking to records with a ULI
		fail_df = self.lar_df[self.lar_df.uli.apply(lambda x: x[:20]==self.lar_df.lei.iloc[0])]
		#get dataframe of check digit failures
		fail_df = fail_df[fail_df.uli.map(lambda x: str(x)[-2:]) != fail_df.uli.map(lambda x: check_digit(ULI=str(x)[:-2]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v610_1(self):
		"""An invalid date field was reported.
		1) Application Date must be either a valid date using YYYYMMDD format or NA, and cannot be left blank."""
		edit_name = "v610_1"
		field = "app_date"
		fail_df = self.lar_df[(self.lar_df.app_date!="NA")&(self.lar_df.app_date.map(lambda x: self.valid_date(x))==False)]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v610_2(self):
		"""An invalid date field was reported.
		2) If Action Taken equals 6, then Application Date must be NA, and the reverse must be true."""
		edit_name = "v610_2"
		field = "app_date"
		fail_df = self.lar_df[((self.lar_df.app_date=="NA")&(self.lar_df.action_taken!="6"))|((self.lar_df.action_taken=="6")&(self.lar_df.app_date!="NA"))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v611(self):
		"""An invalid Loan Type was reported.
		1) Loan Type must equal 1, 2, 3, or 4, and cannot be left blank."""
		edit_name = "v611"
		field = "loan_type"
		fail_df = self.lar_df[~(self.lar_df.loan_type.isin(("1", "2", "3", "4")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)


	def v612_1(self):
		"""An invalid Loan Purpose was reported.
		1) Loan Purpose must equal 1, 2, 31, 32, 4, or 5 and cannot be left blank."""
		edit_name = "v612_1"
		field = "loan_purpose"
		fail_df = self.lar_df[~self.lar_df.loan_purpose.isin(("1", "2", "31", "32", "4", "5"))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v612_2(self):
		"""An invalid Loan Purpose was reported.
		2) If Preapproval equals 1, then Loan Purpose must equal 1."""
		field = "loan_purpose"
		edit_name = "v612_2"
		fail_df = self.lar_df[((self.lar_df.preapproval=="1")&(self.lar_df.loan_purpose!="1"))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v613_1(self):
		"""An invalid Preapproval data field was provided.
		1) Preapproval must equal 1 or 2, and cannot be left blank."""
		edit_name = "v613_1"
		field = "preapproval"
		fail_df = self.lar_df[~(self.lar_df.preapproval.isin(("1", "2")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v613_2(self):
		"""An invalid Preapproval data field was provided.
		2) If Action Taken equals 7 or 8, then Preapproval must equal 1."""
		field = "preapproval"
		edit_name = "v613_2"
		fail_df = self.lar_df[(self.lar_df.action_taken.isin(("7", "8")))&(self.lar_df.preapproval!="1")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v613_3(self):
		"""An invalid Preapproval data field was provided.
		3) If Action Taken equals 3, 4, 5 or 6, then Preapproval must equal 2."""
		field = "preapproval"
		edit_name = "v613_3"
		fail_df = self.lar_df[(self.lar_df.action_taken.isin(("3", "4", "5", "6")))&(self.lar_df.preapproval!="2")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v613_4(self):
		"""An invalid Preapproval data field was provided.
		4) If Preapproval equals 1, then Action Taken must equal 1, 2, 7 or 8."""
		field = "preapproval"
		edit_name = "v613_4"
		fail_df = self.lar_df[(self.lar_df.preapproval=="1")&(~(self.lar_df.action_taken.isin(("1","2","7","8"))))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v614_1(self):
		"""An invalid Preapproval was provided.
		1) If Loan Purpose equals 2, 4, 31, 32, or 5, then Preapproval must equal 2."""
		field = "preapproval"
		edit_name = "v614_1"
		fail_df = self.lar_df[(self.lar_df.loan_purpose.isin(("2", "4", "31", "32", "5")))&(self.lar_df.preapproval!="2")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)
	def v614_2(self):
		"""An invalid Preapproval was provided.
		2) If Multifamily Affordable Units is a number, then Preapproval must equal 2."""
		field = "preapproval"
		edit_name = "v614_2"
		fail_df = self.lar_df[(self.lar_df.affordable_units.map(lambda x: x.isdigit())==True)&(self.lar_df.preapproval!="2")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)
	def v614_3(self):
		"""An invalid Preapproval was provided.
		3) If Reverse Mortgage equals 1, then Preapproval must equal 2."""
		field = "preapproval"
		edit_name = "v614_3"
		fail_df = self.lar_df[(self.lar_df.reverse_mortgage=="1")&(self.lar_df.preapproval!="2")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)
	def v614_4(self):
		"""An invalid Preapproval was provided.
		4) If Open-End Line of Credit equals 1, then Preapproval must equal 2."""
		field = "preapproval"
		edit_name = "v614_4"
		fail_df = self.lar_df[(self.lar_df.open_end_credit=="1")&(self.lar_df.preapproval!="2")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v615_1(self):
		"""An invalid Construction Method was reported.
		1) Construction Method must equal 1 or 2, and cannot be left blank."""
		field = "const_method"
		edit_name = "v615_1"
		fail_df = self.lar_df[~self.lar_df.const_method.isin(("1","2"))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v615_2(self):
		"""An invalid Construction Method was reported.
		2) If Manufactured Home Land Property Interest equals 1, 2, 3 or 4, then Construction Method must equal 2."""
		field = "const_method"
		edit_name = "v615_2"
		fail_df = self.lar_df[(self.lar_df.manufactured_interest.isin(("1","2", "3","4")))&(self.lar_df.const_method!="2")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v615_3(self):
		"""An invalid Construction Method was reported.
		3) If Manufactured Home Secured Property Type equals 1 or 2 then Construction Method must equal 2."""
		field = "const_method"
		edit_name = "v615_3"
		fail_df = self.lar_df[(self.lar_df.manufactured_type.isin(("1","2")))&(self.lar_df.const_method!="2")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v616(self):
		"""An invalid Occupancy Type was reported.
		1) Occupancy Type must equal 1, 2, or 3, and cannot be left blank."""
		field = "occupancy"
		edit_name = "v616"
		fail_df = self.lar_df[~(self.lar_df.occ_type.isin(("1","2","3")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v617(self):
		"""An invalid Loan Amount was reported.
		1) Loan Amount must be a number greater than 0, and cannot be left blank."""
		field = "loan_amount"
		edit_name = "v617"
		fail_df = self.lar_df.copy()
		fail_df["amount"] = fail_df.loan_amount
		fail_df.amount = fail_df.amount.map(lambda x: 0 if x == "" else x)
		fail_df = fail_df[(fail_df.amount.map(lambda x: int(x))<1)]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v618(self):
		"""An invalid Action Taken was reported.
		1) Action Taken must equal 1, 2, 3, 4, 5, 6, 7, or 8, and cannot be left blank."""
		field = "action_taken"
		edit_name = "v618"
		fail_df = self.lar_df[~(self.lar_df.action_taken.isin(("1","2","3","4","5","6","7","8")))|(self.lar_df.action_taken=="")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v619_1(self):
		"""An invalid Action Taken Date was reported.
		1) Action Taken Date must be a valid date using YYYYMMDD format, and cannot be left blank."""
		field = "action_date"
		edit_name = "v619_1"
		fail_df = self.lar_df[(self.lar_df.action_date=="")|(self.lar_df.action_date.map(lambda x: self.valid_date(x))==False)]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v619_2(self):
		"""An invalid Action Taken Date was reported.
		2) The Action Taken Date must be in the reporting year."""
		field = "action_date"
		edit_name = "v619_2"
		fail_df = self.lar_df[(self.lar_df.action_date.map(lambda x: str(x)[:4])!=str(self.year))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v619_3(self):
		"""An invalid Action Taken Date was reported.
		3) The Action Taken Date must be on or after the Application Date."""
		field = "action_date"
		edit_name = "v619_3"
		fail_df = self.lar_df[(self.lar_df.action_date < self.lar_df.app_date)&(self.lar_df.app_date!="NA")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v620(self):
		"""An invalid Street Address was provided.
		1) Street Address cannot be left blank."""
		field = "street_address"
		edit_name = "v620"
		fail_df = self.lar_df[(self.lar_df.street_address=="")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v621(self):
		"""An invalid City was provided.
		1) City cannot be left blank."""
		field = "city"
		edit_name = "v621"
		fail_df = self.lar_df[(self.lar_df.city=="")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v622_1(self):
		"""An invalid City, State and/or Zip Code were provided.
		1) If Street Address was not reported NA, then City, State, and Zip Code must be provided, and not reported NA.

		Impact of S2155: Update to: 1) If Street Address was not reported NA or Exempt, 
		then City, State and Zip Code must be provided, and not reported NA."""
		field = "city"
		edit_name = "v622_1"
		fail_df = self.lar_df[~(self.lar_df.street_address.isin(["NA", "Exempt"]))&(self.lar_df.city=="NA")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v622_2(self):
		"""An invalid City, State and/or Zip Code were provided.
		1) If Street Address was not reported NA, then City, State, and Zip Code must be provided, and not reported NA.

		Impact of S2155: Update to: 1) If Street Address was not reported NA or Exempt, 
		then City, State and Zip Code must be provided, and not reported NA."""
		field = "state"
		edit_name = "v622_2"
		fail_df = self.lar_df[~(self.lar_df.street_address.isin(["NA", "Exempt"]))&(self.lar_df.state=="NA")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v622_3(self):
		"""An invalid City, State and/or Zip Code were provided.
		1) If Street Address was not reported NA, then City, State, and Zip Code must be provided, and not reported NA.

		Impact of S2155: Update to: 1) If Street Address was not reported NA or Exempt, 
		then City, State and Zip Code must be provided, and not reported NA."""
		field = "zip_code"
		edit_name = "v622_3"
		fail_df = self.lar_df[~(self.lar_df.street_address.isin(["NA", "Exempt"]))&(self.lar_df.zip_code=="NA")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v623(self):
		"""An invalid State was provided.
		1) State must be either a two letter state code or NA, and cannot be left blank."""
		field = "state"
		edit_name = "v623"
		fail_df = self.lar_df[~(self.lar_df.state.isin(self.state_codes))|(self.lar_df.state=="NA")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v624(self):
		"""An invalid Zip Code was provided.
		1) The required format for Zip Code is 12345-1010 or 12345 or NA, and it cannot be left blank.

		Impact of S2155: Update to 1) The required format for Zip Code is 12345-1010, 12345, 
		Exempt, or NA, and it cannot be left blank."""
		field = "zip_code"
		edit_name = "v624"
		fail_df = self.lar_df[((self.lar_df.zip_code.map(lambda x: len(x) 
			not in (10, 5)))|(self.lar_df.zip_code.map(lambda x: x.replace("-","").isdigit())==False))
		&(~self.lar_df.zip_code.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v625_1(self):
		"""An invalid Census Tract was provided.
		1) The required format for Census Tract is an eleven digit number or NA, and it cannot be left blank."""
		field = "tract"
		edit_name = "v625_1"
		fail_df = self.lar_df[(self.lar_df.tract!="NA")&((self.lar_df.tract.map(lambda x: len(x)!=11))|(self.lar_df.tract.map(lambda x: x.isdigit())==False))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v625_2(self):
		"""An invalid Census Tract was provided.
		2) If Census Tract is not reported NA, then the number provided must be a valid census tract number defined by the U.S. Census Bureau."""
		field = "tract"
		edit_name = "v625_2"
		fail_df = self.lar_df[(self.lar_df.tract!="NA")&(~self.lar_df.tract.isin(self.tracts))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v626(self):
		"""v626 An invalid County was provided.
		1) The required format for County is a five digit FIPS code or NA, and it cannot be left blank"""
		field = "county"
		edit_name = "v626"
		fail_df = self.lar_df[(self.lar_df.county!="NA")&((self.lar_df.county.map(lambda x: len(x))!=5)|(self.lar_df.county.map(lambda x: x.isdigit())==False))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v627(self):
		"""An invalid Census Tract or County was provided.
		1) If County and Census Tract are not reported NA, they must be a valid combination of information.
		The first five digits of the Census Tract must match the reported five digit County FIPS code."""
		field = "tract/county"
		edit_name = "v627"
		fail_df = self.lar_df[((self.lar_df.county!="NA")&(self.lar_df.tract!="NA"))&(self.lar_df.tract.map(lambda x: str(x)[:5])!=self.lar_df.county)]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v628_1(self):
		"""An invalid Ethnicity data field was reported.
		1) Ethnicity of Applicant or Borrower: 1 must equal 1, 11, 12, 13, 14, 2, 3, or 4, and cannot be left blank,
		unless an ethnicity is provided in Ethnicity of Applicant or Borrower: Free Form Text Field for Other Hispanic or Latino."""
		field = "app_eth_1"
		edit_name = "v628_1"
		fail_df = self.lar_df[~(self.lar_df.app_eth_1.isin(("1","11", "12", "13", "14", "2", "3","4")))|((self.lar_df.app_eth_free=="")&(self.lar_df.app_eth_1==""))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v628_2(self):
		"""An invalid Ethnicity data field was reported.
		2) Ethnicity of Applicant or Borrower: 2 must equal 1, 11, 12, 13, 14, 2, or be left blank."""
		field = "app ethnicities 2-4"
		edit_name = "v628_2"
		fail_df = self.lar_df[~(self.lar_df.app_eth_2.isin(("1","11", "12", "13", "14", "2","")))|
							  ~(self.lar_df.app_eth_3.isin(("1","11", "12", "13", "14", "2","")))|
							  ~(self.lar_df.app_eth_4.isin(("1","11", "12", "13", "14", "2","")))|
							  ~(self.lar_df.app_eth_5.isin(("1","11", "12", "13", "14", "2","")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)
	
	def v628_3(self):
		"""An invalid Ethnicity data field was reported.
		3) Each Ethnicity of Applicant or Borrower code can only be reported once."""
		field = "applicant ethnicities"
		edit_name = "v628_3"
		dupe_fields = ["app_eth_1", "app_eth_2", "app_eth_3", "app_eth_4", "app_eth_5"]
		fail_df = self.lar_df[(self.lar_df.apply(lambda x: self.check_dupes(x, fields=dupe_fields), axis=1)=="fail")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v628_4(self):
		"""An invalid Ethnicity data field was reported.
		4) If Ethnicity of Applicant or Borrower: 1 equals 3 or 4; then Ethnicity of Applicant or Borrower: 2; Ethnicity of Applicant or Borrower: 3;
		Ethnicity of Applicant or Borrower: 4; Ethnicity of Applicant or Borrower: 5 must be left blank."""
		field = "applicant ethnicities"
		edit_name = "v628_4"
		fail_df = self.lar_df[(self.lar_df.app_eth_1.isin(("3","4")))&((self.lar_df.app_eth_2!="")|(self.lar_df.app_eth_3!="")|(self.lar_df.app_eth_4!="")|(self.lar_df.app_eth_5!=""))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v629_1(self):
		"""An invalid Ethnicity data field was reported.
		1) Ethnicity of Applicant or Borrower Collected on the Basis of Visual Observation or Surname must equal 1, 2, or 3, and cannot be left blank."""
		field = "app ethnicity basis"
		edit_name = "v629_1"
		fail_df = self.lar_df[~(self.lar_df.app_eth_basis.isin(("1", "2", "3")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v629_2(self):
		"""An invalid Ethnicity data field was reported.
		2) If Ethnicity of Applicant or Borrower Collected on the Basis of Visual Observation or Surname equals 1,
		then Ethnicity of Applicant or Borrower: 1 must equal 1 or 2; and Ethnicity of Applicant or Borrower: 2 must equal 1, 2 or be left blank;
		and Ethnicity of Applicant or Borrower: 3; Ethnicity of Applicant or Borrower: 4; and Ethnicity of Applicant or Borrower: 5 must all be left blank."""
		field = "app ethnicity basis"
		edit_name = "v629_2"
		fail_df = self.lar_df[(self.lar_df.app_eth_basis=="1")&(~(self.lar_df.app_eth_1.isin(("1","2")))|(~self.lar_df.app_eth_2.isin(("1", "2", "")))|
			(self.lar_df.app_eth_3!="")|(self.lar_df.app_eth_4!="")|(self.lar_df.app_eth_5!=""))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v629_3(self):
		"""An invalid Ethnicity data field was reported. 
        3) If Ethnicity of Applicant or Borrower Collected on the Basis of Visual Observation or Surname equals 2 then Ethnicity of Applicant or Borrower: 1 must equal 1, 11, 12, 13, 14, 2 or 3."""
		field = "app ethnicity basis"
		edit_name = "v629_3"
		fail_df = self.lar_df[(self.lar_df.app_eth_basis=="2")&(~self.lar_df.app_eth_1.isin(("1", "11", "12", "13", "14", "2", "3")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v630_1(self):
		"""An invalid Ethnicity data field was reported.
		1) If Ethnicity of Applicant or Borrower: 1 equals 4, then Ethnicity of Applicant or Borrower Collected on the Basis of Visual Observation or Surname must equal 3."""
		field = "app ethnicity basis"
		edit_name = "v630_1"
		fail_df = self.lar_df[(self.lar_df.app_eth_basis!="3")&(self.lar_df.app_eth_1=="4")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v630_2(self):
		"""An invalid Ethnicity data field was reported.
		2) If Ethnicity of Applicant or Borrower Collected on the Basis of Visual Observation or Surname equals 3, then 
		Ethnicity of Applicant or Borrower: 1 must equal 3 or 4."""
		field = "app ethnicity basis"
		edit_name = "v630_2"
		fail_df = self.lar_df[(self.lar_df.app_eth_basis=="3")&(~self.lar_df.app_eth_1.isin(("3","4")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)


	def v631_1(self):
		"""An invalid Ethnicity data field was reported.
		1) Ethnicity of Co-Applicant or Co-Borrower: 1 must equal 1, 11, 12, 13, 14, 2, 3, 4, or 5, and cannot be left blank,
		unless an ethnicity is provided in Ethnicity of Co-Applicant or Co-Borrower: Free Form Text Field for Other Hispanic or Latino."""
		field = "co-app ethnicities"
		edit_name = "v631_1"
		fail_df = self.lar_df[(self.lar_df.co_app_eth_free=="")&(~self.lar_df.co_app_eth_1.isin(("1","11","12","13", "14", "2", "3", "4", "5")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v631_2(self):
		"""An invalid Ethnicity data field was reported.
		2) Ethnicity of Co-Applicant or Co-Borrower: 2; Ethnicity of Co-Applicant or Co-Borrower: 3; Ethnicity of Co-Applicant or Co-Borrower: 4;
		Ethnicity of Co- Applicant or Co-Borrower: 5 must equal 1, 11, 12, 13, 14, 2, or be left blank."""
		field = "co-app ethnicities"
		edit_name = "v631_2"
		fail_df = self.lar_df[(~self.lar_df.co_app_eth_2.isin(("1", "11", "12", "13", "14", "2", "")))|(~self.lar_df.co_app_eth_3.isin(("1", "11", "12", "13", "14", "2", "")))|
			(~self.lar_df.co_app_eth_4.isin(("1", "11", "12", "13", "14", "2", "")))|(~self.lar_df.co_app_eth_5.isin(("1", "11", "12", "13", "14", "2", "")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v631_3(self):
		"""An invalid Ethnicity data field was reported.
		3) Each Ethnicity of Co-Applicant or Co-Borrower code can only be reported once."""
		field = "Co-App Ethnicities"
		edit_name = "v631_3"
		dupe_fields = ["co_app_eth_1", "co_app_eth_2", "co_app_eth_3", "co_app_eth_4", "co_app_eth_5"]
		fail_df = self.lar_df[(self.lar_df.apply(lambda x: self.check_dupes(x, fields=dupe_fields), axis=1)=="fail")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v631_4(self):
		"""An invalid Ethnicity data field was reported.
		4) If Ethnicity of Co-Applicant or Co-Borrower: 1 equals 3, 4, or 5; then
		Ethnicity of Co-Applicant or Co-Borrower: 2; Ethnicity of Co-Applicant or Co- Borrower: 3; Ethnicity of Co-Applicant or Co- Borrower: 4;
		Ethnicity of Co-Applicant or Co- Borrower: 5 must be left blank."""
		field = "Co-App Ethnicities"
		edit_name = "v631_4"
		fail_df = self.lar_df[(self.lar_df.co_app_eth_1.isin(("3", "4", "5")))&((self.lar_df.co_app_eth_2!="")|(self.lar_df.co_app_eth_3!="")|
			(self.lar_df.co_app_eth_4!="")|(self.lar_df.co_app_eth_5!=""))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v632_1(self):
		"""An invalid Ethnicity data field was reported.
		1) ethnicity of co-applicant or co-borrow collected on the basis of visual observation or surname must equal 1,2,3,4 and cannot be left blank"""
		field = "Co-App Ethnicity Basis"
		edit_name = "v632_1"
		fail_df = self.lar_df[~(self.lar_df.co_app_eth_basis.isin(("1", "2", "3", "4")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v632_2(self):
		"""An invalid Ethnicity data field was reported.
		2) if ethnicity of co-applicant or co-borrower collected on the basis of visual observation or surname equals 1;
		then ethnicity of co-applicant or co-borrower: 1 must equal 1 or 2; and ethnicity of co-applicant or co-borrower: 2 must equal 1 or 2 or be blank
		and the remaining co borrower ethnicity fields must be left blank."""
		field = "Co-App Ethnicity Basis"
		edit_name = "v632_2"
		fail_df = self.lar_df[(self.lar_df.co_app_eth_basis=="1")&(~(self.lar_df.co_app_eth_1.isin(("1", "2")))|(~self.lar_df.co_app_eth_2.isin(("1", "2")))|
			(self.lar_df.co_app_eth_3!="")|(self.lar_df.co_app_eth_4!="")|(self.lar_df.co_app_eth_5!=""))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v632_3(self):
		"""An invalid Ethnicity data field was reported.
		2) if ethnicity of co-applicant or co-borrower collected on the basis of visual observation or surname equals 2;
		then ethnicity of co-applicant or co-borrower: 1 must equal 1, 11, 12, 13, 14, 2 or 3."""
		field = "Co-App Ethnicity Basis"
		edit_name = "v632_3"
		fail_df = self.lar_df[(self.lar_df.co_app_eth_basis=="2")&(~self.lar_df.co_app_eth_1.isin(("1", "11", "12", "13", "14", "2", "3")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v633_1(self):
		"""An invalid Ethnicity data field was reported.
		1) If Ethnicity of Co-Applicant or Co-Borrower: 1 equals 4,
		then Ethnicity of Co-Applicant or Co- Borrower Collected on the Basis of Visual Observation or Surname must equal 3."""
		field = "Co-App Ethnicity basis"
		edit_name = "v633_1"
		fail_df = self.lar_df[(self.lar_df.co_app_eth_1=="4")&(self.lar_df.co_app_eth_basis!="3")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v633_2(self):
		"""An invalid Ethnicity data field was reported.
		2) If Ethnicity of Co-Applicant or Co-Borrower Collected on the Basis of Visual Observation or Surname equals 3;
		then Ethnicity of Co-Applicant or Co-Borrower: 1 must equal 3 or 4."""
		field = "Co-App Ethnicity Basis"
		edit_name = "v633_2"
		fail_df = self.lar_df[(self.lar_df.co_app_eth_basis=="3")&(~self.lar_df.co_app_eth_1.isin(("3", "4")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v634(self):
		"""An invalid Ethnicity data field was reported.
		1) If Ethnicity of Co-Applicant or Co-Borrower: 1 equals 5,
		then Ethnicity of Co-Applicant or Co- Borrower Collected on the Basis of Visual Observation or Surname must equal 4, and the reverse must be true."""
		field = "Co-App Ethnicity Basis"
		edit_name = "v634"
		fail_df = self.lar_df[((self.lar_df.co_app_eth_1=="5")&(self.lar_df.co_app_eth_basis!="4"))|
		((self.lar_df.co_app_eth_basis=="4")&(self.lar_df.co_app_eth_1!="5"))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df) 

	def v635_1(self):
		"""An invalid Race data field was reported.
		1) Race of Applicant or Borrower: 1 must equal 1, 2, 21, 22, 23, 24, 25, 26, 27, 3, 4, 41, 42, 43, 44, 5, 6, or 7, and cannot be left blank,
		unless a race is provided in Race of Applicant or Borrower: Free Form Text Field for American Indian or Alaska Native Enrolled or Principal Tribe,
		Race of Applicant or Borrower: Free Form Text Field for Other Asian, or Race of Applicant or Borrower: Free Form Text Field for Other Pacific Islander."""
		field = "App Race 1"
		edit_name = "v635_1"
		fail_df = self.lar_df[(~self.lar_df.app_race_1.isin(("1", "2", "21", "22", "23", "24", "25", "26", "27", "3", "4", "41", "42", "43", "44", "5", "6", "7")))|
		((self.lar_df.app_race_1=="")&((self.lar_df.app_race_native_text=="")&(self.lar_df.app_race_islander_text=="")&(self.lar_df.app_race_asian_text=="")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v635_2(self):
		"""An invalid Race data field was reported.
		2) Race of Applicant or Borrower: 2; Race of Applicant or Borrower: 3; Race of Applicant or Borrower: 4;
		Race of Applicant or Borrower: 5 must equal 1, 2, 21, 22, 23, 24, 25, 26, 27, 3, 4, 41, 42, 43, 44, 5, or be left blank."""
		field = "App Race 2 - 5"
		edit_name = "v635_2"
		fail_df = self.lar_df[~(self.lar_df.app_race_2.isin(("1", "2", "21", "22", "23", "24", "25", "26", "27", "3", "4", "41", "42", "43", "44", "5", "")))|
			~(self.lar_df.app_race_3.isin(("1", "2", "21", "22", "23", "24", "25", "26", "27", "3", "4", "41", "42", "43", "44", "5", "")))|
			~(self.lar_df.app_race_4.isin(("1", "2", "21", "22", "23", "24", "25", "26", "27", "3", "4", "41", "42", "43", "44", "5", "")))|
			~(self.lar_df.app_race_5.isin(("1", "2", "21", "22", "23", "24", "25", "26", "27", "3", "4", "41", "42", "43", "44", "5", "")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v635_3(self):
		"""An invalid Race data field was reported.
		3) Each Race of Applicant or Borrower code can only be reported once."""
		field = "Applicant Races"
		edit_name = "v635_3"
		race_fields = ["app_race_1", "app_race_2", "app_race_3", "app_race_4", "app_race_5"]
		fail_df = self.lar_df[(self.lar_df.apply(lambda x: self.check_dupes(x, fields=race_fields), axis=1)=="fail")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v635_4(self):
		"""An invalid Race data field was reported.
		4) If Race of Applicant or Borrower: 1 equals 6 or 7; then Race of Applicant or Borrower: 2;
		Race of Applicant or Borrower: 3; Race of Applicant or Borrower: 4; Race of Applicant or Borrower: 5 must all be left blank."""
		field = "Applicant Races"
		edit_name = "v635_4"
		fail_df = self.lar_df[(self.lar_df.app_race_1.isin(("6", "7")))&((self.lar_df.app_race_2!="")|(self.lar_df.app_race_3!="")|(self.lar_df.app_race_4!="")
			|(self.lar_df.app_race_5!=""))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v636_1(self):
		"""An invalid Race data field was reported.
		1) Race of Applicant or Borrower Collected on the Basis of Visual Observation or Surname must equal 1, 2, or 3, and cannot be left blank."""
		field = "Applicant Race Basis"
		edit_name = "v636_1"
		fail_df = self.lar_df[~(self.lar_df.app_race_basis.isin(("1", "2", "3")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v636_2(self):
		"""An invalid Race data field was reported.
		2) If Race of Applicant or Borrower Collected on the Basis of Visual Observation or Surname equals 1;
		then Race of Applicant or Borrower: 1 must equal 1, 2, 3, 4, or 5; and Race of Applicant or Borrower: 2; Race of Applicant or Borrower: 3;
		Race of Applicant or Borrower: 4; Race of Applicant or Borrower: 5 must equal 1, 2, 3, 4, or 5, or be left blank."""
		field = "Applicant Race Basis"
		edit_name = "v636_2"
		fail_df = self.lar_df[(self.lar_df.app_race_basis=="1")&((~self.lar_df.app_race_1.isin(("1", "2", "3", "4", "5")))|
			(~self.lar_df.app_race_2.isin(("1", "2", "3", "4", "5","")))|(~self.lar_df.app_race_3.isin(("1", "2", "3", "4", "5","")))|
			(~self.lar_df.app_race_4.isin(("1", "2", "3", "4", "5","")))|(~self.lar_df.app_race_5.isin(("1", "2", "3", "4", "5",""))))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v636_3(self):
		"""An invalid Race data field was reported.
		3) If Race of Applicant or Borrower Collected on the Basis of Visual Observation or Surname equals 2,
		Race of Applicant or Borrower: 1 must equal 1, 2, 21, 22, 23, 24, 25, 26, 27, 3, 4, 41, 42, 43, 44, 5 or 6; and
		Race of Applicant or Borrower: 2; Race of Applicant or Borrower: 3; Race of Applicant or Borrower: 4;
		Race of Applicant or Borrower: 5 must equal 1, 2, 21, 22, 23, 24, 25, 26, 27, 3, 4, 41, 42, 43, 44, 5, or be left blank."""
		field = "Applicant Race Basis"
		edit_name = "v636_3"
		app_1_races = ["1", "2", "21", "22", "23", "24", "25", "26", "27", "3", "4", "41", "42", "43", "44", "5", "6"]
		app_n_races = app_1_races[:-1]
		app_n_races.append("")
		fail_df = self.lar_df[(self.lar_df.app_race_basis=="2")&((~self.lar_df.app_race_1.isin(app_1_races))|
			(~self.lar_df.app_race_2.isin(app_n_races))|(~self.lar_df.app_race_3.isin(app_n_races))|
			(~self.lar_df.app_race_4.isin(app_n_races))|(~self.lar_df.app_race_4.isin(app_n_races)))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v637_1(self):
		"""An invalid Race data field was reported.
		1) If Race of Applicant or Borrower: 1 equals 7, then Race of Applicant or Borrower Collected on the Basis of Visual Observation or Surname must equal 3."""
		field = "Applicant Race Basis"
		edit_name = "v637_1"
		fail_df = self.lar_df[(self.lar_df.app_race_1=="7")&(self.lar_df.app_race_basis!="3")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v637_2(self):
		"""An invalid Race data field was reported.
		2) If Race of Applicant or Borrower Collected on the Basis of Visual Observation or Surname equals 3; then Race of Applicant or Borrower: 1 must equal 6 or 7."""
		field = "Applicant Race 1"
		edit_name ="v637_2"
		fail_df = self.lar_df[(self.lar_df.app_race_basis=="3")&(~self.lar_df.app_race_1.isin(("6", "7")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v638_1(self):
		"""An invalid Race data field was reported.
		1) Race of Co-Applicant or Co-Borrower: 1 must equal 1, 2, 21, 22, 23, 24, 25, 26, 27, 3, 4, 41, 42, 43, 44, 5, 6, 7, or 8, and cannot be left blank,
		unless a race is provided in Race of Co-Applicant or Co- Borrower: Free Form Text Field for American Indian or Alaska Native Enrolled or Principal Tribe,
		Race of Co-Applicant or Co-Borrower: Free Form Text Field for Other Asian, or
		Race of Co-Applicant or Co- Borrower: Free Form Text Field for Other Pacific Islander."""
		field = "Co-Applicant Race 1"
		edit_name = "v638_1"
		fail_df = self.lar_df[(~self.lar_df.co_app_race_1.isin(("1", "2", "21", "23", "24", "25", "26", "27", "3", "4", "41", "42", "43", "44", "5", "6", "7", "8")))&
			((self.lar_df.co_app_race_1=="")&((self.lar_df.co_app_race_native_text=="")&(self.lar_df.co_app_race_islander_text=="")&
			(self.lar_df.co_app_race_asian_text=="")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v638_2(self):
		"""An invalid Race data field was reported.
		2) Race of Co-Applicant or Co-Borrower: 2; Race of Co-Applicant or Co-Borrower: 3;
		Race of Co- Applicant or Co-Borrower: 4; Race of Co-Applicant or Co-Borrower: 5
		must equal 1, 2, 21, 22, 23, 24, 25, 26, 27, 3, 4, 41, 42, 43, 44, 5, or be left blank."""
		field = "Co-Applicant Race 2-5"
		edit_name = "v638_2"
		fail_df = self.lar_df[~(self.lar_df.co_app_race_2.isin(("1", "2", "21", "22", "23", "24", "25", "26", "27", "3", "4", "41", "42", "43", "44", "5", "")))|
			~(self.lar_df.co_app_race_3.isin(("1", "2", "21", "22", "23", "24", "25", "26", "27", "3", "4", "41", "42", "43", "44", "5", "")))|
			~(self.lar_df.co_app_race_4.isin(("1", "2", "21", "22", "23", "24", "25", "26", "27", "3", "4", "41", "42", "43", "44", "5", "")))|
			~(self.lar_df.co_app_race_5.isin(("1", "2", "21", "22", "23", "24", "25", "26", "27", "3", "4", "41", "42", "43", "44", "5", "")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v638_3(self):
		"""An invalid Race data field was reported.
		3) Each Race of Co-Applicant or Co-Borrower code can only be reported once."""
		field = "Co-Applicant Races"
		edit_name = "v638_3"
		race_fields = ["co_app_race_1", "co_app_race_2", "co_app_race_3", "co_app_race_4", "co_app_race_5"]
		fail_df = self.lar_df[(self.lar_df.apply(lambda x: self.check_dupes(x, fields=race_fields), axis=1)=="fail")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v638_4(self):
		"""An invalid Race data field was reported.
		4) If Race of Co-Applicant or Co-Borrower: 1 equals 6, 7, or 8, then Race of Co-Applicant or Co-Borrower: 2;
		Race of Co-Applicant or Co-Borrower: 3; Race of Co-Applicant or Co-Borrower: 4; and Race of Co- Applicant or Co-Borrower: 5 must be left blank."""
		field = "Co-Applicant Races"
		edit_name = "v638_4"
		fail_df = self.lar_df[(self.lar_df.co_app_race_1.isin(("6", "7", "8")))&((self.lar_df.co_app_race_2!="")|(self.lar_df.co_app_race_3!="")|(self.lar_df.co_app_race_4!="")
			|(self.lar_df.co_app_race_5!=""))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v639_1(self):
		"""An invalid Race data field was reported.
		1) Race of Co-Applicant or Co-Borrower Collected on the Basis of Visual Observation or Surname must equal 1, 2, 3, or 4, and cannot be left blank."""
		field = "Co-Applicant Race Basis"
		edit_name = "v639_1"
		fail_df = self.lar_df[(~self.lar_df.co_app_race_basis.isin(("1", "2", "3", "4")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v639_2(self):
		"""An invalid Race data field was reported.
		2) If Race of Co-Applicant or Co-Borrower Collected on the Basis of Visual Observation or Surname equals 1,
		then Race of Co-Applicant or Co-Borrower: 1must equal 1,2,3,4,or 5; and Race of Co- Applicant or Co-Borrower: 2;
		Race of Co-Applicant or Co-Borrower: 3; Race of Co-Applicant or Co- Borrower: 4;
		Race of Co-Applicant or Co-Borrower: 5 must equal 1, 2, 3, 4, or 5, or be left blank."""
		field = "Co-Applicant Race Basis"
		edit_name = "v639_2"
		fail_df = self.lar_df[(self.lar_df.co_app_race_basis=="1")&((~self.lar_df.co_app_race_1.isin(("1", "2", "3", "4", "5", "")))|
		(~self.lar_df.co_app_race_2.isin(("1", "2", "3", "4", "5", "")))|(~self.lar_df.co_app_race_3.isin(("1", "2", "3", "4", "5", "")))|
		(~self.lar_df.co_app_race_4.isin(("1", "2", "3", "4", "5", "")))|(~self.lar_df.co_app_race_5.isin(("1", "2", "3", "4", "5", ""))))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v639_3(self):
		"""An invalid Race data field was reported.
		3) If Race of Co-Applicant or Co-Borrower Collected on the Basis of Visual Observation or Surname equals 2, then
		Race of Co-Applicant or Co-Borrower: 1must equal 1,2,21,22,23,24,25,26,27,3,4,41, 42, 43, 44, 5 or 6; and Race of Co-Applicant or Co- Borrower: 2;
		Race of Co-Applicant or Co-Borrower: 3; Race of Co-Applicant or Co-Borrower: 4; Race of Co- Applicant or Co-Borrower: 5
		must equal 1, 2, 21, 22, 23, 24, 25, 26, 27, 3, 4, 41, 42, 43, 44, 5, or be left blank."""
		field = "Co-Applicant Race Basis"
		edit_name = "v639_3"
		race_1 = ["1", "2", "21", "22", "23", "24", "25", "26", "27", "3", "4", "41", "42", "43", "44", "5", "6"]
		race_n = race_1[:-1]
		race_n.append("")
		fail_df = self.lar_df[(self.lar_df.co_app_race_basis=="2")&((~self.lar_df.co_app_race_1.isin(race_1))|
		(~self.lar_df.co_app_race_2.isin(race_n))|(~self.lar_df.co_app_race_3.isin(race_n))|(~self.lar_df.co_app_race_4.isin(race_n))|
		(~self.lar_df.co_app_race_5.isin(race_n)))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v640_1(self):
		"""An invalid Race data field was reported.
		1) If Race of Co-Applicant or Co-Borrower: 1 equals 7, then
		Race of Co-Applicant or Co-Borrower Collected on the Basis of Visual Observation or Surname must equal 3."""
		field = "Co-Applicant Race Basis"
		edit_name = "v640_1"
		fail_df = self.lar_df[(self.lar_df.co_app_race_1=="7")&(self.lar_df.co_app_race_basis!="3")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v640_2(self):
		"""An invalid Race data field was reported.
		2) If Race of Co-Applicant or Co-Borrower Collected on the Basis of Visual Observation or Surname equals 3, then
		Race of Co-Applicant or Co-Borrower: 1 must equal 6 or 7."""
		field = "Co-Applicant Race Basis"
		edit_name = "v640_2"
		fail_df = self.lar_df[(self.lar_df.co_app_race_basis=="3")&(~self.lar_df.co_app_race_1.isin(("6", "7")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v641(self):
		"""An invalid Race data field was reported.
		1) If Race of Co-Applicant or Co-Borrower: 1 equals 8, then
		Race of Co-Applicant or Co-Borrower Collected on the Basis of Visual Observation or Surname must equal 4, and the reverse must be true."""
		field = "Co-Applicant Race Basis"
		edit_name = "v641"
		fail_df = self.lar_df[((self.lar_df.co_app_race_1=="8")&(self.lar_df.co_app_race_basis!="4"))|
		((self.lar_df.co_app_race_basis=="4")&(self.lar_df.co_app_race_1!="8"))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v642_1(self):
		"""An invalid Sex data field was reported.
		1) Sex of Applicant or Borrower must equal 1, 2, 3, 4, or 6, and cannot be left blank."""
		field = "Applicant Sex"
		edit_name = "v642_1"
		fail_df = self.lar_df[(~self.lar_df.app_sex.isin(("1", "2", "3", "4", "6")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v642_2(self):
		"""An invalid Sex data field was reported.
		2) Sex of Applicant or Borrower Collected on the Basis of Visual Observation or Surname must equal 1, 2, or 3, and cannot be left blank."""
		field = "Applicant Sex Basis"
		edit_name = "v642_2"
		fail_df = self.lar_df[(~self.lar_df.app_sex_basis.isin(("1", "2", "3")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v643_1(self):
		"""An invalid Sex data field was reported.
		1) If Sex of Applicant or Borrower Collected on the Basis of Visual Observation or Surname equals 1,
		then Sex of Applicant or Borrower must equal 1 or 2."""
		field = "Applicant Sex Basis"
		edit_name = "v643_1"
		fail_df = self.lar_df[(self.lar_df.app_sex_basis=="1")&(~self.lar_df.app_sex.isin(("1", "2")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)
	def v643_2(self):
		"""An invalid Sex data field was reported.
		2) If Sex of Applicant or Borrower equals 1 or 2, then the Sex of Applicant or Borrower Collected on the
		Basis of Visual Observation or Surname must equal 1 or 2."""
		field = "Applicant Sex Basis"
		edit_name = "v643_2"
		fail_df = self.lar_df[(self.lar_df.app_sex.isin(("1","2")))&(~self.lar_df.app_sex_basis.isin(("1", "2")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v644_1(self):
		"""An invalid Sex data field was reported.
		1) If Sex of Applicant or Borrower Collected on the Basis of Visual Observation or Surname equals 2,
		then Sex of Applicant or Borrower must equal 1, 2, 3, or 6."""
		field = "Applicant Sex"
		edit_name = "v644_1"
		fail_df = self.lar_df[(self.lar_df.app_sex_basis=="2")&(~self.lar_df.app_sex.isin(("1", "2", "3", "6")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v644_2(self):
		"""An invalid Sex data field was reported.
		2) If Sex of Applicant or Borrower equals 6, then Sex of Applicant or Borrower Collected on the Basis of
		Visual Observation or Surname must equal 2."""
		field = "Applicant Sex Basis"
		edit_name = "v644_2"
		fail_df = self.lar_df[(self.lar_df.app_sex=="6")&(self.lar_df.app_sex_basis!="2")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v645_1(self):
		"""An invalid Sex data field was reported.
		1) If Sex of Applicant or Borrower Collected on the Basis of Visual Observation or Surname equals 3,
		then Sex of Applicant or Borrower must equal 3 or 4."""
		field = "Applicant Sex"
		edit_name = "v645_1"
		fail_df = self.lar_df[(self.lar_df.app_sex_basis=="3")&(~self.lar_df.app_sex.isin(("3", "4")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v645_2(self):
		"""An invalid Sex data field was reported.
		2) If Sex of Applicant or Borrower equals 4, then Sex of Applicant or Borrower Collected on the Basis of Visual Observation or Surname must equal 3."""
		field = "Applicant Sex Basis"
		edit_name = "v645_2"
		fail_df = self.lar_df[(self.lar_df.app_sex=="4")&(self.lar_df.app_sex_basis!="3")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v646_1(self):
		"""An invalid Sex data field was reported.
		1) Sex of Co-Applicant or Co-Borrower must equal 1, 2, 3, 4, 5, or 6, and cannot be left blank."""
		field = "Co-Applicant Sex"
		edit_name = "v646_1"
		fail_df = self.lar_df[(~self.lar_df.co_app_sex.isin(("1", "2", "3", "4", "5", "6")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v646_2(self):
		"""An invalid Sex data field was reported.
		2) Sex of Co-Applicant or Co-Borrower Collected on the Basis of Visual Observation or Surname must
		equal 1, 2, 3, or 4, and cannot be left blank."""
		field = "Co-Applicant Sex Basis"
		edit_name = "v646_2"
		fail_df = self.lar_df[~(self.lar_df.co_app_sex_basis.isin(("1", "2", "3", "4")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v647_1(self):
		"""An invalid Sex data field was reported.
		1) If Sex of Co-Applicant or Co-Borrower Collected on the Basis of Visual Observation or Surname equals 1, then
		Sex of Co-Applicant or Co-Borrower must equal 1 or 2."""
		field = "Co-Applicant Sex"
		edit_name = "v647_1"
		fail_df = self.lar_df[(self.lar_df.co_app_sex_basis=="1")&(~self.lar_df.co_app_sex.isin(("1", "2")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v647_2(self):
		"""An invalid Sex data field was reported.
		2) If Sex of Co-Applicant or Co-Borrower equals 1 or 2, then
		Sex of Co-Applicant or Co-Borrower Collected on the Basis of Visual Observation or Surname must equal 1 or 2."""
		field = "Co-Applicant Sex Basis"
		edit_name = "v647_2"
		fail_df = self.lar_df[(self.lar_df.co_app_sex.isin(("1", "2")))&(~self.lar_df.co_app_sex_basis.isin(("1", "2")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v648_1(self):
		"""An invalid Sex data field was reported.
		1) If Sex of Co-Applicant or Co-Borrower Collected on the Basis of Visual Observation or Surname equals 2,
		then Sex of Co-Applicant or Co-Borrower must equal 1, 2, 3 or 6."""
		field = "Co Applicant Sex"
		edit_name = "v648_1"
		fail_df = self.lar_df[(self.lar_df.co_app_sex_basis=="2")&(~self.lar_df.co_app_sex.isin(("1","2", "3", "6")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v648_2(self):
		"""An invalid Sex data field was reported.
		2) If Sex of Co-Applicant or Co-Borrower equals 6, then
		Sex of Co-Applicant or Co-Borrower Collected on the Basis of Visual Observation or Surname must equal 2."""
		field = "Co-Applicant Sex Basis"
		edit_name = "v648_2"
		fail_df = self.lar_df[(self.lar_df.co_app_sex=="6")&(self.lar_df.co_app_sex_basis!="2")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v649_1(self):
		"""An invalid Sex data field was reported.
		1) If Sex of Co-Applicant or Co-Borrower Collected on the Basis of Visual Observation or Surname equals 3,
		then Sex of Co-Applicant or Co-Borrower must equal 3 or 4."""
		field = "Co-Applicant Sex"
		edit_name = "v649_1"
		fail_df = self.lar_df[(self.lar_df.co_app_sex_basis=="3")&(~self.lar_df.co_app_sex.isin(("3", "4")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v649_2(self):
		"""An invalid Sex data field was reported.
		2) If Sex of Co-Applicant or Co-Borrower equals 4, then
		Sex of Co-Applicant or Co-Borrower Collected on the Basis of Visual Observation or Surname must equal 3."""
		field = "Co-Applicant Sex Basis"
		edit_name = "v649_2"
		fail_df = self.lar_df[(self.lar_df.co_app_sex=="4")&(self.lar_df.co_app_sex_basis!="3")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v650(self):
		"""An invalid Sex data field was reported.
		1) If Sex of Co-Applicant or Co-Borrower Collected on the Basis of Visual Observation or Surname equals 4,
		then Sex of Co-Applicant or Co-Borrower must equal 5, and the reverse must be true."""
		field = "Co-Applicant Sex"
		edit_name = "v650"
		fail_df = self.lar_df[((self.lar_df.co_app_sex_basis=="4")&(self.lar_df.co_app_sex!="5"))|
			((self.lar_df.co_app_sex=="5")&(self.lar_df.co_app_sex_basis!="4"))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v651_1(self):
		"""An invalid Age of Applicant or Borrower was reported.
		1) Age of Applicant or Borrower must be a whole number greater than zero, and cannot be left blank."""
		field = "Applicant Age"
		edit_name = "v651_1"
		fail_df = self.lar_df[(self.lar_df.app_age.map(lambda x: self.check_number(field=x, min_val=0))==False)]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v651_2(self):
		"""An invalid Age of Applicant or Borrower was reported.
		2) If the Ethnicity of Applicant or Borrower: 1 equals 4; and Race of Applicant or Borrower: 1 equals 7; and
		Sex of Applicant or Borrower equals 4 indicating the applicant or borrower is a non-natural person,
		then Age of Applicant or Borrower must equal 8888."""
		field = "Applicant Age"
		edit_name = "v651_2"
		fail_df = self.lar_df[((self.lar_df.app_eth_1=="4")&(self.lar_df.app_race_1=="7")&(self.lar_df.app_sex=="4"))&
					(self.lar_df.app_age!="8888")&(self.lar_df.action_taken!="6")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v652_1(self):
		"""An invalid Age of Co-Applicant or Co-Borrower was reported.
		1) Age of Co-Applicant or Co-Borrower must be a whole number greater than zero, and cannot be left blank."""
		field = "Co-Applicant Age"
		edit_name = "v652_1"
		fail_df = self.lar_df[(self.lar_df.co_app_age.map(lambda x: self.check_number(field=x, min_val=0))==False)]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v652_2(self):
		"""An invalid Age of Co-Applicant or Co-Borrower was reported.
		2) If the Ethnicity of Co-Applicant or Co-Borrower: 1 equals 4; and Race of Co-Applicant or Co-Borrower: 1 equals 7;
		and Sex of Co-Applicant or Co-Borrower: 1 equals 4 indicating that the co-applicant or co- borrower is a non-natural person,
		then Age of Co- Applicant or Co-Borrower must equal 8888."""
		field = "Co-Applicant Age"
		edit_name = "v652_2"
		fail_df = self.lar_df[((self.lar_df.co_app_eth_1=="4")&(self.lar_df.co_app_race_1=="7")&(self.lar_df.co_app_sex=="4"))&
					(self.lar_df.co_app_age!="8888")&(self.lar_df.action_taken!="6")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v654_1(self):
		"""An invalid Income was reported.
		1) Income must be either a positive or negative integer rounded to the nearest thousand or NA, and cannot be left blank."""
		field = "Income"
		edit_name = "v654_1"
		fail_df = self.lar_df[(self.lar_df.income!="NA")&(self.lar_df.income.map(lambda x: x.isdigit())==False)]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v654_2(self):
		"""An invalid Income was reported.
		2) If Multifamily Affordable Units is a number, then Income must be NA."""
		field = "Income"
		edit_name = "v654_2"
		fail_df = self.lar_df[(self.lar_df.affordable_units.map(lambda x: x.isdigit())==True)&(self.lar_df.income!="NA")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v655_1(self):
		"""An invalid income was reported.
		1) If Ethnicity of Applicant or Borrower: 1 equals 4; and Race of Applicant or Borrower: 1 equals 7; and
		Sex of Applicant or Borrower: 1 equals 4 indicating the applicant is a non-natural person, then Income must be NA."""
		field = "Income"
		edit_name = "v655_1"
		fail_df = self.lar_df[((self.lar_df.app_eth_1=="4")&(self.lar_df.app_race_1=="7")&(self.lar_df.app_sex=="4"))&
					(self.lar_df.income!="NA")&(self.lar_df.action_taken!="6")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v655_2(self):
		"""An invalid income was reported.
		2) If Ethnicity of Co-Applicant or Co-Borrower: 1 equals 4; and Race of Co-Applicant or Co-Borrower: 1 equals 7;
		and Sex of Co-Applicant or Co-Borrower: 1 equals 4 indicating that the co-applicant or co- borrower is a non-natural person, then Income must be NA"""
		field = "Income"
		edit_name = "v655_2"
		fail_df = self.lar_df[((self.lar_df.co_app_eth_1=="4")&(self.lar_df.co_app_race_1=="7")&(self.lar_df.co_app_sex=="4"))&
					(self.lar_df.income!="NA")&(self.lar_df.action_taken!="6")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v656_1(self):
		"""An invalid Type of Purchaser was reported.
		1) Type of Purchaser must equal 0, 1, 2, 3, 4, 5, 6, 71, 72, 8 or 9, and cannot be left blank."""
		field = "Type of Purchaser"
		edit_name = "v656_1"
		fail_df = self.lar_df[~(self.lar_df.purchaser_type.isin(("0", "1", "2", "3", "4", "5", "6", "71", "72", "8", "9")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v656_2(self):
		"""An invalid Type of Purchaser was reported.
		2) If Action Taken equals 2, 3, 4, 5, 7 or 8, then Type of Purchaser must equal 0."""
		field = "Type of Purchaser"
		edit_name = "v656_2"
		fail_df = self.lar_df[(self.lar_df.action_taken.isin(("2", "3", "4", "5", "7","8")))&(self.lar_df.purchaser_type!="0")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v657_1(self):
		"""An invalid Rate Spread was reported.
		1) Rate Spread must be a number or NA, and cannot be left blank."""

		field = "Rate Spread"
		edit_name = "v657_1"
		fail_df = self.lar_df[~(self.lar_df.rate_spread.isin(["NA", "Exempt"]))&
			(self.lar_df.rate_spread.map(lambda x: self.check_number(x))==False)]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v657_2(self):
		"""An invalid Rate Spread was reported.
		2) If Action Taken equals 3, 4, 5, 6, or 7, then Rate Spread must be NA.
		Impact of S2155: Update to: 
		2) If Action Taken equals 3, 4, 5, 6, or 7, then Rate Spread must be Exempt or NA. 
		"""
		field = "Rate Spread"
		edit_name = "v657_2"
		fail_df = self.lar_df[(self.lar_df.action_taken.isin(("3", "4", "5", "6", "7")))&
			(~self.lar_df.rate_spread.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v657_3(self):
		"""An invalid Rate Spread was reported.
		3) If Reverse Mortgage equals 1, then Rate Spread must be NA.
		Impact of S2155: Update to: 
		3) If Reverse Mortgage equals 1, then Rate Spread must be Exempt or NA."""
		field = "Rate Spread"
		edit_name = "v657_3"
		fail_df = self.lar_df[(self.lar_df.reverse_mortgage=="1")&(~self.lar_df.rate_spread.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v658_1(self):
		"""An invalid HOEPA Status was reported.
		1) HOEPA Status must equal 1, 2, or 3, and cannot be left blank."""
		field = "HOEPA"
		edit_name  = "v658_1"
		fail_df = self.lar_df[~(self.lar_df.hoepa.isin(("1", "2", "3")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v658_2(self):
		"""An invalid HOEPA Status was reported.
		2) If Action Taken equals 2, 3, 4, 5, 7, or 8, then HOEPA Status must be 3."""
		field = "HOEPA"
		edit_name = "v658_2"
		fail_df = self.lar_df[(self.lar_df.action_taken.isin(("2", "3", "4", "5", "7", "8")))&(self.lar_df.hoepa!="3")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v659(self):
		"""An invalid Lien Status was reported.
		1) Lien Status must equal 1 or 2, and cannot be left blank."""
		field = "Lien Status"
		edit_name = "v659"
		fail_df = self.lar_df[~(self.lar_df.lien.isin(("1", "2")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v660_1(self):
		"""An invalid Credit Score data field was reported.
		1) Credit Score of Applicant or Borrower must be a number, and cannot be left blank."""
		field = "App Credit Score"
		edit_name = "v660_1"
		fail_df = self.lar_df[(self.lar_df.app_credit_score.map(lambda x: self.check_number(x))==False)]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v660_2(self):
		"""An invalid Credit Score data field was reported.
		2) Applicant or Borrower, Name and Version of Credit Scoring Model must equal 1, 2, 3, 4, 5, 6, 7, 8, or 9."""
		field = "App Credit Score"
		edit_name = "v660_2"
		fail_df = self.lar_df[(~self.lar_df.app_score_name.isin(("1111", "1", "2", "3", "4", "5", "6", "7", "8", "9")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v661(self):
		"""An invalid Credit Score data field was reported.
		1) If Credit Score of Applicant or Borrower equals 8888 indicating not applicable, then
		Applicant or Borrower, Name and Version of Credit Scoring Model must equal 9, and the reverse must be true."""
		field = "App Credit Score"
		edit_name = "v661"
		fail_df = self.lar_df[((self.lar_df.app_credit_score=="8888")&(self.lar_df.app_score_name!="9"))|
			((self.lar_df.app_score_name=="9")&(self.lar_df.app_credit_score!="8888"))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v662_1(self):
		"""An invalid Credit Score data field was reported.
		1) If Applicant or Borrower, Name and Version of Credit Scoring Model equals 1, 2, 3, 4, 5, 6, 7, or 9, then
		Applicant or Borrower, Name and Version of Credit Scoring Model: Conditional Free Form Text Field for Code 8 
		must be left blank, and the reverse must be true.

		Impact of S2155: Update to: 
		1) If Applicant or Borrower, Name and Version of Credit Scoring Model equals 1111, 1, 2, 3, 4, 5, 6, 7, or 9, 
		then Applicant or Borrower, Name and Version of Credit Scoring Model: Conditional Free Form Text Field for Code 8 
		must be left blank, and the reverse must be true. 
"""
		field = "App Score Name"
		edit_name = "v662_1"
		fail_df = self.lar_df[((self.lar_df.app_score_name.isin(("1111", "1", "2", "3", "4", "5", "6", "7", "9")))&
			(self.lar_df.app_score_code_8!=""))|
			((self.lar_df.app_score_code_8=="")&
				(~self.lar_df.app_score_name.isin(("1", "2", "3", "4", "5", "6", "7", "9"))))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v662_2(self):
		"""An invalid Credit Score data field was reported.
		2) If Applicant or Borrower, Name and Version of Credit Scoring Model equals 8, then
		Applicant or Borrower, Name and Version of Credit Scoring Model: Conditional Free Form Text Field for Code 8 must not be blank,
		and the reverse must be true.

		Impact of S2155: Update to:
		2) If Applicant or Borrower, Name and Version of Credit Scoring Model equals 8, 
		then Applicant or Borrower, Name and Version of Credit Scoring Model: Conditional Free Form Text Field for Code 8 
		must not be blank, and the reverse must be true."""
		field = "App Score Name"
		edit_name= "v662_2"
		fail_df = self.lar_df[((self.lar_df.app_score_name=="8")&(self.lar_df.app_score_code_8==""))|
			((self.lar_df.app_score_code_8!="")&(self.lar_df.app_score_name!="8"))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v663(self):
		"""An invalid Credit Score data field was reported.
		1) If Action Taken equals 4, 5, or 6, then Credit Score of Applicant or Borrower must equal 8888; and
		Applicant or Borrower, Name and Version of Credit Scoring Model must equal 9; and
		Applicant or Borrower, Name and Version of Credit Scoring Model: Conditional Free Form Text Field for Code 8 must be left blank.

		Impact of S2155: Update to: 1) If Action Taken equals 4, 5, or 6, 
		then Credit Score of Applicant or Borrower must equal 8888 or Exempt; 
		and Applicant or Borrower, Name and Version of Credit Scoring Model must equal 9 or Exempt; 
		and Applicant or Borrower, Name and Version of Credit Scoring Model: Conditional Free Form Text Field for Code 8 
		must be left blank."""
		field = "App Credit Score"
		edit_name = "v663"
		fail_df = self.lar_df[(self.lar_df.action_taken.isin(("4", "5", "6")))&
			((~self.lar_df.app_credit_score.isin(["8888", "Exempt"]))|
			(~self.lar_df.app_score_name.isin(["9", "Exempt"]))|
			(self.lar_df.app_score_code_8!=""))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v664(self):
		"""An invalid Credit Score data field was reported.
		1) If Action Taken equals 4, 5, or 6, then Credit Score of Co-Applicant or Co-Borrower must equal 8888; and
		Co-Applicant or Co-Borrower, Name and Version of Credit Scoring Model must equal 9; and
		Co- Applicant or Co-Borrower, Name and Version of Credit Scoring Model: Conditional Free Form Text Field for Code 8 must be left blank

		Impact of S2155: Update to: 
		1) If Action Taken equals 4, 5, or 6, then Credit Score of Co-Applicant or Co-Borrower must equal 8888 or Exempt; 
		and Co-Applicant or Co-Borrower, Name and Version of Credit Scoring Model must equal 9 or Exempt; 
		and Co-Applicant or Co-Borrower, Name and Version of Credit Scoring Model: 
			Conditional Free Form Text Field for Code 8 must be left blank."""
		field = "Co-App Credit Score"
		edit_name = "v664"
		fail_df = self.lar_df[(self.lar_df.action_taken.isin(("4", "5", "6")))&((~self.lar_df.co_app_credit_score.isin(["8888", "Exempt"]))|
			(~self.lar_df.co_app_score_name.isin(["9", "Exempt"]))|(self.lar_df.co_app_score_code_8!=""))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v665_1(self):
		"""An invalid Credit Score data field was reported.
		1) Credit Score of Co-Applicant or Co-Borrower must be a number, and cannot be left blank."""
		field = "Co-App Credit Score"
		edit_name = "v665_1"
		fail_df = self.lar_df[(self.lar_df.co_app_credit_score.map(lambda x: self.check_number(x))==False)]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v665_2(self):
		"""An invalid Credit Score data field was reported.
		2) Co-Applicant or Co-Borrower, Name and Version of Credit Scoring Model must equal 1, 2, 3, 4, 5, 6, 7, 8, 9, or 10, 
		and cannot be left blank.

		Impact of S2155: Update to: 
		1) Credit Score of Co-Applicant or Co-Borrower must be a number, and cannot be left blank. 

		2) Co-Applicant or Co-Borrower, Name and Version of Credit Scoring Model must equal 1111, 1, 2, 3, 4, 5, 6, 7, 8, 9, or 10, 
		and cannot be left blank."""
		field = "Co-App Score Name"
		edit_name = "v665_2"
		fail_df = self.lar_df[~(self.lar_df.co_app_score_name.isin(("1111", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v666_1(self):
		"""An invalid Credit Score data field was reported.
		1) If Credit Score of Co-Applicant or Co-Borrower equals 8888 indicating not applicable, then
		Co- Applicant or Co-Borrower, Name and Version of Credit Scoring Model must equal 9, and the reverse must be true."""
		field = "Co-App Credit Score"
		edit_name = "v666_1"
		fail_df = self.lar_df[((self.lar_df.co_app_credit_score=="8888")&(self.lar_df.co_app_score_name!="9"))|
			((self.lar_df.co_app_score_name=="9")&(self.lar_df.co_app_credit_score!="8888"))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v666_2(self):
		"""An invalid Credit Score data field was reported.
		2) If Credit Score of Co-Applicant or Co-Borrower equals 9999 indicating no co-applicant, then
		Co- Applicant or Co-Borrower, Name and Version of Credit Scoring Model must equal 10, and the reverse must be true."""
		field = "Co-App Credit Score"
		edit_name = "v666_2"
		fail_df = self.lar_df[((self.lar_df.co_app_credit_score=="9999")&(self.lar_df.co_app_score_name!="10"))|
			((self.lar_df.co_app_score_name=="10")&(self.lar_df.co_app_credit_score!="9999"))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v667_1(self):
		"""An invalid Credit Score data field was reported.
		1) If Co-Applicant or Co-Borrower, Name and Version of Credit Scoring Model equals 1, 2, 3, 4, 5, 6, 7, 9, or 10, then
		Co-Applicant or Co-Borrower, Name and Version of Credit Scoring Model: Conditional Free Form Text Field for Code 8 must be left blank,
		and the reverse must be true.

		Impact of S2155: Update to: 
		1) If Co-Applicant or Co-Borrower, Name and Version of Credit Scoring Model equals 1111, 1, 2, 3, 4, 5, 6, 7, 9, or 10, 
		then Co-Applicant or Co-Borrower, Name and Version of Credit Scoring Model: Conditional Free Form Text Field for Code 8 
		must be left blank, and the reverse must be true. """
		field = "Co-App Credit Score Text"
		edit_name = "v667_1"
		fail_df = self.lar_df[((self.lar_df.co_app_score_name.isin(("1111", "1", "2", "3", "4", "5", "6", "7", "9", "10")))&
			(self.lar_df.co_app_score_code_8!=""))|
			((self.lar_df.co_app_score_code_8=="")&(~self.lar_df.co_app_score_name.isin(("1111", "1", "2", "3", "4", "5", "6", "7", "9", "10"))))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v667_2(self):
		"""An invalid Credit Score data field was reported.
		2) If Co-Applicant or Co-Borrower, Name and Version of Credit Scoring Model equals 8, then
		Co-Applicant or Co-Borrower, Name and Version of Credit Scoring Model: Conditional Free Form Text Field for Code 8 must not be left blank,
		and the reverse must be true.

		Impact of S2155: Update to: 
		2) If Co-Applicant or Co-Borrower, Name and Version of Credit Scoring Model equals 8, 
		then Co-Applicant or Co-Borrower, Name and Version of Credit Scoring Model: Conditional Free Form Text Field for Code 8 
		must not be left blank, and the reverse must be true."""
		field = "Co-App Credit Score Text"
		edit_name = "v667_2"
		fail_df = self.lar_df[((self.lar_df.co_app_score_name=="8")&(self.lar_df.co_app_score_code_8==""))|
			((self.lar_df.co_app_score_code_8!="")&(self.lar_df.co_app_score_name!="8"))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v668_1(self):
		"""An invalid Credit Score data point was reported.
		1) If Ethnicity of Applicant or Borrower: 1 equals 4; and Race of Applicant or Borrower: 1 equals 7;
		and Sex of Applicant or Borrower equals 4 indicating the applicant is a non-natural person then
		Credit Score of Applicant or Borrower must equal 8888 indicating not applicable.

		Impact of S2155: Update to: 
		1) If Ethnicity of Applicant or Borrower: 1 equals 4; and Race of Applicant or Borrower: 1 equals 7; 
		and Sex of Applicant or Borrower equals 4 indicating the applicant is a non-natural person 
		then Credit Score of Applicant or Borrower must equal 8888, indicating not applicable, or Exempt. """
		field = "App Credit Score"
		edit_name = "v668_1"
		fail_df = self.lar_df[((self.lar_df.app_eth_1=="4")&(self.lar_df.app_race_1=="7")&(self.lar_df.app_sex=="4"))&
		(~self.lar_df.app_credit_score.isin(["8888", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v668_2(self):
		"""An invalid Credit Score data point was reported.
		2) If Ethnicity of Co-Applicant or Co-Borrower: 1 equals 4; and
		Race of Co-Applicant or Co-Borrower: 1 equals 7;
		and Sex of Co-Applicant or Co-Borrower equals 4 indicating that the co-applicant is a non- natural person,
		then Credit Score of Co-Applicant or Co-Borrower must equal 8888 indicating not applicable.

		Impact of S2155: Update to: 		
		2) If Ethnicity of Co-Applicant or Co-Borrower: 1 equals 4; and Race of Co-Applicant or Co-Borrower: 1 equals 7; 
		and Sex of Co-Applicant or Co-Borrower equals 4 indicating that the co-applicant is a non-natural person, 
		then Credit Score of Co-Applicant or Co-Borrower must equal 8888, indicating not applicable, or Exempt."""
		field = "Co-App Credit Score"
		edit_name = "v668_2"
		fail_df = self.lar_df[(self.lar_df.co_app_eth_1=="4")&(self.lar_df.co_app_race_1=="7")&(self.lar_df.co_app_sex=="4")&
		(~self.lar_df.co_app_credit_score.isin(["8888", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v669_1(self):
		"""An invalid Reason for Denial data field was reported.
		1) Reason for Denial: 1 must equal 1, 2, 3, 4, 5, 6, 7, 8, 9, or 10, and cannot be left blank.

		Impact of S2155: Update to: 
		1) Reason for Denial: 1 must equal 1111, 1, 2, 3, 4, 5, 6, 7, 8, 9, or 10, and cannot be left blank. """
		field = "Denial Reason 1"
		edit_name = "v669_1"
		fail_df = self.lar_df[(~self.lar_df.denial_1.isin(("1111", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v669_2(self):
		"""An invalid Reason for Denial data field was reported.
		2) Reason for Denial: 2; Reason for Denial: 3; and Reason for Denial: 4 must equal 1, 2, 3, 4, 5, 6, 7, 8, 9, or be left blank."""
		field = "Denial Reason 2-4"
		edit_name = "v669_2"
		denials = ["1", "2", "3", "4", "5", "6", "7", "8", "9", ""]
		fail_df = self.lar_df[~(self.lar_df.denial_2.isin(denials))|(~self.lar_df.denial_3.isin(denials))|(~self.lar_df.denial_4.isin(denials))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v669_3(self):
		"""An invalid Reason for Denial data field was reported.
		3) Each Reason for Denial code can only be reported once."""
		field = "Denial Reasons 1-4"
		edit_name = "v669_3"
		dupe_fields = ["denial_1", "denial_2", "denial_3", "denial_4"]
		fail_df = self.lar_df[(self.lar_df.apply(lambda x: self.check_dupes(x, fields=dupe_fields), axis=1)=="fail")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v669_4(self):
		"""An invalid Reason for Denial data field was reported.
		4) If Reason for Denial: 1 equals 10, then Reason for Denial: 2; Reason for Denial: 3; and Reason for Denial: 4 must all be left blank.
		
		Impact of S2155: Update to: 
		4) If Reason for Denial: 1 equals 1111 or 10, then Reason for Denial: 2; Reason for Denial: 3; and Reason for Denial: 4 
		must all be left blank."""
		field = "Denial Reasons 1-4"
		edit_name = "v669_4"
		fail_df = self.lar_df[(self.lar_df.denial_1.isin(["1111", "10"]))&
			((self.lar_df.denial_2!="")|(self.lar_df.denial_3!="")|(self.lar_df.denial_4!=""))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v670_1(self):
		"""An invalid Reason for Denial data field was reported.
		1) If Action Taken equals 3 or 7, then the Reason for Denial: 1 must equal 1, 2, 3, 4, 5, 6, 7, 8, or 9, and the reverse must be true.

		Impact of S2155: Update to: 
		1) If Action Taken equals 3 or 7, then the Reason for Denial: 1 must equal 1111, 1, 2, 3, 4, 5, 6, 7, 8, or 9. 
		2) If Reason for Denial: 1 equals 1, 2, 3, 4, 5, 6, 7, 8, or 9, then Action Taken must equal 3 or 7."""
		field = "Denial Reason 1"
		edit_name = "v670_1"
		fail_df = self.lar_df[((self.lar_df.action_taken.isin(("3","7")))&
			(~self.lar_df.denial_1.isin(("1111", "1", "2", "3", "4", "5", "6", "7", "8", "9"))))|
			((self.lar_df.denial_1.isin(("1111", "1", "2", "3", "4", "5", "6", "7", "8", "9")))&(~self.lar_df.action_taken.isin(("3", "7"))))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v670_2(self):
		"""An invalid Reason for Denial data field was reported.
		2) If Action Taken equals 1, 2, 4, 5, 6, or 8, then Reason for Denial: 1 must equal 10, and the reverse must be true.
		
		Impact of S2155: Update to: 
		3) If Action Taken equals 1, 2, 4, 5, 6, or 8, then Reason for Denial: 1 must equal 1111 or 10. 
		4) If Reason for Denial: 1 equals 10, then Action Taken must equal 1, 2, 4, 5, 6, or 8."""
		field = "Denial Reason 1"
		edit_name = "v670_2"
		fail_df = self.lar_df[((self.lar_df.action_taken.isin(("1", "2", "4", "5", "6", "8")))&(~self.lar_df.denial_1.isin(["1111", "10"])))|
			((self.lar_df.denial_1.isin(["1111","10"]))&(~self.lar_df.action_taken.isin(("1", "2", "3", "4", "5", "6", "8"))))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v671_1(self):
		"""An invalid Reason for Denial data field was reported.
		1) Reason for Denial: 1; Reason for Denial: 2; Reason for Denial: 3;
		or Reason for Denial: 4 was reported Code 9: Other; however,
		the Reason for Denial: Conditional Free Form Text Field for Code 9 was left blank."""
		field = "Denail Reasons 1-4"
		edit_name = "v671_1"
		fail_df = self.lar_df[((self.lar_df.denial_1=="9")|(self.lar_df.denial_2=="9")|(self.lar_df.denial_3=="9")|(self.lar_df.denial_4=="9"))&
			(self.lar_df.denial_code_9=="")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v671_2(self):
		"""An invalid Reason for Denial data field was reported.
		2) The Reason for Denial: Conditional Free Form Text Field for Code 9 was reported,
		but Code 9 was not reported in Reason for Denial: 1; Reason for Denial: 2; Reason for Denial: 3; or Reason for Denial: 4."""
		field = "Denial Reasons 1-4"
		edit_name = "v671_2"
		fail_df = self.lar_df[((self.lar_df.denial_1!="9")&(self.lar_df.denial_2!="9")&(self.lar_df.denial_3!="9")&(self.lar_df.denial_4!="9"))&
			(self.lar_df.denial_code_9!="")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v672_1(self):
		"""An invalid Total Loan Costs or Total Points and Fees data field was reported.
		1) Total Loan Costs must be a number greater than or equal to 0 or NA, and cannot be left blank.
		
		Impact of S2155: Update to: 
		1) Total Loan Costs must be a number greater than or equal to 0, Exempt, or NA, and cannot be left blank. """
		field = "Loan Costs"
		edit_name = "v672_1"
		fail_df = self.lar_df[(self.lar_df.loan_costs.map(lambda x: 
			self.check_number(x, min_val=0))==False)&(~self.lar_df.loan_costs.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v672_2(self):
		"""An invalid Total Loan Costs or Total Points and Fees data field was reported.
		2) If Total Points and Fees is a number greater than or equal to 0, then Total Loan Costs must be NA."""
		field = "Loan Costs"
		edit_name = "v672_2"
		fail_df = self.lar_df[(self.lar_df.points_fees.map(lambda x: self.check_number(x, min_val=0))==True)&(self.lar_df.loan_costs!="NA")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v672_3(self):
		"""An invalid Total Loan Costs or Total Points and Fees data field was reported.
		3) If Reverse Mortgage equals 1, then Total Loan Costs must be NA.

		Impact of S2155: Update to:
		3) If Reverse Mortgage equals 1, then Total Loan Costs must be Exempt or NA."""
		field = "Loan Costs"
		edit_name = "v672_3"
		fail_df = self.lar_df[(self.lar_df.reverse_mortgage=="1")&(~self.lar_df.loan_costs.isin(["NA","Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v672_4(self):
		"""An invalid Total Loan Costs or Total Points and Fees data field was reported.
		4) If Open-End Line of Credit equals 1, then Total Loan Costs must be NA.
		
		Impact of S2155: Update to:
		4) If Open-End Line of Credit equals 1, then Total Loan Costs must be Exempt or NA. """
		field = "Loan Costs"
		edit_name = "v672_4"
		fail_df = self.lar_df[(self.lar_df.open_end_credit=="1")&(~self.lar_df.loan_costs.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v672_5(self):
		"""An invalid Total Loan Costs or Total Points and Fees data field was reported.
		5) If Business or Commercial Purpose equals 1, then Total Loan Costs must be NA.

		Impact of S2155: Update to:
		5) If Business or Commercial Purpose equals 1, then Total Loan Costs must be Exempt or NA. """
		field = "Loan Costs"
		edit_name = "v672_5"
		fail_df = self.lar_df[(self.lar_df.business_purpose=="1")&(~self.lar_df.loan_costs.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v672_6(self):
		"""An invalid Total Loan Costs or Total Points and Fees data field was reported.
		6) If Action Taken equals 2, 3, 4, 5, 7 or 8, then Total Loan Costs must be NA.

		Impact of S2155: Update to:
		6) If Action Taken equals 2, 3, 4, 5, 7 or 8, then Total Loan Costs must be Exempt or NA."""
		field = "Loan Costs"
		edit_name = "v672_6"
		fail_df = self.lar_df[(self.lar_df.action_taken.isin(("2", "3", "4", "5", "7", "8"))&(~self.lar_df.loan_costs.isin(["NA", "Exempt"])))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v673_1(self):
		"""An invalid Total Points and Fees was reported.
		1) Total Points and Fees must be a number greater than or equal to 0 or NA, and cannot be left blank.

		Impact of S2155: Update to: 
		1) Total Points and Fees must be a number greater than or equal to 0, Exempt, or NA, and cannot be left blank. 
		
		
		 
		"""
		field = "Points and Fees"
		edit_name = "v673_1"
		fail_df = self.lar_df[(self.lar_df.points_fees.map(lambda x: 
			self.check_number(x, min_val=0))==False)&(~self.lar_df.points_fees.isin(["NA"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v673_2(self):
		"""An invalid Total Points and Fees was reported.
		2) If Action Taken equals 2, 3, 4, 5, 6, 7 or 8 then Total Points and Fees must be NA.

		Impact of S2155: Update to:
		2) If Action Taken equals 2, 3, 4, 5, 6, 7 or 8 then Total Points and Fees must be Exempt or NA."""
		field = "Points and Fees"
		edit_name = "v673_2"
		fail_df = self.lar_df[(self.lar_df.action_taken.isin(("2", "3", "4", "5", "6", "7", "8")))&(self.lar_df.points_fees!="NA")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v673_3(self):
		"""An invalid Total Points and Fees was reported.
		3) If Reverse Mortgage equals 1, then Total Points and Fees must be NA.
		
		Impact of S2155: Update to: 
		3) If Reverse Mortgage equals 1, then Total Points and Fees must be Exempt or NA."""
		field = "Points and Fees"
		edit_name = "v673_3"
		fail_df = self.lar_df[(self.lar_df.reverse_mortgage=="1")&(self.lar_df.points_fees!="NA")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v673_4(self):
		"""An invalid Total Points and Fees was reported.
		4) If Business or Commercial Purpose equals 1, then Total Points and Fees must be NA.
		
		Impact of S2155: Update to: 
		4) If Business or Commercial Purpose equals 1, then Total Points and Fees must be Exempt or NA."""
		field = "Points and Fees"
		edit_name = "v673_4"
		fail_df = self.lar_df[(self.lar_df.business_purpose=="1")&(self.lar_df.points_fees!="NA")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v673_5(self):
		"""An invalid Total Points and Fees was reported.
		5) If Total Loan Costs is a number greater than or equal to 0, then Total Points and Fees must be NA.
		
		Impact of S2155: Update to:
		5) If Total Loan Costs is a number greater than or equal to 0, then Total Points and Fees must be NA."""
		field = "Points and Fees"
		edit_name = "v673_5"
		fail_df = self.lar_df[(self.lar_df.loan_costs.map(lambda x: self.check_number(x, min_val=0))==True)&(self.lar_df.points_fees!="NA")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v674_1(self):
		"""An invalid Origination Charges was reported.
		1) Origination Charges must be a number greater than or equal to 0 or NA, and cannot be left blank.

		Impact of S2155: Update to: 
		1) Origination Charges must be a number greater than or equal to 0, Exempt, or NA, and cannot be left blank. """
		field = "Origination Charges"
		edit_name = "v674_1"
		fail_df = self.lar_df[(self.lar_df.origination_fee.map(lambda x: self.check_number(x, min_val=0))==False)&
			(~self.lar_df.origination_fee.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v674_2(self):
		"""An invalid Origination Charges was reported.
		2) If Reverse Mortgage equals 1, then Origination Charges must be NA.

		Impact of S2155: Update to: 
		2) If Reverse Mortgage equals 1, then Origination Charges must be Exempt or NA. """
		field = "Origination Charges"
		edit_name = "v674_2"
		fail_df = self.lar_df[(self.lar_df.reverse_mortgage=="1")&(~self.lar_df.origination_fee.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v674_3(self):
		"""An invalid Origination Charges was reported.
		3) If Open-End Line of Credit equals 1, then Origination Charges must be NA.

		Impact of S2155: Update to: 
		3) If Open-End Line of Credit equals 1, then Origination Charges must be Exempt or NA. """
		field = "Origination Charges"
		edit_name = "v674_3"
		fail_df = self.lar_df[(self.lar_df.open_end_credit=="1")&(~self.lar_df.origination_fee.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v674_4(self):
		"""An invalid Origination Charges was reported.
		4) If Business or Commercial Purpose equals 1, then Origination Charges must be NA.

		Impact of S2155: Update to: 
		4) If Business or Commercial Purpose equals 1, then Origination Charges must be Exempt or NA. """
		field = "Origination Charges"
		edit_name = "v674_4"
		fail_df = self.lar_df[(self.lar_df.business_purpose=="1")&(~self.lar_df.origination_fee.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v674_5(self):
		"""An invalid Origination Charges was reported.
		5) If Action Taken equals 2, 3, 4, 5, 7 or 8, then Origination Charges must be NA.

		Impact of S2155: Update to: 
		5) If Action Taken equals 2, 3, 4, 5, 7 or 8, then Origination Charges must be Exempt or NA."""
		field = "Origination Charges"
		edit_name = "v674_5"
		fail_df = self.lar_df[(self.lar_df.action_taken.isin(("2", "3", "4", "5", "7", "8")))&
			(~self.lar_df.origination_fee.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v675_1(self):
		"""An invalid Discount Points was reported.
		1) Discount Points must be a number greater than 0, blank, or NA.

		Impact of S2155: Update to: 
		1) Discount Points must be a number greater than 0, blank, Exempt, or NA."""
		field = "Discount Points"
		edit_name = "v675_1"
		fail_df = self.lar_df[(self.lar_df.discount_points.map(lambda x: 
			self.check_number(x, min_val=1))==False)&(~self.lar_df.discount_points.isin(["NA", "Exempt", ""]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v675_2(self):
		"""An invalid Discount Points was reported.
		2) If Reverse Mortgage equals 1, then Discount Points must be NA.

		Impact of S2155: Update to: 
		2) If Reverse Mortgage equals 1, then Discount Points must be Exempt or NA. """
		field = "Discount Points"
		edit_name = "v675_2"
		fail_df = self.lar_df[(self.lar_df.reverse_mortgage=="1")&(~self.lar_df.discount_points.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v675_3(self):
		"""An invalid Discount Points was reported.
		3) If Open-End Line of Credit equals 1, then Discount Points must be NA.

		Impact of S2155: Update to: 
		3) If Open-End Line of Credit equals 1, then Discount Points must be Exempt or NA."""
		field = "Discount Points"
		edit_name = "v675_3"
		fail_df = self.lar_df[(self.lar_df.open_end_credit=="1")&(~self.lar_df.discount_points.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v675_4(self):
		"""An invalid Discount Points was reported.
		4) If Business or Commercial Purpose equals 1, then Discount Points must be NA.

		Impact of S2155: Update to: 
		4) If Business or Commercial Purpose equals 1, then Discount Points must be Exempt or NA."""
		field = "Discount Points"
		edit_name = "v675_4"
		fail_df = self.lar_df[(self.lar_df.business_purpose=="1")&(~self.lar_df.discount_points.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v675_5(self):
		"""An invalid Discount Points was reported.
		5) If Action Taken equals 2, 3, 4, 5, 7 or 8, then Discount Points must be NA.

		Impact of S2155: Update to: 
		5) If Action Taken equals 2, 3, 4, 5, 7 or 8, then Discount Points must be Exempt or NA."""
		field = "Discount Points"
		edit_name = "v675_5"
		fail_df = self.lar_df[(self.lar_df.action_taken.isin(("2", "3", "4", "5", "7", "8")))&
			(~self.lar_df.discount_points.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v676_1(self):
		"""An invalid Lender Credits was reported.
		1) Lender Credits must be a number greater than 0, blank, or NA.

		Impact of S2155: Update to: 
		1) Lender Credits must be a number greater than 0, blank, Exempt, or NA. """
		field = "Lender Credits"
		edit_name = "v676_1"
		print(self.lar_df["lender_credits"])
		fail_df = self.lar_df[(self.lar_df.lender_credits.map(lambda x: 
			self.check_number(x, min_val=1))==False)&(~self.lar_df.lender_credits.isin(["NA", "Exempt", ""]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v676_2(self):
		"""An invalid Lender Credits was reported.
		2) If Reverse Mortgage equals 1, then Lender Credits must be NA.

		Impact of S2155: Update to: 
		2) If Reverse Mortgage equals 1, then Lender Credits must be Exempt or NA. """
		field = "Lender Credits"
		edit_name = "v676_2"
		fail_df = self.lar_df[(self.lar_df.reverse_mortgage=="1")&(~self.lar_df.lender_credits.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v676_3(self):
		"""An invalid Lender Credits was reported.
		3) If Open-End Line of Credit equals 1, then Lender Credits must be NA.
		
		Impact of S2155: Update to: 
		3) If Open-End Line of Credit equals 1, then Lender Credits must be Exempt or NA. """
		field = "Lender Credits"
		edit_name = "v676_3"
		fail_df = self.lar_df[(self.lar_df.open_end_credit=="1")&(~self.lar_df.lender_credits.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v676_4(self):
		"""An invalid Lender Credits was reported.
		4) If Business or Commercial Purpose equals 1, then Lender Credits must be NA.

		Impact of S2155: Update to: 
		4) If Business or Commercial Purpose equals 1, then Lender Credits must be Exempt or NA."""
		field = "Lender Credits"
		edit_name = "v676_4"
		fail_df = self.lar_df[(self.lar_df.business_purpose=="1")&(~self.lar_df.lender_credits.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v676_5(self):
		"""An invalid Lender Credits was reported.
		5) If Action Taken equals 2, 3, 4, 5, 7 or 8, then Lender Credits must be NA.

		Impact of S2155: Update to: 
		5) If Action Taken equals 2, 3, 4, 5, 7 or 8, then Lender Credits must be Exempt or NA."""
		field = "Lender Credits"
		edit_name = "v676_5"
		fail_df = self.lar_df[(self.lar_df.action_taken.isin(("2", "3", "4", "5", "7", "8")))&
			(~self.lar_df.lender_credits.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v677_1(self):
		"""An invalid Interest Rate was reported.
		1) Interest Rate must be a number greater than 0 or NA, and cannot be left blank.

		Impact of S2155: Update to: 
		1) Interest Rate must be a number greater than 0, Exempt or NA, and cannot be left blank."""
		field = "Interest Rate"
		edit_name = "v677_1"
		fail_df = self.lar_df[(self.lar_df.interest_rate.map(lambda x: self.check_number(x, min_val=1))==False)&
			(~self.lar_df.interest_rate.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v677_2(self):
		"""An invalid Interest Rate was reported.
		2) If Action Taken equals 3, 4, 5, or 7; then Interest Rate must be NA.
		
		Impact of S2155: Update to: 
		2) If Action Taken equals 3, 4, 5, or 7; then Interest Rate must be Exempt or NA."""
		field = "Interest Rate"
		edit_name = "v677_2"
		fail_df = self.lar_df[(self.lar_df.action_taken.isin(("3", "4", "5", "7")))&(~self.lar_df.interest_rate.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v678_1(self):
		"""An invalid Prepayment Penalty Term was reported.
		1) Prepayment Penalty Term must be a whole number greater than 0 or NA, and cannot be left blank.

		Impact of S2155: Update to: 
		1) Prepayment Penalty Term must be a whole number greater than 0, Exempt, or NA, and cannot be left blank."""
		field = "Prepayment Term"
		edit_name = "v678_1"
		fail_df = self.lar_df[(self.lar_df.prepayment_penalty.map(lambda x: self.check_number(x, min_val=0))==False)&
			(~self.lar_df.prepayment_penalty.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v678_2(self):
		"""An invalid Prepayment Penalty Term was reported.
		2) If Action Taken equals 6, then Prepayment Penalty Term must be NA.

		Impact of S2155: Update to: 
		2) If Action Taken equals 6, then Prepayment Penalty Term must be Exempt or NA. """
		field = "Prepayment Term"
		edit_name = "v678_2"
		fail_df = self.lar_df[(self.lar_df.action_taken=="6")&(~self.lar_df.prepayment_penalty.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v678_3(self):
		"""An invalid Prepayment Penalty Term was reported.
		3) If Reverse Mortgage equals 1, then Prepayment Penalty Term must be NA.

		Impact of S2155: Update to:
		3) If Reverse Mortgage equals 1, then Prepayment Penalty Term must be Exempt or NA.  """
		field = "Prepayment Term"
		edit_name = "v678_3"
		fail_df = self.lar_df[(self.lar_df.reverse_mortgage=="1")&(~self.lar_df.prepayment_penalty.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v678_4(self):
		"""An invalid Prepayment Penalty Term was reported.
		4) If Business or Commercial Purpose equals 1, then Prepayment Penalty Term must be NA.

		Impact of S2155: Update to:
		4) If Business or Commercial Purpose equals 1, then Prepayment Penalty Term must be Exempt or NA. """
		field = "Prepayment Term"
		edit_name = "v678_4"
		fail_df = self.lar_df[(self.lar_df.business_purpose=="1")&(~self.lar_df.prepayment_penalty.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v678_5(self):
		"""An invalid Prepayment Penalty Term was reported.
		5) If both Prepayment Penalty Term and Loan Term are numbers, then Prepayment Penalty Term must be less than or equal to Loan Term."""
		field = "Prepayment Term"
		edit_name = "v678_5"
		fields = ["prepayment_penalty", "loan_term"]
		fail_df = self.lar_df[(self.lar_df.apply(lambda x: self.compare_nums(x, fields=fields), axis=1)==True)]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v679_1(self):
		"""An invalid Debt-to-Income Ratio was reported.
		1) Debt-to-Income Ratio must be either a number or NA, and cannot be left blank.

		Impact of S2155: Update to: 
		1) Debt-to-Income Ratio must be either a number, Exempt or NA, and cannot be left blank. """
		field = "DTI"
		edit_name = "v679_1"
		fail_df = self.lar_df[(self.lar_df.dti.map(lambda x: self.check_number(x))==False)&(~self.lar_df.dti.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v679_2(self):
		"""An invalid Debt-to-Income Ratio was reported.
		2) If Action Taken equals 4, 5 or 6, then Debt-to- Income Ratio must be NA.

		Impact of S2155: Update to: 
		2) If Action Taken equals 4, 5 or 6, then Debt-to-Income Ratio must be Exempt or NA. """
		field = "DTI"
		edit_name = "v679_2"
		fail_df = self.lar_df[(self.lar_df.action_taken.isin(("4", "5", "6")))&(~self.lar_df.dti.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v679_3(self):
		"""An invalid Debt-to-Income Ratio was reported.
		3) If Multifamily Affordable Units is a number, then Debt-to-Income Ratio must be NA.

		Impact of S2155: Update to: 
		3) If Multifamily Affordable Units is a number, then Debt-to-Income Ratio must be Exempt or NA."""
		field = "DTI"
		edit_name = "v679_3"
		fail_df = self.lar_df[(self.lar_df.affordable_units.map(lambda x: self.check_number(x))==True)&(~self.lar_df.dti.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v680_1(self):
		"""An invalid Debt-to-Income Ratio was reported.
		1) If Ethnicity of Applicant or Borrower: 1 equals 4; and Race of Applicant or Borrower: 1 equals 7;
		and Sex of Applicant or Borrower: 1 equals 4 indicating the applicant or borrower is a non-natural person;
		and the Ethnicity of Co-Applicant or Co-Borrower: 1 equals 5; and Race of Co-Applicant or Co-Borrower: 1 equals 8;
		and Sex of Co-Applicant or Co-Borrower: 1 equals 5 indicating that there is no co-applicant or co-borrower,
		then Debt-to-Income Ratio must be NA.

		Impact of S2155: Update to: 
		1) If Ethnicity of Applicant or Borrower: 1 equals 4; and Race of Applicant or Borrower: 1 equals 7; 
		and Sex of Applicant or Borrower: 1 equals 4 indicating the applicant or borrower is a non-natural person; 
		and the Ethnicity of Co-Applicant or Co-Borrower: 1 equals 5; and Race of Co-Applicant or Co-Borrower: 1 equals 8; 
		and Sex of Co-Applicant or Co-Borrower: 1 equals 5 indicating that there is no co-applicant or co-borrower, 
		then Debt-to-Income Ratio must be Exempt or NA. """
		field = "DTI"
		edit_name = "v680_1"
		fail_df = self.lar_df[(self.lar_df.app_eth_1=="4")&(self.lar_df.app_race_1=="7")&(self.lar_df.app_sex=="4")&
			(self.lar_df.co_app_eth_1=="5")&(self.lar_df.co_app_race_1=="8")&(self.lar_df.co_app_sex=="5")&
			(~self.lar_df.dti.isin(["NA","Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v680_2(self):
		"""An invalid Debt-to-Income Ratio was reported.
		2) If Ethnicity of Applicant or Borrower: 1 equals 4; and Race of Applicant or Borrower: 1 equals 7;
		and Sex of Applicant or Borrower: 1 equals 4 indicating the applicant or borrower is a non-natural person;
		and the Ethnicity of Co-Applicant or Co-Borrower: 1 equals 4; and Race of Co-Applicant or Co-Borrower: 1 equals 7;
		and Sex of Co-Applicant or Co-Borrower: 1 equals 4 indicating that the co-applicant or co- borrower is also a non-natural person,
		then Debt-to- Income Ratio must be NA.

		Impact of S2155: Update to: 
		2) If Ethnicity of Applicant or Borrower: 1 equals 4; and Race of Applicant or Borrower: 1 equals 7; 
		and Sex of Applicant or Borrower: 1 equals 4 indicating the applicant or borrower is a non-natural person; 
		and the Ethnicity of Co-Applicant or Co-Borrower: 1 equals 4; and Race of Co-Applicant or Co-Borrower: 1 equals 7; 
		and Sex of Co-Applicant or Co-Borrower: 1 equals 4 indicating that the co-applicant or co-borrower is also a non-natural person, 
		then Debt-to-Income Ratio must be Exempt or NA."""
		field = "DTI"
		edit_name = "v680_2"
		fail_df = self.lar_df[(self.lar_df.app_eth_1=="4")&(self.lar_df.app_race_1=="7")&(self.lar_df.app_sex=="4")&
			(self.lar_df.co_app_eth_1=="4")&(self.lar_df.co_app_race_1=="7")&(self.lar_df.co_app_sex=="4")&
			(~self.lar_df.dti.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v681_1(self):
		"""An invalid Combined Loan-to-Value Ratio was reported.
		1) Combined Loan-to-Value Ratio must be either a number greater than 0 or NA, and cannot be left blank.

		Impact of S2155: Update to: 
		1) Combined Loan-to-Value Ratio must be either a number greater than 0, Exempt or NA, and cannot be left blank."""
		field = "CLTV"
		edit_name = "v681_1"
		fail_df = self.lar_df[(self.lar_df.cltv.map(lambda x: self.check_number(x, min_val=0))==False)&
			(~self.lar_df.cltv.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v681_2(self):
		"""An invalid Combined Loan-to-Value Ratio was reported.
		2) If Action Taken equals 4, 5, or 6, then Combined Loan-to-Value ratio must be NA.
		
		Impact of S2155: Update to: 
		2) If Action Taken equals 4, 5, or 6, then Combined Loan-to-Value ratio must be Exempt or NA."""
		field = "CLTV"
		edit_name = "v681_2"
		fail_df = self.lar_df[(self.lar_df.action_taken.isin(("4", "5", "6")))&(~self.lar_df.cltv.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v682_1(self):
		"""An invalid Loan Term was reported.
		1) Loan Term must be either a whole number greater than zero or NA, and cannot be left blank.

		Impact of S2155: Update to: 
		1) Loan Term must be either a whole number greater than zero, Exempt, or NA, and cannot be left blank. """
		field = "Loan Term"
		edit_name = "v682_1"
		fail_df = self.lar_df[(self.lar_df.loan_term.map(lambda x: self.check_number(x, min_val=0))==False)&
			(~self.lar_df.loan_term.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v682_2(self):
		"""An invalid Loan Term was reported.
		2) If Reverse Mortgage equals 1, then Loan Term must be NA.

		Impact of S2155: Update to: 
		2) If Reverse Mortgage equals 1, then Loan Term must be Exempt or NA."""
		field = "Loan Term"
		edit_name = "v682_2"
		fail_df = self.lar_df[(self.lar_df.reverse_mortgage=="1")&(~self.lar_df.loan_term.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v683(self):
		"""An invalid Introductory Rate Period was reported.
		1) Introductory Rate Period must be either a whole number greater than zero or NA, and cannot be left blank.

		Impact of S2155: Update to: 
		1) Introductory Rate Period must be either a whole number greater than zero, Exempt, or NA, and cannot be left blank."""
		field = "Introductory Rate"
		edit_name = "v683"
		fail_df = self.lar_df[(self.lar_df.intro_rate.map(lambda x: self.check_number(x, min_val=0))==False)&
			(~self.lar_df.intro_rate.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v684(self):
		"""An invalid Balloon Payment was reported.
		1) Balloon Payment must equal 1 or 2, and cannot be left blank.

		Impact of S2155: Update to: 
		1) Balloon Payment must equal 1111, 1 or 2, and cannot be left blank."""
		field = "Balloon Payment"
		edit_name = "v684"
		fail_df = self.lar_df[~(self.lar_df.balloon.isin(("1111", "1", "2")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v685(self):
		"""An invalid Interest Only Payments was reported.
		1) Interest Only Payments must equal 1 or 2, and cannot be left blank.

		Impact of S2155: Update to: 
		1) Interest Only Payments must equal 1111, 1 or 2, and cannot be left blank."""
		field = "Interest Only Payments"
		edit_name = "v685"
		fail_df = self.lar_df[(~self.lar_df.int_only_pmts.isin(("1111", "1", "2")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v686(self):
		"""An invalid Negative Amortization was reported.
		1) Negative Amortization must equal 1 or 2, and cannot be left blank.

		Impact of S2155: Update to: 
		1) Negative Amortization must equal 1111, 1 or 2, and cannot be left blank."""
		field = "Negative Amortization"
		edit_name = "v686"
		fail_df = self.lar_df[~(self.lar_df.neg_amort.isin(("1111", "1", "2")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v687(self):
		"""An invalid Other Non-amortizing Features was reported.
		1) Other Non-amortizing Features must equal 1 or 2, and cannot be left blank.

		Impact of S2155: Update to: 
		1) Other Non-amortizing Features must equal 1111, 1 or 2, and cannot be left blank."""
		field = "Non-amortizing Features"
		edit_name = "v687"
		fail_df = self.lar_df[~(self.lar_df.non_amort_features.isin(("1111", "1", "2")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v688_1(self):
		"""An invalid Property Value was reported.
		1) Property Value must be either a number greater than 0 or NA, and cannot be left blank.

		Impact of S2155: Update to: 
		1) Property Value must be either a number greater than 0, Exempt, or NA, and cannot be left blank."""
		field = "Property Value"
		edit_name = "v688_1"
		fail_df = self.lar_df[(self.lar_df.property_value.map(lambda x: self.check_number(x, min_val=0)==False))&
			(~self.lar_df.property_value.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v688_2(self):
		"""An invalid Property Value was reported.
		2) If Action Taken equals 4 or 5, then Property Value must be NA.

		Impact of S2155: Update to: 
		2) If Action Taken equals 4 or 5, then Property Value must be Exempt or NA."""
		field = "Property Value"
		edit_name = "v688_2"
		fail_df = self.lar_df[(self.lar_df.action_taken.isin(("4", "5")))&
			(~self.lar_df.property_value.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v689_1(self):
		"""An invalid Manufactured Home Secured Property Type was reported.
		1) Manufactured Home Secured Property Type must equal 1, 2 or 3, and cannot be left blank.

		Impact of S2155: Update to: 
		1) Manufactured Home Secured Property Type must equal 1111, 1, 2 or 3, and cannot be left blank. """
		field = "Manufactured Property Type"
		edit_name = "v689_1"
		fail_df = self.lar_df[~(self.lar_df.manufactured_type.isin(("1111", "1", "2", "3")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v689_2(self):
		"""An invalid Manufactured Home Secured Property Type was reported.
		2) If Multifamily Affordable Units is a number, then Manufactured Home Secured Property Type must equal 3.

		Impact of S2155: Update to: 
		2) If Multifamily Affordable Units is a number, then Manufactured Home Secured Property Type must equal 1111 or 3. """
		field = "Manufactured Property Type"
		edit_name = "v689_2"
		fail_df = self.lar_df[(self.lar_df.affordable_units.map(lambda x: x.isdigit())==True)&
			(~self.lar_df.manufactured_type.isin(["1111", "3"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v689_3(self):
		"""An invalid Manufactured Home Secured Property Type was reported.
		3) If Construction Method equals 1, then Manufactured Home Secured Property Type must equal 3.

		Impact of S2155: Update to: 
		3) If Construction Method equals 1, then Manufactured Home Secured Property Type must equal 1111 or 3."""
		field = "Manufactured Property Type"
		edit_name = "v689_3"
		fail_df = self.lar_df[(self.lar_df.const_method=="1")&(~self.lar_df.manufactured_type.isin(["3", "1111"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v690_1(self):
		"""An invalid Manufactured Home Land Property Interest was reported.
		1) Manufactured Home Land Property Interest must equal 1, 2, 3, 4, or 5, and cannot be left blank.

		Impact of S2155: Update to: 
		1) Manufactured Home Land Property Interest must equal 1111, 1, 2, 3, 4, or 5, and cannot be left blank. """

		field = "Manufactured Land Interest"
		edit_name = "v690_1"
		fail_df = self.lar_df[~(self.lar_df.manufactured_interest.isin(("1111", "1", "2", "3", "4", "5")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v690_2(self):
		"""An invalid Manufactured Home Land Property Interest was reported.
		2 If Multifamily Affordable Units is a number, then Manufactured Home Land Property Interest must equal 5.

		Impact of S2155: Update to: 
		2) If Multifamily Affordable Units is a number, then Manufactured Home Land Property Interest must equal 1111 or 5. """
		field = "Manufactured Land Interest"
		edit_name = "v690_2"
		fail_df = self.lar_df[(self.lar_df.affordable_units.map(lambda x: x.isdigit())==True)&
			(~self.lar_df.manufactured_interest.isin(["5", "1111"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v690_3(self):
		"""An invalid Manufactured Home Land Property Interest was reported.
		3) If Construction Method equals 1, then Manufactured Home Land Property Interest must equal 5.

		Impact of S2155: Update to: 
		3) If Construction Method equals 1, then Manufactured Home Land Property Interest must equal 1111 or 5."""
		field = "Manufactured Land Interest"
		edit_name = "v690_3"
		fail_df = self.lar_df[(self.lar_df.const_method=="1")&(~self.lar_df.manufactured_interest.isin(["5", "1111"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v691(self):
		"""An invalid Total Units was reported.
		1) Total Units must be a whole number greater than 0, and cannot be left blank."""
		field = "Total Units"
		edit_name = "v691"
		fail_df = self.lar_df[(self.lar_df.total_units.map(lambda x: self.check_number(x, min_val=0))==False)]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v692_1(self):
		"""An invalid Multifamily Affordable Units was reported.
		1) Multifamily Affordable Units must be either a whole number or NA, and cannot be left blank.

		Impact of S2155: Update to: 
		1) Multifamily Affordable Units must be either a whole number, Exempt, or NA, and cannot be left blank."""
		field = "Affordable Units"
		edit_name = "v692_1"
		fail_df = self.lar_df[(self.lar_df.affordable_units.map(lambda x: self.check_number(x))==False)&
			(~self.lar_df.affordable_units.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v692_2(self):
		"""An invalid Multifamily Affordable Units was reported.
		2) If Total Units is less than 5, then Multifamily Affordable Units must be NA.

		Impact of S2155: Update to:
		2) If Total Units is less than 5, then Multifamily Affordable Units must be Exempt or NA. """
		field = "Affordable Units"
		edit_name = "v692_2"
		fail_df = self.lar_df[(self.lar_df.total_units.map(lambda x: int(x)<5))&(~self.lar_df.affordable_units.isin(["NA", "Exempt"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v692_3(self):
		"""An invalid Multifamily Affordable Units was reported.
		3) If Total Units is greater than or equal to 5, then Multifamily Affordable Units must be less than or equal to Total Units.

		Impact of S2155: Update to: 
		3) If Total Units is greater than or equal to 5, then Multifamily Affordable Units must be 
		less than or equal to Total Units, Exempt or NA """
		field = "Affordable Units"
		edit_name = "v692_3"
		fields = ["affordable_units", "total_units"]
		#fail_df = self.lar_df[(self.lar_df.apply(lambda x: self.compare_nums(x, fields=fields), axis=1)==True)&
		#	(~self.lar_df.affordable_units.isin(["NA", "Exempt"]))]
		fail_df = self.lar_df[~self.lar_df.affordable_units.isin(["Exempt", "NA"])]
		fail_df = fail_df[fail_df.apply(lambda x: self.compare_nums(x, fields=fields), axis=1)==True]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v693_1(self):
		"""An invalid Application Channel data field was reported.
		1) Submission of Application must equal 1, 2 or 3, and cannot be left blank.

		Impact of S2155: Update to: 
		1) Submission of Application must equal 1111, 1, 2 or 3, and cannot be left blank. """
		field = "Applicaiton Submission"
		edit_name = "v693_1"
		fail_df = self.lar_df[~(self.lar_df.app_submission.isin(("1111", "1", "2", "3")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v693_2(self):
		"""An invalid Application Channel data field was reported.
		2) If Action Taken equals 6, then Submission of Application must equal 3, and the reverse must be true.

		Impact of S2155: Update to: 
		2) If Action Taken equals 6, then Submission of Application must equal 1111 or 3."""
		field = "Applicaiton Channel"
		edit_name = "v693_2"
		fail_df = self.lar_df[((self.lar_df.action_taken=="6")&(~self.lar_df.app_submission.isin(["3", "1111"])))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v693_3(self):
		"""
		Impact of S2155: Update to: 
		3) If Submission of Application equals 3, then Action Taken must equal 6."""
		field = "Application Channel"
		edit_name = "v693_3"
		fail_df = self.lar_df[((self.lar_df.app_submission=="3")&(self.lar_df.action_taken!="6"))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v694_1(self):
		"""An invalid Application Channel data field was reported.
		1) Initially Payable to Your Institution must equal 1, 2 or 3, and cannot be left blank.

		Impact of S2155: Update to: 
		1) Initially Payable to Your Institution must equal 1111, 1, 2 or 3, and cannot be left blank. """
		field = "initially_payable"
		edit_name = "v694_1"
		fail_df = self.lar_df[~(self.lar_df.initially_payable.isin(("1111", "1", "2", "3")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v694_2(self):
		"""An invalid Application Channel data field was reported.
		2) If Action Taken equals 6, then Initially Payable to Your Institution must equal 3.

		Impact of S2155: Update to: 
		2) If Action Taken equals 6, then Initially Payable to Your Institution must equal 1111 or 3. """
		field = "initially_payable"
		edit_name = "v694_2"
		fail_df = self.lar_df[(self.lar_df.action_taken=="6")&(~self.lar_df.initially_payable.isin(["1111", "3"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v694_3(self):
		"""An invalid Application Channel data field was reported.
		3) If Action Taken equals 1, then Initially Payable to Your Institution must equal 1 or 2.

		Impact of S2155: Update to: 
		3) If Action Taken equals 1, then Initially Payable to Your Institution must equal 1111, 1 or 2."""
		field = "initially_payable"
		edit_name = "v694_3"
		fail_df = self.lar_df[(self.lar_df.action_taken=="1")&(~self.lar_df.initially_payable.isin(("1111", "1", "2")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v695(self):
		"""An invalid NMLSR Identifier was reported.
		1) NMLSR Identifier cannot be left blank."""
		field = "NMLS ID"
		edit_name = "v695"
		fail_df = self.lar_df[(self.lar_df.mlo_id=="")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v696_1(self):
		"""An invalid Automated Underwriting System data field was reported.
		1) Automated Underwriting System: 1 must equal 1, 2, 3, 4, 5, or 6, and cannot be left blank.
		Automated Underwriting System: 2; Automated Underwriting System: 3; Automated Underwriting System: 4;
		and Automated Underwriting System: 5 must equal 1, 2, 3, 4, 5, or be left blank.


		Impact of S2155: Update to: 
		1) Automated Underwriting System: 1 must equal 1111, 1, 2, 3, 4, 5, or 6, and cannot be left blank. Automated Underwriting System: 2; 
		Automated Underwriting System: 3; Automated Underwriting System: 4; and Automated Underwriting System: 5 
		must equal 1, 2, 3, 4, 5, or be left blank. 

	
"""
		field = "AUS 1-5"
		edit_name = "v696_1"
		fail_df = self.lar_df[~(self.lar_df.aus_1.isin(("1111", "1", "2", "3", "4", "5", "6")))|
			(~self.lar_df.aus_2.isin(("1", "2", "3", "4", "5","")))|(~self.lar_df.aus_3.isin(("1", "2", "3", "4", "5","")))|
			(~self.lar_df.aus_4.isin(("1", "2", "3", "4", "5","")))|(~self.lar_df.aus_5.isin(("1", "2", "3", "4", "5","")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v696_2(self):
		"""An invalid Automated Underwriting System data field was reported.
		2) Automated Underwriting System Result: 1 must equal 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, or 17,
		and cannot be left blank.
		Automated Underwriting System Result: 2; Automated Underwriting System Result: 3;
		Automated Underwriting System Result: 4; and Automated Underwriting System Result: 5
		must equal 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, or be left blank.

		Impact of S2155: Update to: 
		2) Automated Underwriting System Result: 1 must equal 1111, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, or 17, 
		and cannot be left blank. 
		Automated Underwriting System Result: 2; Automated Underwriting System Result: 3; Automated Underwriting System Result: 4; 
		and Automated Underwriting System Result: 5 must equal 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, or be left blank. """
		field = "AUS 1-5 Result"
		edit_name = "v696_2"
		aus_1_results = ["1111", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17"]
		aus_n_results = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", ""]
		fail_df = self.lar_df[~(self.lar_df.aus_result_1.isin(aus_1_results))|(~self.lar_df.aus_result_2.isin(aus_n_results))|(~self.lar_df.aus_result_3.isin(aus_n_results))
		|(~self.lar_df.aus_result_4.isin(aus_n_results))|(~self.lar_df.aus_result_5.isin(aus_n_results))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v696_3(self):
		"""An invalid Automated Underwriting System data field was reported.
		3) The number of reported Automated Underwriting Systems must equal the number of reported Automated Underwriting System Results."""
		field = "AUS Systems and Results"
		edit_name = "v696_3"
		fields_1 = ["aus_1", "aus_2", "aus_3", "aus_4", "aus_5"]
		fields_2 = ["aus_result_1", "aus_result_2", "aus_result_3", "aus_result_4", "aus_result_5"]
		vals_1 = ("1", "2", "3", "4", "5")
		vals_2 = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16")
		fail_df = self.lar_df[(self.lar_df.apply(lambda x: self.check_counts(x, fields_1=fields_1, fields_2=fields_2, vals_1=vals_1, 
			vals_2=vals_2),axis=1)==False)]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v697(self):
		"""An invalid Automated Underwriting System data field was reported.
		1) If Automated Underwriting System: 1, Automated Underwriting System: 2;
		Automated Underwriting System: 3; Automated Underwriting System: 4; or Automated Underwriting System: 5 equals 1,
		then the corresponding Automated Underwriting System Result: 1; Automated Underwriting System Result: 2;
		Automated Underwriting System Result: 3; Automated Underwriting System Result: 4; or
		Automated Underwriting System Result: 5 must equal 1, 2, 3, 4, 5, 6, or 7."""
		field = "AUS and Results"
		edit_name = "v697"
		aus_results = ("1", "2", "3", "4", "5", "6", "7")
		fail_df = self.lar_df[((self.lar_df.aus_1=="1")&(~self.lar_df.aus_result_1.isin(aus_results)))|
			((self.lar_df.aus_2=="1")&(~self.lar_df.aus_result_2.isin(aus_results)))|
			((self.lar_df.aus_3=="1")&(~self.lar_df.aus_result_3.isin(aus_results)))|
			((self.lar_df.aus_4=="1")&(~self.lar_df.aus_result_4.isin(aus_results)))|
			((self.lar_df.aus_5=="1")&(~self.lar_df.aus_result_5.isin(aus_results)))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v698(self):
		"""An invalid Automated Underwriting System data field was reported.
		1) If Automated Underwriting System: 1; Automated Underwriting System: 2; Automated Underwriting System: 3;
		Automated Underwriting System: 4; or Automated Underwriting System: 5 equals 2,
		then the corresponding Automated Underwriting System Result: 1; Automated Underwriting System Result: 2;
		Automated Underwriting System Result: 3; Automated Underwriting System Result: 4; or Automated Underwriting System Result: 5
		must equal 8, 9, 10, 11, or 12."""
		field = "AUS and Results"
		edit_name = "v698"
		aus_results = ("8", "9", "10", "11", "12")
		fail_df = self.lar_df[((self.lar_df.aus_1=="2")&(~self.lar_df.aus_result_1.isin(aus_results)))|
			((self.lar_df.aus_2=="2")&(~self.lar_df.aus_result_2.isin(aus_results)))|
			((self.lar_df.aus_3=="2")&(~self.lar_df.aus_result_3.isin(aus_results)))|
			((self.lar_df.aus_4=="2")&(~self.lar_df.aus_result_4.isin(aus_results)))|
			((self.lar_df.aus_5=="2")&(~self.lar_df.aus_result_5.isin(aus_results)))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v699(self):
		"""An invalid Automated Underwriting System data field was reported.
		1) If Automated Underwriting System: 1; Automated Underwriting System: 2; Automated Underwriting System: 3;
		Automated Underwriting System: 4; or Automated Underwriting System: 5 equals 5,
		then the corresponding Automated Underwriting System Result: 1; Automated Underwriting System Result: 2;
		Automated Underwriting System Result: 3; Automated Underwriting System Result: 4; or Automated Underwriting System Result: 5
		must equal 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, or 16."""
		field = "AUS and Results"
		edit_name = "v699"
		aus_results = ("1","2","3", "4", "5", "6", "7", "8", "9", "10", "11", "12","13", "14","15", "16")
		fail_df = self.lar_df[((self.lar_df.aus_1=="5")&(~self.lar_df.aus_result_1.isin(aus_results)))|
			((self.lar_df.aus_2=="5")&(~self.lar_df.aus_result_2.isin(aus_results)))|
			((self.lar_df.aus_3=="5")&(~self.lar_df.aus_result_3.isin(aus_results)))|
			((self.lar_df.aus_4=="5")&(~self.lar_df.aus_result_4.isin(aus_results)))|
			((self.lar_df.aus_5=="5")&(~self.lar_df.aus_result_5.isin(aus_results)))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v700_1(self):
		"""An invalid Automated Underwriting System data field was reported.
		1) If Automated Underwriting System: 1 equals 6, then the corresponding Automated Underwriting System Result: 1 must equal 17;
		and the Automated Underwriting System: 2; Automated Underwriting System: 3; Automated Underwriting System: 4;
		Automated Underwriting System: 5; Automated Underwriting System Result: 2; Automated Underwriting System Result: 3;
		Automated Underwriting System Result: 4; and Automated Underwriting System Result: 5 must all be left blank."""
		field = "AUS and Results"
		edit_name = "v700_1"
		fail_df = self.lar_df[(self.lar_df.aus_1=="6")&((self.lar_df.aus_result_1!="17")|(self.lar_df.aus_result_2!="")|(self.lar_df.aus_result_3!="")|
			(self.lar_df.aus_result_4!="")|(self.lar_df.aus_result_5!="")|(self.lar_df.aus_2!="")|(self.lar_df.aus_3!="")|(self.lar_df.aus_3!="")|
			(self.lar_df.aus_4!="")|(self.lar_df.aus_5!=""))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v700_2(self):
		"""An invalid Automated Underwriting System data field was reported.
		2) If Automated Underwriting System Result: 1 equals 17, then the corresponding Automated Underwriting System: 1 must equal 6;
		and the Automated Underwriting System: 2; Automated Underwriting System: 3; Automated Underwriting System: 4;
		Automated Underwriting System: 5; Automated Underwriting System Result: 2; Automated Underwriting System Result: 3;
		Automated Underwriting System Result: 4; and Automated Underwriting System Result: 5 must all be left blank."""
		field = "AUS and Results"
		edit_name = "v700_2"
		fail_df = self.lar_df[(self.lar_df.aus_result_1=="17")&((self.lar_df.aus_1!="6")|(self.lar_df.aus_result_2!="")|(self.lar_df.aus_result_3!="")|
			(self.lar_df.aus_result_4!="")|(self.lar_df.aus_result_5!="")|(self.lar_df.aus_2!="")|(self.lar_df.aus_3!="")|(self.lar_df.aus_3!="")|
			(self.lar_df.aus_4!="")|(self.lar_df.aus_5!=""))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v701(self):
		"""An invalid Automated Underwriting System data field was reported.
		1) If Automated Underwriting System: 2; Automated Underwriting System: 3; Automated Underwriting System: 4;
		or Automated Underwriting System: 5 was left blank, then the corresponding reported Automated Underwriting System Result: 2;
		Automated Underwriting System Result: 3; Automated Underwriting System Result: 4; or Automated Underwriting System Result: 5
		must be left blank."""
		field = "AUS and Results"
		edit_name = "v701"
		fail_df = self.lar_df[((self.lar_df.aus_2=="")&(self.lar_df.aus_result_2!=""))|
			((self.lar_df.aus_3=="")&(self.lar_df.aus_result_3!=""))|
			((self.lar_df.aus_4=="")&(self.lar_df.aus_result_4!=""))|
			((self.lar_df.aus_5=="")&(self.lar_df.aus_result_5!=""))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v702_1(self):
		"""An invalid Automated Underwriting System data field was reported.
		1) Automated Underwriting System: 1; Automated Underwriting System: 2; Automated Underwriting System: 3;
		Automated Underwriting System: 4; or Automated Underwriting System: 5 was reported Code 5: Other.
		However, the Automated Underwriting System: Conditional Free Form Text Field for Code 5 was left blank;"""
		field = "AUS"
		edit_name = "v702_1"
		fail_df = self.lar_df[((self.lar_df.aus_1=="5")|(self.lar_df.aus_2=="5")|(self.lar_df.aus_3=="5")|(self.lar_df.aus_4=="5")|(self.lar_df.aus_5=="5"))&
			(self.lar_df.aus_code_5=="")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v702_2(self):
		"""An invalid Automated Underwriting System data field was reported.
		2) The Automated Underwriting System: Conditional Free Form Text Field for Code 5 was reported,
		but Code 5 was not reported in Automated Underwriting System: 1; Automated Underwriting System: 2;
		Automated Underwriting System: 3; Automated Underwriting System: 4; or Automated Underwriting System: 5."""
		field = "AUS"
		edit_name = "v702_2"
		fail_df = self.lar_df[((self.lar_df.aus_1!="5")&(self.lar_df.aus_2!="5")&(self.lar_df.aus_3!="5")&(self.lar_df.aus_4!="5")&(self.lar_df.aus_5!="5"))&
			(self.lar_df.aus_code_5!="")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v703_1(self):
		"""An invalid Automated Underwriting System Result data field was reported.
		1) Automated Underwriting System Result: 1; Automated Underwriting System Result: 2; Automated Underwriting System Result: 3;
		Automated Underwriting System Result: 4; or Automated Underwriting System Result: 5 was reported Code 16: Other.
		However, the Automated Underwriting System Result: Conditional Free Form Text Field for Code 16 was left blank;"""
		field = "AUS Results"
		edit_name = "v703_1"
		fail_df = self.lar_df[((self.lar_df.aus_result_1=="16")|(self.lar_df.aus_result_2=="16")|(self.lar_df.aus_result_3=="16")|
			(self.lar_df.aus_result_4=="16")|(self.lar_df.aus_result_5=="16"))&(self.lar_df.aus_code_16=="")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v703_2(self):
		"""An invalid Automated Underwriting System Result data field was reported.
		2) The Automated Underwriting System Result: Conditional Free Form Text Field for Code 16 was reported,
		but Code 16 was not reported in Automated Underwriting System Result: 1; Automated Underwriting System Result: 2;
		Automated Underwriting System Result: 3; Automated Underwriting System Result: 4; or Automated Underwriting System Result: 5."""
		field = "AUS Results"
		edit_name = "v703_2"
		fail_df = self.lar_df[(self.lar_df.aus_code_16!="")&((self.lar_df.aus_result_1!="16")&(self.lar_df.aus_result_2!="16")&
			(self.lar_df.aus_result_3!="16")&(self.lar_df.aus_result_4!="16")&(self.lar_df.aus_result_5!="16"))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v704_1(self):
		"""An invalid Automated Underwriting System data field was reported.
		1) If Action Taken equals 6, then Automated Underwriting System: 1 must equal 6.

		Impact of S2155: Update to: 
		1) If Action Taken equals 6, then Automated Underwriting System: 1 must equal 1111 or 6. """
		field = "AUS"
		edit_name = "v704_1"
		fail_df = self.lar_df[(self.lar_df.action_taken=="6")&(~self.lar_df.aus_1.isin(["6", "1111"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v704_2(self):
		"""An invalid Automated Underwriting System data field was reported.
		2) If Action Taken equals 6, then Automated Underwriting System Result: 1 must equal 17.

		Impact of S2155: Update to: 
		2) If Action Taken equals 6, then Automated Underwriting System Result: 1 must equal 1111 or 17."""
		field = "AUS Result"
		edit_name = "v704_2"
		fail_df = self.lar_df[(self.lar_df.action_taken=="6")&(~self.lar_df.aus_result_1.isin(["17", "1111"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v705_1(self):
		"""An invalid Automated Underwriting System data field was reported.
		1) If Ethnicity of Applicant or Borrower: 1 equals 4; and Race of Applicant or Borrower: 1 equals 7;
		and Sex of Applicant or Borrower: 1 equals 4 indicating the applicant is a non-natural person; and
		the Ethnicity of Co-Applicant or Co-Borrower: 1 equals 5; and Race of Co-Applicant or Co-Borrower: 1 equals 8;
		and Sex of Co-Applicant or Co-Borrower: 1 equals 5 indicating that there is no co-applicant or co- borrower,
		then Automated Underwriting System: 1 must equal 6; and Automated Underwriting System Result: 1 must equal 17.


		Impact of S2155: Update to: 
		1) If Ethnicity of Applicant or Borrower: 1 equals 4; and Race of Applicant or Borrower: 1 equals 7; 
		and Sex of Applicant or Borrower: 1 equals 4 indicating the applicant is a non-natural person; 
		and the Ethnicity of Co-Applicant or Co-Borrower: 1 equals 5; and Race of Co-Applicant or Co-Borrower: 1 equals 8; 
		and Sex of Co-Applicant or Co-Borrower: 1 equals 5 indicating that there is no co-applicant or co-borrower, 
		then Automated Underwriting System: 1 must equal 1111 or 6; 
		and Automated Underwriting System Result: 1 must equal 1111 or 17. """
		field = "AUS and Results"
		edit_name = "v705_1"
		fail_df = self.lar_df[((self.lar_df.app_eth_1=="4")&(self.lar_df.app_race_1=="7")&(self.lar_df.app_sex=="4"))&
			((self.lar_df.co_app_eth_1=="5")&(self.lar_df.co_app_race_1=="8")&(self.lar_df.co_app_sex=="5"))&
			((~self.lar_df.aus_1.isin(["1111","6"]))|(~self.lar_df.aus_result_1.isin(["17", "1111"])))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v705_2(self):
		"""An invalid Automated Underwriting System data field was reported.
		2) If the Ethnicity of Applicant or Borrower: 1 equals 4; and Race of Applicant or Borrower: 1 equals 7;
		and Sex of Applicant or Borrower: 1 equals 4 indicating the applicant or borrower is a non-natural person;
		and Ethnicity of Co-Applicant or Co- Borrower: 1 equals 4; and Race of Co-Applicant or Co-Borrower: 1 equals 7;
		and Sex of Co-Applicant or Co-Borrower: 1 equals 4 indicating that the co- applicant or co-borrower is also a non-natural person,
		then Automated Underwriting System: 1 must equal 6; and aus result 1 must equal 17

		Impact of S2155: Update to: 
		2) If the Ethnicity of Applicant or Borrower: 1 equals 4; and Race of Applicant or Borrower: 1 equals 7; 
		and Sex of Applicant or Borrower: 1 equals 4 indicating the applicant or borrower is a non-natural person; 
		and Ethnicity of Co-Applicant or Co-Borrower: 1 equals 4; and Race of Co-Applicant or Co-Borrower: 1 equals 7; 
		and Sex of Co-Applicant or Co-Borrower: 1 equals 4 indicating that the co-applicant or co-borrower is also a non-natural person, 
		then Automated Underwriting System: 1 must equal 1111 or 6; and Automated Underwriting System Result: 1 must equal 1111 or 17."""
		field = "AUS and Results"
		edit_name = "v705_2"
		fail_df = self.lar_df[((self.lar_df.app_eth_1=="4")&(self.lar_df.app_race_1=="7")&(self.lar_df.app_sex=="4"))&
			((self.lar_df.co_app_eth_1=="4")&(self.lar_df.co_app_race_1=="7")&(self.lar_df.co_app_sex=="4"))&
			((~self.lar_df.aus_1.isin(["6", "1111"]))|(~self.lar_df.aus_result_1.isin(["17","1111"])))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v706(self):
		"""An invalid Reverse Mortgage was reported.
		1) Reverse Mortgage must equal 1 or 2, and cannot be left blank.

		Impact of S2155: Update to: 
		1) Reverse Mortgage must equal 1111, 1 or 2, and cannot be left blank."""
		field = "Reverse Mortgage"
		edit_name = "v706"
		fail_df = self.lar_df[~(self.lar_df.reverse_mortgage.isin(("1111", "1", "2")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v707(self):
		"""An invalid Open-End Line of Credit was reported.
		1) Open-End Line of Credit must equal 1 or 2, and cannot be left blank.

		Impact of S2155: Update to: 
		1) Open-End Line of Credit must equal 1111, 1, or 2, and cannot be left blank."""
		field = "Open End Credit"
		edit_name = "v707"
		fail_df = self.lar_df[~(self.lar_df.open_end_credit.isin(("1111", "1", "2")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v708(self):
		"""An invalid Business or Commercial Purpose was reported.
		1) Business or Commercial Purpose must equal 1 or 2, and cannot be left blank.

		Impact of S2155: Update to: 
		1) Business or Commercial Purpose must equal 1111, 1 or 2, and cannot be left blank."""
		field = "Business Purpose"
		edit_name = "v708"
		fail_df = self.lar_df[~(self.lar_df.business_purpose.isin(("1111", "1", "2")))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v709(self):
		"""An invalid Property Address was reported. Please
		review the information below and update your file
		accordingly.
		1) If Street Address, City, and Zip Code is reported
		Exempt, then all three must be reported Exempt. """

		field = "Property Address"
		edit_name = "v709"
		fail_df = self.lar_df[((self.lar_df.street_address=="Exempt")&(self.lar_df.city=="Exempt")&(self.lar_df.zip_code == "Exempt"))&
			((~self.lar_df.street_address=="Exempt") & (~self.lar_df.city =="Exempt") & (~self.lar_df.zip_code== "Exempt"))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v710_1(self):
		"""If the Credit Score exemption election is taken,
			1) Credit Score of Applicant or Borrower, Credit
			Score of Co-Applicant or Co-Borrower, Applicant or
			Borrower, Name and Version of Credit Scoring
			Model, and Co-Applicant or Co-Borrower, Name and
			Version of Credit Scoring Model must be reported
			1111.""" 
		field = "Credit Score"
		edit_name = "v710_1"
		fail_df = self.lar_df[(self.lar_df.app_credit_score=="1111")&((~self.lar_df.co_app_credit_score=="1111")& 
				(~self.lar_df.app_score_name=="1111")&(~self.lar_df.co_app_score_name=="1111"))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)
	
	def v710_2(self):
		"""If the Credit Score exemption election is taken,
			2) Applicant or Borrower, Name and Version of
				Credit Scoring Model: Conditional Free Form Text
				Field for Code 8 and Co-Applicant or Co-Borrower,
				Name and Version of Credit Scoring Model:
				Conditional Free Form Text Field for Code 8 must be
				left blank."""
		field = "Credit Score"
		edit_name = "v710_2"
		fail_df = self.lar_df[(self.lar_df.app_credit_score=="1111")&((~self.lar_df.app_score_name=="")& 
				(~self.lar_df.app_score_code_8=="")&(~self.lar_df.co_app_score_name=="")&(~self.lar_df.co_app_score_code_8==""))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v711_1(self):
		"""1) If the Reason for Denial exemption election is
			taken, Reason for Denial: 1 must be reported 1111;"""
		field = "Reason for Denial"
		edit_name = "v711_1"
		fail_df = self.lar_df[(self.lar_df.denial_1=="1111")&(~self.lar_df.denial_1=="1111")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v711_2(self):
		"""2)If the Reason for Denial exemption election is
			taken, 
			Reason for Denial: 2, Reason for Denial: 3,
			Reason for Denial: 4, and Reason for Denial:
			Conditional Free Form Text Field for Code 9 must be
			left blank."""
		field = "Reason for Denial"
		edit_name = "v711_2"
		fail_df = self.lar_df[(self.lar_df.denial_1=="1111")&((~self.lar_df.denial_2=="")&(~self.lar_df.denial_3=="")
					&(~self.lar_df.denial_4=="")&(~self.lar_df.denial_code_9==""))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v712(self):
		"""1) If the Total Loan Costs or Total Points and Fees
				exemption election is taken, Total Loan Costs and
				Total Points and Fees must be reported Exempt."""
		field = "Total Loan Costs/Points and Fees"
		edit_name = "v712"
		fail_df = self.lar_df[((self.lar_df.loan_costs=="Exempt")|(self.lar_df.points_fees=="Exempt")) & ((~self.lar_df.loan_costs=="Exempt")
					& (~self.lar_df.points_fees=="Exempt"))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)
	def v713_1(self):
		"""If the Automated Underwriting System exemption
			election is taken,
			1) Automated Underwriting System: 1 and
			Automated Underwriting System Result: 1 must be
			reported 1111; and"""
		field = "Automated Underwriting System"
		edit_name = "v713_1"
		fail_df = self.lar_df[(self.lar_df.aus_1=="1111") & ((~self.lar_df.aus_1=="1111") & (~self.lar_df.aus_result_1=="1111"))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)
	
	def v713_2(self):
		"""If the Automated Underwriting System exemption
			election is taken,
			2) Automated Underwriting System: 2, Automated
			Underwriting System: 3, Automated Underwriting
			System: 4, Automated Underwriting System: 5,
			Automated Underwriting System: Conditional Free
			Form Text Field for Code 5, Automated Underwriting
			System Result: 2, Automated Underwriting System
			Result: 3, Automated Underwriting System Result: 4,
			Automated Underwriting System Result: 5, and
			Automated Underwriting System Result: Conditional
			Free Form Text Field for Code 16 must be left blank."""
		field = "Automated Underwriting System"
		edit_name = "v713_2"
		fail_df = self.lar_df[(self.lar_df.aus_1=="1111") & ((~self.lar_df.aus_2=="") & (~self.lar_df.aus_3=="") & (~self.lar_df.aus_4=="") & 
			(~self.lar_df.aus_5=="") & (~self.lar_df.aus_code_5=="") & (~self.lar_df.aus_result_2=="") & (~self.lar_df.aus_result_3=="") 
			& (~self.lar_df.aus_result_4=="") & (~self.lar_df.aus_result_5=="") & (~self.lar_df.aus_code_16==""))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def v714(self):
		"""1) If the Application Channel exemption election is
			taken, Submission of Application and Initially Payable
			to Your Institution must be reported 1111."""
		field = "Application Channel"
		edit_name = "v714"
		fail_df = self.lar_df[(self.lar_df.app_submission=="1111") & ((~self.lar_df.app_submission=="1111") & (~self.lar_df.initially_payable=="1111"))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)
	
	def v715(self):
		"""1) If the Non-Amortizing Features exemption election
			is taken, Balloon Payment, Interest-Only Payments,
			Negative Amortization and Other Non-amortizing
			Features must be reported 1111."""
		field = "Non-Amortizing Features"
		edit_name = "v715"
		fail_df = self.lar_df[(self.lar_df.non_amort_features=="1111") & ((~self.lar_df.balloon=="1111") 
			& (~self.lar_df.int_only_pmts="1111") & (~self.lar_df.neg_amort="1111") & (~self.lar_df.non_amort_features="1111"))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q600(self):
		"""1) A duplicate ULI was reported. """
		field = "ULI"
		edit_name = "q600"
		fail_df = self.lar_df[~(self.lar_df.duplicated(keep=False, subset='uli'))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q601(self):
		"""1) Application Date occurs more than two years prior to Action Taken Date. """
		field = "Application Date"
		edit_name = "q601"
		fail_df = self.lar_df[self.lar_df.app_date!="NA"].copy()
		fail_df = fail_df[(fail_df.app_date.apply(lambda x: int(x[:4])<2016))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q602(self):
		"""Street Address was reported NA, however City, State and Zip Code were provided. """
		field = "Street Address"
		edit_name = "q602"
		fail_df = self.lar_df[(self.lar_df.street_address=="NA")&
			(self.lar_df.city!="NA")&(self.lar_df.state!="NA")&(self.lar_df.zip_code!="NA")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q603(self):
		"""1) The County has a population of greater than 30,000
			according to the most recent decennial census and
			was not reported NA; however Census Tract was reported NA"""
		field = "County/Census Tract"
		edit_name = "q603"
		fail_df = self.lar_df[(self.lar_df.tract=="NA")&(~self.lar_df.county.isin(self.small_counties))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q604(self):
		"""The reported State and County are not a valid combination. 
		If neither State nor County were reported NA, then the County must be located within the State."""
		field = "State/County"
		edit_name = "q604"
		self.lar_df['fail_flag'] = "" #set flag to filter lar_df by fail rows
		#iterate over lar to match state code with list of counties inside the state
		for index, row in self.lar_df.iterrows():
			county_list = list(self.cbsa_data.countyFips[self.cbsa_data.stateCode==row["state"]])
			if row["county"] not in county_list:
				self.lar_df.at[index,'fail_flag'] = "1"
		fail_df = self.lar_df[(self.lar_df.fail_flag=="1")]
		fail_df.drop("fail_flag", inplace=True, axis=1)
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q605_1(self):
		"""If Type of Purchaser equals 1 or 3, then Loan Type generally should equal 1."""
		field = "Purchaser Type"
		edit_name = "q605_1"
		fail_df = self.lar_df[(self.lar_df.purchaser_type.isin(["1","3"]))&(self.lar_df.loan_type!="1")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q605_2(self):
		"""If Type of Purchaser equals 2, then Loan Type generally should equal 2, 3 or 4."""
		field = "Purhaser Type"
		edit_name = "q605_2"
		fail_df = self.lar_df[(self.lar_df.purchaser_type=="2")&(~self.lar_df.loan_type.isin(["2", "3", "4"]))].copy()
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q606(self):
		"""If Income is a number, then it generally should be less than $3 million (entered as 3000)."""
		field = "Income"
		edit_name = "q606"
		fail_df = self.lar_df[(self.lar_df.income!="NA")].copy()
		fail_df = fail_df[(fail_df.income.apply(lambda x: int(x)>=3000))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q607(self):
		"""If Lien Status equals 2, 
		then Loan Amount generally should be less than or equal to $250 thousand (entered as 250000)."""
		field = "Loan Amount/Lien Status"
		edit_name = "q607"
		fail_df = self.lar_df[(self.lar_df.loan_amount!="NA")].copy()
		fail_df = fail_df[(fail_df.lien=="2")&(fail_df.loan_amount.apply(lambda x: int(x)>250))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q608(self):
		"""If Action Taken equals 1, then the Action Taken Date generally should occur after the Application Date."""
		field = "Action Taken/Action Taken Date/Application Date"
		edit_name = "q608"
		fail_df = self.lar_df[(self.lar_df.action_taken=="1")&(self.lar_df.action_date<self.lar_df.app_date)]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q609(self):
		"""If Type of Purchaser equals 1, 2, 3 or 4, 
		then Rate Spread generally should be less than or equal to 10% or be NA.

		Impact of S2155: Update to: 
		1) If Type of Purchaser equals 1, 2, 3 or 4, 
		then Rate Spread generally should be less than or equal to 10%, Exempt, or NA."""
		field = "Purchaser Type/Rate Spread"
		edit_name = "q609"
		fail_df = self.lar_df[(~self.lar_df.rate_spread.isin(["NA", "Exempt",""]))].copy()
		fail_df = fail_df[fail_df.purchaser_type.isin(["1","2","3","4"])&(fail_df.rate_spread.apply(lambda x: float(x)>10))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)	

	def q610(self):
		"""If Action Taken equals 1, Lien Status equals 1, and Rate Spread is greater than 6.5%, 
		then HOEPA Status generally should be 1."""
		field = "Action Taken/Lien Status/Rate Spread/HOEPA Status"
		edit_name = "q610"
		fail_df = self.lar_df[~self.lar_df.rate_spread.isin(["NA", "Exempt", ""])].copy()
		fail_df = fail_df[(fail_df.action_taken=="1")&(fail_df.lien=="1")&
			(fail_df.rate_spread.apply(lambda x: float(x)>6.5))&(fail_df.hoepa!="1")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q611(self):
		"""If Action Taken equals 1, Lien Status equals 2, and Rate Spread is greater than 8.5%, 
		then HOEPA Status generally should be 1."""	
		field = "Action Taken/Lien Status/Rate Spread/HOEPA Status"
		edit_name = "q611"
		fail_df = self.lar_df[~self.lar_df.rate_spread.isin(["NA", "Exempt", ""])]
		fail_df = fail_df[(fail_df.action_taken=="1")&(fail_df.lien=="2")&(fail_df.hoepa!="1")&
			(fail_df.rate_spread.apply(lambda x: float(x)>8.5))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q612(self):
		"""If Type of Purchaser equals 1 or 3, then HOEPA Status generally should be 2 or 3."""
		field = "Type of Purchaser/HOEPA Status"
		edit_name = "q612"
		fail_df = self.lar_df[(self.lar_df.purchaser_type.isin(["1", "3"]))&(~self.lar_df.hoepa.isin(["2","3'"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)
		
	def q613(self):
		"""If Business or Commercial Purpose equals 1, then Loan Purpose generally should equal 1, 2, 31, 32, or 5."""
		field = "Business or Commercial Purpose/Loan Purpose"
		edit_name = "q613"
		fail_df = self.lar_df[(self.lar_df.business_purpose=="1")&(~self.lar_df.loan_purpose.isin(["1","2","31","32","5"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q614(self):
		"""The Age of Applicant or Borrower generally should be between 18 and 100 
		unless the Age of Applicant or Borrower is reported 8888 indicating NA. 
		Your data indicates a number outside of this range."""
		field = "Age of Applicant or Borrower"
		edit_name = "q614"
		fail_df = self.lar_df[self.lar_df.app_age!="NA"].copy()
		fail_df = fail_df[~(fail_df.app_age.apply(lambda x: 17 <= int(x) <= 101))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q615_1(self):
		"""If Total Loan Costs and Origination Charges are not reported NA, 
		then Total Loan Costs generally should be greater than Origination Charges.

		Impact of S2155: Update to: 
		1) If Total Loan Costs and Origination Charges are not reported Exempt or NA, 
		then Total Loan Costs generally should be greater than Origination Charges. """
		field = "Origination Charges/Total Loan Costs/Total Points and Fees"
		edit_name = "q615_1"
		fail_df = self.lar_df[(~self.lar_df.origination_fee.isin(["NA", "Exempt"]))&(~self.lar_df.loan_costs.isin(["NA", "Exempt"]))].copy()
		fail_df = fail_df[(fail_df.loan_costs<fail_df.origination_fee)]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q615_2(self):
		"""If Total Points and Fees and Origination Charges are not reported NA, 
		then Total Points and Fees generally should be greater than Origination Charges.

		Impact of S2155: Update to: 
		2) If Total Points and Fees and Origination Charges are not reported Exempt or NA, 
		then Total Points and Fees generally should be greater than Origination Charges."""
		field = "Origination Charges/Total Loan Costs/Total Points and Fees"
		edit_name = "q615_2"
		fail_df = self.lar_df[(~self.lar_df.origination_fee.isin(["NA", "Exempt", ""]))&(~self.lar_df.points_fees.isin(["NA", "Exempt"]))]
		fail_df.origination_fee = fail_df.origination_fee.apply(lambda x: float(x))
		fail_df.points_fees = fail_df.points_fees.apply(lambda x: float(x))
		fail_df = fail_df[fail_df.points_fees < fail_df.origination_fee]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q616_1(self):
		"""If Total Loan Costs and Discount Points are not reported NA, 
		then Total Loan Costs generally should be greater than Discount Points.

		Impact of S2155: Update to: 
		1) If Total Loan Costs and Discount Points are not reported Exempt or NA, 
		then Total Loan Costs generally should be greater than Discount Points."""
		field = "Discount Points; Total Loan Costs; Total Points and Fees"
		edit_name = "q616_1"
		fail_df = self.lar_df[(~self.lar_df.loan_costs.isin(["NA", "Exempt"]))&(~self.lar_df.discount_points.isin(["NA", "Exempt"]))].copy()
		fail_df.loan_costs = fail_df.loan_costs.apply(lambda x: float(x))
		fail_df.discount_points = fail_df.discount_points.apply(lambda x: float(x))
		fail_df = fail_df[(fail_df.loan_costs<fail_df.discount_points)]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q616_2(self):
		"""If Total Points and Fees and Discount Points are not
		reported NA, then Total Points and Fees generally 
		should be greater than Discount Points.

		Impact of S2155: Update to: 
		2) If Total Points and Fees and Discount Points are not reported Exempt or NA, 
		then Total Points and Fees generally should be greater than Discount Points."""
		field = "Discount Points; Total Loan Costs; Total Points and Fees"
		edit_name = "q616_2"
		fail_df = self.lar_df[(~self.lar_df.points_fees.isin(["Exempt", "NA"]))&(~self.lar_df.discount_points.isin(["NA", "Exempt"]))]
		fail_df.points_fees = fail_df.points_fees.apply(lambda x: float(x))
		fail_df.discount_points = fail_df.discount_points.apply(lambda x: float(x))
		fail_df = fail_df[(fail_df.discount_points>fail_df.points_fees)]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)
		
	def q617(self):
		"""If Combined Loan-to-Value Ratio and Property Value are not reported NA, 
		then the Combined Loan-to Value Ratio generally should be greater than or equal to the Loan-to-Value Ratio 
		(calculated as Loan Amount divided by the Property Value).

		Impact of S2155: Update to: 
		1) If Combined Loan-to-Value Ratio and Property Value are not reported Exempt or NA, 
		then the Combined Loan-to Value Ratio generally should be greater than or equal to the Loan-to-Value Ratio 
		(calculated as Loan Amount divided by the Property Value)."""
		field = "Combined Loanto-Value Ratio, Loan Amount, and Property Value"
		edit_name = "q617"
		fail_df = self.lar_df[(~self.lar_df.cltv.isin(["NA", "Exempt", ""]))&(~self.lar_df.property_value.isin(["NA", "Exempt",""]))].copy()
		fail_df.cltv = fail_df.cltv.apply(lambda x: float(x))
		fail_df["ltv"] = (fail_df.loan_amount.apply(lambda x: float(x)) / fail_df.property_value.apply(lambda x: float(x))) *100
		fail_df = fail_df[fail_df.cltv < fail_df.ltv]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q618(self):
		"""If Construction Method equals 2, then Manufactured Home Secured Property Type generally should not be 3."""
		field = "Manufactured Home Secured Property Type"
		edit_name = "q618"
		fail_df = self.lar_df[(self.lar_df.const_method=="2")&(self.lar_df.manufactured_type=="3")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q619(self):
		"""If Construction Method equals 2, then Manufactured Home Land Property Interest generally should not be 5."""
		field = "Construction Method; Manufactured Home Land Property Interest"
		edit_name = "q619"
		fail_df = self.lar_df[(self.lar_df.const_method=="2")&(self.lar_df.manufactured_interest=="5")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q620(self):
		"""If Business or Commercial Purpose equals 2, then NMLSR ID generally should not be NA."""
		field = "Business or Commercial Purpose; NMLSR ID"
		edit_name = "q620"
		fail_df = self.lar_df[(self.lar_df.business_purpose=="2")&(self.lar_df.mlo_id=="NA")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q621(self):
		"""The NMLSR ID should be alphanumeric up to 12 characters. Your data indicates a number outside of this range."""
		field = "NMLSR ID"
		edit_name = "q621"
		invalid_chars = set(string.punctuation)
		fail_df = self.lar_df[(self.lar_df.mlo_id.apply(lambda x: len(x)>12))|
			(self.lar_df.mlo_id.apply(lambda x: any(char in invalid_chars for char in x)==True))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q622(self):
		"""If Reverse Mortgage equals 1, 
		then the Age of Applicant or Borrower generally should be greater than or equal to 62. 
		Your data indicates a number outside this range."""
		field = "Reverse Mortgage; Age of Applicant or Borrower"
		edit_name = "q622"
		fail_df = self.lar_df[(self.lar_df.reverse_mortgage=="1")&(self.lar_df.app_age.apply(lambda x: int(x)<62))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df) 

	def q623(self):
		"""If Total Units is less than or equal to 4, and Income is less than or equal to $200,000 (reported as 200), 
		then Loan Amount generally should be less than $2,000,000 (reported as 2000000)."""
		field = "Loan Amount; Total Units; Income"
		edit_name = "q623"
		#income
		fail_df = self.lar_df[self.lar_df.income!="NA"]
		fail_df = fail_df[(fail_df.total_units.apply(lambda x: int(x)<=4))&
			(fail_df.income.apply(lambda x: int(x) <=200))&
				(fail_df.loan_amount.apply(lambda x: int(x)>=2000000))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q624(self):
		"""If Loan Type equals 2, and Total Units equals 1, 
		then Loan Amount generally should be less than or equal to $637,000 (reported as 637000)."""
		field = "Loan Type; Total Units; Loan Amount"
		edit_name = "q624"
		fail_df = self.lar_df[(self.lar_df.loan_type=="2")&(self.lar_df.total_units=="1")&
			(self.lar_df.loan_amount.apply(lambda x: int(x)>637000))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q625(self):
		"""If Loan Type equals 3, and Total Units is less than or equal to 4, 
		then Loan Amount generally should be less than or equal to $1,050,000 (reported as 1050000)."""
		field = "Loan Type; Total Units; Loan Amount"
		edit_name = "q625"
		fail_df = self.lar_df[(self.lar_df.loan_type=="3")&(self.lar_df.total_units.apply(lambda x: int(x)<=4))&
		(self.lar_df.loan_amount.apply(lambda x: int(x)>1050000))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q626(self):
		"""If Type of Purchaser equals 1, 2, 3, or 4, and Total Units is less than or equal to 4, 
		then Loan Amount generally should be less than or equal to $1,225,000 (reported as 1225000)."""
		field = "Type of Purchaser; Total Units; Loan Amount"
		edit_name = "q626"
		fail_df = self.lar_df[(self.lar_df.purchaser_type.isin(["1","2","3","4"]))&
			(self.lar_df.total_units.apply(lambda x: int(x)<=4))&
			(self.lar_df.loan_amount.apply(lambda x: int(x)>1225000))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q627(self):
		"""If Total Units is greater than or equal to 5, 
		then Loan Amount generally should be between $100,000 (reported as 100000) and $10,000,000 (reported as 10000000)."""
		field = "Total Units; Loan Amount"
		edit_name = "q627"
		fail_df = self.lar_df[(self.lar_df.total_units.apply(lambda x: int(x)>=5))&
			(self.lar_df.loan_amount.apply(lambda x: int(x)<=100000))|
			(self.lar_df.loan_amount.apply(lambda x: int(x)>=10000000))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q628(self):
		"""If Loan Purpose equals 1, and Total Units is less than or equal to 4, 
		then Loan Amount generally should be greater than $10,000 (reported as 10000)."""
		field = "Loan Purpose; Loan Amount; Total Units"
		edit_name = "q628"
		fail_df = self.lar_df[(self.lar_df.loan_purpose=="1")&(self.lar_df.total_units.apply(lambda x: int(x)<=4))&
			(self.lar_df.loan_amount.apply(lambda x: int(x)<=10000))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q629(self):
		"""If Action Taken equals 1, 2, 3, 4, 5, 7, or 8, and Total Units is less than or equal to 4, 
		and Loan Purpose equals 1, 2 or 4, then Income generally should not be NA."""
		field = "Action Taken; Total Units; Loan Purpose; Income"
		edit_name = "q629"
		fail_df = self.lar_df[(self.lar_df.action_taken.isin(["1","2","3","4","5","7","8"]))&
			(self.lar_df.total_units.apply(lambda x: int(x)<=4))&(self.lar_df.loan_purpose.isin(["1","2","4"]))&
			(self.lar_df.income=="NA")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q630(self):
		"""If Total Units is greater than or equal to 5, then HOEPA Status generally should equal 3."""
		field = "Total Units; HOEPA Status"
		edit_name = "q630"
		fail_df = self.lar_df[(self.lar_df.total_units.apply(lambda x: int(x)>=5))&
			(self.lar_df.hoepa!="3")]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q631(self):
		"""If Loan Type equals 2, 3 or 4, then Total Units generally should be less than or equal to 4."""
		field = "Loan Type; Total Units"
		edit_name = "q631"
		fail_df = self.lar_df[(self.lar_df.loan_type.isin(["2","3","4"]))&
			(self.lar_df.total_units.apply(lambda x: int(x)>4))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q632(self):
		"""If Automated Underwriting System: 1; Automated Underwriting System: 2; Automated Underwriting System: 3; 
		Automated Underwriting System: 4; or Automated Underwriting System: 5 equals 3,
		
		then the corresponding Automated Underwriting System Result: 1; Automated Underwriting System Result: 2; 
		Automated Underwriting System Result: 3; Automated Underwriting System Result: 4; 
		or Automated Underwriting System Result: 5 should equal 8 or 13."""
		field = """Automated Underwriting System: 1; Automated Underwriting System: 2; Automated Underwriting System: 3; 
				Automated Underwriting System: 4; Automated Underwriting System: 5; Automated Underwriting System Result: 1; 
				Automated Underwriting System Result: 2; Automated Underwriting System Result: 3; 
				Automated Underwriting System Result: 4; Automated Underwriting System Result: 5"""
		edit_name = "q632"
		fail_df = self.lar_df[
			((self.lar_df.aus_1=="3")&(~self.lar_df.aus_result_1.isin(["8","13"])))|
			((self.lar_df.aus_2=="3")&(~self.lar_df.aus_result_2.isin(["8","13"])))|
			((self.lar_df.aus_3=="3")&(~self.lar_df.aus_result_3.isin(["8","13"])))|
			((self.lar_df.aus_4=="3")&(~self.lar_df.aus_result_4.isin(["8","13"])))|
			((self.lar_df.aus_5=="3")&(~self.lar_df.aus_result_5.isin(["8","13"])))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q633(self):
		"""If Automated Underwriting System: 1; Automated Underwriting System: 2; Automated Underwriting System: 3; 
		Automated Underwriting System: 4; or Automated Underwriting System: 5 equals 4,
		then the corresponding Automated Underwriting System Result: 1; Automated Underwriting System Result: 2; 
		Automated Underwriting System Result: 3; Automated Underwriting System Result: 4; or 
		Automated Underwriting System Result: 5 should equal 5, 8, 10, 13, 14, 15, or 16"""
		field = """Automated Underwriting System: 1; Automated Underwriting System: 2; Automated Underwriting System: 3; 
				Automated Underwriting System: 4; Automated Underwriting System: 5; Automated Underwriting System Result: 1; 
				Automated Underwriting System Result: 2; Automated Underwriting System Result: 3; 
				Automated Underwriting System Result: 4; Automated Underwriting System Result: 5"""
		edit_name = "q633"
		fail_df = self.lar_df[
			((self.lar_df.aus_1=="4")&(~self.lar_df.aus_result_1.isin(["5","8","10","13","14","15","16"])))|
			((self.lar_df.aus_2=="4")&(~self.lar_df.aus_result_2.isin(["5","8","10","13","14","15","16"])))|
			((self.lar_df.aus_3=="4")&(~self.lar_df.aus_result_3.isin(["5","8","10","13","14","15","16"])))|
			((self.lar_df.aus_4=="4")&(~self.lar_df.aus_result_4.isin(["5","8","10","13","14","15","16"])))|
			((self.lar_df.aus_5=="4")&(~self.lar_df.aus_result_5.isin(["5","8","10","13","14","15","16"])))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q634(self):
		"""If more than 25 loans reported Action Taken equals 1 and Loan Purpose equals 1, 
		then the number of these loans should be less than or equal to 95% of the loans reported with Loan Purpose equals 1. 
		Your data indicates a percentage outside of this range."""
		field = "Action Taken; Loan Purpose"
		edit_name = "q634"
		action_1 = len(self.lar_df[(self.lar_df.action_taken=="1")&(self.lar_df.loan_purpose=="1")])
		denom_count = len(self.lar_df)
		if (action_1 * 1.0) / denom_count > .95 and len(self.lar_df)>25:
			fail_df = self.lar_df[(self.lar_df.action_taken=="1")&(self.lar_df.loan_purpose=="1")]
		else:
			fail_df = fail_df = []
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q635(self):
		"""No more than 15% of the loans in the file should report Action Taken equals 2. 
		Your data indicates a percentage outside of this range."""
		field = "Action Taken; Total Number of Entries Contained in Submission"
		edit_name = "q635"
		action_2 = len(self.lar_df[self.lar_df.action_taken=="2"])
		denom_count = len(self.lar_df)
		if (action_2 * 1.0) / denom_count > .15:
			fail_df = self.lar_df[(self.lar_df.action_taken=="2")]
		else:
			fail_df = []
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q636(self):
		"""No more than 30% of the loans in the file should report Action Taken equals 4. 
		Your data indicates a percentage outside of this range."""
		field = "Action Taken; Total Number of Entries Contained in Submission"
		edit_name = "q636"
		action_4 = len(self.lar_df[self.lar_df.action_taken=="4"])
		denom_count = len(self.lar_df)
		if (action_4 * 1.0) / denom_count > .30:
			fail_df = self.lar_df[self.lar_df.action_taken=="4"]
		else:
			fail_df = []
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q637(self):
		"""No more than 15% of the loans in the file should report Action Taken equals 5. 
		Your data indicates a percentage outside of this range."""
		field = "Action Taken; Total Number of Entries Contained in Submission"
		edit_name = "q637"
		action_5 = len(self.lar_df[self.lar_df.action_taken=="5"])
		denom_count = len(self.lar_df)
		if (action_5 * 1.0) / denom_count > .15:
			fail_df = self.lar_df[self.lar_df.action_taken=="5"]
		else:
			fail_df = []
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q638(self):
		"""The number of loans in the file that reported Action Taken equals 1 should be greater than or equal to 20% 
		of the total number of loans that reported Action Taken 1, 2, 3, 4, 5, or 6. 
		Your data indicates a percentage outside of this range."""
		field = "Action Taken"
		edit_name = "q638"
		action_1 = len(self.lar_df[self.lar_df.action_taken=="1"])
		denom_count = len(self.lar_df[self.lar_df.action_taken.isin(["1","2","3","4","5","6"])])
		if (action_1 * 1.0) / denom_count < .20:
			fail_df = self.lar_df[self.lar_df.action_taken.isin(["1","2","3","4","5","6"])]
		else:
			fail_df = []
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q639(self):
		"""If more than 1000 loans were reported with Preapproval equals 1, 
		then there should be at least 1 loan reported with Action Taken equals 7. 
		Your data indicates a number outside of this range."""
		field = "Action Taken; Preapproval"
		edit_name = "q639"
		preapprovals = len(self.lar_df[self.lar_df.preapproval=="1"])
		if preapprovals > 1000 and len(self.lar_df[self.lar_df.action_taken=="7"])<1:
			fail_df = self.lar_df[self.lar_df.preapproval=="1"]
		else:
			fail_df = []
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q640(self):
		"""No more than 20% of the loans in the file should report Income less than $10 thousand (entered as 10). 
		Your file indicates a percentage outside of this range."""
		field = "Income; Total Number of Entries Contained in Submission"
		edit_name = "q640"
		income_less_10k = self.lar_df[self.lar_df.income!="NA"].copy()
		income_less_10k_ct = len(income_less_10k[income_less_10k.income.apply(lambda x: int(x)<10)])
		denom_count = len(self.lar_df)
		if (income_less_10k_ct * 1.0) / denom_count > .20:
			fail_df = income_less_10k
		else:
			fail_df = []
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q642_1(self):
		"""1) If Credit Score of Applicant or Borrower equals 7777 indicating a credit score that is not a number, 
		then Applicant or Borrower, Name and Version of Credit Scoring Model should equal 7 or 8. """
		field = """Credit Score of Applicant or Borrower; Applicant or Borrower, Name and Version of Credit Scoring Model; 
		Credit Score of CoApplicant or CoBorrower; CoApplicant or CoBorrower, Name and Version of Credit Scoring Model"""
		edit_name = "q642_1"
		fail_df = self.lar_df[(self.lar_df.app_credit_score=="7777")&(~self.lar_df.app_score_name.isin(["7","8"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q642_2(self):
		"""If Credit Score of Co-Applicant or Co-Borrower equals 7777 indicating a credit score that is not a number, 
		then Co-Applicant or Co-Borrower, Name and Version of Credit Scoring Model should equal 7 or 8."""
		field = """Credit Score of Applicant or Borrower; Applicant or Borrower, Name and Version of Credit Scoring Model; 
		Credit Score of CoApplicant or CoBorrower; CoApplicant or CoBorrower, Name and Version of Credit Scoring Model"""
		edit_name = "q642_2"
		fail_df = self.lar_df[(self.lar_df.co_app_credit_score=="7777")&(~self.lar_df.co_app_score_name.isin(["7","8"]))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q643(self):
		"""If Automated Underwriting System: 1, Automated Underwriting System: 2; Automated Underwriting System: 3; 
		Automated Underwriting System: 4; or Automated Underwriting System: 5 equals 1,
		then the corresponding Automated Underwriting System Result: 1; Automated Underwriting System Result: 2; 
		Automated Underwriting System Result: 3; Automated Underwriting System Result: 4; or 
		Automated Underwriting System Result: 5 should equal 1, 2, 3, 4, 5, 6, 7, or 15."""
		field = """Automated Underwriting System: 1; Automated Underwriting System: 2; Automated Underwriting System: 3; 
			Automated Underwriting System: 4; Automated Underwriting System: 5; Automated Underwriting System Result: 1; 
			Automated Underwriting System Result: 2; Automated Underwriting System Result: 3; 
			Automated Underwriting System Result: 4; Automated Underwriting System Result: 5"""
		edit_name = "q643"
		fail_df = self.lar_df[
				((self.lar_df.aus_1=="1")&(~self.lar_df.aus_result_1.isin(["1","2","3","4","5","6","7","15"])))|
				((self.lar_df.aus_2=="1")&(~self.lar_df.aus_result_2.isin(["1","2","3","4","5","6","7","15"])))|
				((self.lar_df.aus_3=="1")&(~self.lar_df.aus_result_3.isin(["1","2","3","4","5","6","7","15"])))|
				((self.lar_df.aus_4=="1")&(~self.lar_df.aus_result_4.isin(["1","2","3","4","5","6","7","15"])))|
				((self.lar_df.aus_5=="1")&(~self.lar_df.aus_result_5.isin(["1","2","3","4","5","6","7","15"])))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)

	def q644(self):
		"""If Automated Underwriting System: 1; Automated Underwriting System: 2; Automated Underwriting System: 3; 
		Automated Underwriting System: 4; or Automated Underwriting System: 5 equals 2,
		then the corresponding Automated Underwriting System Result: 1; Automated Underwriting System Result: 2; 
		Automated Underwriting System Result: 3; Automated Underwriting System Result: 4; or 
		Automated Underwriting System Result: 5 should equal 8, 9, 10, 11, or 12."""
		field = """Automated Underwriting System: 1; Automated Underwriting System: 2; Automated Underwriting System: 3; 
			Automated Underwriting System: 4; Automated Underwriting System: 5; Automated Underwriting System Result: 1; 
			Automated Underwriting System Result: 2; Automated Underwriting System Result: 3; 
			Automated Underwriting System Result: 4; Automated Underwriting System Result: 5"""
		edit_name = "q644"
		fail_df = self.lar_df[
				((self.lar_df.aus_1=="2")&(~self.lar_df.aus_result_1.isin(["8","9","10","11","12"])))|
				((self.lar_df.aus_2=="2")&(~self.lar_df.aus_result_2.isin(["8","9","10","11","12"])))|
				((self.lar_df.aus_3=="2")&(~self.lar_df.aus_result_3.isin(["8","9","10","11","12"])))|
				((self.lar_df.aus_4=="2")&(~self.lar_df.aus_result_4.isin(["8","9","10","11","12"])))|
				((self.lar_df.aus_5=="2")&(~self.lar_df.aus_result_5.isin(["8","9","10","11","12"])))]
		self.results_wrapper(edit_name=edit_name, field_name=field, fail_df=fail_df)