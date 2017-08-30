import json
import os
import pandas as pd
import random
import string
from collections import OrderedDict


class lar_gen(object):
	""""""
	def __init__(self, LAR_df=None, TS_df=None, counties=None, tracts=None):
		self.LAR_df = LAR_df
		self.TS_df = TS_df
		#external data lists
		self.county_list = counties #list of CBSA counties, dtype string
		self.tract_list = tracts #list of CBSA tracts, dtype string
		self.state_codes = [] #list of valid state and territory codes (two digit letter)


		#Base LAR File range limits
		self.street_addy = "1234 Hocus Potato Way"
		self.city = "Tatertown"
		self.state = "UT"
		self.zip_code = "84096"
		self.max_age = 130
		self.max_amount = 10000
		self.max_income = 10000
		self.max_rs = 100
		self.max_credit_score = 900
		self.min_credit_score = 300
		self.loan_costs = 10000
		self.points_and_fees = 5000
		self.orig_charges = 5000
		self.discount_points = 5000
		self.lender_credits = 5000
		self.interest_rate = 25
		self.penalty_max = 36
		self.dti = 100
		self.cltv = 200
		self.loan_term = 360
		self.intro_rate = 36
		self.prop_val_max = 30000
		self.prop_val_min = 10
		self.max_units = 100
	#helper functions
	def char_string_gen(self,length):
		"""Generates a string of chosen length using ascii uppercase and numerical characters"""
		return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

	def date_gen(self, year=2018, valid=True):
		"""Generates and returns a semi-valid date string or an invalid date string. Does not check days per month."""
		months = list(range(1,13))
		days = list(range(1,32))
		
		if valid:
			date = str(year)+str(random.choice(months)).zfill(2)+str(random.choice(days)).zfill(2)
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

	def get_schema_list(self, schema="LAR", field=None):
		"""Returns the list of valid values for the specifid schema and field."""
		if not field:
			raise ValueError("must specify which field")
		if schema=="LAR":
			return self.LAR_df.valid_vals[self.LAR_df.field==field].iloc[0]
		elif schema=="TS":
			return self.TS_df.valid_vals[self.TS_df.field==field].iloc[0]

	def range_and_enum(self, field=None, rng_min=1, rng_max=100, dtype="int"):
		"""Returns a list of integers or floats. if na is True the list will also contain NA"""
		lst=[]
		lst = self.get_schema_list(field=field) #get NA values from schema if present
		if dtype=="int":
			for i in range(rng_min, rng_max):
				lst.append(i)
		elif dtype=="float":
			for i in range(rng_min, rng_max):
				lst.append(i*.97)
		return lst

	def float_gen(self):
		pass

	def gen_enums(self):
		"""generates int/string or float/string value lists. this is done to include NA and randomly generated values"""
		pass

	#this file will have valid values for all column/row entries
#some valid value lists contain only "NA", other entries are also valid

	def make_row(self):
		"""Make num_rows LAR rows and return them as a list of ordered dicts"""
		valid_lar_row = OrderedDict() 
		valid_lar_row["record_id"] = str(self.LAR_df.valid_vals[self.LAR_df.field=="record_id"].iloc[0][0])
		valid_lar_row["lei"] = self.char_string_gen(20)
		valid_lar_row["uli"] = valid_lar_row['lei'] + self.char_string_gen(25)
		valid_lar_row["app_date"] = str(self.date_gen())
		valid_lar_row["loan_type"] = str(self.random_enum(self.get_schema_list(field="loan_type")))
		valid_lar_row["loan_purpose"] = str(self.random_enum(self.get_schema_list(field="loan_purpose")))
		valid_lar_row["preapproval"] = str(self.random_enum(self.get_schema_list(field="preapproval")))
		valid_lar_row["const_method"] = str(self.random_enum(self.get_schema_list(field="const_method")))
		valid_lar_row["occ_type"] = str(self.random_enum(self.get_schema_list(field="occ_type")))
		valid_lar_row["loan_amount"] = str(self.random_enum(range(1,self.max_amount)))
		valid_lar_row["action_taken"] = str(self.random_enum(self.get_schema_list(field='action_taken')))
		valid_lar_row["action_date"] = str(self.date_gen())
		valid_lar_row["street_address"] = self.street_addy
		valid_lar_row["city"] = self.city
		valid_lar_row["state"] = self.state
		valid_lar_row["zip_code"] = self.zip_code
		valid_lar_row["county"] = self.random_enum(self.county_list)
		valid_lar_row["tract"] = self.random_enum(self.tract_list)
		valid_lar_row["app_eth_1"] = str(self.random_enum(self.get_schema_list(field="app_eth_1")))
		valid_lar_row["app_eth_2"] = str(self.random_enum(self.get_schema_list(field="app_eth_2")))
		valid_lar_row["app_eth_3"] = str(self.random_enum(self.get_schema_list(field="app_eth_3")))
		valid_lar_row["app_eth_4"] = str(self.random_enum(self.get_schema_list(field="app_eth_4")))
		valid_lar_row["app_eth_5"] = str(self.random_enum(self.get_schema_list(field="app_eth_5")))
		valid_lar_row["app_eth_code_14"] = self.char_string_gen(random.choice(range(100)))
		valid_lar_row["co_app_eth_1"] = str(self.random_enum(self.get_schema_list(field="co_app_eth_1")))
		valid_lar_row["co_app_eth_2"] = str(self.random_enum(self.get_schema_list(field="co_app_eth_2")))
		valid_lar_row["co_app_eth_3"] = str(self.random_enum(self.get_schema_list(field="co_app_eth_3")))
		valid_lar_row["co_app_eth_4"] = str(self.random_enum(self.get_schema_list(field="co_app_eth_4")))
		valid_lar_row["co_app_eth_5"] = str(self.random_enum(self.get_schema_list(field="co_app_eth_5")))
		valid_lar_row["co_app_eth_code_14"] = self.char_string_gen(random.choice(range(100)))
		valid_lar_row["app_eth_basis"] = str(self.random_enum(self.get_schema_list(field="app_eth_basis")))
		valid_lar_row["co_app_eth_basis"] = str(self.random_enum(self.get_schema_list(field="co_app_eth_basis")))
		valid_lar_row["app_race_1"] = str(self.random_enum(self.get_schema_list(field="app_race_1")))
		valid_lar_row["app_race_2"] = str(self.random_enum(self.get_schema_list(field="app_race_2")))
		valid_lar_row["app_race_3"] = str(self.random_enum(self.get_schema_list(field="app_race_3")))
		valid_lar_row["app_race_4"] = str(self.random_enum(self.get_schema_list(field="app_race_4")))
		valid_lar_row["app_race_5"] = str(self.random_enum(self.get_schema_list(field="app_race_5")))
		valid_lar_row["app_race_code_1"] = self.char_string_gen(random.choice(range(100)))
		valid_lar_row["app_race_code_27"] = self.char_string_gen(random.choice(range(100)))
		valid_lar_row["app_race_code_44"] = self.char_string_gen(random.choice(range(100)))
		valid_lar_row["co_app_race_1"] = str(self.random_enum(self.get_schema_list(field="co_app_race_1")))
		valid_lar_row["co_app_race_2"] = str(self.random_enum(self.get_schema_list(field="co_app_race_2")))
		valid_lar_row["co_app_race_3"] = str(self.random_enum(self.get_schema_list(field="co_app_race_3")))
		valid_lar_row["co_app_race_4"] = str(self.random_enum(self.get_schema_list(field="co_app_race_4")))
		valid_lar_row["co_app_race_5"] = str(self.random_enum(self.get_schema_list(field="co_app_race_5")))
		valid_lar_row["co_app_race_code_1"] = self.char_string_gen(random.choice(range(100)))
		valid_lar_row["co_app_race_code_27"] = self.char_string_gen(random.choice(range(100)))
		valid_lar_row["co_app_race_code_44"] = self.char_string_gen(random.choice(range(100)))
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
		valid_lar_row["app_score_code_8"] = str(self.char_string_gen(random.choice(range(100))))
		valid_lar_row["co_app_score_name"] = str(self.random_enum(self.get_schema_list(field="co_app_score_name")))
		valid_lar_row["co_app_code_8"] = self.char_string_gen(random.choice(range(100)))
		valid_lar_row["denial_1"] = str(self.random_enum(self.get_schema_list(field="denial_1")))
		valid_lar_row["denial_2"] = str(self.random_enum(self.get_schema_list(field="denial_2")))
		valid_lar_row["denial_3"] = str(self.random_enum(self.get_schema_list(field="denial_3")))
		valid_lar_row["denial_4"] = str(self.random_enum(self.get_schema_list(field="denial_4")))
		valid_lar_row["denial_code_9"] = self.char_string_gen(random.choice(range(255)))
		valid_lar_row["loan_costs"] = str(self.random_enum(self.range_and_enum(field="loan_costs",rng_max=self.loan_costs)))
		valid_lar_row["points_fees"] = str(self.random_enum(self.range_and_enum(field="points_fees", rng_max=self.points_and_fees)))
		valid_lar_row["origination_fee"] = str(self.random_enum(self.range_and_enum(field="origination_fee", rng_max=self.orig_charges)))
		valid_lar_row["discount_points"] = str(self.random_enum(self.range_and_enum(field="discount_points", rng_max=self.discount_points)))
		valid_lar_row["lender_credits"] = str(self.random_enum(self.range_and_enum(field="lender_credits", rng_max=self.lender_credits)))
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
		valid_lar_row["total_units"] = str(self.random_enum(self.range_and_enum(field="property_value", rng_min=1, rng_max = self.max_units)))
		valid_lar_row["affordable_units"] = self.random_enum(self.range_and_enum(field="affordable_units", rng_min=0, rng_max=int(valid_lar_row["total_units"])))
		valid_lar_row["submission_type"] = str(self.random_enum(self.get_schema_list(field="submission_type")))
		valid_lar_row["initially_payable"] = str(self.random_enum(self.get_schema_list(field="initially_payable")))
		valid_lar_row["mlo_id"] = self.char_string_gen(random.choice(range(25)))
		valid_lar_row["aus_1"] = str(self.random_enum(self.get_schema_list(field="aus_1")))
		valid_lar_row["aus_2"] = str(self.random_enum(self.get_schema_list(field="aus_2")))
		valid_lar_row["aus_3"] = str(self.random_enum(self.get_schema_list(field="aus_3")))
		valid_lar_row["aus_4"] = str(self.random_enum(self.get_schema_list(field="aus_4")))
		valid_lar_row["aus_5"] = str(self.random_enum(self.get_schema_list(field="aus_5")))
		valid_lar_row["aus_code_5"] = self.char_string_gen(random.choice(range(255)))
		valid_lar_row["aus_result_1"] = str(self.random_enum(self.get_schema_list(field="aus_result_1")))
		valid_lar_row["aus_result_2"] = str(self.random_enum(self.get_schema_list(field="aus_result_2")))
		valid_lar_row["aus_result_3"] = str(self.random_enum(self.get_schema_list(field="aus_result_3")))
		valid_lar_row["aus_result_4"] = str(self.random_enum(self.get_schema_list(field="aus_result_4")))
		valid_lar_row["aus_result_5"] = str(self.random_enum(self.get_schema_list(field="aus_result_5")))
		valid_lar_row["aus_code_16"] = self.char_string_gen(random.choice(range(255)))
		valid_lar_row["reverse_mortgage"] = str(self.random_enum(self.get_schema_list(field="reverse_mortgage")))
		valid_lar_row["open_end_credit"] = str(self.random_enum(self.get_schema_list(field="open_end_credit")))
		valid_lar_row["business_purpose"] = str(self.random_enum(self.get_schema_list(field="business_purpose")))
		return valid_lar_row