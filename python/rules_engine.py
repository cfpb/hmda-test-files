#This file will contain the python class used to check LAR data using the edits as described in the HMDA FIG
#This class should be able to return a list of row fail counts for each S/V edit for each file passed to the class.
#The return should be JSON formatted data, written to a file?
#input to the class will be a pandas dataframe
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
		self.results["s300"] = {}  #create s300 section of results
		self.results["s300"]["lar_fail_ids"] = [] #create list for failed row ids
		self.results["s300"]["ts_row"] = ""
		if self.ts_df.get_value(0,"record_id") != "1":
			self.results["s300"]["ts_row"] ="failed"
		else:
			self.results["s300"]["ts_row"] ="passed"
		count = 0 #initialize count of fail rows
		for index, row in self.lar_df.iterrows():
			if self.lar_df.get_value(index, "record_id")!="2":
				count+=1
				self.results["s300"]["lar_fail_ids"].append(self.lar_df.get_value(index, "uli"))
		self.results["s300"]["lar_fail_count"] = count


	def s301(self):
		"""The LEI in this row does not match the reported LEI in the transmittal sheet (the first row of your file). Please update your file accordingly."""
		self.results["s301"] = {}
		self.results["s301"]["lar_fail_ids"] = []
		ts_lei = self.ts_df.get_value(0, "lei")
		count = 0
		for index, row in self.lar_df.iterrows():
			if self.lar_df.get_value(index, "lei") != ts_lei:
				count+=1
				self.results["s301"]["lar_fail_ids"].append(self.lar_df.get_value(index, "lei"))
		self.results["s301"]["lar_fail_count"] = count


	def v600(self):
		"""1) The required format for LEI is alphanumeric with 20 characters, and it cannot be left blank."""
		self.results["v600"] = {}
		self.results["v600"]["lar_fail_ids"] = []
		#check LAR rows for LEI issues
		count = 0 #initialize fail count
		for index, row in self.lar_df.iterrows():
			if self.lar_df.get_value(index, "lei") == "" or len(self.lar_df.get_value(index, "lei"))!=20:
				count +=1
				self.results["v600"]["lar_fail_ids"].append(self.lar_df.get_value(index, "lei")) #append failed LEI value to list of fails
		self.results["v600"]["lar_fail_count"] = count #add count of fails to result

	def s302(self, year="2018"):
		""" The reported Calendar Year does not match the filing year indicated at the start of the filing."""
		#this applies to the TS only
		self.results["s302"] = {}
		self.results["s302"]["ts_row"] = ""
		if self.ts_df.get_value(0, "calendar_year") !=year:
			self.results["s302"]["ts_row"] = "failed"
		else:
			self.results["s302"]["ts_row"] = "passed"

	def s304(self):
		"""The reported Total Number of Entries Contained in Submission does not match the total number of LARs in the HMDA file."""
		self.results["s304"] = {}
		self.results["s304"]["ts_row"] = ""
		if self.ts_df.get_value(0, "lar_entries") != str(len(self.lar_df)):
			self.results["s304"]["ts_row"] = "failed"
		else:
			self.results["s304"]["ts_row"] = "passed"

	def v601(self):
		"""The following data fields are required, and cannot be left blank. A blank value(s) was provided.
		1) Financial Institution Name;
		2) Contact Person's Name;
		3) Contact Person's E-mail Address;
		4) Contact Person's Office Street Address;
		5) Contact Person's Office City"""
		self.results["v601"] = {}
		self.results["v601"]["ts_row"] = {}
		fields = ["contact_name", "contact_tel", "contact_street_address", "office_city", "contact_email"]
		for field in fields:
			if self.ts_df.get_value(0, field) == "":
				self.results["v601"]["ts_row"][field] = "failed"
			else:
				self.results["v601"]["ts_row"][field] = "passed"

	def v602(self):
		"""An invalid Calendar Quarter was reported. 1) Calendar Quarter must equal 4, and cannot be left blank."""
		self.results["v602"] = {}
		self.results["v602"]["calendar_quarter"] = ""
		if self.ts_df.get_value(0, "calendar_quarter") != "4":
			self.results["v602"]["calendar_quarter"] = "failed"
		else:
			self.results["v602"]["calendar_quarter"] = "passed"

	def v603(self):
		"""An invalid Contact Person's Telephone Number was provided.
		1) The required format for the Contact Person's Telephone Number is 999-999-9999, and it cannot be left blank."""
		self.results["v603"] = {}
		self.results["v603"]["contact_tel"] = ""
		tel = self.ts_df.get_value(0, "contact_tel")
		tel2 = tel.replace("-", "")
		if tel == "" or len(tel) != 12 or tel2.isdigit() == False: #invalid telephone format provided
			self.results["v603"]["contact_tel"] = "failed"
		else: #valid telephone format provided
			self.results["v603"]["contact_tel"] = "passed"

	def v604(self):
		"""V604 An invalid Contact Person's Office State was provided. Please review the information below and update your file accordingly.
			1) Contact Person's Office State must be a two letter state code, and cannot be left blank."""
		self.results["v604"] = {}
		self.results["v604"]["contact_office_state"] = ""
		#office code is not valid for US states or territories
		if self.ts_df.get_value(0, "office_state") not in self.state_codes.keys():
			print("not here")
			self.results["v604"]["contact_office_state"] = "failed"
		#office code is valid for US states or territories
		else:
			self.results["v604"]["contact_office_state"] = "passed"

	def v605(self):
		"""V605 An invalid Contact Person's ZIP Code was provided. Please review the information below and update your file accordingly.
			1) The required format for the Contact Person's ZIP Code is 12345-1010 or 12345, and it cannot be left blank."""
		self.results["v605"] = {}
		self.results["v605"]["office_zip"] = ""
		#office zip is not valid format
		if len(self.ts_df.get_value(0, "office_zip")) not in (5, 10) or self.ts_df.get_value(0, "office_zip").replace("-","").isdigit==False:
			self.results["v605"]["office_zip"] = "failed"
		#offize zip is valid format
		else:
			self.results["v605"]["office_zip"] = "passed"
			
	"""
	V606 The reported Total Number of Entries Contained in Submission is not in the valid format. Please review the information below and update your file accordingly.
	1) The required format for the Total Number of Entries Contained in Submission is a whole number that is greater than zero, and it cannot be left blank.
	
	V607 An invalid Federal Taxpayer Identification Number was provided. Please review the information below and update your file accordingly.
	1) The required format for the Federal Taxpayer Identification Number is 99-9999999, and it cannot be left blank.
	
	S305 A duplicate transaction has been reported. Please review and update your file accordingly.
	
	V608 A ULI with an invalid format was provided. Please review the information below and update your file accordingly.
	1) The required format for ULI is alphanumeric with at least 23 characters and up to 45 characters, and it cannot be left blank.
	
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