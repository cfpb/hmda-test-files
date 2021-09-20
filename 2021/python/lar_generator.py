import json
import os
import pandas as pd
import random
import string
import time
import yaml

from collections import OrderedDict
import utils

class lar_gen(object):
	"""
	Contains functions to create a valid LAR and TS record
	Functions:
	- date_gen
	- random_enum
	- get_schema_val
	- get_schema_list
	- range_and_enum
	- tract_from_county
	- make_ts_row
	- make_row
	"""
	def __init__(self, lar_schema_file="../schemas/lar_schema.json", ts_schema_file="../schemas/ts_schema.json"):
	#, config_file='configurations/clean_file_config.yaml', geo_config_file='configurations/geographic_data.yaml'):
		"""
		lar_schema_file: JSON file with LAR schema
		ts_schema_file: JSON file with TS schema
		config_file: configuration file holding bank identifers and LAR value configs
		geo_config_file: the FFIEC flat file with census data used in the HMDA Platform see https://github.com/cfpb/hmda-census
		"""
		print("start initialization of LAR generator")

		#load Schemas for valid values for fields for LAR and TS
		with open(lar_schema_file, 'r') as f:
			lar_schema_json = json.load(f)
		self.lar_schema_df = pd.DataFrame(lar_schema_json)

		with open(ts_schema_file, 'r') as f:
			ts_schema_json = json.load(f)
		self.ts_schema_df = pd.DataFrame(ts_schema_json)

		#with open(self.geo_config["zip_code_file"], 'r') as f:
		#	self.zip_codes = json.load(f)
		#self.zip_codes.append("Exempt") #add Exempt as valid zip code
		#self.state_codes_rev = self.geo_config["state_codes_rev"]
		#cleanup unneeded variables
		#del self.geo_config
		del lar_schema_json
		del ts_schema_json
		print("LAR generator initialization complete")

	def date_gen(self, activity_year, valid=True):
		"""Generates and returns a semi-valid date string or an invalid date string. Does not check days per month."""
		months = list(range(1,13))
		days = list(range(1,32))
		if valid:
			valid_date = False
			while valid_date == False:
				date = str(activity_year)+str(random.choice(months)).zfill(2)+str(random.choice(days)).zfill(2)
				try:
					time.strptime(date,'%Y%m%d')
					valid_date = True
				except:
					valid_date = False
		else:
			date = str(lar_file_config["calendar_year"]["value"])+str(16)+str(33)
		return date

	def get_schema_val(self, schema="LAR", position=0, item=0, field=None):
		"""Returns a value from the valid_vals list in the schema for the named field. Default is the first value in the list."""
		if not field:
			raise ValueError("must specify which field")
		if schema=="LAR":
			return self.lar_schema_df.valid_vals[self.lar_schema_df.field==field].iloc[position][item]
		elif schema=="TS":
			return self.ts_schema_df.valid_vals[self.ts_schema_df.field==field].iloc[position][item]
		else:
			pass

	def get_schema_list(self, schema="LAR", field=None, empty=False):
		"""
		Returns the list of valid values for the specified schema and field. 
		Optionally adds blanks to the list of values.
		"""
		
		if not field:
			raise ValueError("must specify which field")

		if schema=="LAR":
			if empty:
				schema_enums = self.lar_schema_df.valid_vals[self.lar_schema_df.field==field].iloc[0]
				schema_enums.append("")
				return schema_enums
			else: 
				return self.lar_schema_df.valid_vals[self.lar_schema_df.field==field].iloc[0]

		elif schema=="TS":
			if empty:
				schema_enums = self.ts_schema_df.valid_vals[self.ts_schema_df.field==field].iloc[0]
				schema_enums.append("")
				return schema_enums
			else:
				return self.ts_schema_df.valid_vals[self.ts_schema_df.field==field].iloc[0]

	def range_and_enum(self, field=None, rng_min=1, rng_max=100, dtype="int", empty=False):
		"""
		Returns a list of integers or floats. 
		if na is True the returned list will contain NA
		if empty is True the returned list will contain an empty string
		"""

		lst=[]
		lst = self.get_schema_list(field=field) #get NA values from schema if present
		if dtype=="int":
			for i in range(rng_min, rng_max):
				lst.append(i)
		elif dtype=="float":
			for i in range(rng_min, rng_max):
				lst.append(i*1.01)
		if empty:
			lst.append("")
		return lst

	def tract_from_county(self, county):
		"""Returns a Census Tract FIPS that is valid for the passed county."""
		valid_tracts = [tract for tract in self.tract_list if tract[:5]==county]
		return random.choice(valid_tracts)

	def make_ts_row(self, bank_file_config):
		"""Creates a TS row as a dictionary and returns it."""
		ts_row = OrderedDict()
		ts_row["record_id"] ="1"
		ts_row["inst_name"] = bank_file_config["name"]["value"]
		ts_row["calendar_year"] = bank_file_config["activity_year"]["value"]
		ts_row["calendar_quarter"] = bank_file_config["calendar_quarter"]["value"]
		ts_row["contact_name"] = bank_file_config["contact_name"]["value"]
		ts_row["contact_tel"] = bank_file_config["contact_tel"]["value"]
		ts_row["contact_email"] = bank_file_config["contact_email"]["value"]
		ts_row["contact_street_address"] = bank_file_config["street_addy"]["value"]
		ts_row["office_city"] = bank_file_config["city"]["value"]
		ts_row["office_state"] = bank_file_config["state"]["value"]
		ts_row["office_zip"] = str(bank_file_config["zip_code"]["value"])
		ts_row["federal_agency"] = bank_file_config["agency_code"]["value"]
		ts_row["lar_entries"]= str(bank_file_config["file_length"]["value"])
		ts_row["tax_id"] = bank_file_config["tax_id"]["value"]
		ts_row["lei"] = bank_file_config["lei"]["value"]
		return ts_row

	#all valid values, including blanks and NAs, are included in the selection lists.
	#Some of these values are added using helper functions if they are not present in the JSON schema.
	def make_row(self, lar_file_config, geographic_data, state_codes, zip_code_list):
		"""Make num_rows LAR rows and return them as a list of ordered dicts"""
		valid_lar_row = OrderedDict() 
		valid_lar_row["record_id"] = str(self.lar_schema_df.valid_vals[self.lar_schema_df.field=="record_id"].iloc[0][0])
		valid_lar_row["lei"] = lar_file_config["lei"]["value"]
		valid_lar_row["uli"] = valid_lar_row['lei'] + utils.char_string_gen(23)
		valid_lar_row["uli"] = valid_lar_row["uli"] + utils.check_digit_gen(ULI=valid_lar_row["uli"])
		valid_lar_row["uli"] = random.choice([valid_lar_row["uli"], utils.char_string_gen(22)])
		valid_lar_row["app_date"] = str(self.date_gen(activity_year=lar_file_config["activity_year"]["value"]))
		valid_lar_row["loan_type"] = str(random.choice(self.get_schema_list(field="loan_type")))
		valid_lar_row["loan_purpose"] = str(random.choice(self.get_schema_list(field="loan_purpose")))
		valid_lar_row["preapproval"] = str(random.choice(self.get_schema_list(field="preapproval")))
		valid_lar_row["const_method"] = str(random.choice(self.get_schema_list(field="const_method")))
		valid_lar_row["occ_type"] = str(random.choice(self.get_schema_list(field="occ_type")))
		valid_lar_row["loan_amount"] = str(random.choice(range(1, lar_file_config["max_amount"]["value"])))
		valid_lar_row["action_taken"] = str(random.choice(self.get_schema_list(field='action_taken')))
		valid_lar_row["action_date"] = str(self.date_gen(activity_year=lar_file_config["activity_year"]["value"]))
		valid_lar_row["street_address"] = random.choice([lar_file_config["street_addy"]["value"], lar_file_config["street_addy"]["value"], "Exempt"])
		valid_lar_row["city"] = lar_file_config["city"]["value"]
		valid_lar_row["state"] = "" #placeholder to preserve LAR order
		valid_lar_row["zip_code"] = random.choice(zip_code_list)
		valid_lar_row["county"] = "" #placeholder to preserve LAR order
		valid_lar_row["tract"] = random.choice(geographic_data["tract_fips"])
		valid_lar_row["state"] = state_codes[str(valid_lar_row["tract"][:2])]
		valid_lar_row["county"] = valid_lar_row["tract"][:5]
		valid_lar_row["app_eth_1"] = str(random.choice(self.get_schema_list(field="app_eth_1", empty=True)))
		valid_lar_row["app_eth_2"] = str(random.choice(self.get_schema_list(field="app_eth_2", empty=True)))
		valid_lar_row["app_eth_3"] = str(random.choice(self.get_schema_list(field="app_eth_3", empty=True)))
		valid_lar_row["app_eth_4"] = str(random.choice(self.get_schema_list(field="app_eth_4", empty=True)))
		valid_lar_row["app_eth_5"] = str(random.choice(self.get_schema_list(field="app_eth_5", empty=True)))
		valid_lar_row["app_eth_free"] = utils.char_string_gen(random.choice(range(100)))
		valid_lar_row["co_app_eth_1"] = str(random.choice(self.get_schema_list(field="co_app_eth_1", empty=True)))
		valid_lar_row["co_app_eth_2"] = str(random.choice(self.get_schema_list(field="co_app_eth_2", empty=True)))
		valid_lar_row["co_app_eth_3"] = str(random.choice(self.get_schema_list(field="co_app_eth_3", empty=True)))
		valid_lar_row["co_app_eth_4"] = str(random.choice(self.get_schema_list(field="co_app_eth_4", empty=True)))
		valid_lar_row["co_app_eth_5"] = str(random.choice(self.get_schema_list(field="co_app_eth_5", empty=True)))
		valid_lar_row["co_app_eth_free"] = utils.char_string_gen(random.choice(range(100)))
		valid_lar_row["app_eth_basis"] = str(random.choice(self.get_schema_list(field="app_eth_basis")))
		valid_lar_row["co_app_eth_basis"] = str(random.choice(self.get_schema_list(field="co_app_eth_basis")))
		valid_lar_row["app_race_1"] = str(random.choice(self.get_schema_list(field="app_race_1", empty=True)))
		valid_lar_row["app_race_2"] = str(random.choice(self.get_schema_list(field="app_race_2", empty=True)))
		valid_lar_row["app_race_3"] = str(random.choice(self.get_schema_list(field="app_race_3", empty=True)))
		valid_lar_row["app_race_4"] = str(random.choice(self.get_schema_list(field="app_race_4", empty=True)))
		valid_lar_row["app_race_5"] = str(random.choice(self.get_schema_list(field="app_race_5", empty=True)))
		valid_lar_row["app_race_native_text"] = utils.char_string_gen(random.choice(range(100)))
		valid_lar_row["app_race_asian_text"] = utils.char_string_gen(random.choice(range(100)))
		valid_lar_row["app_race_islander_text"] = utils.char_string_gen(random.choice(range(100)))
		valid_lar_row["co_app_race_1"] = str(random.choice(self.get_schema_list(field="co_app_race_1", empty=True)))
		valid_lar_row["co_app_race_2"] = str(random.choice(self.get_schema_list(field="co_app_race_2", empty=True)))
		valid_lar_row["co_app_race_3"] = str(random.choice(self.get_schema_list(field="co_app_race_3", empty=True)))
		valid_lar_row["co_app_race_4"] = str(random.choice(self.get_schema_list(field="co_app_race_4", empty=True)))
		valid_lar_row["co_app_race_5"] = str(random.choice(self.get_schema_list(field="co_app_race_5", empty=True)))
		valid_lar_row["co_app_race_native_text"] = utils.char_string_gen(random.choice(range(100)))
		valid_lar_row["co_app_race_asian_text"] = utils.char_string_gen(random.choice(range(100)))
		valid_lar_row["co_app_race_islander_text"] = utils.char_string_gen(random.choice(range(100)))
		valid_lar_row["app_race_basis"] = str(random.choice(self.get_schema_list(field="app_race_basis")))
		valid_lar_row["co_app_race_basis"] = str(random.choice(self.get_schema_list(field="co_app_race_basis")))
		valid_lar_row["app_sex"] = str(random.choice(self.get_schema_list(field="app_sex")))
		valid_lar_row["co_app_sex"] = str(random.choice(self.get_schema_list(field="co_app_sex")))
		valid_lar_row["app_sex_basis"] = str(random.choice(self.get_schema_list(field="app_sex_basis")))
		valid_lar_row["co_app_sex_basis"] = str(random.choice(self.get_schema_list(field="co_app_sex_basis")))
		valid_lar_row["app_age"] = str(random.choice(self.range_and_enum(field="app_age", rng_max=lar_file_config["max_age"]["value"])))
		valid_lar_row["co_app_age"] = str(random.choice(self.range_and_enum(field="co_app_age", rng_max=lar_file_config["max_age"]["value"])))
		valid_lar_row["income"] = str(random.choice(range(1, lar_file_config["max_income"]["value"])))
		valid_lar_row["purchaser_type"] = str(random.choice(self.get_schema_list(field="purchaser_type")))
		valid_lar_row["rate_spread"]= str(random.choice(self.range_and_enum(field="rate_spread", rng_max=lar_file_config["max_rs"]["value"], dtype="float")))
		valid_lar_row["hoepa"] = str(random.choice(self.get_schema_list(field="hoepa")))
		valid_lar_row["lien"] = str(random.choice(self.get_schema_list(field="lien")))
		valid_lar_row["app_credit_score"] = str(random.choice(self.range_and_enum(field="app_credit_score", rng_min=lar_file_config["min_credit_score"]["value"], rng_max=lar_file_config["max_credit_score"]["value"])))
		valid_lar_row["co_app_credit_score"] = str(random.choice(self.range_and_enum(field="co_app_credit_score", rng_min=lar_file_config["min_credit_score"]["value"], rng_max=lar_file_config["max_credit_score"]["value"])))
		valid_lar_row["app_score_name"] = str(random.choice(self.get_schema_list(field="app_score_name")))
		valid_lar_row["app_score_code_8"] = str(utils.char_string_gen(random.choice(range(100))))
		valid_lar_row["co_app_score_name"] = str(random.choice(self.get_schema_list(field="co_app_score_name")))
		valid_lar_row["co_app_score_code_8"] = utils.char_string_gen(random.choice(range(100)))
		valid_lar_row["denial_1"] = str(random.choice(self.get_schema_list(field="denial_1")))
		valid_lar_row["denial_2"] = str(random.choice(self.get_schema_list(field="denial_2", empty=True)))
		valid_lar_row["denial_3"] = str(random.choice(self.get_schema_list(field="denial_3", empty=True)))
		valid_lar_row["denial_4"] = str(random.choice(self.get_schema_list(field="denial_4", empty=True)))
		valid_lar_row["denial_code_9"] = utils.char_string_gen(random.choice(range(255)))
		valid_lar_row["loan_costs"] = str(random.choice(self.range_and_enum(field="loan_costs",rng_max=lar_file_config["loan_costs"]["value"])))
		valid_lar_row["points_fees"] = str(random.choice(self.range_and_enum(field="points_fees", rng_max=lar_file_config["points_and_fees"]["value"])))
		valid_lar_row["origination_fee"] = str(random.choice(self.range_and_enum(field="origination_fee", rng_max=lar_file_config["orig_charges"]["value"])))
		valid_lar_row["discount_points"] = str(random.choice(self.range_and_enum(field="discount_points", rng_max=lar_file_config["discount_points"]["value"], empty=True)))
		valid_lar_row["lender_credits"] = str(random.choice(self.range_and_enum(field="lender_credits", rng_max=lar_file_config["lender_credits"]["value"], empty=True)))
		valid_lar_row["interest_rate"] = str(random.choice(self.range_and_enum(field="interest_rate", rng_max=lar_file_config["interest_rate"]["value"], dtype="float")))
		valid_lar_row["prepayment_penalty"] = str(random.choice(self.range_and_enum(field="prepayment_penalty", rng_max=lar_file_config["penalty_max"]["value"])))
		valid_lar_row["dti"] = str(random.choice(self.range_and_enum(field="dti", rng_max=lar_file_config["dti"]["value"])))
		valid_lar_row["cltv"] = str(random.choice(self.range_and_enum(field="cltv", rng_max=lar_file_config["cltv"]["value"])))
		valid_lar_row["loan_term"] = str(random.choice(self.range_and_enum(field="loan_term", rng_max=lar_file_config["loan_term"]["value"])))
		valid_lar_row["intro_rate"] = str(random.choice(self.range_and_enum(field="intro_rate", rng_max=lar_file_config["intro_rate"]["value"])))
		valid_lar_row["balloon"] = str(random.choice(self.get_schema_list(field="balloon")))
		valid_lar_row["int_only_pmts"] = str(random.choice(self.get_schema_list(field="int_only_pmts")))
		valid_lar_row["neg_amort"] = str(random.choice(self.get_schema_list(field="neg_amort")))
		valid_lar_row["non_amort_features"] = str(random.choice(self.get_schema_list(field="non_amort_features")))
		valid_lar_row["property_value"] = str(random.choice(self.range_and_enum(field="property_value", rng_min=lar_file_config["prop_val_min"]["value"], rng_max=lar_file_config["prop_val_max"]["value"])))
		valid_lar_row["manufactured_type"] = str(random.choice(self.get_schema_list(field="manufactured_type")))
		valid_lar_row["manufactured_interest"] = str(random.choice(self.get_schema_list(field="manufactured_interest")))
		valid_lar_row["total_units"] = str(random.choice(self.range_and_enum(field="total_units", rng_min=1, rng_max=lar_file_config["max_units"]["value"])))
		valid_lar_row["affordable_units"] = str(random.choice(self.range_and_enum(field="affordable_units", rng_min=0, rng_max=int(valid_lar_row["total_units"]))))
		valid_lar_row["app_submission"] = str(random.choice(self.get_schema_list(field="app_submission")))
		valid_lar_row["initially_payable"] = str(random.choice(self.get_schema_list(field="initially_payable")))
		valid_lar_row["mlo_id"] = utils.char_string_gen(random.choice(range(25)))
		valid_lar_row["aus_1"] = str(random.choice(self.get_schema_list(field="aus_1")))
		valid_lar_row["aus_2"] = str(random.choice(self.get_schema_list(field="aus_2", empty=True)))
		valid_lar_row["aus_3"] = str(random.choice(self.get_schema_list(field="aus_3", empty=True)))
		valid_lar_row["aus_4"] = str(random.choice(self.get_schema_list(field="aus_4", empty=True)))
		valid_lar_row["aus_5"] = str(random.choice(self.get_schema_list(field="aus_5", empty=True)))
		valid_lar_row["aus_code_5"] = utils.char_string_gen(random.choice(range(255)))
		valid_lar_row["aus_result_1"] = str(random.choice(self.get_schema_list(field="aus_result_1")))
		valid_lar_row["aus_result_2"] = str(random.choice(self.get_schema_list(field="aus_result_2", empty=True)))
		valid_lar_row["aus_result_3"] = str(random.choice(self.get_schema_list(field="aus_result_3", empty=True)))
		valid_lar_row["aus_result_4"] = str(random.choice(self.get_schema_list(field="aus_result_4", empty=True)))
		valid_lar_row["aus_result_5"] = str(random.choice(self.get_schema_list(field="aus_result_5", empty=True)))
		valid_lar_row["aus_code_16"] = utils.char_string_gen(random.choice(range(255)))
		valid_lar_row["reverse_mortgage"] = str(random.choice(self.get_schema_list(field="reverse_mortgage")))
		valid_lar_row["open_end_credit"] = str(random.choice(self.get_schema_list(field="open_end_credit")))
		valid_lar_row["business_purpose"] = str(random.choice(self.get_schema_list(field="business_purpose")))

		return valid_lar_row