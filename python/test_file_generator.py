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

	def v623_file(self):
		"""Set state code to blank or 11."""
		name = "v623.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.state = random.choice(("", "11"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v624_file(self):
		"""Set ZIP code to blank or random string of letters."""
		name = "v624.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.zip_code = random.choice(("", "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v625_1_file(self):
		"""Set Census Tract to blank or 11 digit letter string."""
		name = "v625_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.tract = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(11))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v625_2_file(self):
		"""Set Census Tract to 12345679012."""
		name = "v625_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.tract = "12345678901"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v626_file(self):
		"""Set County to 6 digit number."""
		name = "v626.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.county = "654321"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v627_file(self):
		"""Set County and Tract to strings of 5 and 11 digit length."""
		name = "v627.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.county = "654321"
		lar.tract = "12345678901"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v628_1_file(self):
		"""Set all applicant ethnicity fields to blank."""
		name = "v628_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_1 = ""
		lar.app_eth_2 = ""
		lar.app_eth_3 = ""
		lar.app_eth_4 = ""
		lar.app_eth_5 = ""
		lar.app_eth_free = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v628_2_file(self):
		"""Set app ethnicity 2-5 to 3."""
		name = "v628_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_2 = "3"
		lar.app_eth_3 = "3"
		lar.app_eth_4 = "3"
		lar.app_eth_5 = "3"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v628_3_file(self):
		"""Set all applicant ethnicity codes to 1."""
		name = "v628_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_1 = "1"
		lar.app_eth_2 = "1"
		lar.app_eth_3 = "1"
		lar.app_eth_4 = "1"
		lar.app_eth_5 = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v628_4_file(self):
		"""Set applicant ethnicity 1 = 3 or 4. Set all other applicant ethnicities to 1."""
		name = "v628_4.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_1 = random.choice(("3", "4"))
		lar.app_eth_2 = "1"
		lar.app_eth_3 = "1"
		lar.app_eth_4 = "1"
		lar.app_eth_5 = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v629_1_file(self):
		"""Set applicant ethnicity basis to 4."""
		name = "v629_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_basis = "4"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v629_2_file(self):
		"""Set applicant ethnicity basis to 1. Set applicant ethnicity 1 = 3. Set all other applicant ethnicities to 1."""
		name = "v629_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_basis = "1"
		lar.app_eth_1 = "3"
		lar.app_eth_2 = "1"
		lar.app_eth_3 = "1"
		lar.app_eth_4 = "1"
		lar.app_eth_5 = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v629_3_file(self):
		"""Set applicant ethnicity basis to 2. Set applicant ethnicity 1 to 4."""
		name = "v629_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_basis = "2"
		lar.app_eth_1 = "4"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v630_1_file(self):
		"""Set applicant ethnicity 1 to 4. Set applicant ethnicity basis to 2."""
		name = "v630_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_basis = "2"
		lar.app_eth_1 = "4"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v630_2_file(self):
		"""Set applicant ethnicity basis to 3. Set applicant ethnicity 1 to 2."""
		name = "v630_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_basis = "3"
		lar.app_eth_1 = "2"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v631_1_file(self):
		"""Set co-app ethnicity 1 to blank. Set co-app ethnicity free text to blank."""
		name = "v631_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_eth_1 = ""
		lar.co_app_eth_free = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v631_2_file(self):
		"""Set co-app ethnicity 2-5 to 3."""
		name = "v631_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_eth_2 = "3"
		lar.co_app_eth_3 = "3"
		lar.co_app_eth_4 = "3"
		lar.co_app_eth_5 = "3"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v631_3_file(self):
		"""Set all co-app ethnicities to 1."""
		name = "v631_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_eth_1 = "1"
		lar.co_app_eth_2 = "1"
		lar.co_app_eth_3 = "1"
		lar.co_app_eth_4 = "1"
		lar.co_app_eth_5 = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v631_4_file(self):
		"""Set co-app ethnicity 1 to random choice of 3, 4, 5. Set co-app ethnicity 2-5 to 1."""
		name = "v631_4.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_eth_1 = random.choice(("3", "4", "5"))
		lar.co_app_eth_2 = "1"
		lar.co_app_eth_3 = "1"
		lar.co_app_eth_4 = "1"
		lar.co_app_eth_5 = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v632_1_file(self):
		"""Set co-app ethnicity basis to blank."""
		name = "v632_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_eth_basis = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v632_2_file(self):
		"""Set co-app ethnicity basis to 1. Set co-app ethnicity 1 to 3. Set co-app ethnicity 2 to 3. Set co-app ethnicity 3-5 to 1"""
		name = "v632_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_eth_basis = "1"
		lar.co_app_eth_1 = "3"
		lar.co_app_eth_2 = random.choice(("2", "3"))
		lar.co_app_eth_3 = "1"
		lar.co_app_eth_4 = "1"
		lar.co_app_eth_5 = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v632_3_file(self):
		"""Set co-app ethnicity basis to 2. Set co-app ethnicity 1 to 4."""
		name = "v632_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_eth_1 = "4"
		lar.co_app_eth_basis = "2"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v633_1_file(self):
		"""Set co-app ethnicity 1 to 4. Set co-app ethnicity basis to 1."""
		name = "v633_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_eth_1 = "4"
		lar.co_app_eth_basis = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v633_2_file(self):
		"""Set co-app ethnicity basis to 3. Set co-app ethnicity 1 to random choice of 3 or 4."""
		name = "v633_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_eth_1 = random.choice(("1", "2"))
		lar.co_app_eth_basis = "3"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v634_file(self):
		"""For the first half of the file:
		Set co-app ethnicity 1 to 5.
		Set co-app ethnicity basis to 3
		For the second half of the file:
		Set co-app ethnicity 1 to 4.
		Set co-app ethnicity basis to 4."""
		name = "v634.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		midpoint = len(lar)/2
		lar.co_app_eth_1[lar.index <= midpoint] = "5"
		lar.co_app_eth_basis[lar.index <= midpoint] = "3"
		lar.co_app_eth_1[lar.index > midpoint] = "4"
		lar.co_app_eth_basis[lar.index > midpoint] = "4"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v635_1_file(self):
		"""Set app race 1 to blank. Set all race text fields to blank."""
		name = "v635_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_race_1 = ""
		lar.app_race_native_text = ""
		lar.app_race_islander_text = ""
		lar.app_race_asian_text = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v635_2_file(self):
		"""Set app races 2-5 to 6."""
		name = "v635_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_race_2 = "6"
		lar.app_race_3 = "6"
		lar.app_race_4 = "6"
		lar.app_race_5 = "6"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v635_3_file(self):
		"""Set all applicant race fields to 1."""
		name = "v635_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_race_1 = "1"
		lar.app_race_2 = "1"
		lar.app_race_3 = "1"
		lar.app_race_4 = "1"
		lar.app_race_5 = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v635_4_file(self):
		"""Set app race to random choice of 6 or 7. Set app races 2-5 to random choice of 1-5."""
		name = "v635_4.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_race_1 = random.choice(("6", "7"))
		lar.app_race_2 = random.choice(("1", "2", "3", "4", "5"))
		lar.app_race_3 = random.choice(("1", "2", "3", "4", "5"))
		lar.app_race_4 = random.choice(("1", "2", "3", "4", "5"))
		lar.app_race_5 = random.choice(("1", "2", "3", "4", "5"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v636_1_file(self):
		"""Set app race basis to 4."""
		name = "v636_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_race_basis = "4"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v636_2_file(self):
		"""Set app race basis to 1. Set app race 1 to blank. Set app races 2-5 to 6."""
		name = "v636_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_race_basis = "1"
		lar.app_race_1 = ""
		lar.app_race_2 = "6"
		lar.app_race_3 = "6"
		lar.app_race_4 = "6"
		lar.app_race_5 = "6"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v636_3_file(self):
		"""Set app race basis to 2. Set app race 1 to blank. Set app races 2-5 to 6."""
		name = "v636_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_race_basis = "2"
		lar.app_race_1 = ""
		lar.app_race_2 = "6"
		lar.app_race_3 = "6"
		lar.app_race_4 = "6"
		lar.app_race_5 = "6"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v637_1_file(self):
		"""Set app race 1 to 7. Set app race basis to random choice of 1, 2."""
		name = "v637_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_race_1 = "7"
		lar.app_race_basis = random.choice(("1", "2"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v637_2_file(self):
		"""Set app race basis to 3. Set app race 1 to random choice of 1-5."""
		name = "v637_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_race_basis = "3"
		lar.app_race_1 = random.choice(("1", "2", "3", "4", "5"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v638_1_file(self):
		"""Set co-app race 1 to blank. Set all co-app race text fields to blank."""
		name = "v638_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_race_1 = ""
		lar.co_app_race_asian_text = ""
		lar.co_app_race_islander_text = ""
		lar.co_app_race_native_text = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v638_2_file(self):
		"""Set co-applicant races 2-5 to 6."""
		name = "v638_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_race_2 = "6"
		lar.co_app_race_3 = "6"
		lar.co_app_race_4 = "6"
		lar.co_app_race_5 = "6"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v638_3_file(self):
		"""Set all co-applicant race codes to 1."""
		name = "v638_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_race_1 = "1"
		lar.co_app_race_2 = "1"
		lar.co_app_race_3 = "1"
		lar.co_app_race_4 = "1"
		lar.co_app_race_5 = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v638_4_file(self):
		"""Set co-applicant race 1 to random choice of 6, 7, 8. Set co-applicant races 2-5 to 1."""
		name = "v638_4.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_race_1 = random.choice(("6","7","8"))
		lar.co_app_race_2 = "1"
		lar.co_app_race_3 = "1"
		lar.co_app_race_4 = "1"
		lar.co_app_race_5 = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v639_1_file(self):
		"""Set co-applicant race basis to blank."""
		name = "v639_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_race_basis = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v639_2_file(self):
		"""Set co_app race basis to 1. Set co-app race 1 to 21. Set co-app races 2-5 to 21."""
		name = "v639_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_race_basis = "1"
		lar.co_app_race_1 = "21"
		lar.co_app_race_2 = "21"
		lar.co_app_race_3 = "21"
		lar.co_app_race_4 = "21"
		lar.co_app_race_5 = "21"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v639_3_file(self):
		"""Set co-app race basis to 2. Set co-app race 1 to blank. Set co-app races 2-5 to 6."""
		name = "v639_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_race_basis = "2"
		lar.co_app_race_1 = "1"
		lar.co_app_race_2 = "6"
		lar.co_app_race_3 = "6"
		lar.co_app_race_4 = "6"
		lar.co_app_race_5 = "6"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v640_1_file(self):
		"""Set co-app race 1 to 7. Set co-app race basis to random choice of 1, 2."""
		name = "v640_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_race_basis = random.choice(("1", "2"))
		lar.co_app_race_1 = "7"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v640_2_file(self):
		"""Set co-app race basis to 3. Set co-app race 1 to random choice of 1-5."""
		name = "v640_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_race_basis = "3"
		lar.co_app_race_1 = random.choice(("1", "2", "3", "4", "5"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v641_file(self):
		"""Set co-app race 1 = 8. Set co-app race basis to random choice of 1-3."""
		name = "v641.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_race_basis = random.choice(("1", "2", "3"))
		lar.co_app_race_1 = "8"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v642_1_file(self):
		"""Set applicant sex to blank."""
		name = "v642_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_sex = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v642_2_file(self):
		"""Set applicant sex basis to blank."""
		name = "v642_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_sex_basis = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v643_1_file(self):
		"""Set applicant sex basis to 1. Set applicant sex to 3."""
		name = "v643_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_sex_basis = "1"
		lar.app_sex = "3"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v643_2_file(self):
		"""Set applicant sex to random choice of 1, 2. Set applicant sex basis to random choice of 3, 4."""
		name = "v643_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_sex = random.choice(("1", "2"))
		lar.app_sex_basis = random.choice(("3", "4"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v644_1_file(self):
		"""Set applicant sex basis to 2. Set applicant sex to random choice of 4, 5."""
		name = "v644_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_sex_basis = "2"
		lar.app_sex = random.choice(("4", "5"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v644_2_file(self):
		"""Set applicant sex to 6. Set applicant sex basis to 1."""
		name = "v644_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_sex = "6"
		lar.app_sex_basis = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v645_1_file(self):
		"""Set applicant sex basis to 3. Set applicant sex to random choice of 1, 2."""
		name = "v645_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_sex_basis = "3"
		lar.app_sex = random.choice(("1", "2"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v645_2_file(self):
		"""Set applicant sex to 4. Set applicant sex basis to random choice of 1, 2."""
		name = "v645_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_sex = "4"
		lar.app_sex_basis = random.choice(("1", "2"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v646_1_file(self):
		"""Set co-applicant sex to blank."""
		name = "v646_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_sex = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v646_2_file(self):
		"""Set co-applicant sex basis to blank."""
		name = "v646_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_sex_basis = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v647_1_file(self):
		"""Set co-app sex basis to 1. Set co-app sex to random choice of 3, 4."""
		name = "v647_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_sex_basis = "1"
		lar.co_app_sex = random.choice(("3", "4"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v647_2_file(self):
		"""Set co-app sex to random choice of 1, 2. Set co-app sex basis to random choice of 3, 4."""
		name = "v647_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_sex_basis = random.choice(("3", "4"))
		lar.co_app_sex = random.choice(("1", "2"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v648_1_file(self):
		"""Set co-app sex basis to 2. Set co-app sex to 4 or 5."""
		name = "v648_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_sex_basis = "2"
		lar.co_app_sex = random.choice(("4", "5"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v648_2_file(self):
		"""Set co-app sex to 6. Set co app sex basis to random choice of 1, 3, 4."""
		name = "v648_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_sex_basis = random.choice(("1", "3", "4"))
		lar.co_app_sex = "6"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v649_1_file(self):
		"""Set co-app sex basis to 3. Set co-app sex to random choice of 1, 2."""
		name = "v649_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_sex_basis = "3"
		lar.co_app_sex = random.choice(("1", "2"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v649_2_file(self):
		"""Set co-app sex to 4. Set co-app sex basis to random choice of 1, 2."""
		name = "v649_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_sex_basis = random.choice(("1", "2"))
		lar.co_app_sex = "4"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v650_file(self):
		"""Set co-app sex basis to 4. Set co-app sex to random choice of 1-4."""
		name = "v650.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_sex_basis = "4"
		lar.co_app_sex = random.choice(("1", "2", "3", "4"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v651_1_file(self):
		"""Set app age to random choice of 0 or blank."""
		name = "v651_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_age = random.choice(("0", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v651_2_file(self):
		"""Set app ethnicity 1 to 4. Set app race 1 to 7. Set app sex to 4. Set app age to 42."""
		name = "v651_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_1 = "4"
		lar.app_race_1 = "7"
		lar.app_sex = "4"
		lar.app_age = "42"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v652_1_file(self):
		"""Set co-app age to random choice of 0, blank."""
		name = "v652_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_age = random.choice(("0", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v652_2_file(self):
		"""Set co-app ethnicity 1 to 4. Set co-app race 1 to 7. Set co-app sex to 4. Set co-app age to 42."""
		name = "v652_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_eth_1 = "4"
		lar.co_app_race_1 = "7"
		lar.co_app_sex = "4"
		lar.co_app_age = "42"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v654_1_file(self):
		"""Set income to random of blank, 1.5."""
		name = "v654_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.income = random.choice(("1.5", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v654_2_file(self):
		"""Set affordable units to 5. Set income to 42."""
		name = "v654_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.affordable_units = "5"
		lar.income = "42"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v655_1_file(self):
		"""Set app ethnicity 1 to 4. Set app race 1 to 7. Set app sex to 4. Set income to 42."""
		name = "v655_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_1 = "4"
		lar.app_race_1 = "7"
		lar.app_sex = "4"
		lar.income = "42"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v655_2_file(self):
		"""Set co-app ethnicity 1 to 4. Set co-app race 1 to 7. Set co-app sex to 4. Set income to 42."""
		name = "v655_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_eth_1 = "4"
		lar.co_app_race_1 = "7"
		lar.co_app_sex = "4"
		lar.income = "42"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v656_1_file(self):
		"""Set purchaser type to random of blank or 10."""
		name = "v656_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.purchaser_type = random.choice(("", "10"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v656_2_file(self):
		"""Set action taken to random choice of 2, 3, 4, 5, 7, 8. Set purchaser type to random 1-9."""
		name = "v656_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.purchaser_type = random.choice(("1", "2", "3", "4", "5", "6", "7", "8", "9"))
		lar.action_taken = random.choice(("2", "3", "4", "5", "7", "8"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v657_1_file(self):
		"""Set rate spread to blank."""
		name = "v657_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.rate_spread = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v657_2_file(self):
		"""Set action taken to random choice of 3, 4, 5, 6, 7. Set rate spread to 5.0."""
		name = "v657_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.rate_spread = "5.0"
		lar.action_taken = random.choice(("3", "4", "5", "7"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v657_3_file(self):
		"""Set reverse mortgage to 1. Set rate spread to 5.0."""
		name = "v657_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.rate_spread = "5.0"
		lar.reverse_mortgage = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v658_1_file(self):
		"""Set HOEPA status to blank."""
		name = "v658_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.hoepa = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v658_2_file(self):
		"""Set action taken to random choice of 2, 3, 4, 5, 7, 8. Set HOEPA to random of 1, 2."""
		name = "v658_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.hoepa = random.choice(("1", "2"))
		lar.action_taken = random.choice(("2", "3", "4", "5", "7", "8"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v659_file(self):
		"""Set lien status to random of 3, blank."""
		name = "v659.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.lien = random.choice(("3", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v660_1_file(self):
		"""Set app credit score to random of blank or "aaa"."""
		name = "v660_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_credit_score = random.choice(("aaa", ""))
		lar.action_taken = random.choice(("2", "3", "4", "5", "7", "8"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v660_2_file(self):
		"""Set app credit score model to random of blank or 10."""
		name = "v660_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_score_name = random.choice(("10", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v661_file(self):
		"""Set app credit score to 8888. Set app score model to random of 1-8."""
		name = "v661.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_credit_score = "8888"
		lar.app_score_name = random.choice(("1", "2", "3", "4", "5", "6", "7", "8"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v662_1_file(self):
		"""Set app credit score model to random of 1-7, 9. Set app score model text field to random string."""
		name = "v662_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_score_code_8 = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
		lar.app_score_name = random.choice(("1", "2", "3", "4", "5", "6", "7", "9"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v662_2_file(self):
		"""Set app score model to 8. Set app score model text field to blank."""
		name = "v662_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_score_code_8 = ""
		lar.app_score_name = "8"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v663_file(self):
		""" Set action taken to random of 4, 5, 6. Set app credit score to 700. Set app score model to random 1-8.
		Set app score model text field to random string."""
		name = "v663.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = random.choice(("4", "5", "6"))
		lar.app_credit_score = "700"
		lar.app_score_name = random.choice(("1", "2", "3", "4", "5", "6", "7", "8"))
		lar.app_score_code_8 = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v664_file(self):
		"""Set action taken to random of 4, 5, 6. Set co-app score to 700. Set co-app score model to random 1-8.
		Set co-app score text field to blank."""
		name = "v664.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = random.choice(("4", "5", "6"))
		lar.co_app_credit_score = "700"
		lar.co_app_score_name = random.choice(("1", "2", "3", "4", "5", "6", "7", "8"))
		lar.co_app_score_code_8 = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v665_1_file(self):
		"""Set co-app score to random of blank, 'aaa'."""
		name = "v665_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_credit_score = random.choice(("aaa", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v665_2_file(self):
		"""Set co-app score name to random of 0, blank."""
		name = "v665_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_score_name = random.choice(("0", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v666_1_file(self):
		"""Set co-app credit score to 8888. Set co app score name to random 1-8."""
		name = "v666_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_credit_score = "8888"
		lar.co_app_score_name = random.choice(("1", "2", "3", "4", "5", "6", "7", "8"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v666_2_file(self):
		"""Set co-app score to 9999. Set co app score name to random 1-9."""
		name = "v666_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_score_name = random.choice(str(random.randrange(1,10)))
		lar.co_app_credit_score = "9999"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v667_1_file(self):
		"""Set co-app score name to 1-7, 9, 10. Set co-app score text to random string."""
		name = "v667_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_score_code_8 = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
		lar.co_app_score_name = random.choice(("1", "2", "3", "4", "5", "6", "7", "9", "10"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v667_2_file(self):
		"""Set co-app score name to 8. Set co-app score text to blank."""
		name = "v667_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_score_name = "8"
		lar.co_app_score_code_8 = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v668_1_file(self):
		"""Set app ethnicity 1 to 4. Set app race 1 to 7. Set app sex to 4. Set app credit score to 700."""
		name = "v668_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_1 = "4"
		lar.app_race_1 = "7"
		lar.app_sex = "4"
		lar.app_credit_score = "700"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v668_2_file(self):
		"""Set co-app ethnicity to 4. Set co-app race to 7. Set co-app sex to 4. Set co-app credit score to 700."""
		name = "v668_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_eth_1 = "4"
		lar.co_app_race_1 = "7"
		lar.co_app_sex = "4"
		lar.co_app_credit_score = "700"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v669_1_file(self):
		"""Set denial reason 1 to blank."""
		name = "v669_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.denial_1 = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v669_2_file(self):
		"""Set denial reason 2-4 to random of 10 or blank."""
		name = "v669_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.denial_2 = random.choice(("10", ""))
		lar.denial_3 = random.choice(("10", ""))
		lar.denial_4 = random.choice(("10", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v669_3_file(self):
		"""Set all reasons for denial to 1."""
		name = "v669_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.denial_1 = "1"
		lar.denial_2 = "1"
		lar.denial_3 = "1"
		lar.denial_4 = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v669_4_file(self):
		"""Set denial reason 1 to 10. Set denial reasons 2-4 to 2,3,4."""
		name = "v669_4.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.denial_1 = "10"
		lar.denial_2 = random.choice(("2", "3", "4"))
		lar.denial_3 = random.choice(("2", "3", "4"))
		lar.denial_4 = random.choice(("2", "3", "4"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v670_1_file(self):
		"""Set action taken to random 3, 7. Set denial reason 1 to 10."""
		name = "v670_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.denial_1 = "10"
		lar.action_taken = random.choice(("3", "7"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v670_2_file(self):
		"""Set action taken to random 1-6, 8. Set denial 1 to random 1-9."""
		name = "v670_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.denial_1 = random.choice(str(random.randrange(1,10)))
		lar.action_taken = random.choice(("1", "2", "4", "5", "6", "8"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v671_1_file(self):
		"""Set denial 1-4 to code 9. Set denial text to blank."""
		name = "v671_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.denial_1 = "9"
		lar.denial_2 = "9"
		lar.denial_3 = "9"
		lar.denial_4 = "9"
		lar.denial_code_9 = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v671_2_file(self):
		"""Set denial 1-4 to random 1-8. Set denial text to random string."""
		name = "v671_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.denial_1 = random.choice(str(random.randrange(1,9)))
		lar.denial_2 = random.choice(str(random.randrange(1,9)))
		lar.denial_3 = random.choice(str(random.randrange(1,9)))
		lar.denial_4 = random.choice(str(random.randrange(1,9)))
		lar.denial_code_9 = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v672_1_file(self):
		"""Set loan costs to random of -1 or blank."""
		name = "v672_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_costs = random.choice(("-1", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v672_2_file(self):
		"""Set points and fees to 1. Set loan costs to 500."""
		name = "v672_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.points_fees = "1"
		lar.loan_costs = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v672_3_file(self):
		"""Set reverse mortgage to 1. Set loan costs to 500."""
		name = "v672_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.reverse_mortgage = "1"
		lar.loan_costs = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v672_4_file(self):
		"""Set open-end-credit to 1. Set loan costs to 500."""
		name = "v672_4.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.open_end_credit = "1"
		lar.loan_costs = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v672_5_file(self):
		"""Set business purpose to 1. Set loan costs to 500."""
		name = "v672_5.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.business_purpose = "1"
		lar.loan_costs = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v672_6_file(self):
		""" Set action taken to random of 2, 3, 4, 5, 7, 8. Set loan costs to 500."""
		name = "v672_6.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = random.choice(("2", "3", "4", "5", "7", "8"))
		lar.loan_costs = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v673_1_file(self):
		"""Set points and fees to random of -1 or blank."""
		name = "v673_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.points_fees = random.choice(("-1", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v673_2_file(self):
		"""Set action taken to random of 2, 3, 4, 5, 6, 7 or 8. Set points and fees to 500."""
		name = "v673_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.points_fees = "500"
		lar.action_taken = random.choice(("2", "3", "4", "5", "6", "7", "8"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v673_3_file(self):
		"""Set reverse mortgage to 1. Set points and fees to 500."""
		name = "v673_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.reverse_mortgage = "1"
		lar.points_fees = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v673_4_file(self):
		"""Set business purpose to 1. Set points and fees to 500."""
		name = "v673_4.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.business_purpose = "1"
		lar.points_fees = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v673_5_file(self):
		"""Set loan costs to 1. Set points and fees to 500."""
		name = "v673_5.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_costs = "1"
		lar.points_fees = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v674_1_file(self):
		"""Set origination charges to blank or -1."""
		name = "v674_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.origination_fee = random.choice(("-1", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v674_2_file(self):
		"""Set reverse mortgage to 1. Set origination charges to 500."""
		name = "v674_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.reverse_mortgage = "1"
		lar.origination_fee = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v674_3_file(self):
		"""set open-end-credit to 1. Set origination charges to 500."""
		name = "v674_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.open_end_credit = "1"
		lar.origination_fee = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v674_4_file(self):
		"""Set business purpose to 1. Set origination charges to 500."""
		name = "v674_4.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.business_purpose = "1"
		lar.origination_fee = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v674_5_file(self):
		"""Set action taken to random of 2, 3, 4, 5, 7 or 8. Set origination charges to 500."""
		name = "v674_5.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = random.choice(("2", "3", "4", "5", "7", "8"))
		lar.origination_fee = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v675_1_file(self):
		"""Set discount points to 0."""
		name = "v675_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.discount_points = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v675_2_file(self):
		"""Set reverse mortgage to 1. Set discount points to 500."""
		name = "v675_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.reverse_mortgage = "1"
		lar.discount_points = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v675_3_file(self):
		"""Set open end credit to 1. Set discount points to 500."""
		name = "v675_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.open_end_credit = "1"
		lar.discount_points = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v675_4_file(self):
		"""Set business purpose to 1. Set discount points to 500."""
		name = "v675_4.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.business_purpose = "1"
		lar.discount_points = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v675_5_file(self):
		"""Set action taken to random of 2, 3, 4, 5, 7 or 8. Set discount points to 500."""
		name = "v675_5.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = random.choice(("2", "3", "4", "5", "7", "8"))
		lar.discount_points = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v676_1_file(self):
		"""Set lender credits to 0 or -1."""
		name = "v676_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.lender_credits = random.choice(("0", "-1"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v676_2_file(self):
		"""Set reverse mortgage to 1. Set lender credits to 500."""
		name = "v676_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.reverse_mortgage = "1"
		lar.lender_credits = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v676_3_file(self):
		"""Set open end credit to 1. Set lender credits to 500."""
		name = "v676_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.open_end_credit = "1"
		lar.lender_credits = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v676_4_file(self):
		"""Set business purpose to 1. Set lender credits to 500."""
		name = "v676_4.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.business_purpose = "1"
		lar.lender_credits = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v676_5_file(self):
		"""Set action taken to random of 2, 3, 4, 5, 7 or 8. Set lender credits to 500."""
		name = "v676_5.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = random.choice(("2", "3", "4", "5", "7", "8"))
		lar.lender_credits = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v677_1_file(self):
		"""Set interest rate to 0, -1 or blank."""
		name = "v677_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.interest_rate = random.choice(("0", "-1", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v677_2_file(self):
		"""Set action taken to 3, 4, 5, or 7. Set interest rate to 10.0."""
		name = "v677_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = random.choice(("3", "4", "5", "7"))
		lar.interest_rate = "10.0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v678_1_file(self):
		"""Set penalty term to 0, -1, or blank."""
		name = "v678_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.prepayment_penalty = random.choice(("0", "-1", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v678_2_file(self):
		"""Set action taken to 6. Set penalty term to 30."""
		name = "v678_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = "6"
		lar.prepayment_penalty = "30"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v678_3_file(self):
		"""Set reverse mortgage to 1. Set penalty term to 30."""
		name = "v678_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.reverse_mortgage = "1"
		lar.prepayment_penalty= "30"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v678_4_file(self):
		"""Set business purpose to 1. Set penalty term to 30."""
		name = "v678_4.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.business_purpose = "1"
		lar.prepayment_penalty = "30"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v678_5_file(self):
		"""Set penalty term to 360. Set loan term to 30."""
		name = "v678_5.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.prepayment_penalty = "360"
		lar.loan_term = "30"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v679_1_file(self):
		"""Set DTI to blank or aa."""
		name = "v679_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.dti = random.choice(("", "aa"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v679_2_file(self):
		"""Set action taken to random of 4, 5, 6. Set DTI to 15."""
		name = "v679_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = random.choice(("4", "5", "6"))
		lar.dti = "15"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v679_3_file(self):
		"""Set affordable units to 1. Set DTI to 15 or blank."""
		name = "v679_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.affordable_units = "1"
		lar.dti= "15"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v680_1_file(self):
		"""Set app eth 1 to 4. Set app race 1 to 7. Set app sex to 4. Set co-app eth 1 to 5.
		Set co-app race 1 to 8. Set co-app sex to 5. Set DTI to 15."""
		name = "v680_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_1 = "4"
		lar.app_race_1 = "7"
		lar.app_sex = "4"
		lar.co_app_eth_1 = "5"
		lar.co_app_race_1 = "8"
		lar.co_app_sex = "5"
		lar.dti = "15"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v680_2_file(self):
		"""Set app eth 1 to 4. Set app race 1 to 7. Set app sex to 4. Set co-app eth 1 to 4.
		Set co-app race 1 to 7. Set co-app sex to 4. Set DTI to 15 or blank."""
		name = "v680_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_1 = "4"
		lar.app_race_1 = "7"
		lar.app_sex = "4"
		lar.co_app_eth_1 = "4"
		lar.co_app_race_1 = "7"
		lar.co_app_sex = "4"
		lar.dti = "15"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v681_1_file(self):
		"""Set CLTV to 0, blank or -1."""
		name = "v681_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.cltv = random.choice(("0", "", "-1"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v681_2_file(self):
		"""Set action taken to random of 4, 5, 6. Set CLTV to 15."""
		name = "v681_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = random.choice(("4", "5", "6"))
		lar.cltv = "15"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v682_1_file(self):
		"""Set loan term to 0 or blank."""
		name = "v682_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_term = random.choice(("0", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v682_2_file(self):
		"""Set reverse mortgage to 1. Set loan term to 30."""
		name = "v682_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.reverse_mortgage = "1"
		lar.loan_term = "30"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v683_file(self):
		"""Set introductory rate period to 0, blank or -1."""
		name = "v683.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.intro_rate = random.choice(("0", "-1", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v684_file(self):
		"""Set balloon payment to NA, blank or 0."""
		name = "v684.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.balloon = random.choice(("0", "", "NA"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v685_file(self):
		"""Set interest only payments to 0 or blank."""
		name = "v685.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.int_only_pmts = random.choice(("0", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v686_file(self):
		"""Set negative amortization to 0 or blank."""
		name = "v686.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.neg_amort = random.choice(("0", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v687_file(self):
		"""Set non-amortizing features to 0 or blank."""
		name = "v687.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.non_amort_features = random.choice(("0", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v688_1_file(self):
		"""Set property value to 0 or blank."""
		name = "v688_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.property_value = random.choice(("0", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v688_2_file(self):
		"""Set action taken to 4 or 5. Set property value to 1."""
		name = "v688_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = random.choice(("4", "5"))
		lar.property_value = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v689_1(self):
		"""Set manufactured type to 0 or blank."""
		name = "v689_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.manufactured_type = random.choice(("", "0"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v689_2(self):
		"""Set affordable units to 1.
		   Set manufactured type to random of 1, 2."""
		name = "v689_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.affordable_units = "1"
		lar.manufactured_type = random.choice(("1", "2"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v689_3(self):
		"""Set construction method to 1.
		   Set manufactured type to 3."""
		name = "v689_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.const_method = "1"
		lar.manufactured_type = random.choice(("1", "2"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v690_1(self):
		"""Set manufactured interest to random of 0 or blank."""
		name = "v690_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.manufactured_interest = random.choice(("0", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v690_2(self):
		"""Set affordable units to 1.
		   Set manufactured interest to random 1-4."""
		name = "v690_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.affordable_units = "1"
		lar.manufactured_interest = random.choice(("1", "2", "3", "4"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v690_3(self):
		"""Set construction method to 1.
		   Set manufactured interest to random 1-4."""
		name = "v690_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.const_method = "1"
		lar.manufactured_interest = random.choice(("1", "2", "3", "4"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v691(self):
		"""Set total units to 0 or blank."""
		name = "v691.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.total_units = random.choice(("0", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v692_1(self):
		"""Set affordable units to blank."""
		name = "v692_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.affordable_units = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v692_2(self):
		"""Set total units to random 1-4.
		   Set affordable units to 0, or blank."""
		name = "v692_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.total_units = random.choice(("1", "2", "3", "4"))
		lar.affordable_units = random.choice(("0", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)
	
	def v692_3(self):
		"""Set total units to 6.
		   Set affordable units to 7."""
		name = "v692_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.total_units = "6"
		lar.affordable_units = "7"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v693_1(self):
		"""Set app submission to 0 or blank."""
		name = "V693_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_submission = random.choice(("0",""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v693_2(self):
		"""Set action taken to 6.
		   Set app submission to 1 or 2."""
		name = "V693_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = "6"
		lar.app_submission = random.choice(("1", "2"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v694_1(self):
		"""Set initially payable to blank or 0."""
		name = "v694_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.initially_payable = random.choice(("0", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v694_2(self):
		"""Set action taken to 6 and initially payable to 1 or 2."""
		name = "v694_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = "6"
		lar.initially_payable = random.choice(("1", "2"))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v694_3(self):
		"""Set action taken to 1 and initially payable to 3."""
		name = "v694_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = "1"
		lar.initially_payable = "3"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v695(self):
		"""Set NMLSR ID to blank."""
		name = "v695.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.mlo_id = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v696_1(self):
		"""Set AUS 1 to blank or set AUS 2-5 to 6."""
		name = "v696_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_1 = ""
		lar.aus_2 = "6"
		lar.aus_3 = "6"
		lar.aus_4 = "6"
		lar.aus_5 = "6"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v696_2(self):
		"""Set AUS result 1 to blank and set AUS 2-5 to 17."""
		name = "v696_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_result_1 = ""
		lar.aus_result_2 = "17"
		lar.aus_result_3 = "17"
		lar.aus_result_4 = "17"
		lar.aus_result_5 = "17"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v696_3(self):
		"""Set AUS 1 to 1 and AUS 2-5 to blank.
		   Set AUS result 1-5 to blank."""
		name = "v696_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_1 = "1"
		lar.aus_2 = ""
		lar.aus_3 = ""
		lar.aus_4 = ""
		lar.aus_5 = ""
		lar.aus_result_1 = ""
		lar.aus_result_2 = ""
		lar.aus_result_3 = ""
		lar.aus_result_4 = ""
		lar.aus_result_5 = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v699(self):
		"""Set AUS 1 to 5, set AUS Result 1 to 17."""
		name = "v699.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_1 = "5"
		lar.aus_result_1 = "17"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)
		
	def v700_1(self):
		"""Set AUS 1 to 6 and AUS Result 1-5 to 1-16."""
		name = "v700_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_1 = "6"
		lar.aus_result_1 = str(random.choice(range(16))+1)
		lar.aus_result_2 = str(random.choice(range(16))+1)
		lar.aus_result_3 = str(random.choice(range(16))+1)
		lar.aus_result_4 = str(random.choice(range(16))+1)
		lar.aus_result_5 = str(random.choice(range(16))+1)
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)
		
	def v700_2(self):
		"""Set AUS Result 1 to 17 and set AUS 1 to 1-5.
		   Set AUS Result 2-5 to 1-16."""
		name = "v700_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_result_1 = "17"
		lar.aus_1 = str(random.choice(range(5))+1)
		lar.aus_result_2 = str(random.choice(range(16))+1)
		lar.aus_result_3 = str(random.choice(range(16))+1)
		lar.aus_result_4 = str(random.choice(range(16))+1)
		lar.aus_result_5 = str(random.choice(range(16))+1)
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)
		
	def v701(self):
		"""Set AUS 2 to blank and set AUS Result 2 to 1-16."""
		name = "v701.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_2 = ""
		lar.aus_result_2 = str(random.choice(range(16))+1)
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v702_1(self):
		"""Set AUS 1 to 5 and set AUS: conditional text to blank."""
		name = "v702_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_1 = "5"
		lar.aus_code_5 = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v702_2(self):
		"""Set AUS conditional text to a non-empty string and set AUS 1-5 != 5."""
		name = "v702_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_1 = random.choice(("1", "2", "3", "4"))
		lar.aus_2 = random.choice(("1", "2", "3", "4"))
		lar.aus_3 = random.choice(("1", "2", "3", "4"))
		lar.aus_4 = random.choice(("1", "2", "3", "4"))
		lar.aus_5 = random.choice(("1", "2", "3", "4"))
		lar.aus_code_5 = "HMDA"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v703_1(self):
		"""Set AUS Result 1 to 16 and set AUS Result free form text to blank."""
		name = "v703_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_result_1 = "16"
		lar.aus_code_16 = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)
		
	def v703_2(self):
		"""Set AUS Result free form text to non-empty string 
		   and set AUS Result 1-5 != 16."""
		name = "v703_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_code_16 = "HMDA"
		lar.aus_result_1 = str(random.choice(range(15))+1)
		lar.aus_result_2 = str(random.choice(range(15))+1)
		lar.aus_result_3 = str(random.choice(range(15))+1)
		lar.aus_result_4 = str(random.choice(range(15))+1)
		lar.aus_result_5 = str(random.choice(range(15))+1)
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v704_1(self):
		"""Set action taken = 6 and set AUS 1 to 1-5."""
		name = "v704_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = "6"
		lar.aus_1 = str(random.choice(range(5))+1)
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v704_2(self):
		"""Set action taken = 6 and set AUS Result 1 to 1-16."""
		name = "v704_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = "6"
		lar.aus_result_1 = str(random.choice(range(16))+1)
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v705_1(self):
		"""Set app ethnicity 1 = 4 and app race 1 = 7 and app sex = 4 (non-natural person).
			Set co-app ethnicity 1 = 5 and co app race 1 = 8 and co app sex = 5.
			Set AUS 1 to 1-5.
			Set AUS Result 1 to 1-16."""
		name = "v705_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_1 = "4"
		lar.app_race_1 = "7"
		lar.app_sex = "4"
		lar.co_app_eth_1 = "5"
		lar.co_app_race_1 = "8"
		lar.co_app_sex = "5"
		lar.aus_1 = str(random.choice(range(5))+1)
		lar.aus_result_1 = str(random.choice(range(16))+1)
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v705_2(self):
		"""Set app ethnicity 1 = 4 and app race 1 = 7 and app sex = 4.
			Set co-app ethnicity 1 = 5 and co app race 1 = 8 and co app sex = 5.
			Set AUS 1 = 1-5 and AUS Result 1 = 1-16."""
		name = "v705_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_1 = "4"
		lar.app_race_1 = "7"
		lar.app_sex = "4"
		lar.co_app_eth_1 = "4"
		lar.co_app_race_1 = "7"
		lar.co_app_sex = "4"
		lar.aus_1 = str(random.choice(range(5))+1)
		lar.aus_result_1 = str(random.choice(range(16))+1)
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v706(self):
		"""Set reverse mortgage to 0 or blank."""
		name = "v706.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.reverse_mortgage = random.choice(("0", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v707(self):
		"""Set Open-End Line of Credit to 0 or blank."""
		name = "v707.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.open_end_credit = random.choice(("0", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)
