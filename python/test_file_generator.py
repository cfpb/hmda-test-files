import os
import pandas as pd
import random
import string

import utils

class test_data(object):
	"""This class alters clean synthetic data files in order to cause the altered file to fail the specified edit. Modified files may fail other edits as well."""

	def __init__(self, ts_schema, lar_schema):
		"""Set initial class variables"""
		self.clean_file_path = "../edits_files/"
		self.validity_path = "../edits_files/validity/"
		self.syntax_path = "../edits_files/syntax/"
		self.lar_field_names = list(lar_schema.field)
		self.ts_field_names = list(ts_schema.field)

	def load_data_frames(self, ts_data, lar_data):
		"""Receives dataframes for TS and LAR and writes them as object attributes"""
		self.ts_df = ts_data
		self.lar_df = lar_data

	def load_lar_data(self, lar_df=None):
		"""Takes a dataframe of LAR data and stores it as a class variable."""
		self.lar_df = lar_df

	def load_ts_data(self, ts_df=None):
		"""Takes a dataframe of TS data and stores it as a class variable. TS data must be a single row."""
		self.ts_df = ts_df
	#edits will be broken out into sub parts as in the rules_engine.py class. This will allow test files to be generated such that they fail conditions inside each edit.
	#When possible each file will only fail the condition listed in the file name. There will be cases when test files fail additional edits, these cases will be documented
	#to the extent possible.
	def s300_1_file(self):
		"""Sets the first character of the first row of the file to 3."""
		name = "s300_1.txt"
		path = self.syntax_path
		ts = self.ts_df.copy() #change to local data from class data object
		lar = self.lar_df.copy()
		ts.record_id = "3" #modify local data to fail edit test
		#write local data to file
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def s300_2_file(self):
		""""Sets the first character of each LAR row to 3."""
		name = "s300_2_file"
		path = self.syntax_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy() #set to local data from class data object
		lar.record_id = "3" #modify data to fail edit test
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def s301_file(self):
		"""Changes the LEI of a LAR file such that it does not match the TS."""
		name = "s301.txt"
		path = self.syntax_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		while lar.lei[0] == self.ts_df.lei[0]:
			lar.lei = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
		print("writing {name}".format(name=name))
		utils.write_file(name="s301.txt", path="../edits_files/syntax/", ts_input=ts, lar_input=lar)

	def s302_file(self):
		"""Sets the year of submission to 2016"""
		name = "s302.txt"
		path = self.syntax_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.calendar_year = "2016"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v600_file(self):
		"""Modifies the LEI of TS and LAR so that they do not meed schema requirements"""
		name = "v600.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.lei = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
		lar.lei = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def s304_file(self):
		"""Changes the number of entries data so that it does not match the number of LAR rows in the file."""
		name = "s304.txt"
		path = self.syntax_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.lar_entries = 0
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v601_1_file(self):
		"""Modifies the TS to blank the FI name."""
		name = "v601_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.inst_name = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v601_2_file(self):
		"""Modify the TS by blanking out the contact person's name."""
		name = "v601_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.contact_name = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v601_3_file(self):
		"""Modify the TS by blanking the contact person's E-mail address."""
		name = "v601_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.contact_email = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v601_4_file(self):
		"""Modify the TS so to blank out the contact person's office street address."""
		name = "v601_4.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.contact_street_address = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v602_file(self):
		"""Changes TS calendar quarter to 5."""
		name = "v602.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.calendar_quarter = "5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v603_file(self):
		"""Changes contact number to alphanumeric string."""
		name = "v603.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.contact_tel = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v604_file(self):
		"""Converts contact person's office state to two digit number."""
		name = "v604.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.office_state = str(random.randint(10,99))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v605_file(self):
		"""Convert contact person's ZIP to string of letters."""
		name = "v605.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.office_zip = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v606_file(self):
		"""Convert number of entries to a negative decimal number."""
		name = "v606.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.lar_entries = "-1.67"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v607_file(self):
		"""Changes tax ID to string of letters."""
		name = "v607.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.tax_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v608_file(self):
		"""Changes ULI to be 22 characters or less. Preserves the LEI prefix of ULI to reduce the number of edits failed."""
		name = "v608.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.uli = lar.uli.map(lambda x: x[:20] + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(2)))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v609_file(self):
		"""Change check digit on each row. Ensure that the new check digit fails."""
		name = "v609.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.uli = lar.uli.map(lambda x: x[:-2] + "xy")
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v610_1_file(self):
		"""Change application date to blank."""
		name = "v610_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_date = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v610_2_file(self):
		"""Set each row to action taken = 3 and application date = NA."""
		name = "v610_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_date = "NA"
		lar.action_taken = "3"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def s305_file(self):
		"""Copies the first line of the file into all subsequent lines."""
		name = "s305.txt"
		path = self.syntax_path
		ts = self.ts_df.copy()
		lar_start = self.lar_df.copy()
		line = pd.DataFrame(lar_start.iloc[0]).transpose()
		lar = line.copy()
		for i in range(len(lar_start)-1):
			lar = pd.concat([lar, line])
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v611_file(self):
		"""Sets loan type to 5 or blank."""
		name = "v611.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_type = random.choice(("5", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v612_1_file(self):
		"""Set loan purpose to 3 or blank."""
		name = "v612_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_purpose = random.choice(("3", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v612_2_file(self):
		"""Set preapproval to 1 and loan purpose to a random enumeration that is not 1."""
		name = "v612_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.preapproval = "1"
		lar.loan_purpose = random.choice(("2", "31", "32", "4", "5"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v613_1_file(self):
		"""Set preapproval to 3 or blank."""
		name = "v613_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.preapproval = random.choice(("3", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v613_2_file(self):
		"""Set action to random of 7 or 8, set preapproval to random != 1."""
		name = "v613_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = random.choice(("7", "8"))
		lar.preapproval = "2"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v613_3_file(self):
		"""Set action to random 3, 4, 5, or 6 and preapproval to 1."""
		name = "v613_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.preapproval = "1"
		lar.action_taken = random.choice(("3", "4", "5", "6"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v613_4_file(self):
		"""Set preapproval to 1 and action taken to random 0, 3, 4, 5, 6."""
		name = "v613_4.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.preapproval = "1"
		lar.action_taken = random.choice(("0", "3", "4", "5", "6"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v614_1_file(self):
		"""Set loan purpose to random 2, 4, 31, 32, or 5 and preapproval to 1."""
		name = "v614_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.preapproval = "1"
		lar.loan_purpose = random.choice(("2", "4", "31", "32", "5"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v614_2_file(self):
		"""Set affordable units to 1 and preapproval to 1."""
		name = "v614_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.preapproval = "1"
		lar.affordable_units = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v614_3_file(self):
		"""Set reverse mortgage to 1 and preapproval to 1."""
		name = "v614_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.preapproval = "1"
		lar.reverse_mortgage = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v614_4_file(self):
		"""Set open end credit to 1 and preapproval to 1."""
		name = "v614_4.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.preapproval = "1"
		lar.open_end_credit = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v615_1_file(self):
		"""Set construction method to random 3 or blank."""
		name = "v615_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.const_method = random.choice(("3", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v615_2_file(self):
		"""Set manufactured interest to random 1, 2, 3 or 4 and construction method to 1."""
		name = "v615_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.manufactured_interest = random.choice(("1", "2", "3", "4"))
		lar.const_method = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v615_3_file(self):
		"""Set manufactured type to random 1, 2 and construction method to 1."""
		name = "v615_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.manufactured_type = random.choice(("1", "2"))
		lar.const_method = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v616_file(self):
		"""Set occupancy to random 4 or blank."""
		name = "v616.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.occ_type = random.choice(("4", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v617_file(self):
		"""Set loan amount to random 0 or blank."""
		name = "v617.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_amount = random.choice(("0", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v618_file(self):
		"""Set action taken to random 0, NA or blank."""
		name = "v618.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = random.choice(("0", "NA", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v619_1_file(self):
		"""Set action taken date to random NA or blank."""
		name = "v619_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_date = random.choice(("NA", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v619_2_file(self):
		"""Set action taken date to 20160101."""
		name = "v619_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_date = "20160101"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v619_3_file(self):
		"""Set action taken date to 20160101"""
		name = "v619_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_date = "20160101"
		lar.app_date = "20181231"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v620_file(self):
		"""Set street address to blank."""
		name = "v620.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.street_address = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v621_file(self):
		"""Set city to blank."""
		name = "v621.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.city = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v622_1_file(self):
		"""Set street address to random string, set City to NA."""
		name = "v622_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.street_address = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
		lar.city = "NA"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v622_2_file(self):
		"""Set street address to random string, set State to NA."""
		name = "v622_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.street_address = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
		lar.state = "NA"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v622_3_file(self):
		"""Set street address to random string, set ZIP code to NA."""
		name = "v622_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.street_address = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
		lar.zip_code = "NA"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)