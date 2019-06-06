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
	""""""
	def __init__(self, LAR_df=None, TS_df=None, counties=None, tracts=None):
		
		self.LAR_df = LAR_df
		self.TS_df = TS_df
		#external data lists
		
		#list of counties from the geographic crosswalk data file, dtype string
		self.county_list = counties 
		#list of tracts from the geographic crosswalk data file, dtype string
		self.tract_list = tracts 
		#list of valid state and territory codes (two digit letter)
		self.state_codes = [] 
		
		with open('configurations/clean_file_config.yaml') as f:
			# use safe_load instead load
			data_map = yaml.safe_load(f)
		#Loads geographic configuration file. 
		with open('configurations/geographic_data.yaml') as f:
			geographic = yaml.safe_load(f)

		#Loading in state codes. 
		self.state_codes = geographic['state_codes']
		
		#load TS data
		self.street_addy = data_map['street_addy']["value"]
		self.city = data_map["city"]["value"]
		self.bank_name = data_map["name"]["value"]
		#Base LAR File range limits
		self.zip_codes = json.load(open(geographic['zip_code_file']))
		self.lar_zips = self.zip_codes.append("Exempt")
		self.max_age = data_map["max_age"]["value"]
		self.max_amount = data_map["max_amount"]["value"]
		self.max_income = data_map["max_income"]["value"]
		self.max_rs = data_map["max_rs"]["value"]
		self.max_credit_score = data_map["max_credit_score"]["value"]
		self.min_credit_score = data_map["min_credit_score"]["value"]
		self.loan_costs = data_map["loan_costs"]["value"]
		self.points_and_fees = data_map["points_and_fees"]["value"]
		self.orig_charges = data_map["orig_charges"]["value"]
		self.discount_points = data_map["discount_points"]["value"]
		self.lender_credits = data_map["lender_credits"]["value"]
		self.interest_rate = data_map["interest_rate"]["value"]
		self.penalty_max = data_map["penalty_max"]["value"]
		self.dti = data_map["dti"]["value"]
		self.cltv = data_map["cltv"]["value"]
		self.loan_term = data_map["loan_term"]["value"]
		self.intro_rate = data_map["intro_rate"]["value"]
		self.max_units = data_map["max_units"]["value"]
		self.prop_val_max = data_map["prop_val_max"]["value"]
		self.prop_val_min = data_map["prop_val_min"]["value"]

	def date_gen(self, year=2019, valid=True):
		"""Generates and returns a semi-valid date string or an invalid date string. Does not check days per month."""
		months = list(range(1,13))
		days = list(range(1,32))
		if valid:
			valid_date = False
			while not valid_date:
				date = str(year)+str(random.choice(months)).zfill(2)+str(random.choice(days)).zfill(2)
				try:
					time.strptime(date,'%Y%m%d')
					valid_date = True
				except:
					valid_date = False
		else:
			date = str(year)+str(16)+str(33)
		return date

	def random_enum(self, enums):
		""""""
		return random.choice(enums)

	def get_schema_val(self, schema="LAR", position=0, item=0, field=None):
		"""Returns a value from the valid_vals list in the schema for the named field. Default is the first value in the list."""
		if not field:
			raise ValueError("must specify which field")
		if schema=="LAR":
			return self.LAR_df.valid_vals[self.LAR_df.field==field].iloc[position][item]
		elif schema=="TS":
			return self.TS_df.valid_vals[self.TS_df.field==field].iloc[position][item]
		else:
			pass

	def get_schema_list(self, schema="LAR", field=None, empty=False):
		"""Returns the list of valid values for the specified schema and field. Optionally adds blanks to the list of values."""
		if not field:
			raise ValueError("must specify which field")
		if schema=="LAR":
			if empty:
				schema_enums = self.LAR_df.valid_vals[self.LAR_df.field==field].iloc[0]
				schema_enums.append("")
				return schema_enums
			else: 
				return self.LAR_df.valid_vals[self.LAR_df.field==field].iloc[0]
		elif schema=="TS":
			if empty:
				schema_enums = self.TS_df.valid_vals[self.TS_df.field==field].iloc[0]
				schema_enums.append("")
				return schema_enums
			else:
				return self.TS_df.valid_vals[self.TS_df.field==field].iloc[0]

	def range_and_enum(self, field=None, rng_min=1, rng_max=100, dtype="int", empty=False):
		"""Returns a list of integers or floats. if na is True the list will also contain NA"""
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
		valid_tracts = [tract for tract in self.tract_list if tract[:5]==county ]
		return random.choice(valid_tracts)

	def float_gen(self):
		pass

	def gen_enums(self):
		"""generates int/string or float/string value lists. this is done to include NA and randomly generated values"""
		pass

	def make_ts_row(self, data_map):
		"""Creates a TS row as a dictionary and returns it."""
		ts_row = OrderedDict()
		ts_row["record_id"] ="1"
		ts_row["inst_name"] = data_map["name"]["value"]
		ts_row["calendar_year"] = data_map["calendar_year"]["value"]
		ts_row["calendar_quarter"] = data_map["calendar_quarter"]["value"]
		ts_row["contact_name"] = data_map["contact_name"]["value"]
		ts_row["contact_tel"] = data_map["contact_tel"]["value"]
		ts_row["contact_email"] = data_map["contact_email"]["value"]
		ts_row["contact_street_address"] = data_map["street_addy"]["value"]
		ts_row["office_city"] = data_map["city"]["value"]
		ts_row["office_state"] = data_map["state"]["value"]
		ts_row["office_zip"] = data_map["zip_code"]["value"]
		ts_row["federal_agency"] = data_map["agency_code"]["value"]
		ts_row["lar_entries"]= str(data_map["file_length"]["value"])
		ts_row["tax_id"] = data_map["tax_id"]["value"]
		ts_row["lei"] = data_map["lei"]["value"]
		return ts_row

	#all valid values, including blanks and NAs, are included in the selection lists.
	#Some of these values are added using helper functions if they are not present in the JSON schema.
	def make_row(self, lei=None):
		"""Make num_rows LAR rows and return them as a list of ordered dicts"""
		valid_lar_row = OrderedDict() 
		valid_lar_row["record_id"] = str(self.LAR_df.valid_vals[self.LAR_df.field=="record_id"].iloc[0][0])	
		valid_lar_row["lei"] = lei
		valid_lar_row["uli"] = valid_lar_row['lei'] + utils.char_string_gen(23)
		valid_lar_row["uli"] = valid_lar_row["uli"] + utils.check_digit_gen(ULI=valid_lar_row["uli"])
		valid_lar_row["uli"] = random.choice([valid_lar_row["uli"], utils.char_string_gen(22)])
		valid_lar_row["app_date"] = str(self.date_gen())
		valid_lar_row["loan_type"] = str(self.random_enum(self.get_schema_list(field="loan_type")))
		valid_lar_row["loan_purpose"] = str(self.random_enum(self.get_schema_list(field="loan_purpose")))
		valid_lar_row["preapproval"] = str(self.random_enum(self.get_schema_list(field="preapproval")))
		valid_lar_row["const_method"] = str(self.random_enum(self.get_schema_list(field="const_method")))
		valid_lar_row["occ_type"] = str(self.random_enum(self.get_schema_list(field="occ_type")))
		valid_lar_row["loan_amount"] = str(self.random_enum(range(1,self.max_amount)))
		valid_lar_row["action_taken"] = str(self.random_enum(self.get_schema_list(field='action_taken')))
		valid_lar_row["action_date"] = str(self.date_gen())
		valid_lar_row["street_address"] = random.choice([self.street_addy, self.street_addy, "Exempt"])
		valid_lar_row["city"] = self.city
		valid_lar_row["state"] = random.choice(list(self.state_codes.keys()))
		valid_lar_row["zip_code"] = random.choice(self.zip_codes)
		valid_lar_row["county"] = self.random_enum(self.county_list)
		valid_lar_row["tract"] = self.tract_from_county(valid_lar_row["county"])
		valid_lar_row["app_eth_1"] = str(self.random_enum(self.get_schema_list(field="app_eth_1", empty=True)))
		valid_lar_row["app_eth_2"] = str(self.random_enum(self.get_schema_list(field="app_eth_2", empty=True)))
		valid_lar_row["app_eth_3"] = str(self.random_enum(self.get_schema_list(field="app_eth_3", empty=True)))
		valid_lar_row["app_eth_4"] = str(self.random_enum(self.get_schema_list(field="app_eth_4", empty=True)))
		valid_lar_row["app_eth_5"] = str(self.random_enum(self.get_schema_list(field="app_eth_5", empty=True)))
		valid_lar_row["app_eth_free"] = utils.char_string_gen(random.choice(range(100)))
		valid_lar_row["co_app_eth_1"] = str(self.random_enum(self.get_schema_list(field="co_app_eth_1", empty=True)))
		valid_lar_row["co_app_eth_2"] = str(self.random_enum(self.get_schema_list(field="co_app_eth_2", empty=True)))
		valid_lar_row["co_app_eth_3"] = str(self.random_enum(self.get_schema_list(field="co_app_eth_3", empty=True)))
		valid_lar_row["co_app_eth_4"] = str(self.random_enum(self.get_schema_list(field="co_app_eth_4", empty=True)))
		valid_lar_row["co_app_eth_5"] = str(self.random_enum(self.get_schema_list(field="co_app_eth_5", empty=True)))
		valid_lar_row["co_app_eth_free"] = utils.char_string_gen(random.choice(range(100)))
		valid_lar_row["app_eth_basis"] = str(self.random_enum(self.get_schema_list(field="app_eth_basis")))
		valid_lar_row["co_app_eth_basis"] = str(self.random_enum(self.get_schema_list(field="co_app_eth_basis")))
		valid_lar_row["app_race_1"] = str(self.random_enum(self.get_schema_list(field="app_race_1", empty=True)))
		valid_lar_row["app_race_2"] = str(self.random_enum(self.get_schema_list(field="app_race_2", empty=True)))
		valid_lar_row["app_race_3"] = str(self.random_enum(self.get_schema_list(field="app_race_3", empty=True)))
		valid_lar_row["app_race_4"] = str(self.random_enum(self.get_schema_list(field="app_race_4", empty=True)))
		valid_lar_row["app_race_5"] = str(self.random_enum(self.get_schema_list(field="app_race_5", empty=True)))
		valid_lar_row["app_race_native_text"] = utils.char_string_gen(random.choice(range(100)))
		valid_lar_row["app_race_asian_text"] = utils.char_string_gen(random.choice(range(100)))
		valid_lar_row["app_race_islander_text"] = utils.char_string_gen(random.choice(range(100)))
		valid_lar_row["co_app_race_1"] = str(self.random_enum(self.get_schema_list(field="co_app_race_1", empty=True)))
		valid_lar_row["co_app_race_2"] = str(self.random_enum(self.get_schema_list(field="co_app_race_2", empty=True)))
		valid_lar_row["co_app_race_3"] = str(self.random_enum(self.get_schema_list(field="co_app_race_3", empty=True)))
		valid_lar_row["co_app_race_4"] = str(self.random_enum(self.get_schema_list(field="co_app_race_4", empty=True)))
		valid_lar_row["co_app_race_5"] = str(self.random_enum(self.get_schema_list(field="co_app_race_5", empty=True)))
		valid_lar_row["co_app_race_native_text"] = utils.char_string_gen(random.choice(range(100)))
		valid_lar_row["co_app_race_asian_text"] = utils.char_string_gen(random.choice(range(100)))
		valid_lar_row["co_app_race_islander_text"] = utils.char_string_gen(random.choice(range(100)))
		valid_lar_row["app_race_basis"] = str(self.random_enum(self.get_schema_list(field="app_race_basis")))
		valid_lar_row["co_app_race_basis"] = str(self.random_enum(self.get_schema_list(field="co_app_race_basis")))
		valid_lar_row["app_sex"] = str(self.random_enum(self.get_schema_list(field="app_sex")))
		valid_lar_row["co_app_sex"] = str(self.random_enum(self.get_schema_list(field="co_app_sex")))
		valid_lar_row["app_sex_basis"] = str(self.random_enum(self.get_schema_list(field="app_sex_basis")))
		valid_lar_row["co_app_sex_basis"] = str(self.random_enum(self.get_schema_list(field="co_app_sex_basis")))
		valid_lar_row["app_age"] = str(self.random_enum(self.range_and_enum(field="app_age", rng_max=self.max_age)))
		valid_lar_row["co_app_age"] = str(self.random_enum(self.range_and_enum(field="co_app_age", rng_max=self.max_age)))
		valid_lar_row["income"] = str(self.random_enum(range(1, self.max_income)))
		valid_lar_row["purchaser_type"] = str(self.random_enum(self.get_schema_list(field="purchaser_type")))
		valid_lar_row["rate_spread"]= str(self.random_enum(self.range_and_enum(field="rate_spread", rng_max=self.max_rs, dtype="float")))
		valid_lar_row["hoepa"] = str(self.random_enum(self.get_schema_list(field="hoepa")))
		valid_lar_row["lien"] = str(self.random_enum(self.get_schema_list(field="lien")))
		valid_lar_row["app_credit_score"] = str(self.random_enum(self.range_and_enum(field="app_credit_score", rng_min=self.min_credit_score,rng_max=self.max_credit_score)))
		valid_lar_row["co_app_credit_score"] = str(self.random_enum(self.range_and_enum(field="co_app_credit_score", rng_min=self.min_credit_score, rng_max=self.max_credit_score)))
		valid_lar_row["app_score_name"] = str(self.random_enum(self.get_schema_list(field="app_score_name")))
		valid_lar_row["app_score_code_8"] = str(utils.char_string_gen(random.choice(range(100))))
		valid_lar_row["co_app_score_name"] = str(self.random_enum(self.get_schema_list(field="co_app_score_name")))
		valid_lar_row["co_app_score_code_8"] = utils.char_string_gen(random.choice(range(100)))
		valid_lar_row["denial_1"] = str(self.random_enum(self.get_schema_list(field="denial_1")))
		valid_lar_row["denial_2"] = str(self.random_enum(self.get_schema_list(field="denial_2", empty=True)))
		valid_lar_row["denial_3"] = str(self.random_enum(self.get_schema_list(field="denial_3", empty=True)))
		valid_lar_row["denial_4"] = str(self.random_enum(self.get_schema_list(field="denial_4", empty=True)))
		valid_lar_row["denial_code_9"] = utils.char_string_gen(random.choice(range(255)))
		valid_lar_row["loan_costs"] = str(self.random_enum(self.range_and_enum(field="loan_costs",rng_max=self.loan_costs)))
		valid_lar_row["points_fees"] = str(self.random_enum(self.range_and_enum(field="points_fees", rng_max=self.points_and_fees)))
		valid_lar_row["origination_fee"] = str(self.random_enum(self.range_and_enum(field="origination_fee", rng_max=self.orig_charges)))
		valid_lar_row["discount_points"] = str(self.random_enum(self.range_and_enum(field="discount_points", rng_max=self.discount_points, empty=True)))
		valid_lar_row["lender_credits"] = str(self.random_enum(self.range_and_enum(field="lender_credits", rng_max=self.lender_credits, empty=True)))
		valid_lar_row["interest_rate"] = str(self.random_enum(self.range_and_enum(field="interest_rate", rng_max=25, dtype="float")))
		valid_lar_row["prepayment_penalty"] = str(self.random_enum(self.range_and_enum(field="prepayment_penalty", rng_max=self.penalty_max)))
		valid_lar_row["dti"] = str(self.random_enum(self.range_and_enum(field="dti", rng_max=self.dti)))
		valid_lar_row["cltv"] = str(self.random_enum(self.range_and_enum(field="cltv", rng_max=self.cltv)))
		valid_lar_row["loan_term"] = str(self.random_enum(self.range_and_enum(field="loan_term", rng_max=self.loan_term)))
		valid_lar_row["intro_rate"] = str(self.random_enum(self.range_and_enum(field="intro_rate", rng_max=self.intro_rate)))
		valid_lar_row["balloon"] = str(self.random_enum(self.get_schema_list(field="balloon")))
		valid_lar_row["int_only_pmts"] = str(self.random_enum(self.get_schema_list(field="int_only_pmts")))
		valid_lar_row["neg_amort"] = str(self.random_enum(self.get_schema_list(field="neg_amort")))
		valid_lar_row["non_amort_features"] = str(self.random_enum(self.get_schema_list(field="non_amort_features")))
		valid_lar_row["property_value"] = str(self.random_enum(self.range_and_enum(field="property_value", rng_min=self.prop_val_min, rng_max=self.prop_val_max)))
		valid_lar_row["manufactured_type"] = str(self.random_enum(self.get_schema_list(field="manufactured_type")))
		valid_lar_row["manufactured_interest"] = str(self.random_enum(self.get_schema_list(field="manufactured_interest")))
		valid_lar_row["total_units"] = str(self.random_enum(self.range_and_enum(field="total_units", rng_min=1, rng_max=self.max_units)))
		valid_lar_row["affordable_units"] = str(self.random_enum(self.range_and_enum(field="affordable_units", rng_min=0, rng_max=int(valid_lar_row["total_units"]))))
		valid_lar_row["app_submission"] = str(self.random_enum(self.get_schema_list(field="app_submission")))
		valid_lar_row["initially_payable"] = str(self.random_enum(self.get_schema_list(field="initially_payable")))
		valid_lar_row["mlo_id"] = utils.char_string_gen(random.choice(range(25)))
		valid_lar_row["aus_1"] = str(self.random_enum(self.get_schema_list(field="aus_1")))
		valid_lar_row["aus_2"] = str(self.random_enum(self.get_schema_list(field="aus_2", empty=True)))
		valid_lar_row["aus_3"] = str(self.random_enum(self.get_schema_list(field="aus_3", empty=True)))
		valid_lar_row["aus_4"] = str(self.random_enum(self.get_schema_list(field="aus_4", empty=True)))
		valid_lar_row["aus_5"] = str(self.random_enum(self.get_schema_list(field="aus_5", empty=True)))
		valid_lar_row["aus_code_5"] = utils.char_string_gen(random.choice(range(255)))
		valid_lar_row["aus_result_1"] = str(self.random_enum(self.get_schema_list(field="aus_result_1")))
		valid_lar_row["aus_result_2"] = str(self.random_enum(self.get_schema_list(field="aus_result_2", empty=True)))
		valid_lar_row["aus_result_3"] = str(self.random_enum(self.get_schema_list(field="aus_result_3", empty=True)))
		valid_lar_row["aus_result_4"] = str(self.random_enum(self.get_schema_list(field="aus_result_4", empty=True)))
		valid_lar_row["aus_result_5"] = str(self.random_enum(self.get_schema_list(field="aus_result_5", empty=True)))
		valid_lar_row["aus_code_16"] = utils.char_string_gen(random.choice(range(255)))
		valid_lar_row["reverse_mortgage"] = str(self.random_enum(self.get_schema_list(field="reverse_mortgage")))
		valid_lar_row["open_end_credit"] = str(self.random_enum(self.get_schema_list(field="open_end_credit")))
		valid_lar_row["business_purpose"] = str(self.random_enum(self.get_schema_list(field="business_purpose")))
		return valid_lar_row