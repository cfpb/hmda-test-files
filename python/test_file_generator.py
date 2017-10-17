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