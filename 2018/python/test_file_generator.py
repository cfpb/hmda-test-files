import os
import pandas as pd
import random
import string
import yaml
import utils

class test_data(object):
	"""This class alters clean synthetic data files in order to cause the 
	altered file to fail the specified edit. Modified files may fail other 
	edits as well."""

	def __init__(self, ts_schema, lar_schema, crosswalk_data):
		"""
		Set initial class variables.

		The crosswak_data variable contains the filepath and name for geographic 
		cross walk data located in the dependencies folder. The crosswalk data file contains 
		relationships between variables such as state, county, census tract, MSA, and 
		population that are used to generate clean files and edit files. The file 
		is located in "dependencies/census_2018_MSAMD_name.txt."
		"""

		#load configuration data from YAML file
		#use safe_load instead load
		
		#Loads the clean file configuration. 
		with open('configurations/clean_file_config.yaml') as f:
			data_map = yaml.safe_load(f)

		#Loads the filepath configuration. 
		with open('configurations/test_filepaths.yaml') as f:
			filepaths = yaml.safe_load(f)

		#Loads geographic configuration file. 
		with open('configurations/geographic_data.yaml') as f:
			self.geographic = yaml.safe_load(f)
		
		self.clean_file_path = filepaths['clean_filepath'].format(bank_name=data_map["name"]["value"])
		self.validity_path = filepaths['validity_filepath'].format(bank_name=data_map["name"]["value"])
		self.syntax_path = filepaths['syntax_filepath'].format(bank_name=data_map["name"]["value"])
		self.quality_path = filepaths['quality_filepath'].format(bank_name=data_map["name"]["value"])
		
		self.lar_field_names = list(lar_schema.field)
		self.ts_field_names = list(ts_schema.field)

		self.crosswalk_data = crosswalk_data
	
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

	def get_random_state_code(self, state_codes):
		state_code = random.choice(state_codes)
		if state_code in self.geographic['state_FIPS_to_abbreviation']:
			return state_code
		else:
			return self.get_random_state_code(state_codes)

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
		name = "s300_2.txt"
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
		"""Convert number of entries to a negative number."""
		name = "v606.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.lar_entries = "-15"
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

	# under construction
	# def v608_1_file(self):
	# 	"""Set a ULI to be a random choice of 22 characters or 46 characters"""
	# 	name = "v608_1.txt"
	# 	path = self.validity_path
	# 	ts = self.ts_df.copy()
	# 	lar = self.lar_df.copy()
	# 	lar['uli'] = random.choice([lar.lei + "DCM78AVG3FFL1YB5H2BR2EDJKLMNO", lar.lei+"AB"])
	# 	print("writing {name}".format(name=name))
	# 	utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	# def v608_2_file(self):
	# 	"""Set a NULI to be greater than 22 characters."""
	# 	name = "v608_2.txt"
	# 	path = self.validity_path
	# 	ts = self.ts_df.copy()
	# 	lar = self.lar_df.copy()
	# 	lar["uli"] = "DCM78AVG3FFL1YB5H2BR2EDJKLMNO"
	# 	print("writing {name}".format(name=name))
	# 	utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)


	def v609_file(self):
		"""Change check digit on each row. Ensure that the new check digit fails."""
		name = "v609.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		#lar.uli = lar.uli.map(lambda x: x[:-2] + "xy")
		lar.uli = lar.lei.map(lambda x: x + ''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(10)))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v610_1_file(self):
		"""Change application date to nine 2's."""
		name = "v610_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_date = "222222222"
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
		"""Sets loan type to 5."""
		name = "v611.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_type = "5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v612_1_file(self):
		"""Set loan purpose to 3."""
		name = "v612_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_purpose = "3"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v612_2_file(self):
		"""Set preapproval to 1 and loan purpose to a random enumeration that is not 1."""
		name = "v612_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.preapproval = "1"
		lar.loan_purpose = lar.loan_purpose.map(lambda x: random.choice(["2", "31", "32", "4", "5"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v613_1_file(self):
		"""Set preapproval to 3."""
		name = "v613_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.preapproval =  "3"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v613_2_file(self):
		"""Set action to 7 or 8, set preapproval to 2."""
		name = "v613_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["7", "8"]))
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
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["3", "4", "5", "6"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v613_4_file(self):
		"""Set preapproval to 1 and action taken to random 0, 3, 4, 5, 6."""
		name = "v613_4.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.preapproval = "1"
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["0", "3", "4", "5", "6"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v614_1_file(self):
		"""Set loan purpose to random 2, 4, 31, 32, or 5 and preapproval to 1."""
		name = "v614_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.preapproval = "1"
		lar.loan_purpose = lar.loan_purpose.map(lambda x: random.choice(["2", "4", "31", "32", "5"]))
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
		"""Set construction method to 3."""
		name = "v615_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.const_method =  "3"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v615_2_file(self):
		"""Set manufactured interest to random 1, 2, 3 or 4 and construction method to 1."""
		name = "v615_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.manufactured_interest = lar.manufactured_interest.map(lambda x: random.choice(["1", "2", "3", "4"]))
		lar.const_method = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v615_3_file(self):
		"""Set manufactured type to 1 or 2 and construction method to 1."""
		name = "v615_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.manufactured_type = lar.manufactured_type.map(lambda x: random.choice(["1", "2"]))
		lar.const_method = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v616_file(self):
		"""Set occupancy to 4."""
		name = "v616.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.occ_type =  "4"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v617_file(self):
		"""Set loan amount to 0."""
		name = "v617.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_amount =  "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v618_file(self):
		"""Set action taken to 0 or NA."""
		name = "v618.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["0", "NA"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v619_1_file(self):
		"""Set action taken date to NA."""
		name = "v619_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_date = "NA"
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
		lar.street_address = lar.street_address.map(lambda x: "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)))
		lar.city = "NA"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v622_2_file(self):
		"""Set street address to random string, set State to NA."""
		name = "v622_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.street_address = lar.street_address.map(lambda x: "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)))
		lar.state = "NA"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v622_3_file(self):
		"""Set street address to random string, set ZIP code to NA."""
		name = "v622_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		street_addy = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
		lar.street_address = lar.street_address.map(lambda x: random.choice([street_addy, street_addy, "Exempt"]))
		lar.zip_code = "NA"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v623_file(self):
		"""Set state code to blank or 11."""
		name = "v623.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.state = lar.state.map(lambda x: random.choice(["", "11"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v624_file(self):
		"""Set ZIP code to blank or random string of letters.

		Impact of S2155: Update to 1) The required format for Zip Code is 12345-1010, 12345, Exempt, or NA, 
		and it cannot be left blank."""
		name = "v624.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		zip_code = "".join(str(random.choice(string.ascii_uppercase + string.digits)) for _ in range(5))
		lar.zip_code = lar.zip_code.map(lambda x: random.choice([zip_code, ""]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v625_1_file(self):
		"""Set Census Tract to blank or 11 digit letter string."""
		name = "v625_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.tract = lar.tract.map(lambda x: "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(11)))
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
		"""Set applicant ethnicity 1 to 3 or 4. Set all other applicant ethnicities to 1."""
		name = "v628_4.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_1 = lar.app_eth_1.map(lambda x: random.choice(["3", "4"]))
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

	def v630_file(self):
		"""Set applicant ethnicity 1 to 4. Set applicant ethnicity basis to 2."""
		name = "v630.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_basis = "2"
		lar.app_eth_1 = "4"
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
		lar.co_app_eth_1 = lar.co_app_eth_1.map(lambda x: random.choice(["3", "4", "5"]))
		lar.co_app_eth_2 = "1"
		lar.co_app_eth_3 = "1"
		lar.co_app_eth_4 = "1"
		lar.co_app_eth_5 = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v632_1_file(self):
		"""Set co-app ethnicity basis to 5"""
		name = "v632_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_eth_basis = "5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v632_2_file(self):
		"""Set co-app ethnicity basis to 1. Set co-app ethnicity 1 to 3. 
		Set co-app ethnicity 2 to 3. Set co-app ethnicity 3-5 to 1"""
		name = "v632_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_eth_basis = "1"
		lar.co_app_eth_1 = "3"
		lar.co_app_eth_2 = lar.co_app_eth_2.map(lambda x: random.choice(["2", "3"]))
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

	def v633_file(self):
		"""Set co-app ethnicity 1 to 4. Set co-app ethnicity basis to 1."""
		name = "v633.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_eth_1 = "4"
		lar.co_app_eth_basis = "1"
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
		"""Set app race to 6 or 7. 
		Set app races 2-5 to random choice of 1-5."""
		name = "v635_4.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_race_1 = lar.app_race_1.map(lambda x: random.choice(["6", "7"]))
		lar.app_race_2 = lar.app_race_1.map(lambda x: random.choice(["1", "2", "3", "4", "5"]))
		lar.app_race_3 = lar.app_race_1.map(lambda x: random.choice(["1", "2", "3", "4", "5"]))
		lar.app_race_4 = lar.app_race_1.map(lambda x: random.choice(["1", "2", "3", "4", "5"]))
		lar.app_race_5 = lar.app_race_1.map(lambda x: random.choice(["1", "2", "3", "4", "5"]))
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

	def v637_file(self):
		"""Set app race 1 to 7. Set app race basis to 1 or 2."""
		name = "v637.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_race_1 = "7"
		lar.app_race_basis = lar.app_race_basis.map(lambda x: random.choice(["1", "2"]))
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
		lar.co_app_race_1 = lar.co_app_race_1.map(lambda x: random.choice(["6","7","8"]))
		lar.co_app_race_2 = "1"
		lar.co_app_race_3 = "1"
		lar.co_app_race_4 = "1"
		lar.co_app_race_5 = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v639_1_file(self):
		"""Set co-applicant race basis to 5."""
		name = "v639_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_race_basis = "5"
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

	def v640_file(self):
		"""Set co-app race 1 to 7. Set co-app race basis to 1 or 2."""
		name = "v640.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_race_basis = lar.co_app_race_basis.map(lambda x: random.choice(["1", "2"]))
		lar.co_app_race_1 = "7"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v641_file(self):
		"""Set co-app race 1 = 8. Set co-app race basis to random choice of 1-3."""
		name = "v641.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_race_basis = lar.co_app_race_basis.map(lambda x: random.choice(["1", "2", "3"]))
		lar.co_app_race_1 = "8"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v642_1_file(self):
		"""Set applicant sex to 5."""
		name = "v642_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_sex = "5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v642_2_file(self):
		"""Set applicant sex basis to 5."""
		name = "v642_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_sex_basis = "5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v643_1_file(self):
		"""Set applicant sex basis to 1. Set applicant sex to 3."""
		name = "v643.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_sex_basis = "1"
		lar.app_sex = "3"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v644_1_file(self):
		"""Set applicant sex basis to 2. Set applicant sex to 4 or 5."""
		name = "v644_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_sex_basis = "2"
		lar.app_sex = lar.app_sex.map(lambda x: random.choice(["4", "5"]))
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

	def v645_file(self):
		"""Set applicant sex to 4. Set applicant sex basis to 1 or 2."""
		name = "v645.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_sex = "4"
		lar.app_sex_basis = lar.app_sex_basis.map(lambda x: random.choice(["1", "2"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v646_1_file(self):
		"""Set co-applicant sex to 5."""
		name = "v646_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_sex = "5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v646_2_file(self):
		"""Set co-applicant sex basis to 5."""
		name = "v646_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_sex_basis = "5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v647_1_file(self):
		"""Set co-app sex basis to 1. Set co-app sex to 3 or 4."""
		name = "v647.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_sex_basis = "1"
		lar.co_app_sex = lar.co_app_sex.map(lambda x: random.choice(["3", "4"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v648_1_file(self):
		"""Set co-app sex basis to 2. Set co-app sex to 4 or 5."""
		name = "v648_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_sex_basis = "2"
		lar.co_app_sex = lar.co_app_sex.map(lambda x: random.choice(["4", "5"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v648_2_file(self):
		"""Set co-app sex to 6. Set co app sex basis to random choice of 1, 3, 4."""
		name = "v648_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_sex_basis = lar.co_app_sex_basis.map(lambda x: random.choice(["1", "3", "4"]))
		lar.co_app_sex = "6"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v649_file(self):
		"""Set co-app sex to 4. Set co-app sex basis to 1 or 2."""
		name = "v649.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_sex_basis = lar.co_app_sex_basis.map(lambda x: random.choice(["1", "2"]))
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
		lar.co_app_sex = lar.co_app_sex.map(lambda x: random.choice(["1", "2", "3", "4"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v651_1_file(self):
		"""Set app age to 0."""
		name = "v651_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_age = "0"
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
		"""Set co-app age to 0."""
		name = "v652_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_age = "0"
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
		"""Set income to 1.5."""
		name = "v654_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.income = "1.5"
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
		"""Set purchaser type to 10."""
		name = "v656_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.purchaser_type = "10"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v656_2_file(self):
		"""Set action taken to random choice of 2, 3, 4, 5, 7, 8. Set purchaser type to random 1-9."""
		name = "v656_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.purchaser_type = lar.purchaser_type.map(lambda x: random.choice(["1", "2", "3", "4", "5", "6", "7", "8", "9"]))
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["2", "3", "4", "5", "7", "8"]))
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
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["3", "4", "5", "7"]))
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
		"""Set HOEPA status to 5."""
		name = "v658_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.hoepa = "5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v658_2_file(self):
		"""Set action taken to random choice of 2, 3, 4, 5, 7, 8. Set HOEPA to 1 or 2."""
		name = "v658_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.hoepa = lar.hoepa.map(lambda x: random.choice(["1", "2"]))
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["2", "3", "4", "5", "7", "8"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v659_file(self):
		"""Set lien status to 3."""
		name = "v659.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.lien = "3"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v660_1_file(self):
		"""Set app credit score to "aaa".
		Set action taken to a random choice of 2, 3, 4, 5, 7, or 8."""
		name = "v660_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_credit_score =  "aaa"
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["2", "3", "4", "5", "7", "8"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v660_2_file(self):
		"""Set app credit score model to 10."""
		name = "v660_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_score_name =  "10"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v661_file(self):
		"""Set app credit score to 8888. Set app score model to random of 1-8."""
		name = "v661.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_credit_score = "8888"
		lar.app_score_name = lar.app_score_name.map(lambda x: random.choice(["1", "2", "3", "4", "5", "6", "7", "8"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v662_1_file(self):
		"""Set app credit score model to random of 1-7, 9. Set app score model text field to random string."""
		name = "v662_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_score_code_8 = lar.app_score_code_8.map(lambda x: ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20)))
		lar.app_score_name = lar.app_score_name.map(lambda x: random.choice(["-1", "1", "2", "3", "4", "5", "6", "7", "9"]))
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
		""" Set action taken to random of 4, 5, 6. 
		Set app credit score to 700. 
		Set app score model to random 1-8.
		Set app score model text field to random string."""
		name = "v663.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["4", "5", "6"]))
		lar.app_credit_score = "700"
		lar.app_score_name = lar.app_score_name.map(lambda x: random.choice(["1", "2", "3", "4", "5", "6", "7", "8"]))
		lar.app_score_code_8 = lar.app_score_code_8.map(lambda x: "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20)))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v664_file(self):
		"""Set action taken to random of 4, 5, 6. 
		Set co-app score to 700. 
		Set co-app score model to random 1-8.
		Set co-app score text field to blank."""
		name = "v664.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["4", "5", "6"]))
		lar.co_app_credit_score = "700"
		lar.co_app_score_name = lar.co_app_score_name.map(lambda x: random.choice(["1", "2", "3", "4", "5", "6", "7", "8"]))
		lar.co_app_score_code_8 = lar.co_app_score_code_8.map(lambda x: "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20)))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v665_1_file(self):
		"""Set co-app score to 'aaa'."""
		name = "v665_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_credit_score = "aaa"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v665_2_file(self):
		"""Set co-app score name to 0."""
		name = "v665_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_score_name = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v666_1_file(self):
		"""Set co-app credit score to 8888. Set co app score name to random 1-8."""
		name = "v666_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_credit_score = "8888"
		lar.co_app_score_name = lar.co_app_score_name.map(lambda x: random.choice(["1", "2", "3", "4", "5", "6", "7", "8"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v666_2_file(self):
		"""Set co-app score to 9999. Set co app score name to random 1-9."""
		name = "v666_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_score_name = lar.co_app_score_name.map(lambda x: random.choice(str(random.randrange(1,10))))
		lar.co_app_credit_score = "9999"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v667_1_file(self):
		"""Set co-app score name to 1-7, 9, 10. Set co-app score text to random string."""
		name = "v667_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_score_code_8 = lar.co_app_score_code_8.map(lambda x: "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20)))
		lar.co_app_score_name = lar.co_app_score_name.map(lambda x: random.choice(["1", "2", "3", "4", "5", "6", "7", "9", "10"]))
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
		"""Set denial reason 1 to 25."""
		name = "v669_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.denial_1 = "25"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v669_2_file(self):
		"""Set denial reason 2-4 to 10 or blank."""
		name = "v669_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.denial_2 = lar.denial_2.map(lambda x: random.choice(["10", ""]))
		lar.denial_3 = lar.denial_3.map(lambda x: random.choice(["10", ""]))
		lar.denial_4 = lar.denial_4.map(lambda x: random.choice(["10", ""]))
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
		lar.denial_2 = lar.denial_2.map(lambda x: random.choice(["2", "3", "4"]))
		lar.denial_3 = lar.denial_3.map(lambda x: random.choice(["2", "3", "4"]))
		lar.denial_4 = lar.denial_4.map(lambda x: random.choice(["2", "3", "4"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v670_1_file(self):
		"""Set action taken to 3 or 7. Set denial reason 1 to 10."""
		name = "v670_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.denial_1 = "10"
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["3", "7"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v670_2_file(self):
		"""Set action taken to random 1-6, 8. Set denial 1 to random 1-9."""
		name = "v670_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.denial_1 = lar.denial_1.map(lambda x: random.choice(["1", "2", "3", "4", "5", "6", "7", "8", "9"]))
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["1", "2", "4", "5", "6", "8"]))
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
		lar.denial_1 = lar.denial_1.map(lambda x: random.choice(str(random.randrange(1,9))))
		lar.denial_2 = lar.denial_2.map(lambda x: random.choice(str(random.randrange(1,9))))
		lar.denial_3 = lar.denial_3.map(lambda x: random.choice(str(random.randrange(1,9))))
		lar.denial_4 = lar.denial_4.map(lambda x: random.choice(str(random.randrange(1,9))))
		lar.denial_code_9 = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v672_1_file(self):
		"""Set loan costs to -1."""
		name = "v672_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_costs = "-1"
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
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["2", "3", "4", "5", "7", "8"]))
		lar.loan_costs = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v673_1_file(self):
		"""Set points and fees to -1 or blank."""
		name = "v673_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.points_fees = lar.points_fees.map(lambda x: random.choice(["-1", ""]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v673_2_file(self):
		"""Set action taken to random of 2, 3, 4, 5, 6, 7 or 8. Set points and fees to 500."""
		name = "v673_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.points_fees = "500"
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["2", "3", "4", "5", "6", "7", "8"]))
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
		"""Set origination charges to '-1.'"""
		name = "v674_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.origination_fee = "-1"
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
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["2", "3", "4", "5", "7", "8"]))
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
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["2", "3", "4", "5", "7", "8"]))
		lar.discount_points = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v676_1_file(self):
		"""Set lender credits to 0 or -1."""
		name = "v676_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.lender_credits = lar.lender_credits.map(lambda x: random.choice(["0", "-1"]))
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
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["2", "3", "4", "5", "7", "8"]))
		lar.lender_credits = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v677_1_file(self):
		"""Set interest rate to 0 or -1."""
		name = "v677_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.interest_rate = lar.interest_rate.map(lambda x: random.choice(["0", "-1"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v677_2_file(self):
		"""Set action taken to 3, 4, 5, or 7. Set interest rate to 10.0."""
		name = "v677_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["3", "4", "5", "7"]))
		lar.interest_rate = "10.0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v678_1_file(self):
		"""Set penalty term to 0 or -1."""
		name = "v678_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.prepayment_penalty = lar.prepayment_penalty.map(lambda x: random.choice(["0", "-1"]))
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
		"""Set DTI to AA."""
		name = "v679_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.dti = "AA"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v679_2_file(self):
		"""Set action taken to random of 4, 5, 6. Set DTI to 15."""
		name = "v679_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["4", "5", "6"]))
		lar.dti = "15"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v679_3_file(self):
		"""Set affordable units to 1. Set DTI to 15."""
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
		Set co-app race 1 to 7. Set co-app sex to 4. Set DTI to 15."""
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
		"""Set CLTV to 0 or -1."""
		name = "v681_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.cltv = lar.cltv.map(lambda x: random.choice(["0", "-1"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v681_2_file(self):
		"""Set action taken to random of 4, 5, 6. Set CLTV to 15."""
		name = "v681_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["4", "5", "6"]))
		lar.cltv = "15"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v682_1_file(self):
		"""Set loan term to 0."""
		name = "v682_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_term = "0"
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
		"""Set introductory rate period to 0 or -1."""
		name = "v683.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.intro_rate = lar.intro_rate.map(lambda x: random.choice(["0", "-1"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v684_file(self):
		"""Set balloon payment to "3" """
		name = "v684.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.balloon = "3"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v685_file(self):
		"""Set interest only payments to 0."""
		name = "v685.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.int_only_pmts = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v686_file(self):
		"""Set negative amortization to 0 or blank."""
		name = "v686.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.neg_amort = lar.neg_amort.map(lambda x: random.choice(["0", ""]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v687_file(self):
		"""Set Other Non-Amortizing features to 0."""
		name = "v687.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.non_amort_features = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v688_1_file(self):
		"""Set property value to 0."""
		name = "v688_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.property_value = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v688_2_file(self):
		"""Set action taken to 4 or 5. Set property value to 1."""
		name = "v688_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["4", "5"]))
		lar.property_value = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v689_1(self):
		"""Set manufactured type to 0."""
		name = "v689_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.manufactured_type = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v689_2(self):
		"""Set affordable units to 1.
		   Set manufactured type to 1 or 2."""
		name = "v689_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.affordable_units = "1"
		lar.manufactured_type = lar.manufactured_type.map(lambda x: random.choice(["1", "2"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v689_3(self):
		"""Set construction method to 1.
		   Set manufactured type to 1 or 2."""
		name = "v689_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.const_method = "1"
		lar.manufactured_type = lar.manufactured_type.map(lambda x: random.choice(["1", "2"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v690_1(self):
		"""Set manufactured interest to 0."""
		name = "v690_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.manufactured_interest = "0"
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
		lar.manufactured_interest = lar.manufactured_interest.map(lambda x: random.choice(["1", "2", "3", "4"]))
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
		lar.manufactured_interest = lar.manufactured_interest.map(lambda x: random.choice(["1", "2", "3", "4"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v691(self):
		"""Set total units to 0."""
		name = "v691.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.total_units = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v692_1(self):
		"""Set affordable units to 40.5."""
		name = "v692_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.affordable_units = "40.5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v692_2(self):
		"""Set total units to random 1-4.
		   Set affordable units to 0."""
		name = "v692_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.total_units = lar.total_units.map(lambda x: random.choice(["1", "2", "3", "4"]))
		lar.affordable_units = "0"
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
		"""Set app submission to 0."""
		name = "V693_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_submission = "0"
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
		lar.app_submission = lar.app_submission.map(lambda x: random.choice(["1", "2"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v693_3(self):
		"""Set app submission to 3 and action taken to != 6"""
		name = "V693_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_submission = "3"
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["1", "2", "3", "4", "5"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)
		
	def v694_1(self):
		"""Set initially payable to 0."""
		name = "v694_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.initially_payable = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v694_2(self):
		"""Set action taken to 6 and initially payable to 1 or 2."""
		name = "v694_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = "6"
		lar.initially_payable = lar.initially_payable.map(lambda x: random.choice(["1", "2"]))
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
		lar.aus_result_2 = "17"
		lar.aus_result_3 = "17"
		lar.aus_result_4 = "17"
		lar.aus_result_5 = "17"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v696_3(self):
		"""Set AUS 1 to 1 and AUS 2-5 to blank.
		   Set AUS Result: 1 to 9, AUS Result: 2 to 10,
		   and AUS Result: 3-5 to blank."""
		name = "v696_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_1 = "1"
		lar.aus_2 = ""
		lar.aus_3 = ""
		lar.aus_4 = ""
		lar.aus_5 = ""
		lar.aus_result_1 = "9"
		lar.aus_result_2 = "10"
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
		lar.aus_result_1 = lar.aus_result_1.map(lambda x: str(random.choice(range(16))+1))
		lar.aus_result_2 = lar.aus_result_2.map(lambda x: str(random.choice(range(16))+1))
		lar.aus_result_3 = lar.aus_result_3.map(lambda x: str(random.choice(range(16))+1))
		lar.aus_result_4 = lar.aus_result_4.map(lambda x: str(random.choice(range(16))+1))
		lar.aus_result_5 = lar.aus_result_5.map(lambda x: str(random.choice(range(16))+1))
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
		lar.aus_1 = lar.aus_1.map(lambda x: str(random.choice(range(5))+1))
		lar.aus_result_2 = lar.aus_2.map(lambda x: str(random.choice(range(16))+1))
		lar.aus_result_3 = lar.aus_3.map(lambda x: str(random.choice(range(16))+1))
		lar.aus_result_4 = lar.aus_4.map(lambda x: str(random.choice(range(16))+1))
		lar.aus_result_5 = lar.aus_5.map(lambda x: str(random.choice(range(16))+1))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)
		
	def v701(self):
		"""Set AUS 2 to blank and set AUS Result 2 to 1-16."""
		name = "v701.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_2 = ""
		lar.aus_result_2 = lar.aus_result_2.map(lambda x: str(random.choice(range(16))+1))
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
		lar.aus_1 = lar.aus_1.map(lambda x: random.choice(["1", "2", "3", "4"]))
		lar.aus_2 = lar.aus_2.map(lambda x: random.choice(["1", "2", "3", "4"]))
		lar.aus_3 = lar.aus_3.map(lambda x: random.choice(["1", "2", "3", "4"]))
		lar.aus_4 = lar.aus_4.map(lambda x: random.choice(["1", "2", "3", "4"]))
		lar.aus_5 = lar.aus_5.map(lambda x: random.choice(["1", "2", "3", "4"]))
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
		lar.aus_result_1 = lar.aus_result_1.map(lambda x: str(random.choice(range(15))+1))
		lar.aus_result_2 = lar.aus_result_2.map(lambda x: str(random.choice(range(15))+1))
		lar.aus_result_3 = lar.aus_result_3.map(lambda x: str(random.choice(range(15))+1))
		lar.aus_result_4 = lar.aus_result_4.map(lambda x: str(random.choice(range(15))+1))
		lar.aus_result_5 = lar.aus_result_5.map(lambda x: str(random.choice(range(15))+1))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v704_1(self):
		"""Set action taken = 6 and set AUS 1 to 1-5."""
		name = "v704_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = "6"
		lar.aus_1 = lar.aus_1.map(lambda x: str(random.choice(range(5))+1))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v704_2(self):
		"""Set action taken = 6 and set AUS Result 1 to 1-16."""
		name = "v704_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = "6"
		lar.aus_result_1 = lar.aus_result_1.map(lambda x: str(random.choice(range(16))+1))
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
		lar.aus_1 = lar.aus_1.map(lambda x: str(random.choice(range(5))+1))
		lar.aus_result_1 = lar.aus_result_1.map(lambda x: str(random.choice(range(16))+1))
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
		lar.aus_1 = lar.aus_1.map(lambda x: str(random.choice(range(5))+1))
		lar.aus_result_1 = lar.aus_result_1.map(lambda x: str(random.choice(range(16))+1))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v706(self):
		"""Set reverse mortgage to 0."""
		name = "v706.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.reverse_mortgage = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v707(self):
		"""Set Open-End Line of Credit to 0."""
		name = "v707.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.open_end_credit = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v708(self):
		"""Set Business or Commercial Purpose to 0."""
		name = "v708.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.business_purpose = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v709(self):
		"""Set City and Zip Code to Exempt and Street Address to not Exempt"""
		name = "v709.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.street_address = "1234 Hocus Potato Way"
		lar.city = "Exempt"
		lar.zip_code = "Exempt"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v710_1(self):
		"""Set Applicant Credit Score to Exempt ("1111"), and set Co-Applicant Credit Score,
		Applicant Score Name, and Co-Applicant Score Name to 650, 1, and 1 
		respectively."""
		name = "v710_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_credit_score = "1111"
		lar.co_app_credit_score = "650"
		lar.app_score_name = "1"
		lar.co_app_score_name = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v710_2(self):
		"""Set Applicant Credit Score to Exempt("1111"), and set
		Applicant Score Name, Co-Applicant Score Name, Applicant Score Code 8
		and Co-Applicant Score Code 8 to 8, 8, "New Scoring Model", and "New Scoring Model" 
		respectively."""
		name = "v710_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_credit_score = "1111"
		lar.app_score_name = "8"
		lar.co_app_score_name = "8"
		lar.app_score_code_8 = "New Scoring Model"
		lar.co_app_score_code_8 = "New Scoring Model"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v711(self):
		"""Set Denial 1 to Exempt ("1111"), and set
		Denial 2, Denial 3, Denial 4
		and Denial Code 9 to 2, 3, 4, and blank 
		respectively."""
		name = "v711.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.denial_1 = "1111"
		lar.denial_2 = "2"
		lar.denial_3 = "3"
		lar.denial_4 = "4"
		lar.denial_code_9 = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v712_a(self):
		"""Set Loan Costs to Exempt, and set
		Points and Fees to 1000."""
		name = "v712_a.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_costs = "Exempt"
		lar.points_fees = "1000"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v712_b(self):
		"""Set Points and Fees to Exempt, and set
		Loan Costs to 1000."""
		name = "v712_b.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_costs = "1000"
		lar.points_fees = "Exempt"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)


	def v713_1(self):
		"""Set AUS 1 to Exempt ("1111"), and AUS Result 1 to 1."""
		name = "v713_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_1 = "1111"
		lar.aus_result_1 = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)
	
	def v713_2(self):
		"""Set AUS 1 to Exempt ("1111"), AUS 2-5, AUS Result 2-5, 
		AUS Code 5, and AUS Code 16 to 1."""
		name = "v713_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_1 = "1111"
		lar.aus_2 = "1"
		lar.aus_3 = "1"
		lar.aus_4 = "1"
		lar.aus_5 = "1"
		lar.aus_result_1 = "1"
		lar.aus_result_2 = "1"
		lar.aus_result_3 = "1"
		lar.aus_result_4 = "1"
		lar.aus_result_5 = "1"
		lar.aus_code_5 = "1"
		lar.aus_code_16 = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)
		
	def v714_a(self):
		"""Set Submission of Application to Exempt ("1111") and Initially Payable
			to Your Institution to 1."""
		name = "v714_a.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_submission = "1111"
		lar.initially_payable= "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v714_b(self):
		"""Set Initially Payable to Your Institution to Exempt ("1111") and 
		Submission of Application to 1."""
		name = "v714_b.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_submission = "1"
		lar.initially_payable= "1111"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v715_a(self):
		"""Set Balloon Payments to Exempt ("1111"); set 
		Interest-Only Payments, Negative Amortizing Features, and Other Non-Amortizing Features 
		to 1."""
		name = "v715_a.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.balloon = "1111"
		lar.non_amort_features = "1"
		lar.int_only_pmts = "1" 
		lar.neg_amort = "1" 
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v715_b(self):
		"""Set Other Non-Amortizing Features to Exempt ("1111"); set 
		Interest-Only Payments, Negative Amortizing Features, and Balloon Payments 
		to 1."""
		name = "v715_b.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.balloon = "1"
		lar.non_amort_features = "1111"
		lar.int_only_pmts = "1" 
		lar.neg_amort = "1" 
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v715_c(self):
		"""Set Interest-Only Payments to Exempt ("1111"); set 
		Balloon Payments, Negative Amortizing Features, and Other Non-Amortizing Features 
		to 1."""
		name = "v715_c.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.balloon = "1"
		lar.non_amort_features = "1"
		lar.int_only_pmts = "1111" 
		lar.neg_amort = "1" 
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v715_d(self):
		"""Set Negative Amortizing Features to Exempt ("1111"); set 
		Balloon Payments, Negative Amortizing Features, and Other Non-Amortizing Features 
		to 1."""
		name = "v715_d.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.balloon = "1"
		lar.non_amort_features = "1"
		lar.int_only_pmts = "1" 
		lar.neg_amort = "1111" 
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q600(self):
		"""Set all ULIs to same value."""
		name = "q600.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		uli = lar.uli.iloc[0]
		lar.uli = uli
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q601(self):
		"""Set all application dates to 2 or more years prior to action taken date."""
		name = "q601.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_date = "20150101"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q602(self):
		"""Set street address to NA. Set city and zip code to not NA"""
		name = "q602.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.street_address = "NA"
		lar.city = "tatertown"
		lar.zip_code = "55555"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q603(self):
		"""Set county to non-small county.
			Set census tract = NA."""
		name = "q603.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.tract = "NA"
		big_counties = list(self.crosswalk_data.county_fips[self.crosswalk_data.small_county!="1"])
		lar.county = lar.county.map(lambda x: random.choice(big_counties))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q604(self):
		"""Set state to != NA.
		Set county to an invalid code for the chosen state."""
		name = "q604.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		state_codes = list(self.crosswalk_data.state_code)
		lar.state = lar.state.map(lambda x: self.geographic['state_FIPS_to_abbreviation'][self.get_random_state_code(state_codes)])
		#Sets a state code for each LAR and a county code that does not match the state code. 
		for index, row in lar.iterrows():
			state_code = self.get_random_state_code(state_codes)
			state_abbrev = self.geographic['state_FIPS_to_abbreviation'][state_code]
			row["state"] = state_abbrev
			row["county"] = random.choice(list(self.crosswalk_data.county_fips[self.crosswalk_data.state_code!=state_code]))
			#forces the census tract to conform to an appropriate subset of county codes in order to pass v625 and v627. 
			row["tract"] = row["county"] + random.choice(list(self.crosswalk_data.tracts[(self.crosswalk_data.county_fips == row["county"])]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q605_1(self):
		"""Set purchaser to 1 or 3.
		Set loan type != 1."""
		name = "q605_1.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.purchaser_type = lar.purchaser_type.map(lambda x: random.choice(["1", "3"]))
		lar.loan_type = lar.loan_type.map(lambda x: random.choice(["2", "3", "4"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q605_2(self):
		"""Set purchaser to 2.
		Set loan type to 1."""
		name = "q605_2.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.purchaser_type = "2"
		lar.loan_type = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q606(self):
		"""Set income to 4000."""
		name = "q606.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.income = "4000"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q607(self):
		"""Set lien status = 2.
		Set loan amount to 300,000."""
		name = "q607.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.lien = "2"
		lar.loan_amount = "300"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q608(self):
		"""Set action taken to 1.
		Set action taken date the same day as the application date."""
		name = "q608.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = "1"
		lar.action_date = "20181231"
		lar.app_date = "20181231"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q609(self):
		"""Set purchaser to 1-4.
		Set rate spread to 15%."""
		name = "q609.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.purchaser_type = lar.purchaser_type.map(lambda x: random.choice(["1", "2", "3", "4"]))
		lar.rate_spread = "15.59"		
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q610(self):
		"""Set action taken to 1.
		Set lien status to 1.
		Set rate spread to 8%.
		Set HOEPA to 2 or 3."""
		name = "q610.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.lien = "1"
		lar.rate_spread = "8.00"
		lar.hoepa = lar.hoepa.map(lambda x: random.choice(["2", "3"]))
		lar.action_taken = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q611(self):
		"""Set action taken to 1.
		Set lien status to 2.
		Set rate spread to 10%.
		Set HOEPA to 2 or 3."""
		name = "q611.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.lien = "2"
		lar.rate_spread = "10.124"
		lar.hoepa = lar.hoepa.map(lambda x: random.choice(["2","3"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)		

	def q612(self):
		"""Set purchaser to 1 or 3.
		Set HOEPA Status to 1."""
		name = "q612.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.purchaser_type = lar.purchaser_type.map(lambda x: random.choice(["1","3"]))
		lar.hoepa = "1"		
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q613(self):
		"""Set business purpose to 1.
		Set loan purpose to 4."""
		name = "q613.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.business_purpose = "1"				
		lar.loan_purpose = "4"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q614(self):
		"""Set borrower age to 240"""
		name = "q614.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_age = "240"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q615_1(self):
		"""Set total loan costs to 1000 and origination charges to 500."""
		name = "q615_1.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_costs = "1000"
		lar.origination_fee = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q615_2(self):
		"""Set origination charges to 1000 and points and fees to 500."""
		name = "q615_2.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.origination_fee = "1000"		
		lar.points_fees = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q616_1(self):
		"""Set total loan costs lower than discount points."""
		name = "q616_1.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_costs = "10000"
		lar.discount_points = "50000"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q616_2(self):
		"""Set total points and fees lower than discount points."""
		name = "q616_2.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.points_fees = "100"
		lar.discount_points = "5000"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q617(self):
		"""Set CLTV lower than LTV (using loan_amount/property_value)."""
		name = "q617.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.cltv = "1.0"
		lar.loan_amount = "240000"
		lar.property_value = "240000"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q618(self):
		"""Set construction method to 2 and manufactured home secured property type to 3."""
		name = "q618.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.const_method = "2"
		lar.manufactured_type = "3"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q619(self):
		"""Set construction method to 2 and manufactured home land property interest to 5"""
		name = "q619.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.const_method = "2"
		lar.manufactured_interest = "5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q620(self):
		"""Set business or commercial purpose to 2 and NMLSR ID to not NA."""
		name = "q620.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.business_purpose = "2"
		lar.mlo_id = "NA"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q621(self):
		"""Set NMLSR to length > 12 characters (1/2 file)
		Set NMLSR to 12 characters with special characters (1/2 file)"""
		name = "q621.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		file_length = len(lar)
		mlo_id = "12345abcde!!"
		lar['mlo_id'] = mlo_id
		lar['mlo_id'][lar.index>int(file_length/2)] = lar['mlo_id'].apply(lambda x: x.replace("!","1")+"1")
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q622(self):
		"""Set reverse mortgage to 1 and age to 15."""
		name = "q622.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_age = "15"
		lar.reverse_mortgage = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q623(self):
		"""Set total units to <= 4.
		Set income to <200.
		Set loan amount to 3,000,000."""
		name = "q623.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.total_units = lar.total_units.map(lambda x: random.choice(["1", "2", "3", "4"]))
		lar.income = "150"
		lar.loan_amount = "3000000"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q624(self):
		"""Set loan type to 2.
		Set total units to 1.
		Set amount to 700,000."""
		name = "q624.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_type = "2"
		lar.total_units = "1"
		lar.loan_amount = "700000"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q625(self):
		"""Set loan type to 3.
		Set total units <= 4.
		Set loan amount to 1,200,000."""
		name = "q625.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_type = "3"
		lar.total_units = lar.total_units.map(lambda x: random.choice(["1", "2", "3", "4"]))
		lar.loan_amount = "1200000"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q626(self):
		"""Set purchaser to 1-4.
		Set total units to <= 4.
		Set loan amount to 3,000,000."""
		name = "q626.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.purchaser_type = lar.purchaser_type.map(lambda x: random.choice(["1", "2","3","4"]))
		lar.total_units = lar.total_units.map(lambda x: random.choice(["1", "2","3","4"]))
		lar.loan_amount = "3000000"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q627(self):
		"""Set total units to >=5.
		Set loan amount to random of 90000 and 11000000."""
		name = "q627.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.total_units = "5"
		lar.loan_amount = lar.loan_amount.map(lambda x: random.choice(["90000", "11000000"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q628(self):
		"""Set loan purpose to 1.
		Set total units <= 4.
		Set loan amount to 5000."""
		name = "q628.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_purpose = "1"
		lar.total_units = lar.total_units.map(lambda x: random.choice(["1","2","3","4"]))
		lar.loan_amount = "5000"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q629(self):
		"""Set action taken to random choice of 1,2,3,4,5,7,8.
		Set total units <=4.
		Set loan purpose to random choice of 1, 2, 4.
		Set income to NA."""
		name = "q629.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["1","2","3","4"]))
		lar.total_units = lar.total_units.map(lambda x: random.choice(["1","2","3","4"]))
		lar.loan_purpose = lar.loan_purpose.map(lambda x: random.choice(["1","2","4"]))
		lar.income = "NA"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q630(self):
		"""Set total units to 5 or more.
		Set HOEPA status to 1 or 2."""
		name = "q630.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.total_units = "6"
		lar.hoepa = lar.hoepa.map(lambda x: random.choice(["1","2"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q631(self):
		"""Set loan type to 2, 3, or 4.
		Set total units to 5 or more."""
		name = "q631.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_type = lar.loan_type.map(lambda x: random.choice(["2","3","4"]))
		lar.total_units = "5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q632(self):
		"""Set all AUS systems to 5.
		Set all AUS results to 1-7."""
		name = "q632.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_1 = "3"
		lar.aus_2 = "3"
		lar.aus_3 = "3"
		lar.aus_4 = "3"
		lar.aus_5 = "3"
		lar.aus_result_1 = lar.aus_result_1.map(lambda x: random.choice(["1","2","3","4","5","6","7"]))
		lar.aus_result_2 = lar.aus_result_2.map(lambda x: random.choice(["1","2","3","4","5","6","7"]))
		lar.aus_result_3 = lar.aus_result_3.map(lambda x: random.choice(["1","2","3","4","5","6","7"]))
		lar.aus_result_4 = lar.aus_result_4.map(lambda x: random.choice(["1","2","3","4","5","6","7"]))
		lar.aus_result_5 = lar.aus_result_5.map(lambda x: random.choice(["1","2","3","4","5","6","7"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q633(self):
		"""Set all AUS systems to 4.
		Set all AUS results to 1-4, 6-7, 11-12."""
		name = "q633.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_1 = "4"
		lar.aus_2 = "4"
		lar.aus_3 = "4"
		lar.aus_4 = "4"
		lar.aus_5 = "4"
		lar.aus_result_1 = lar.aus_result_1.map(lambda x: random.choice(["1","2","3","4","6","7","11","12"]))
		lar.aus_result_2 = lar.aus_result_2.map(lambda x: random.choice(["1","2","3","4","6","7","11","12"]))
		lar.aus_result_3 = lar.aus_result_3.map(lambda x: random.choice(["1","2","3","4","6","7","11","12"]))
		lar.aus_result_4 = lar.aus_result_4.map(lambda x: random.choice(["1","2","3","4","6","7","11","12"]))
		lar.aus_result_5 = lar.aus_result_5.map(lambda x: random.choice(["1","2","3","4","6","7","11","12"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q634(self):
		"""Set action taken to 1.
		Set loan purpose to 1.
		Note: this edit will only trigger for file sizes >= 25."""
		name = "q634.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = "1"
		lar.loan_purpose = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q635(self):
		"""Set action taken = 2."""
		name = "q635.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = "2"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q636(self):
		"""Set action taken = 4."""
		name = "q636.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = "4"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q637(self):
		"""Set action taken = 5."""
		name = "q637.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = "5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q638(self):
		"""Set action taken = 2."""
		name = "q638.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = 	"2"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q639(self):
		"""Set preapproval = 1.
		Set action taken to 1-2.
		Note: this edit will only trigger for files with records of more than 1000 
		rows (in addition to the preapproval condition).
		If the length of the LAR dataframe is less than or equal to 1000, the resulting 
		test file will be made to have 1001 rows. 
		"""
		name = "q639.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.preapproval = "1"
		#Conforming to pass v612_2. This allows for less syntax and validity edits to fail
		#so that a clean q639.txt file can be produced.
		lar.loan_purpose = "1"
		#Setting action taken either to 1 or 2 to conform to v613_4. 
		#This allows for less syntax and validity edits to fail
		#so that a clean q639.txt file can be produced.
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["1","2"]))
		if len(lar) <= 1000:
			ts, lar = utils.new_lar_rows(row_count=1001, lar_df=lar, ts_df=ts)
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q640(self):
		"""Set income to 9."""
		name = "q640.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.income = "9"		
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q642_1(self):
		"""Set borrower credit score to 7777.
		Set borrower score model to 1-6."""
		name = "q642_1.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_credit_score = "7777"
		lar.app_score_name = lar.app_score_name.map(lambda x: random.choice(["1","2","3","4","5","6"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q642_2(self):
		"""Set co-borrower credit score to 7777.
		Set co-orrower score model to 1-6."""
		name = "q642_2.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_credit_score = "7777"
		lar.co_app_score_name = lar.co_app_score_name.map(lambda x: random.choice(["1","2","3","4","5","6"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q643(self):
		"""Set AUS systems to 1.
		Set AUS results to 8-14."""
		name = "q643.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_1 = "1"
		lar.aus_2 = "1"
		lar.aus_3 = "1"
		lar.aus_4 = "1"
		lar.aus_5 = "1"
		lar.aus_result_1 = lar.aus_result_1.map(lambda x: random.choice(["8","9","10","11","12","13","14"]))
		lar.aus_result_2 = lar.aus_result_2.map(lambda x: random.choice(["8","9","10","11","12","13","14"]))
		lar.aus_result_3 = lar.aus_result_3.map(lambda x: random.choice(["8","9","10","11","12","13","14"]))
		lar.aus_result_4 = lar.aus_result_4.map(lambda x: random.choice(["8","9","10","11","12","13","14"]))
		lar.aus_result_5 = lar.aus_result_5.map(lambda x: random.choice(["8","9","10","11","12","13","14"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)		

	def q644(self):
		"""Set all AUS systems to 2.
		Set AUS results to 1-7."""
		name = "q644.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_1 = "2"
		lar.aus_2 = "2"
		lar.aus_3 = "2"
		lar.aus_4 = "2"
		lar.aus_5 = "2"
		lar.aus_result_1 = lar.aus_result_1.map(lambda x: random.choice(["1","2","3","4","5","6","7"]))
		lar.aus_result_2 = lar.aus_result_2.map(lambda x: random.choice(["1","2","3","4","5","6","7"]))
		lar.aus_result_3 = lar.aus_result_3.map(lambda x: random.choice(["1","2","3","4","5","6","7"]))
		lar.aus_result_4 = lar.aus_result_4.map(lambda x: random.choice(["1","2","3","4","5","6","7"]))
		lar.aus_result_5 = lar.aus_result_5.map(lambda x: random.choice(["1","2","3","4","5","6","7"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)
