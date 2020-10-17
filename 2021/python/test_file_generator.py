import json
import os
import pandas as pd
import random
import string
import yaml
import utils

class test_data_creator(object):
	"""This class alters clean synthetic data files in order to cause the 
	altered file to fail the specified edit. Modified files may fail other 
	edits as well."""

	def __init__(self, state_codes, county_df, bank_config_data, filepath_config="configurations/test_filepaths.yaml",
		lar_schema_file="../schemas/lar_schema.json", ts_schema_file="../schemas/ts_schema.json"):
		"""Set initial class variables.

		The crosswak_data variable contains the filepath and name for geographic 
		cross walk data located in the dependencies folder. The geographic data file contains 
		relationships between variables such as state, county, census tract, MSA, and 
		population that are used to generate clean files and edit files. The file 
		is located in "dependencies/census_2018_MSAMD_name.txt."

		state_codes: dictionary of state letter codes to FIPS code
		county_list: dataframe of of 5 digit county codes and a small county indicator
		"""
		with open(lar_schema_file, 'r') as f:
			lar_schema_json = json.load(f)
		self.lar_schema_df = pd.DataFrame(lar_schema_json)

		with open(ts_schema_file, 'r') as f:
			ts_schema_json = json.load(f)
		self.ts_schema_df = pd.DataFrame(ts_schema_json)

		with open(filepath_config, 'r') as f:
			filepaths = yaml.safe_load(f)

		if bank_config_data is None:
			with open("configations/bank1_config.yaml", "r") as f:
				self.bank_config_data = yaml.safe_load(f)

		self.state_codes = state_codes
		self.county_df = county_df

		self.bank_config_data = bank_config_data
		self.name_prefix = "{bank_name}_{line_count}_".format(bank_name=self.bank_config_data["name"]["value"], 
															line_count=self.bank_config_data["file_length"]["value"])

		self.clean_file_path = filepaths['clean_filepath'].format(bank_name=self.bank_config_data["name"]["value"])
		self.validity_path = filepaths['validity_filepath'].format(bank_name=self.bank_config_data["name"]["value"])
		self.syntax_path = filepaths['syntax_filepath'].format(bank_name=self.bank_config_data["name"]["value"])
		self.quality_path = filepaths['quality_filepath'].format(bank_name=self.bank_config_data["name"]["value"])

		self.test_file_funcs = []
		for func in dir(self): 
			#Checks if function is a numbered syntax, validity, or quality edit.
			if func[:1] in ("s", "v", "q") and func[1:4].isdigit()==True: 
				self.test_file_funcs.append(func)

		del filepaths

	def load_lar_data(self, lar_df):
		"""
		Takes a dataframe of LAR data and stores it as a class variable.
		attempts a converstion to dataframe if passed object is not a dataframe
		"""
	
		try: 
			lar_df = pd.DataFrame(lar_df)
		except:
			lar_df = pd.DataFrame(lar_df, index=[1])

		self.lar_df = lar_df

	def load_ts_data(self, ts_df):
		"""
		Takes a dataframe of TS data and stores it as a class variable. TS data must be a single row.
		attempts a converstion to dataframe if passed object is not a dataframe
		"""	
		try:
			self.ts_df = ts_df
		except:
			ts_df = pd.DataFrame(ts_df, index=[0])
			
		self.ts_df = ts_df

	def get_different_state_code(self, state):
		"""
		Returns a random choice of a state letter code that is different from the original
		"""
		state_abbrevs = list(self.state_codes.keys())
		state_abbrevs.remove(state)
		new_state = random.choice(state_abbrevs)
		return random.choice(state_abbrevs)

	#edits will be broken out into sub parts as in the rules_engine.py class. 
	#This will allow test files to be generated that fail conditions inside each edit.

	def s300_1(self):
		"""
		Sets the first character of the first row of the file to 3.
		"""
		name = self.name_prefix + "s300_1.txt"
		ts = self.ts_df.copy() #change to local data from class data object
		lar = self.lar_df.copy()
		ts.record_id = "3" #modify local data to fail edit test
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=self.syntax_path, ts_input=ts, lar_input=lar)

	def s300_2(self):
		""""
		Sets the first character of each LAR row to 3.
		"""
		name = self.name_prefix + "s300_2.txt"
		path = self.syntax_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy() #set to local data from class data object
		lar.record_id = "3" #modify data to fail edit test
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def s301(self):
		"""
		Changes the LEI of a LAR file such that it does not match the TS.
		"""
		name = self.name_prefix + "s301.txt"
		path = self.syntax_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.lei = "KUGELSCHREIBER123456"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def s302(self):
		"""
		Sets the year of submission to 2017
		"""

		name = self.name_prefix + "s302.txt"
		path = self.syntax_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.calendar_year = "2017"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def s306(self):
		"""
		Create duplicate ULIs in LAR data
		"""
		name = self.name_prefix + "s306.txt"
		path = self.syntax_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.uli = "BANK1LEIFORTEST1234509275VSFL41TP9CR2BYRXW507"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v600(self):
		"""
		Modifies the LEI of TS and LAR so that they do not meed schema requirements
		"""
		name = self.name_prefix + "v600.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.lei = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
		lar.lei = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def s304(self):
		"""
		Changes the number of entries data so that it does not match the number of LAR rows in the file.
		"""
		name = self.name_prefix + "s304.txt"
		path = self.syntax_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.lar_entries = 0
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v601_1(self):
		"""
		Modifies the TS to blank the FI name.
		"""

		name = self.name_prefix + "v601_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.inst_name = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v601_2(self):
		"""
		Modify the TS by blanking out the contact person's name.
		"""

		name = self.name_prefix + "v601_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.contact_name = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v601_3(self):
		"""
		Modify the TS by blanking the contact person's E-mail address.
		"""
		name = self.name_prefix + "v601_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.contact_email = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v601_4(self):
		"""
		Modify the TS so to blank out the contact person's office street address.
		"""
		name = self.name_prefix + "v601_4.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.contact_street_address = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v601_5(self):
		"""
		"""
		name = self.name_prefix + "v601_5.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.office_city = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v602(self):
		"""
		Changes TS calendar quarter to 5.
		"""
		name = self.name_prefix + "v602.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.calendar_quarter = "5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v603(self):
		"""
		Changes contact number to alphanumeric string.
		"""
		name = self.name_prefix + "v603.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.contact_tel = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v604(self):
		"""
		Converts contact person's office state to two digit number.
		"""
		name = self.name_prefix + "v604.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.office_state = str(random.randint(10,99))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v605(self):
		"""
		Convert contact person's ZIP to string of letters.
		"""
		name = self.name_prefix + "v605.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.office_zip = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v606(self):
		"""
		Convert number of entries to a negative number.
		"""
		name = self.name_prefix + "v606.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.lar_entries = "-15"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v607(self):
		"""
		Changes tax ID to string of letters.
		"""
		name = self.name_prefix + "v607.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.tax_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)


	def v608_1(self):
		"""
		Set a ULI to be a random choice of 22 characters or 49 characters
		eithr LEI + 29 characters or LEI + 2 characters

		The required format for ULI is alphanumeric with at least 23 characters and up to 45 characters, and it
		cannot be left blank. 

		The platform checks V608 in two parts depending on if the first 20 characters of the ULI/NULI are the LEI
		"""

		name = self.name_prefix + "v608_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar['uli'] = random.choice([lar.lei + "DCM78AVG3FFL1YB5H2BR2EDJKLMNO", lar.lei+"AB"])
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v608_2(self):
		"""
		Set a NULI to be 29 characters.

		The required format for NULI is alphanumeric with at least 1 character and no more than 22 characters,
		and it cannot be left blank.
		"""
		name = self.name_prefix + "v608_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar["uli"] = "DCM78AVG3FFL1YB5H2BR2EDJKLMNO"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)


	def v609(self):
		"""
		Change check digit on each row. Ensure that the new check digit fails.
		"""
		name = self.name_prefix + "v609.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		#lar.uli = lar.uli.map(lambda x: x[:-2] + "xy")
		lar.uli = lar.lei.map(lambda x: x + ''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(10)))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v610_1(self):
		"""
		Change application date to nine 2's.
		"""
		name = self.name_prefix + "v610_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_date = "22222222"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v610_2(self):
		"""
		Set each row to action taken = 3 and application date = NA.
		"""
		name = self.name_prefix + "v610_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_date = "NA"
		lar.action_taken = "3"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def s305(self):
		"""
		Copies the first line of the file into all subsequent lines.
		"""
		name = self.name_prefix + "s305.txt"
		path = self.syntax_path
		ts = self.ts_df.copy()
		lar_start = self.lar_df.copy()
		line = pd.DataFrame(lar_start.iloc[0]).transpose()
		lar = line.copy()
		for i in range(len(lar_start)-1):
			lar = pd.concat([lar, line])
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v611(self):
		"""
		Sets loan type to 5.
		"""
		name = self.name_prefix + "v611.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_type = "5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v612_1(self):
		"""
		Set loan purpose to 3.
		"""
		name = self.name_prefix + "v612_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_purpose = "3"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v612_2(self):
		"""
		Set preapproval to 1 and loan purpose to a random enumeration that is not 1.
		"""
		name = self.name_prefix + "v612_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.preapproval = "1"
		lar.loan_purpose = lar.loan_purpose.map(lambda x: random.choice(["2", "31", "32", "4", "5"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v613_1(self):
		"""
		Set preapproval to 3.
		"""
		name = self.name_prefix + "v613_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.preapproval =  "3"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v613_2(self):
		"""
		Set action to 7 or 8, set preapproval to 2.
		"""
		name = self.name_prefix + "v613_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["7", "8"]))
		lar.preapproval = "2"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v613_3(self):
		"""
		Set action to random 3, 4, 5, or 6 and preapproval to 1.
		"""
		name = self.name_prefix + "v613_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.preapproval = "1"
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["3", "4", "5", "6"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v613_4(self):
		"""
		Set preapproval to 1 and action taken to random 0, 3, 4, 5, 6.
		"""
		name = self.name_prefix + "v613_4.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.preapproval = "1"
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["0", "3", "4", "5", "6"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v614_1(self):
		"""
		Set loan purpose to random 2, 4, 31, 32, or 5 and preapproval to 1.
		"""
		name = self.name_prefix + "v614_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.preapproval = "1"
		lar.loan_purpose = lar.loan_purpose.map(lambda x: random.choice(["2", "4", "31", "32", "5"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v614_2(self):
		"""
		Set affordable units to 1 and preapproval to 1.
		"""
		name = self.name_prefix + "v614_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.preapproval = "1"
		lar.affordable_units = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v614_3(self):
		"""
		Set reverse mortgage to 1 and preapproval to 1.
		"""
		name = self.name_prefix + "v614_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.preapproval = "1"
		lar.reverse_mortgage = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v614_4(self):
		"""Set open end credit to 1 and preapproval to 1."""
		name = "v614_4.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.preapproval = "1"
		lar.open_end_credit = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v615_1(self):
		"""Set construction method to 3."""
		name = "v615_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.const_method =  "3"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v615_2(self):
		"""Set manufactured interest to random 1, 2, 3 or 4 and construction method to 1."""
		name = "v615_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.manufactured_interest = lar.manufactured_interest.map(lambda x: random.choice(["1", "2", "3", "4"]))
		lar.const_method = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v615_3(self):
		"""Set manufactured type to 1 or 2 and construction method to 1."""
		name = "v615_3.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.manufactured_type = lar.manufactured_type.map(lambda x: random.choice(["1", "2"]))
		lar.const_method = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v616(self):
		"""Set occupancy to 4."""
		name = "v616.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.occ_type =  "4"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v617(self):
		"""Set loan amount to 0."""
		name = "v617.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_amount =  "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v618(self):
		"""Set action taken to 0 or NA."""
		name = "v618.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["0", "NA"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v619_1(self):
		"""Set action taken date to NA."""
		name = "v619_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_date = "NA"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v619_2(self):
		"""Set action taken date to 20160101."""
		name = "v619_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_date = "20160101"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v619_3(self):
		"""Set action taken date to 20160101"""
		name = "v619_3.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_date = "20160101"
		lar.app_date = "20181231"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v620(self):
		"""Set street address to blank."""
		name = "v620.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.street_address = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v621(self):
		"""Set city to blank."""
		name = "v621.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.city = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v622_1(self):
		"""Set street address to random string, set City to NA."""
		name = "v622_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.street_address = lar.street_address.map(lambda x: "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)))
		lar.city = "NA"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v622_2(self):
		"""Set street address to random string, set State to NA."""
		name = "v622_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.street_address = lar.street_address.map(lambda x: "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)))
		lar.state = "NA"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v622_3(self):
		"""Set street address to random string, set ZIP code to NA."""
		name = "v622_3.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		street_addy = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
		lar.street_address = lar.street_address.map(lambda x: random.choice([street_addy, street_addy, "Exempt"]))
		lar.zip_code = "NA"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v623(self):
		"""Set state code to blank or 11."""
		name = "v623.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.state = lar.state.map(lambda x: random.choice(["", "11"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v624(self):
		"""Set ZIP code to blank or random string of letters.

		Impact of S2155: Update to 1) The required format for Zip Code is 12345-1010, 12345, Exempt, or NA, 
		and it cannot be left blank."""
		name = "v624.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		zip_code = "".join(str(random.choice(string.ascii_uppercase + string.digits)) for _ in range(5))
		lar.zip_code = lar.zip_code.map(lambda x: random.choice([zip_code, ""]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v625_1(self):
		"""Set Census Tract to blank or 11 digit letter string."""
		name = "v625_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.tract = lar.tract.map(lambda x: "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(11)))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v625_2(self):
		"""Set Census Tract to 12345679012."""
		name = "v625_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.tract = "12345678901"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v626(self):
		"""Set County to 6 digit number."""
		name = "v626.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.county = "024321"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v627(self):
		"""Set County and Tract to strings of 5 and 11 digit length."""
		name = "v627.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		counties = list(self.county_df.county_fips[self.county_df.county_fips.isin(list(lar.county))])
		lar.county = random.choice(counties)
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v628_1(self):
		"""Set all applicant ethnicity fields to blank."""
		name = "v628_1.txt"
		name = self.name_prefix + name
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

	def v628_2(self):
		"""Set app ethnicity 2-5 to 3."""
		name = "v628_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_2 = "3"
		lar.app_eth_3 = "3"
		lar.app_eth_4 = "3"
		lar.app_eth_5 = "3"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v628_3(self):
		"""Set all applicant ethnicity codes to 1."""
		name = "v628_3.txt"
		name = self.name_prefix + name
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

	def v628_4(self):
		"""Set applicant ethnicity 1 to 3 or 4. Set all other applicant ethnicities to 1."""
		name = "v628_4.txt"
		name = self.name_prefix + name
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

	def v629_1(self):
		"""Set applicant ethnicity basis to 4."""
		name = "v629_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_basis = "4"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v629_2(self):
		"""Set applicant ethnicity basis to 1. Set applicant ethnicity 1 = 3. Set all other applicant ethnicities to 1."""
		name = "v629_2.txt"
		name = self.name_prefix + name
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

	def v629_3(self):
		"""
		Set applicant ethnicity basis to 2. Set applicant ethnicity 1 to 4.
		"""
		name = self.name_prefix + "v629_3.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_basis = "2"
		lar.app_eth_1 = "4"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v630(self):
		"""
		1) If Ethnicity of Applicant or Borrower: 1 equals 4, 
		then Ethnicity of Applicant or Borrower Collected on the Basis of Visual Observation or Surname must equal 3.

		Set applicant ethnicity 1 to 4. Set applicant ethnicity basis to 2.
		"""
		name = self.name_prefix + "v630.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_1 = "4"
		lar.app_eth_basis = "2"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v631_1(self):
		"""
		Set co-app ethnicity 1 to blank. Set co-app ethnicity free text to blank.
		"""
		name = self.name_prefix + "v631_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_eth_1 = ""
		lar.co_app_eth_free = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v631_2(self):
		"""Set co-app ethnicity 2-5 to 3."""
		name = "v631_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_eth_2 = "3"
		lar.co_app_eth_3 = "3"
		lar.co_app_eth_4 = "3"
		lar.co_app_eth_5 = "3"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v631_3(self):
		"""Set all co-app ethnicities to 1."""
		name = "v631_3.txt"
		name = self.name_prefix + name
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

	def v631_4(self):
		"""Set co-app ethnicity 1 to random choice of 3, 4, 5. Set co-app ethnicity 2-5 to 1."""
		name = "v631_4.txt"
		name = self.name_prefix + name
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

	def v632_1(self):
		"""Set co-app ethnicity basis to 5"""
		name = "v632_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_eth_basis = "5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v632_2(self):
		"""Set co-app ethnicity basis to 1. Set co-app ethnicity 1 to 3. 
		Set co-app ethnicity 2 to 3. Set co-app ethnicity 3-5 to 1"""
		name = "v632_2.txt"
		name = self.name_prefix + name
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

	def v632_3(self):
		"""Set co-app ethnicity basis to 2. Set co-app ethnicity 1 to 4."""
		name = "v632_3.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_eth_1 = "4"
		lar.co_app_eth_basis = "2"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v633(self):
		"""Set co-app ethnicity 1 to 4. Set co-app ethnicity basis to 1."""
		name = "v633.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_eth_1 = "4"
		lar.co_app_eth_basis = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v634(self):
		"""For the first half of the file:
		Set co-app ethnicity 1 to 5.
		Set co-app ethnicity basis to 3
		For the second half of the file:
		Set co-app ethnicity 1 to 4.
		Set co-app ethnicity basis to 4."""
		name = "v634.txt"
		name = self.name_prefix + name
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

	def v635_1(self):
		"""Set app race 1 to blank. Set all race text fields to blank."""
		name = "v635_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_race_1 = ""
		lar.app_race_native_text = ""
		lar.app_race_islander_text = ""
		lar.app_race_asian_text = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v635_2(self):
		"""Set app races 2-5 to 6."""
		name = "v635_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_race_2 = "6"
		lar.app_race_3 = "6"
		lar.app_race_4 = "6"
		lar.app_race_5 = "6"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v635_3(self):
		"""Set all applicant race fields to 1."""
		name = "v635_3.txt"
		name = self.name_prefix + name
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

	def v635_4(self):
		"""Set app race to 6 or 7. 
		Set app races 2-5 to random choice of 1-5."""
		name = "v635_4.txt"
		name = self.name_prefix + name
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

	def v636_1(self):
		"""Set app race basis to 4."""
		name = "v636_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_race_basis = "4"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v636_2(self):
		"""Set app race basis to 1. Set app race 1 to blank. Set app races 2-5 to 6."""
		name = "v636_2.txt"
		name = self.name_prefix + name
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

	def v636_3(self):
		"""Set app race basis to 2. Set app race 1 to blank. Set app races 2-5 to 6."""
		name = "v636_3.txt"
		name = self.name_prefix + name
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

	def v637(self):
		"""Set app race 1 to 7. Set app race basis to 1 or 2."""
		name = "v637.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_race_1 = "7"
		lar.app_race_basis = lar.app_race_basis.map(lambda x: random.choice(["1", "2"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v638_1(self):
		"""Set co-app race 1 to blank. Set all co-app race text fields to blank."""
		name = "v638_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_race_1 = ""
		lar.co_app_race_asian_text = ""
		lar.co_app_race_islander_text = ""
		lar.co_app_race_native_text = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v638_2(self):
		"""Set co-applicant races 2-5 to 6."""
		name = "v638_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_race_2 = "6"
		lar.co_app_race_3 = "6"
		lar.co_app_race_4 = "6"
		lar.co_app_race_5 = "6"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v638_3(self):
		"""Set all co-applicant race codes to 1."""
		name = "v638_3.txt"
		name = self.name_prefix + name
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

	def v638_4(self):
		"""Set co-applicant race 1 to random choice of 6, 7, 8. Set co-applicant races 2-5 to 1."""
		name = "v638_4.txt"
		name = self.name_prefix + name
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

	def v639_1(self):
		"""Set co-applicant race basis to 5."""
		name = "v639_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_race_basis = "5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v639_2(self):
		"""Set co_app race basis to 1. Set co-app race 1 to 21. Set co-app races 2-5 to 21."""
		name = "v639_2.txt"
		name = self.name_prefix + name
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

	def v639_3(self):
		"""Set co-app race basis to 2. Set co-app race 1 to blank. Set co-app races 2-5 to 6."""
		name = "v639_3.txt"
		name = self.name_prefix + name
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

	def v640(self):
		"""Set co-app race 1 to 7. Set co-app race basis to 1 or 2."""
		name = "v640.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_race_basis = lar.co_app_race_basis.map(lambda x: random.choice(["1", "2"]))
		lar.co_app_race_1 = "7"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v641(self):
		"""Set co-app race 1 = 8. Set co-app race basis to random choice of 1-3."""
		name = "v641.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_race_basis = lar.co_app_race_basis.map(lambda x: random.choice(["1", "2", "3"]))
		lar.co_app_race_1 = "8"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v642_1(self):
		"""Set applicant sex to 5."""
		name = "v642_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_sex = "5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v642_2(self):
		"""Set applicant sex basis to 5."""
		name = "v642_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_sex_basis = "5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v643(self):
		"""
		Set applicant sex basis to 1. Set applicant sex to 3.
		"""
		name = self.name_prefix + "v643.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_sex_basis = "1"
		lar.app_sex = "3"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v644_1(self):
		"""Set applicant sex basis to 2. Set applicant sex to 4 or 5."""
		name = "v644_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_sex_basis = "2"
		lar.app_sex = lar.app_sex.map(lambda x: random.choice(["4", "5"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v644_2(self):
		"""Set applicant sex to 6. Set applicant sex basis to 1."""
		name = "v644_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_sex = "6"
		lar.app_sex_basis = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v645(self):
		"""Set applicant sex to 4. Set applicant sex basis to 1 or 2."""
		name = "v645.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_sex = "4"
		lar.app_sex_basis = lar.app_sex_basis.map(lambda x: random.choice(["1", "2"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v646_1(self):
		"""Set co-applicant sex to 5."""
		name = "v646_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_sex = "5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v646_2(self):
		"""Set co-applicant sex basis to 5."""
		name = "v646_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_sex_basis = "5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v647(self):
		"""
		Set co-app sex basis to 1. Set co-app sex to 3 or 4.
		"""
		name = self.name_prefix + "v647.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_sex_basis = "1"
		lar.co_app_sex = lar.co_app_sex.map(lambda x: random.choice(["3", "4"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v648_1(self):
		"""Set co-app sex basis to 2. Set co-app sex to 4 or 5."""
		name = "v648_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_sex_basis = "2"
		lar.co_app_sex = lar.co_app_sex.map(lambda x: random.choice(["4", "5"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v648_2(self):
		"""
		Set co-app sex to 6. Set co app sex basis to random choice of 1, 4.

		Inclusion of value, 3 is from cfpb/hmda-platform#2774.
		"""
		name = "v648_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_sex_basis = lar.co_app_sex_basis.map(lambda x: random.choice(["1", "4"]))
		lar.co_app_sex = "6"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v649(self):
		"""Set co-app sex to 4. Set co-app sex basis to 1 or 2."""
		name = "v649.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_sex_basis = lar.co_app_sex_basis.map(lambda x: random.choice(["1", "2"]))
		lar.co_app_sex = "4"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v650(self):
		"""Set co-app sex basis to 4. Set co-app sex to random choice of 1-4."""
		name = "v650.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_sex_basis = "4"
		lar.co_app_sex = lar.co_app_sex.map(lambda x: random.choice(["1", "2", "3", "4"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v651_1(self):
		"""Set app age to 0."""
		name = "v651_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_age = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v651_2(self):
		"""Set app ethnicity 1 to 4. Set app race 1 to 7. Set app sex to 4. Set app age to 42."""
		name = "v651_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_1 = "4"
		lar.app_race_1 = "7"
		lar.app_sex = "4"
		lar.app_age = "42"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v652_1(self):
		"""Set co-app age to 0."""
		name = "v652_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_age = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v652_2(self):
		"""Set co-app ethnicity 1 to 4. Set co-app race 1 to 7. Set co-app sex to 4. Set co-app age to 42."""
		name = "v652_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_eth_1 = "4"
		lar.co_app_race_1 = "7"
		lar.co_app_sex = "4"
		lar.co_app_age = "42"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v654_1(self):
		"""Set income to 1.5."""
		name = "v654_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.income = "1.5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v654_2(self):
		"""Set affordable units to 5. Set income to 42."""
		name = "v654_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.affordable_units = "5"
		lar.income = "42"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v655_1(self):
		"""Set app ethnicity 1 to 4. Set app race 1 to 7. Set app sex to 4. Set income to 42."""
		name = "v655_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_1 = "4"
		lar.app_race_1 = "7"
		lar.app_sex = "4"
		lar.income = "42"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v655_2(self):
		"""Set co-app ethnicity 1 to 4. Set co-app race 1 to 7. Set co-app sex to 4. Set income to 42."""
		name = "v655_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_eth_1 = "4"
		lar.co_app_race_1 = "7"
		lar.co_app_sex = "4"
		lar.income = "42"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v656_1(self):
		"""Set purchaser type to 10."""
		name = "v656_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.purchaser_type = "10"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v656_2(self):
		"""Set action taken to random choice of 2, 3, 4, 5, 7, 8. Set purchaser type to random 1-9."""
		name = "v656_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.purchaser_type = lar.purchaser_type.map(lambda x: random.choice(["1", "2", "3", "4", "5", "6", "7", "8", "9"]))
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["2", "3", "4", "5", "7", "8"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v657_1(self):
		"""Set rate spread to blank."""
		name = "v657_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.rate_spread = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v657_2(self):
		"""Set action taken to random choice of 3, 4, 5, 6, 7. Set rate spread to 5.0."""
		name = "v657_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.rate_spread = "5.0"
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["3", "4", "5", "7"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v657_3(self):
		"""Set reverse mortgage to 1. Set rate spread to 5.0."""
		name = "v657_3.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.rate_spread = "5.0"
		lar.reverse_mortgage = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v658_1(self):
		"""Set HOEPA status to 5."""
		name = "v658_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.hoepa = "5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v658_2(self):
		"""Set action taken to random choice of 2, 3, 4, 5, 7, 8. Set HOEPA to 1 or 2."""
		name = "v658_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.hoepa = lar.hoepa.map(lambda x: random.choice(["1", "2"]))
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["2", "3", "4", "5", "7", "8"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v659(self):
		"""Set lien status to 3."""
		name = "v659.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.lien = "3"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v660_1(self):
		"""Set app credit score to "aaa".
		Set action taken to a random choice of 2, 3, 4, 5, 7, or 8."""
		name = "v660_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_credit_score =  "aaa"
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["2", "3", "4", "5", "7", "8"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v660_2(self):
		"""Set app credit score model to 10."""
		name = "v660_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_score_name =  "10"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v661(self):
		"""Set app credit score to 8888. Set app score model to random of 1-8."""
		name = "v661.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_credit_score = "8888"
		lar.app_score_name = lar.app_score_name.map(lambda x: random.choice(["1", "2", "3", "4", "5", "6", "7", "8"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v662_1(self):
		"""Set app credit score model to random of 1-7, 9. Set app score model text field to random string."""
		name = "v662_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_score_code_8 = lar.app_score_code_8.map(lambda x: ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20)))
		lar.app_score_name = lar.app_score_name.map(lambda x: random.choice(["-1", "1", "2", "3", "4", "5", "6", "7", "9"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v662_2(self):
		"""Set app score model to 8. Set app score model text field to blank."""
		name = "v662_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_score_code_8 = ""
		lar.app_score_name = "8"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v663(self):
		""" Set action taken to random of 4, 5, 6. 
		Set app credit score to 700. 
		Set app score model to random 1-8.
		Set app score model text field to random string."""
		name = "v663.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["4", "5", "6"]))
		lar.app_credit_score = "700"
		lar.app_score_name = lar.app_score_name.map(lambda x: random.choice(["1", "2", "3", "4", "5", "6", "7", "8"]))
		lar.app_score_code_8 = lar.app_score_code_8.map(lambda x: "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20)))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v664(self):
		"""Set action taken to random of 4, 5, 6. 
		Set co-app score to 700. 
		Set co-app score model to random 1-8.
		Set co-app score text field to blank."""
		name = "v664.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["4", "5", "6"]))
		lar.co_app_credit_score = "700"
		lar.co_app_score_name = lar.co_app_score_name.map(lambda x: random.choice(["1", "2", "3", "4", "5", "6", "7", "8"]))
		lar.co_app_score_code_8 = lar.co_app_score_code_8.map(lambda x: "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20)))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v665_1(self):
		"""Set co-app score to 'aaa'."""
		name = "v665_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_credit_score = "aaa"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v665_2(self):
		"""Set co-app score name to 0."""
		name = "v665_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_score_name = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v666_1(self):
		"""Set co-app credit score to 8888. Set co app score name to random 1-8."""
		name = "v666_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_credit_score = "8888"
		lar.co_app_score_name = lar.co_app_score_name.map(lambda x: random.choice(["1", "2", "3", "4", "5", "6", "7", "8"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v666_2(self):
		"""Set co-app score to 9999. Set co app score name to random 1-9."""
		name = "v666_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_score_name = lar.co_app_score_name.map(lambda x: random.choice(str(random.randrange(1,10))))
		lar.co_app_credit_score = "9999"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v667_1(self):
		"""Set co-app score name to 1-7, 9, 10. Set co-app score text to random string."""
		name = "v667_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_score_code_8 = lar.co_app_score_code_8.map(lambda x: "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20)))
		lar.co_app_score_name = lar.co_app_score_name.map(lambda x: random.choice(["1", "2", "3", "4", "5", "6", "7", "9", "10"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v667_2(self):
		"""Set co-app score name to 8. Set co-app score text to blank."""
		name = "v667_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_score_name = "8"
		lar.co_app_score_code_8 = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v668_1(self):
		"""Set app ethnicity 1 to 4. Set app race 1 to 7. Set app sex to 4. Set app credit score to 700."""
		name = "v668_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_eth_1 = "4"
		lar.app_race_1 = "7"
		lar.app_sex = "4"
		lar.app_credit_score = "700"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v668_2(self):
		"""Set co-app ethnicity to 4. Set co-app race to 7. Set co-app sex to 4. Set co-app credit score to 700."""
		name = "v668_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_eth_1 = "4"
		lar.co_app_race_1 = "7"
		lar.co_app_sex = "4"
		lar.co_app_credit_score = "700"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v669_1(self):
		"""Set denial reason 1 to 25."""
		name = "v669_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.denial_1 = "25"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v669_2(self):
		"""Set denial reason 2-4 to 10 or blank."""
		name = "v669_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.denial_2 = lar.denial_2.map(lambda x: random.choice(["10", ""]))
		lar.denial_3 = lar.denial_3.map(lambda x: random.choice(["10", ""]))
		lar.denial_4 = lar.denial_4.map(lambda x: random.choice(["10", ""]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v669_3(self):
		"""Set all reasons for denial to 1."""
		name = "v669_3.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.denial_1 = "1"
		lar.denial_2 = "1"
		lar.denial_3 = "1"
		lar.denial_4 = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v669_4(self):
		"""Set denial reason 1 to 10. Set denial reasons 2-4 to 2,3,4."""
		name = "v669_4.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.denial_1 = "10"
		lar.denial_2 = lar.denial_2.map(lambda x: random.choice(["2", "3", "4"]))
		lar.denial_3 = lar.denial_3.map(lambda x: random.choice(["2", "3", "4"]))
		lar.denial_4 = lar.denial_4.map(lambda x: random.choice(["2", "3", "4"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v670_1(self):
		"""
		Set action taken to 3 or 7. 
		Set denial reason 1 to 10.

		1) If Action Taken equals 3 or 7, then the Reason for Denial: 1 must equal 1111, 1, 2, 3, 4, 5, 6, 7, 8, or 9.
		"""
		name = "v670_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.denial_1 = "10"
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["3", "7"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v670_2(self):
		"""
		Set action taken to random 1-6, 8. 
		Set denial 1 to random 1-9.

		2) If Reason for Denial: 1 equals 1, 2, 3, 4, 5, 6, 7, 8, or 9, then Action Taken must equal 3 or 7.
		"""
		name = "v670_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["1", "2", "4", "5", "6", "8"]))
		lar.denial_1 = lar.denial_1.map(lambda x: random.choice(["1", "2", "3", "4", "5", "6", "7", "8", "9"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v670_3(self):
		"""
		Set Denial 1 to random of 1, 2, 3, 4, 5, 6, 7, 8, or 9
		Set action taken to random of 1, 2, 4, 5, 6, 8

		3) If Action Taken equals 1, 2, 4, 5, 6, or 8, then Reason for Denial: 1 must equal 1111 or 10.
		"""
		name = "v670_3.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.denial_1 = random.choice(["1", "2", "3", "4", "5", "6", "7", "8", "9"])
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["1", "2", "4", "5", "6", "8"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v670_4(self):
		"""

		4) If Reason for Denial: 1 equals 10, then Action Taken must equal 1, 2, 4, 5, 6, or 8.
		"""
		name = "v670_4.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.denial_1 = "10"
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["3", "7"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v671_1(self):
		"""Set denial 1-4 to code 9. Set denial text to blank."""
		name = self.name_prefix + "v671_1.txt"
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

	def v671_2(self):
		"""Set denial 1-4 to random 1-8. Set denial text to random string."""
		name = "v671_2.txt"
		name = self.name_prefix + name
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

	def v672_1(self):
		"""Set loan costs to -1."""
		name = "v672_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_costs = "-1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v672_2(self):
		"""Set points and fees to 1. Set loan costs to 500."""
		name = "v672_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.points_fees = "1"
		lar.loan_costs = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v672_3(self):
		"""Set reverse mortgage to 1. Set loan costs to 500."""
		name = "v672_3.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.reverse_mortgage = "1"
		lar.loan_costs = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v672_4(self):
		"""Set open-end-credit to 1. Set loan costs to 500."""
		name = "v672_4.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.open_end_credit = "1"
		lar.loan_costs = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v672_5(self):
		"""Set business purpose to 1. Set loan costs to 500."""
		name = "v672_5.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.business_purpose = "1"
		lar.loan_costs = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v672_6(self):
		""" Set action taken to random of 2, 3, 4, 5, 7, 8. Set loan costs to 500."""
		name = "v672_6.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["2", "3", "4", "5", "7", "8"]))
		lar.loan_costs = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v673_1(self):
		"""Set points and fees to -1 or blank."""
		name = "v673_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.points_fees = lar.points_fees.map(lambda x: random.choice(["-1", ""]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v673_2(self):
		"""Set action taken to random of 2, 3, 4, 5, 6, 7 or 8. Set points and fees to 500."""
		name = "v673_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.points_fees = "500"
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["2", "3", "4", "5", "6", "7", "8"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v673_3(self):
		"""Set reverse mortgage to 1. Set points and fees to 500."""
		name = "v673_3.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.reverse_mortgage = "1"
		lar.points_fees = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v673_4(self):
		"""Set business purpose to 1. Set points and fees to 500."""
		name = "v673_4.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.business_purpose = "1"
		lar.points_fees = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v673_5(self):
		"""Set loan costs to 1. Set points and fees to 500."""
		name = "v673_5.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_costs = "1"
		lar.points_fees = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v674_1(self):
		"""Set origination charges to '-1.'"""
		name = "v674_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.origination_fee = "-1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v674_2(self):
		"""Set reverse mortgage to 1. Set origination charges to 500."""
		name = "v674_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.reverse_mortgage = "1"
		lar.origination_fee = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v674_3(self):
		"""set open-end-credit to 1. Set origination charges to 500."""
		name = "v674_3.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.open_end_credit = "1"
		lar.origination_fee = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v674_4(self):
		"""Set business purpose to 1. Set origination charges to 500."""
		name = "v674_4.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.business_purpose = "1"
		lar.origination_fee = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v674_5(self):
		"""Set action taken to random of 2, 3, 4, 5, 7 or 8. Set origination charges to 500."""
		name = "v674_5.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["2", "3", "4", "5", "7", "8"]))
		lar.origination_fee = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v675_1(self):
		"""Set discount points to 0."""
		name = "v675_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.discount_points = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v675_2(self):
		"""Set reverse mortgage to 1. Set discount points to 500."""
		name = "v675_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.reverse_mortgage = "1"
		lar.discount_points = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v675_3(self):
		"""Set open end credit to 1. Set discount points to 500."""
		name = "v675_3.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.open_end_credit = "1"
		lar.discount_points = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v675_4(self):
		"""Set business purpose to 1. Set discount points to 500."""
		name = "v675_4.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.business_purpose = "1"
		lar.discount_points = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v675_5(self):
		"""Set action taken to random of 2, 3, 4, 5, 7 or 8. Set discount points to 500."""
		name = "v675_5.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["2", "3", "4", "5", "7", "8"]))
		lar.discount_points = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v676_1(self):
		"""Set lender credits to 0 or -1."""
		name = "v676_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.lender_credits = lar.lender_credits.map(lambda x: random.choice(["0", "-1"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v676_2(self):
		"""Set reverse mortgage to 1. Set lender credits to 500."""
		name = "v676_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.reverse_mortgage = "1"
		lar.lender_credits = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v676_3(self):
		"""Set open end credit to 1. Set lender credits to 500."""
		name = "v676_3.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.open_end_credit = "1"
		lar.lender_credits = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v676_4(self):
		"""Set business purpose to 1. Set lender credits to 500."""
		name = "v676_4.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.business_purpose = "1"
		lar.lender_credits = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v676_5(self):
		"""Set action taken to random of 2, 3, 4, 5, 7 or 8. Set lender credits to 500."""
		name = "v676_5.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["2", "3", "4", "5", "7", "8"]))
		lar.lender_credits = "500"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v677_1(self):
		"""Set interest rate to -1."""
		name = "v677_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.interest_rate =  "-1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v677_2(self):
		"""Set action taken to 3, 4, 5, or 7. Set interest rate to 10.0."""
		name = "v677_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["3", "4", "5", "7"]))
		lar.interest_rate = "10.0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v678_1(self):
		"""Set penalty term to 0 or -1."""
		name = "v678_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.prepayment_penalty = lar.prepayment_penalty.map(lambda x: random.choice(["0", "-1"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v678_2(self):
		"""Set action taken to 6. Set penalty term to 30."""
		name = "v678_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = "6"
		lar.prepayment_penalty = "30"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v678_3(self):
		"""Set reverse mortgage to 1. Set penalty term to 30."""
		name = "v678_3.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.reverse_mortgage = "1"
		lar.prepayment_penalty= "30"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v678_4(self):
		"""Set business purpose to 1. Set penalty term to 30."""
		name = "v678_4.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.business_purpose = "1"
		lar.prepayment_penalty = "30"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v678_5(self):
		"""Set penalty term to 360. Set loan term to 30."""
		name = "v678_5.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.prepayment_penalty = "360"
		lar.loan_term = "30"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v679_1(self):
		"""Set DTI to AA."""
		name = "v679_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.dti = "AA"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v679_2(self):
		"""Set action taken to random of 4, 5, 6. Set DTI to 15."""
		name = "v679_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["4", "5", "6"]))
		lar.dti = "15"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v679_3(self):
		"""Set affordable units to 1. Set DTI to 15."""
		name = "v679_3.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.affordable_units = "1"
		lar.dti= "15"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v680_1(self):
		"""Set app eth 1 to 4. Set app race 1 to 7. Set app sex to 4. Set co-app eth 1 to 5.
		Set co-app race 1 to 8. Set co-app sex to 5. Set DTI to 15."""
		name = "v680_1.txt"
		name = self.name_prefix + name
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

	def v680_2(self):
		"""Set app eth 1 to 4. Set app race 1 to 7. Set app sex to 4. Set co-app eth 1 to 4.
		Set co-app race 1 to 7. Set co-app sex to 4. Set DTI to 15."""
		name = "v680_2.txt"
		name = self.name_prefix + name
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

	def v681_1(self):
		"""Set CLTV to 0 or -1."""
		name = "v681_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.cltv = lar.cltv.map(lambda x: random.choice(["0", "-1"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v681_2(self):
		"""Set action taken to random of 4, 5, 6. Set CLTV to 15."""
		name = "v681_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["4", "5", "6"]))
		lar.cltv = "15"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v682_1(self):
		"""Set loan term to 0."""
		name = "v682_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_term = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v682_2(self):
		"""Set reverse mortgage to 1. Set loan term to 30."""
		name = "v682_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.reverse_mortgage = "1"
		lar.loan_term = "30"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v683(self):
		"""Set introductory rate period to 0 or -1."""
		name = "v683.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.intro_rate = lar.intro_rate.map(lambda x: random.choice(["0", "-1"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v684(self):
		"""Set balloon payment to "3" """
		name = "v684.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.balloon = "3"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v685(self):
		"""Set interest only payments to 0."""
		name = "v685.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.int_only_pmts = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v686(self):
		"""Set negative amortization to 0 or blank."""
		name = "v686.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.neg_amort = lar.neg_amort.map(lambda x: random.choice(["0", ""]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v687(self):
		"""Set Other Non-Amortizing features to 0."""
		name = "v687.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.non_amort_features = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v688_1(self):
		"""Set property value to 0."""
		name = "v688_1.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.property_value = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v688_2(self):
		"""Set action taken to 4 or 5. Set property value to 1."""
		name = "v688_2.txt"
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.total_units = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v692_1(self):
		"""Set affordable units to 40.5."""
		name = "v692_1.txt"
		name = self.name_prefix + name
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
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.total_units = lar.total_units.map(lambda x: random.choice(["1", "2", "3", "4"]))
		lar.affordable_units = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)
	
	def v692_3(self):
		"""
		Set total units to 6.
		   Set affordable units to 7.
		   """
		name = "v692_3.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.total_units = "6"
		lar.affordable_units = "7"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v693_1(self):
		"""
		Set app submission to 0.
		"""
		name = self.name_prefix + "v693_1.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_submission = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v693_2(self):
		"""
		Set action taken to 6.
	   	Set app submission to 1 or 2.
	   	"""
		name = self.name_prefix + "v693_2.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = "6"
		lar.app_submission = lar.app_submission.map(lambda x: random.choice(["1", "2"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v693_3(self):
		"""
		Set app submission to 3 and action taken to != 6
		"""
		name = self.name_prefix + "v693_3.txt"
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
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.initially_payable = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v694_2(self):
		"""Set action taken to 6 and initially payable to 1 or 2."""
		name = "v694_2.txt"
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.mlo_id = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v696_1(self):
		"""Set AUS 1 to blank or set AUS 2-5 to 6."""
		name = "v696_1.txt"
		name = self.name_prefix + name
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
		"""Set AUS result 1 to blank and set AUS 2-5 to 25."""
		name = "v696_2.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_result_2 = "25"
		lar.aus_result_3 = "25"
		lar.aus_result_4 = "25"
		lar.aus_result_5 = "25"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v696_3(self):
		"""Set AUS 1 to 1 and AUS 2-5 to blank.
		   Set AUS Result: 1 to 9, AUS Result: 2 to 10,
		   and AUS Result: 3-5 to blank."""
		name = "v696_3.txt"
		name = self.name_prefix + name
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
		"""Set AUS 1 to 5, set AUS Result 1 to 25."""
		name = "v699.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_1 = "5"
		lar.aus_result_1 = "25"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)
		
	def v700_1(self):
		"""Set AUS 1 to 6 and AUS Result 1-5 to 1-16."""
		name = "v700_1.txt"
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.reverse_mortgage = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v707(self):
		"""Set Open-End Line of Credit to 0."""
		name = "v707.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.open_end_credit = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v708(self):
		"""Set Business or Commercial Purpose to 0."""
		name = "v708.txt"
		name = self.name_prefix + name
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.business_purpose = "0"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v709(self):
		"""Set City and Zip Code to Exempt and Street Address to not Exempt"""
		name = "v709.txt"
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		"""
		Set Interest-Only Payments to Exempt ("1111"); set 
		Balloon Payments, Negative Amortizing Features, and Other Non-Amortizing Features 
		to 1.
		"""
		name = self.name_prefix + "v715_c.txt"
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
		"""
		Set Negative Amortizing Features to Exempt ("1111"); set 
		Balloon Payments, Negative Amortizing Features, and Other Non-Amortizing Features 
		to 1.
		"""
		name = self.name_prefix + "v715_d.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.balloon = "1"
		lar.non_amort_features = "1"
		lar.int_only_pmts = "1" 
		lar.neg_amort = "1111" 
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v716(self):
		"""
		Set state and county to invalid combination

		The reported State and County are not a valid combination. If neither State nor County were
		reported NA, then the County must be located within the State.
		"""
		name = self.name_prefix + "v716.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.state = lar.state.apply(lambda x: self.get_different_state_code(x))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v717_a(self):
		"""
		Set email address to blank
		"""

		name = self.name_prefix + "v717_a.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts["contact_email"] = ""
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def v717_b(self):
		"""
		Remove @ symbol from email address
		"""
		name = self.name_prefix + "v717_b.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts["contact_email"] = ts["contact_email"].apply(lambda x: x.replace("@", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)
		
	def v717_c(self):
		"""
		Remove . symbol from email address
		"""
		name = self.name_prefix + "v717_c.txt"
		path = self.validity_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts["contact_email"] = ts["contact_email"].apply(lambda x: x.replace(".", ""))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)
		
	def q600(self):
		"""
		Set all ULIs to same value.
		"""
		name = self.name_prefix + "q600.txt"
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
		name = self.name_prefix + name
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_date = "20160101"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q602(self):
		"""Set street address to NA. Set city and zip code to not NA"""
		name = "q602.txt"
		name = self.name_prefix + name
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
		name = self.name_prefix + name
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.tract = "NA"
		big_counties = list(self.county_df.county_fips[self.county_df.small_county!="1"])
		lar.county = lar.county.map(lambda x: random.choice(big_counties))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)


	def q605_1(self):
		"""Set purchaser to 1 or 3.
		Set loan type != 1."""
		name = "q605_1.txt"
		name = self.name_prefix + name
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
		name = self.name_prefix + name
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.purchaser_type = "2"
		lar.loan_type = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q606(self):
		"""Set income to 40000."""
		name = "q606.txt"
		name = self.name_prefix + name
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.income = "40000"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q607(self):
		"""Set lien status = 2.
		Set loan amount to 300,000."""
		name = "q607.txt"
		name = self.name_prefix + name
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
		name = self.name_prefix + name
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = "1"
		lar.action_date = "20191231"
		lar.app_date = "20191231"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q609(self):
		"""Set purchaser to 1-4.
		Set rate spread to 15%."""
		name = "q609.txt"
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.purchaser_type = lar.purchaser_type.map(lambda x: random.choice(["1","3"]))
		lar.hoepa = "1"		
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q613(self):
		"""
		Set business purpose to 1.
		Set loan purpose to 4.
		"""
		name = self.name_prefix + "q613.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.business_purpose = "1"				
		lar.loan_purpose = "4"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q614_1(self):
		"""Set borrower age to 240"""
		name = self.name_prefix + "q614_1.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_age = "240"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q614_2(self):
		"""
		Set co_borrower age to 240
		"""
		name = self.name_prefix + "q614_2.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_age = "240"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q615_1(self):
		"""
		Set total loan costs to 1000 and origination charges to 500.
		"""
		name = self.name_prefix + "q615_1.txt"
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.points_fees = "100"
		lar.discount_points = "5000"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q617(self):
		"""
		Set CLTV lower than LTV (using loan_amount/property_value).

		If Loan Type equals 1 and Combined Loan-to-Value Ratio and Property Value are not reported NA or Exempt, 
		then the Combined Loan-to Value Ratio generally should be greater than or equal to the Loan to-Value Ratio 
		(calculated as Loan Amount divided by the Property Value).
		"""
		name = self.name_prefix + "q617.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_type = "1"
		lar.cltv = ".08"
		lar.loan_amount = "240000"
		lar.property_value = "240000"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q618(self):
		"""Set construction method to 2 and manufactured home secured property type to 3."""
		name = "q618.txt"
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.loan_type = lar.loan_type.map(lambda x: random.choice(["2","3","4"]))
		lar.total_units = "5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q632(self):
		"""Set all AUS systems to 5.
		Set all AUS results to 5-7."""
		name = "q632.txt"
		name = self.name_prefix + name
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_1 = "3"
		lar.aus_2 = "3"
		lar.aus_3 = "3"
		lar.aus_4 = "3"
		lar.aus_5 = "3"
		lar.aus_result_1 = lar.aus_result_1.map(lambda x: random.choice(["5","6","7"]))
		lar.aus_result_2 = lar.aus_result_2.map(lambda x: random.choice(["5","6","7"]))
		lar.aus_result_3 = lar.aus_result_3.map(lambda x: random.choice(["5","6","7"]))
		lar.aus_result_4 = lar.aus_result_4.map(lambda x: random.choice(["5","6","7"]))
		lar.aus_result_5 = lar.aus_result_5.map(lambda x: random.choice(["5","6","7"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q633(self):
		"""Set all AUS systems to 4.
		Set all AUS results to 1-2, 5-9, 11-14, or 17."""
		name = "q633.txt"
		name = self.name_prefix + name
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_1 = "4"
		lar.aus_2 = "4"
		lar.aus_3 = "4"
		lar.aus_4 = "4"
		lar.aus_5 = "4"
		lar.aus_result_1 = lar.aus_result_1.map(lambda x: random.choice(["1","2","5","6","7","8","9","11","12","13","14","17"]))
		lar.aus_result_2 = lar.aus_result_2.map(lambda x: random.choice(["1","2","5","6","7","8","9","11","12","13","14","17"]))
		lar.aus_result_3 = lar.aus_result_3.map(lambda x: random.choice(["1","2","5","6","7","8","9","11","12","13","14","17"]))
		lar.aus_result_4 = lar.aus_result_4.map(lambda x: random.choice(["1","2","5","6","7","8","9","11","12","13","14","17"]))
		lar.aus_result_5 = lar.aus_result_5.map(lambda x: random.choice(["1","2","5","6","7","8","9","11","12","13","14","17"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def m634(self):
		"""Set action taken to 1.
		Set loan purpose to 1.
		Note: this edit will only trigger for file sizes >= 25."""
		name = "q634.txt"
		name = self.name_prefix + name
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = "1"
		lar.loan_purpose = "1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def m635(self):
		"""Set action taken = 2."""
		name = "q635.txt"
		name = self.name_prefix + name
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = "2"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def m636(self):
		"""Set action taken = 4."""
		name = "q636.txt"
		name = self.name_prefix + name
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = "4"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def m637(self):
		"""Set action taken = 5."""
		name = "q637.txt"
		name = self.name_prefix + name
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = "5"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def m638(self):
		"""Set action taken = 2."""
		name = "q638.txt"
		name = self.name_prefix + name
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = 	"2"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def m639(self):
		"""
		Set preapproval = 1.
		Set action taken to 1-2.
		Note: this edit will only trigger for files with records of more than 1000 
		rows (in addition to the preapproval condition).
		"""
		name = "q639.txt"
		name = self.name_prefix + name
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.preapproval = "1"
		lar.loan_purpose = "1"
		lar.action_taken = lar.action_taken.map(lambda x: random.choice(["1","2"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def m640(self):
		"""Set income to 9."""
		name = "q640.txt"
		name = self.name_prefix + name
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
		name = self.name_prefix + name
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
		name = self.name_prefix + name
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_credit_score = "7777"
		lar.co_app_score_name = lar.co_app_score_name.map(lambda x: random.choice(["1","2","3","4","5","6"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q643(self):
		"""Set AUS systems to 1.
		Set AUS results to 8-14, 17-24."""
		name = "q643.txt"
		name = self.name_prefix + name
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_1 = "1"
		lar.aus_2 = "1"
		lar.aus_3 = "1"
		lar.aus_4 = "1"
		lar.aus_5 = "1"
		lar.aus_result_1 = lar.aus_result_1.map(lambda x: random.choice(["8","9","10","11","12","13","14", 
			"17", "18", "19","20","21","22","23","24"]))
		lar.aus_result_2 = lar.aus_result_2.map(lambda x: random.choice(["8","9","10","11","12","13","14", 
			"17", "18", "19","20","21","22","23","24"]))
		lar.aus_result_3 = lar.aus_result_3.map(lambda x: random.choice(["8","9","10","11","12","13","14", 
			"17", "18", "19","20","21","22","23","24"]))
		lar.aus_result_4 = lar.aus_result_4.map(lambda x: random.choice(["8","9","10","11","12","13","14", 
			"17", "18", "19","20","21","22","23","24"]))
		lar.aus_result_5 = lar.aus_result_5.map(lambda x: random.choice(["8","9","10","11","12","13","14", 
			"17", "18", "19","20","21","22","23","24"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)		

	def q644(self):
		"""Set all AUS systems to 2.
		Set AUS results to 1-7, 14-15, 17-24."""
		name = "q644.txt"
		name = self.name_prefix + name
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.aus_1 = "2"
		lar.aus_2 = "2"
		lar.aus_3 = "2"
		lar.aus_4 = "2"
		lar.aus_5 = "2"
		lar.aus_result_1 = lar.aus_result_1.map(lambda x: random.choice(["1","2","3","4","5","6","7","14",
			"15","17","18","19","20","21","22","23","24"]))
		lar.aus_result_2 = lar.aus_result_2.map(lambda x: random.choice(["1","2","3","4","5","6","7","14",
			"15","17","18","19","20","21","22","23","24"]))
		lar.aus_result_3 = lar.aus_result_3.map(lambda x: random.choice(["1","2","3","4","5","6","7","14",
			"15","17","18","19","20","21","22","23","24"]))
		lar.aus_result_4 = lar.aus_result_4.map(lambda x: random.choice(["1","2","3","4","5","6","7","14",
			"15","17","18","19","20","21","22","23","24"]))
		lar.aus_result_5 = lar.aus_result_5.map(lambda x: random.choice(["1","2","3","4","5","6","7","14",
			"15","17","18","19","20","21","22","23","24"]))
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q645_1(self):
		"""
		Set loan amount to $400.
		"""
		name = "q645_1.txt"
		name = self.name_prefix + name
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()

		lar.loan_amount = '400'

		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q645_2(self):
		"""
		Set loan purpose to 1 and loan amount to $900. 
		"""
		name = "q645_2.txt"
		name = self.name_prefix + name
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()

		lar.loan_purpose = '1'
		lar.loan_amount = '900'

		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def m646_a(self):
		"""
		This tests the TS data condition

		Set Street Address, City, and Zip Code to 'Exempt'.
		"""
		name = "q646_a.txt"
		name = self.name_prefix + name
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()

		lar.street_address = 'Exempt'
		lar.city = 'Exempt'
		lar.zip_code = 'Exempt'

		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def m646_b(self):
		"""
		This tests the LAR data condition
		Set Submission of Application and Initially Payable to 1111.
		"""
		name = "q646_b.txt"
		name = self.name_prefix + name
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()

		lar.app_submission = '1111'
		lar.initially_payable = '1111'

		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def m647_a(self):
		"""
		Set Agency code for TS to 7. Set Street Address, City, and 
		Zip Code in LAR to 'Exempt'.
		"""
		name = self.name_prefix + "q647_a.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.agency_code = '7'
		lar.street_address = 'Exempt'
		lar.city = 'Exempt'
		lar.zip_code = 'Exempt'
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)


	def m647_b(self):
		"""
		Set Agency code for TS to 7. 
		Set Submission of Application and Initially Payable to 1111.
		"""
		name = self.name_prefix + "q647_b.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		ts.agency_code = '7'
		lar.app_submission = '1111'
		lar.initially_payable = '1111'
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q648(self):
		"""
		Set action taken to 6 and set the first 20 characters of the ULI to != the LEI
		If Action Taken equals 1, 2, 3, 4, 5, 7, or 8, the first 20 characters of the ULI should match the reported LEI.
		"""
		name = self.name_prefix + "q648.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.uli = lar.uli.apply(lambda x: "KUGELSCHREIBER123456" + x[20:])
		lar.action_taken = random.choice(["1", "2", "3", "4", "5", "7", "8"])
		#set lar.app_date to other than NA to match removal of 6 from action taken options
		lar.app_df = "20201017"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q649_1(self):
		"""
		Set app credit score to random choice of 200 or 1000

		If Credit Score of Applicant or Borrower does not equal 7777, 8888, or 1111, Credit Score should
		generally be between 300 and 900.
		"""
		name = self.name_prefix + "q649_1.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.app_credit_score = random.choice(["200", "1000"])
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q649_2(self):
		"""
		Set co app credit score to random choice of 200 or 1000

		If Credit Score of Co-Applicant or Co-Borrower does not equal 7777, 8888, 9999, or 1111, 
		Credit Score should generally be between 300 and 900.
		"""
		name = self.name_prefix + "q649_2.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.co_app_credit_score = random.choice(["200", "1000"])
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q650(self):
		"""
		Set interest rate to .1

		The Interest Rate reported is greater than 0 but less than 0.5, which may indicate a misplaced decimal point.
		"""
		name = self.name_prefix + "q650.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.interest_rate = "0.1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q651(self):
		"""
		Set CLTV to .1

		The CLTV reported is greater than 0 but less than 1, which may indicate a misplaced decimal point.
		"""
		name = self.name_prefix + "q651.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		#fix compatibility with v681-2
		lar.action_taken[lar.action_taken.isin(["4", "5", "6"])] = random.choice(["1","2","3","7","8"])
		lar.cltv = "0.1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q652(self):
		"""
		Set DTI to 0.1

		The DTI reported is greater than 0 but less than 1, which may indicate a misplaced decimal point.
		"""
		name = self.name_prefix + "q652.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.dti = "0.1"
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q653_1(self):
		"""
		Set action taken to random choice of 1, 2, or 8 and CLTV to random choice of 0 or 300

		If Action Taken equals 1, 2, or 8, the CLTV should generally be between 0 and 250.
		"""
		name = self.name_prefix + "q653_1.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = random.choice(["1", "2", "8"])
		lar.cltv = random.choice(["0", "250"])
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q653_2(self):
		"""
		Set action taken to random choice of 3, 4, 5, 6, or 7 and CLTV to 0 or 1100

		If Action Taken equals 3, 4, 5, 6, or 7, the CLTV should generally be between 0 and 1,000.
		"""
		name = self.name_prefix + "q653_2.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.action_taken = random.choice(["3", "4", "5", "6", "7"])
		lar.cltv = random.choice(["0", "1100"])
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)

	def q654(self):
		"""
		Set income to 6000, Action Taken to random choice of 1, 2, or 8 and DTI to 0 or 90

		If Income is greater than $5,000 (reported as 5) and Action Taken equals 1, 2, or 8, the DTI should
		generally be between 0 and 80.
		"""
		name = self.name_prefix + "q654.txt"
		path = self.quality_path
		ts = self.ts_df.copy()
		lar = self.lar_df.copy()
		lar.income = "6000"
		lar.action_taken = random.choice(["1", "2", "8"])
		lar.dti = random.choice(["0", "90"])
		print("writing {name}".format(name=name))
		utils.write_file(name=name, path=path, ts_input=ts, lar_input=lar)