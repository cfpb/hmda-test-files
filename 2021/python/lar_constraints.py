import random
import string

import pandas as pd
import yaml


class lar_data_constraints(object):

	def __init__(self, lar_file_config, geographic_data):
		"""
		lar_file_cnfig is a dictionary like object usually loaded from clean_file_config.yaml
		geographic_data is the HMDA Ops cut of the FFIEC Census Flat File
		"""
		self.config_data = lar_file_config
		self.geographic_data = geographic_data
		#create list of LAR data constraint functions
		self.constraints = []
		for func in dir(self):
			if func[:1] in ("s", "v") and func[1:4].isdigit()==True:
				self.constraints.append(func)


	def no_enum_dupes(self, fields=[], enum_list=None):
		"""Checks all fields to ensure that no enumeration is repeated. If one repeats it is reassigned from the remaining valid enumerations.
		enum_list_1 contains values for the first field, enum_list contains values for subsequen fields."""
		if fields[0] in enum_list and fields[0] != "":
			enum_list.remove(fields[0])
		for i in range(1, len(fields)):
			if fields[i] in enum_list and fields[i] != "":
				enum_list.remove(fields[i])
			elif fields[i] not in enum_list:
				fields[i] = random.choice(enum_list)
				enum_list.remove(fields[i])
		return fields

	#constraint functions
	#these functions will be used to re-generate data for a specific LAR row so that the data row is valid 
	#For example, preapproval code 2 limits the valid entries for action taken
	#S303: requires panel (matches LEI, TAX ID, Federal Agency)
	#constraints NOTE: check fields of highest variability (most enumerations) first
	#def s305_const(self, row):
	#	"""duplicate row, checks all fields to determine if it is a duplicate record"""
	#	pass

	def v610_const(self, row):
		"""application date must be NA when action taken = 6, reverse must also be true"""
		if row["app_date"] == "NA" or row["action_taken"] == "6":
			row["app_date"] = "NA"
			row["action_taken"] = "6"
		return row

	def v612_const(self, row):
		"""if preapproval = 1 then loan purpose = 1"""
		if row["preapproval"] == "1" and row["loan_purpose"] != "1":
			row["preapproval"] = "2"
		return row

	def v613_2_const(self, row):
		"""2) If Action Taken equals 7 or 8, then Preapproval must equal 1."""
		if row["action_taken"] in ("7", "8") and row["preapproval"] != "1":
			row["action_taken"] = random.choice(("3", "4", "5", "6"))
			row["affordable_units"] = "NA"
		return row

	def v613_3_const(self, row):
		"""3) If Action Taken equals 3, 4, 5 or 6, then Preapproval must equal 2."""
		if row["action_taken"] in ("3", "4", "5", "6") and row["preapproval"] != "2":
			row["preapproval"] = "2"
		return row

	def v613_4_const(self, row):
		""" 4) If Preapproval equals 1, then Action Taken must equal 1, 2, 7 or 8."""
		if row["preapproval"] == "1" and row["action_taken"] not in ("1", "2", "7", "8"):
			row["preapproval"] = "2"
		return row

	def v614_1_const(self, row):
		"""1) If Loan Purpose equals 2, 4, 31, 32, or 5, then Preapproval must equal 2."""
		if row["loan_purpose"] in ("2", "4", "31", "32", "5"):
			row["preapproval"] = "2"
		return row

	def v614_2_const(self, row):
		"""2) If Multifamily Affordable Units is a number, then Preapproval must equal 2."""
		if row["affordable_units"].isdigit() == True:
			row["preapproval"] = "2"
		return row

	def v614_3_const(self, row):
		"""3) If Reverse Mortgage equals 1, then Preapproval must equal 2."""
		if row["reverse_mortgage"] == "1":
			row["preapproval"] = "2"
		return row

	def v614_4_const(self, row):
		""" 4) If Open-End Line of Credit equals 1, then Preapproval must equal 2."""
		if row["open_end_credit"] == "1":
			row["preapproval"] = "2"
		return row

	def v615_const(self, row):
		"""2) If Manufactured Home Land Property Interest equals 1, 2, 3 or 4, then Construction Method must equal 2.
		   3) If Manufactured Home Secured Property Type equals 1 or 2 then Construction Method must equal 2."""

		if row["manufactured_interest"] in ("1", "2", "3", "4"):
			row["const_method"] = "2"
		if row["manufactured_type"] in ("1", "2"):
			row["const_method"] = "2"
		return row

	def v619_const(self, row):
		"""2) The Action Taken Date must be in the reporting year.
		3) The Action Taken Date must be on or after the Application Date."""
		reporting_year = self.config_data["activity_year"]["value"]
		if row["action_date"][:4] != reporting_year:
			row["action_date"] = str(reporting_year) + str(row["action_date"][4:])
		if row["action_date"] != "NA" and row["app_date"] != "NA":
			if int(row["action_date"]) < int(row["app_date"]):
				row["action_date"] = row["app_date"]
		return row

	def v622_const(self, row):
		"""1) If Street Address was not reported NA, then City, State, and Zip Code must be provided, and not reported NA."""
		if row["street_address"] != "NA":
			if row["city"] == "":
				row["city"] = "Spudfarm"
			if row["state"] == "":
				row["state"] = "UT"
			if row["zip_code"] == "":
				row["zip_code"] = "12345"
		return row

	def v627_const(self, row):
		"""1) If County and Census Tract are not reported NA, they must be a valid combination of information.
		   The first five digits of the Census Tract must match the reported five digit County FIPS code. """
		if row["tract"] != "NA" and row["county"] != "NA":
			if row["tract"] not in list(self.geographic_data["tract_fips"]) or row["county"] not in list(self.geographic_data['county_fips']):
				row["tract"] = random.choice(self.geographic_data["tract_fips"])
				row["county"] = row["tract"][:5]
				print(row["tract"], row["county"])
		return row

	def v628_1_const(self, row):
		"""1) Ethnicity of Applicant or Borrower: 1 must equal 1, 11, 12, 13, 14, 2, 3, or 4, and cannot be left blank,
			   unless an ethnicity is provided in Ethnicity of Applicant or Borrower: Free Form Text Field for Other
			   Hispanic or Latino."""
		eth_enums = ["1", "11", "12", "13", "14", "2", "3", "4"]
		if row["app_eth_1"] =="" and row["app_eth_free"] =="":
			row["app_eth_1"] = random.choice(eth_enums)
		return row

	def v628_2_const(self, row):
		"""2) Ethnicity of Applicant or Borrower: 2; Ethnicity of Applicant or Borrower: 3; Ethnicity of Applicant or
	   	Borrower: 4; Ethnicity of Applicant or Borrower: 5 must equal 1, 11, 12, 13, 14, 2, or be left blank."""
		#this should be handled by lar_generation
		return row

	def v628_3_const(self, row):
		"""3) Each Ethnicity of Applicant or Borrower code can only be reported once."""
		eth_enums = ["1", "11", "12", "13", "14", "2"]
		eth_fields = [row["app_eth_1"], row["app_eth_2"], row["app_eth_3"], row["app_eth_4"], row["app_eth_5"]]
		eth_field_vals = set(eth_fields) #get distinct values
		eth_field_vals.discard("") #discard blanks
		blanks = 0
		for field in eth_fields:
			if field == "":
				blanks +=1
		if len(eth_field_vals) + blanks < 5: #check if total distinct values plust number of blanks is correct
			row["app_eth_1"], row["app_eth_2"], row["app_eth_3"], row["app_eth_4"], row["app_eth_5"] = \
			self.no_enum_dupes(fields=eth_fields,  enum_list=eth_enums)
		return row

	def v628_4_const(self, row):
		"""4) If Ethnicity of Applicant or Borrower: 1 equals 3 or 4; then Ethnicity of Applicant or Borrower: 2; Ethnicity
	   	of Applicant or Borrower: 3; Ethnicity of Applicant or Borrower: 4; Ethnicity of Applicant or Borrower: 5
	  	must be left blank."""
		if row["app_eth_1"] in ("3", "4"):
			row["app_eth_2"] = ""
			row["app_eth_3"] = ""
			row["app_eth_4"] = ""
			row["app_eth_5"] = ""
		return row

	def v629_2_const(self, row):
		"""2) If Ethnicity of Applicant or Borrower Collected on the Basis of Visual Observation or Surname equals 1,
         			then Ethnicity of Applicant or Borrower: 1 must equal 1 or 2;
         			and Ethnicity of Applicant or Borrower: 2 must equal 1, 2 or be left blank;
         			and Ethnicity of Applicant or Borrower: 3;
         			Ethnicity of Applicant or Borrower: 4;
         			and Ethnicity of Applicant or Borrower: 5 must all be left blank."""
		if row["app_eth_basis"] == "1":
			
			row["app_eth_3"] = ""
			row["app_eth_4"] = ""
			row["app_eth_5"] = ""
			if row["app_eth_1"] not in ("1", "2"):
				row["app_eth_1"] = random.choice(("1", "2"))
			if row["app_eth_2"] not in ("1", "2"):
				row["app_eth_2"] = random.choice(("1", "2"))
		return row

	def v629_3_const(self, row):
		"""3) If Ethnicity of Applicant or Borrower Collected on the Basis of Visual Observation or Surname equals 2,
		then Ethnicity of Applicant or Borrower: 1 must equal 1, 11, 12, 13, 14, 2 or 3. """
		if row["app_eth_basis"] == "2" and row["app_eth_1"] not in ("1", "11", "12", "13", "14", "2", "3"):
			row["app_eth_1"] = random.choice(("1", "11", "12", "13", "14", "2", "3"))
		return row

	def v630_const(self, row):
		"""1) If Ethnicity of Applicant or Borrower: 1 equals 4, then Ethnicity of Applicant or Borrower Collected on the Basis of Visual Observation or Surname 
			must equal 3.
		2) If Ethnicity of Applicant or Borrower Collected on the Basis of Visual Observation or Surname equals 3, then Ethnicity of Applicant or Borrower: 1 
			must equal 3 or 4."""
		if row["app_eth_1"] == "4":
			row["app_eth_basis"] = "3"
		if row["app_eth_basis"] == "3" and row["app_eth_1"] not in ("3", "4"):
			row["app_eth_1"] = random.choice(("3", "4"))
		return row

	def v631_1_const(self, row):
		"""1) Ethnicity of Co-Applicant or Co-Borrower: 1 must equal 1, 11, 12, 13, 14, 2, 3, 4, or 5, and cannot be
			left blank, unless an ethnicity is provided in Ethnicity of Co-Applicant or Co-Borrower: Free Form Text
			Field for Other Hispanic or Latino."""
		if row["co_app_eth_1"] == "" and row["co_app_eth_free"] == "":
			row["co_app_eth_1"] = random.choice(["1","11", "12", "13", "14", "2", "3", "4", "5"])
		return row

	def v631_2_const(self, row):
		"""2) Ethnicity of Co-Applicant or Co-Borrower: 2; Ethnicity of Co-Applicant or Co-Borrower: 3; Ethnicity
			of Co-Applicant or Co-Borrower: 4; Ethnicity of CoApplicant or Co-Borrower: 5 must equal 1, 11, 12, 13, 14, 2, or be left blank."""
		#this should be done by the lar_generator code
		return row

	def v631_3_const(self, row):
		"""3) Each Ethnicity of Co-Applicant or Co-Borrower code can only be reported once."""
		co_app_eth_enums=["1","11", "12", "13", "14", "2", ""]
		co_app_eth_fields = [row["co_app_eth_1"], row["co_app_eth_2"], row["co_app_eth_3"], row["co_app_eth_4"], row["co_app_eth_5"]]
		co_app_eth_vals = set(co_app_eth_fields) #get distinct values
		co_app_eth_vals.discard("") #remove blanks
		blanks = 0
		for field in co_app_eth_fields:
			if field == "":
				blanks +=1
		if len(co_app_eth_vals) + blanks < 5:#check if blanks count and distinct values is correct
				row["co_app_eth_1"], row["co_app_eth_2"], row["co_app_eth_3"], row["co_app_eth_4"], row["co_app_eth_5"] = \
				self.no_enum_dupes(fields=co_app_eth_fields,  enum_list=co_app_eth_enums)
		return row

	def v631_4_const(self, row):
		"""4) If Ethnicity of Co-Applicant or Co-Borrower: 1 equals 3, 4, or 5; then Ethnicity of Co-Applicant or
		Co-Borrower: 2; Ethnicity of Co-Applicant or CoBorrower:  3; Ethnicity of Co-Applicant or CoBorrower:
		4; Ethnicity of Co-Applicant or CoBorrower: 5 must be left blank."""
		if row["co_app_eth_1"] in ("3", "4", "5"):
			row["co_app_eth_2"] = ""
			row["co_app_eth_3"] = ""
			row["co_app_eth_4"] = ""
			row["co_app_eth_5"] = ""
		return row

	def v632_const(self, row):
		"""1) If Ethnicity of Co-Applicant or Co-Borrower Collected on the Basis of Visual Observation or Surname equals 1; 
			then Ethnicity of Co-Applicant or Co-Borrower: 1 must equal 1 or 2; and Ethnicity of Co-Applicant or Co-Borrower: 2 
			must equal 1, 2 or be left blank; and Ethnicity of Co-Applicant or CoBorrower: 3; Ethnicity of Co-Applicant or 
			Co-Borrower: 4; Ethnicity of Co-Applicant or CoBorrower: 5 must all be left blank. 
		2) If Ethnicity of Co-Applicant or Co-Borrower Collected on the Basis of Visual Observation or Surname equals  2; 
			then Ethnicity of Co-Applicant or Co-Borrower: 1 must equal 1, 11, 12, 13, 14, 2 or 3"""

		eths = ["1", "2"]
		if row["co_app_eth_basis"] == "1":
			if row["co_app_eth_1"] not in ("1","2"):
				row["co_app_eth_1"] = random.choice(eths)
			if row["co_app_eth_1"] in eths:
				eths.remove(row["co_app_eth_1"])
			if row["co_app_eth_2"] not in ("1","2"):
				row["co_app_eth_2"] = random.choice(eths)
			row["co_app_eth_3"] = ""
			row["co_app_eth_4"] = ""
			row["co_app_eth_5"] = ""

		elif row["co_app_eth_basis"] == "2":
			if row["co_app_eth_1"] not in ("1", "11", "12", "13", "14", "2", "3"):
				row["co_app_eth_1"] = random.choice(("1", "11", "12", "13", "14", "2", "3"))
		return row

	def v633_const(self, row):
		"""1) If Ethnicity of Co-Applicant or Co-Borrower: 1 equals 4, then Ethnicity of Co-Applicant or CoBorrower
			Collected on the Basis of Visual Observation or Surname must equal 3. 
		"""
		if row["co_app_eth_1"] == "4":
			row["co_app_eth_basis"] = "3"
		return row

	def v634_const(self, row):
		"""1) If Ethnicity of Co-Applicant or Co-Borrower: 1 equals 5, then Ethnicity of Co-Applicant or CoBorrower
			Collected on the Basis of Visual Observation or Surname must equal 4, and the reverse must be true."""
		if row["co_app_eth_1"] == "5":
			row["co_app_eth_basis"] = "4"
		if row["co_app_eth_basis"] == "4":
			row["co_app_eth_1"] = "5"
		return row

	def v635_1_const(self, row):
		"""1) Race of Applicant or Borrower: 1 must equal 1, 2, 21, 22, 23, 24, 25, 26, 27, 3, 4, 41, 42, 43, 44, 5, 6, or 7,
			and cannot be left blank, unless a race is provided in Race of Applicant or Borrower: Free Form Text
			Field for American Indian or Alaska Native Enrolled or Principal Tribe, Race of Applicant or Borrower:
			Free Form Text Field for Other Asian, or Race of Applicant or Borrower: Free Form Text Field for Other Pacific Islander."""
		if row["app_race_1"] ==  "" and row["app_race_native_text"]== "" and row["app_race_asian_text"]== "" and row["app_race_islander_text"] == "":
			row["app_race_1"] = random.choice(("1", "2", "21", "22", "23", "24", "25", "26", "27", "3", "4", "41", "42", "43", "44", "5", "6", "7"))
		return row

	def v635_2_const(self, row):
		"""2) Race of Applicant or Borrower: 2; Race of Applicant or Borrower: 3; Race of Applicant or Borrower: 4;
		Race of Applicant or Borrower: 5 must equal 1, 2, 21, 22, 23, 24, 25, 26, 27, 3, 4, 41, 42, 43, 44, 5, or be left blank."""
		#this should be handled by the lar schema
		return row

	def v635_3_const(self, row):
		"""3) Each Race of Applicant or Borrower code can only be reported once."""
		race_fields = [row["app_race_1"], row["app_race_2"], row["app_race_3"], row["app_race_4"], row["app_race_5"]]
		race_enums = ["1", "2", "21", "22", "23", "24", "25", "26", "27", "3", "4", "41", "42", "43", "44", "5"]
		race_field_vals = set(race_fields) #get distinct values
		race_field_vals.discard("") #remove blanks
		blanks = 0
		for field in race_fields:
			if field == "":
				blanks +=1
		if len(race_field_vals) + blanks < 5: #check if blanks and distinct values is correct 
			row["app_race_1"], row["app_race_2"], row["app_race_3"], row["app_race_4"], row["app_race_5"] = \
			self.no_enum_dupes(fields=race_fields,  enum_list=race_enums)
		return row

	def v635_4_const(self, row):
		"""4) If Race of Applicant or Borrower: 1 equals 6 or 7; then Race of Applicant or Borrower: 2; Race of Applicant or Borrower: 3;
			Race of Applicant or Borrower: 4; Race of Applicant or Borrower: 5 must all be left blank."""
		if row["app_race_1"] in ("6", "7"):
			row["app_race_2"] = ""
			row["app_race_3"] = ""
			row["app_race_4"] = ""
			row["app_race_5"] = ""
		return row

	def v636_const(self, row):
		"""1) If Race of Applicant or Borrower Collected on the Basis of Visual Observation or Surname equals 1;
			then Race of Applicant or Borrower: 1 must equal 1, 2, 3, 4, or 5; and Race of Applicant or Borrower: 2;
			Race of Applicant or Borrower: 3; Race of Applicant or Borrower: 4; Race of Applicant or Borrower: 5
			must equal 1, 2, 3, 4, or 5, or be left blank.
		2) If Race of Applicant or Borrower Collected on the Basis of Visual Observation or Surname equals 2,
			Race of Applicant or Borrower: 1 must equal 1, 2, 21, 22, 23, 24, 25, 26, 27, 3, 4, 41, 42, 43, 44, 5 or 6;
			and Race of Applicant or Borrower: 2; Race of Applicant or Borrower: 3; Race of Applicant or Borrower: 4;
			Race of Applicant or Borrower: 5 must equal 1, 2, 21, 22, 23, 24, 25, 26, 27, 3, 4, 41, 42, 43, 44, 5, or be left blank."""
		if row["app_race_basis"] == "1":
			if row["app_race_1"] not in ("1","2","3","4","5"):
				row["app_race_1"] = random.choice(("1","2","3","4","5"))
			if row["app_race_2"] not in ("1","2","3","4","5"):
				row["app_race_2"] = random.choice(("1","2","3","4","5"))
			if row["app_race_3"] not in ("1","2","3","4","5"):
				row["app_race_3"] = random.choice(("1","2","3","4","5"))
			if row["app_race_4"] not in ("1","2","3","4","5"):
				row["app_race_4"] = random.choice(("1","2","3","4","5"))
			if row["app_race_5"] not in ("1","2","3","4","5"):
				row["app_race_5"] = random.choice(("1","2","3","4","5"))
		if row["app_race_basis"] == "2":
			if row["app_race_1"] not in ("1", "2", "21", "22", "23", "24", "25", "26", "27", "3", "4", "41", "42", "43", "44", "5", "6"):
				row["app_race_1"] = random.choice(("1", "2", "21", "22", "23", "24", "25", "26", "27", "3", "4", "41", "42", "43", "44", "5", "6"))
		return row

	def v637_const(self, row):
		"""1) If Race of Applicant or Borrower: 1 equals 7, then Race of Applicant or Borrower Collected on the Basis of Visual Observation 
			or Surname must equal 3.
		2) If Race of Applicant or Borrower Collected on the Basis of Visual Observation or Surname equals 3; then Race of Applicant or 
			Borrower: 1 must equal 6 or 7. """
		if row["app_race_1"] == "7":
			row["app_race_basis"] = "3"
		if row["app_race_basis"] == "3":
			if row["app_race_1"] not in ("6", "7"):
				row["app_race_1"] = random.choice(("6", "7"))
		return row

	def v638_const(self, row):
		"""1) Race of Co-Applicant or Co-Borrower: 1 must equal 1, 2, 21, 22, 23, 24, 25, 26, 27, 3, 4, 41, 42, 43, 44, 5, 6, 7, or 8, 
			and cannot be left blank, unless a race is provided in Race of Co-Applicant or CoBorrower: Free Form Text Field 
			for American Indian or Alaska Native Enrolled or Principal Tribe, Race of Co-Applicant or Co-Borrower: 
			Free Form Text Field for Other Asian, or Race of Co-Applicant or CoBorrower: Free Form Text Field for Other Pacific Islander.
		2) Race of Co-Applicant or Co-Borrower: 2; Race of Co-Applicant or Co-Borrower: 3; Race of Co-Applicant or 
			Co-Borrower: 4; Race of Co-Applicant or Co-Borrower: 5 must equal 1, 2, 21, 22, 23, 24, 25, 26, 27, 3, 4, 41, 42, 43, 44, 5, or be left blank. 
		3) Each Race of Co-Applicant or Co-Borrower code can only be reported once.
		4) If Race of Co-Applicant or Co-Borrower: 1 equals 6, 7, or 8, then Race of Co-Applicant or Co-Borrower: 2; 
			Race of Co-Applicant or Co-Borrower: 3; Race of Co-Applicant or Co-Borrower: 4; and Race of CoApplicant or Co-Borrower: 5 must be left blank."""
		if row["co_app_race_1"] =="" and row["co_app_race_native_text"]=="" and row["co_app_race_asian_text"]=="" and row["co_app_race_islander_text"]=="":
			row["co_app_race_1"] = random.choice(("1", "2", "21", "22", "23", "24", "25", "26", "27", "3", "4", "41", "42", "43", "44", "5", "6", "7", "8"))
		#each code must only be used once
		race_enums = ["1", "2", "21", "22", "23", "24", "25", "26", "27", "3", "4", "41", "42", "43", "44", "5", "6", "7","8"]
		race_fields = [row["co_app_race_1"], row["co_app_race_2"], row["co_app_race_3"], row["co_app_race_4"], row["co_app_race_5"]]
		race_field_vals = set(race_fields) #get distinct values
		race_field_vals.discard("")  #remove blanks
		blanks = 0
		for field in race_fields:
			if field == "":
				blanks +=1
		if len(race_field_vals) + blanks < 5: #check if distinct value plus blanks is correct
			row["co_app_race_1"], row["co_app_race_2"], row["co_app_race_3"], row["co_app_race_4"], row["co_app_race_5"] = \
			self.no_enum_dupes(fields=race_fields,  enum_list=race_enums[:-3])

		if row["co_app_race_1"] in ("6", "7", "8"):
			row["co_app_race_2"] = ""
			row["co_app_race_3"] = ""
			row["co_app_race_4"] = ""
			row["co_app_race_5"] = ""
		return row

	def v639_const(self, row):
		"""1) If Race of Co-Applicant or Co-Borrower Collected on the Basis of Visual Observation or Surname equals 1, 
			then Race of Co-Applicant or Co-Borrower: 1 must equal 1, 2, 3, 4, or 5; and Race of CoApplicant or 
			Co-Borrower: 2; Race of Co-Applicant or Co-Borrower: 3; Race of Co-Applicant or CoBorrower: 4; 
			Race of Co-Applicant or Co-Borrower: 5 must equal 1, 2, 3, 4, or 5, or be left blank.
		2) If Race of Co-Applicant or Co-Borrower Collected on the Basis of Visual Observation or Surname equals 2, 
			then Race of Co-Applicant or Co-Borrower: 1 must equal 1, 2, 21, 22, 23, 24, 25, 26, 27, 3, 4, 41, 42, 43, 44, 5 or 6; 
			and Race of Co-Applicant or CoBorrower: 2; Race of Co-Applicant or Co-Borrower: 3; Race of 
			Co-Applicant or Co-Borrower: 4; Race of CoApplicant or Co-Borrower: 5 must equal 
			1, 2, 21, 22, 23, 24, 25, 26, 27, 3, 4, 41, 42, 43, 44, 5, or be left blank."""
		if row["co_app_race_basis"] == "1":
			if row["co_app_race_1"] not in ("1", "2", "3", "4", "5"):
				row["co_app_race_1"] = random.choice(("1", "2", "3", "4", "5"))
			row["co_app_race_2"] = ""
			row["co_app_race_3"] = ""
			row["co_app_race_4"] = ""
			row["co_app_race_5"] = ""

		if row["co_app_race_basis"] =="2":
			if row["co_app_race_1"] not in ("1", "2", "21", "22", "23", "24", "25", "26", "27", "3", "4", "41", "42", "43", "44", "5", "6"):
				row["co_app_race_1"] = random.choice(("1", "2", "21", "22", "23", "24", "25", "26", "27", "3", "4", "41", "42", "43", "44", "5", "6"))
		return row

	def v640_const(self, row):
		"""If Race of Co-Applicant or Co-Borrower: 1 equals 7, then Race of Co-Applicant or Co-Borrower Collected 
			on the Basis of Visual Observation or Surname must equal 3.
		"""
		if row["co_app_race_1"] =="7":
			row["co_app_race_basis"] = "3"
		return row

	def v641_const(self, row):
		"""1) If Race of Co-Applicant or Co-Borrower: 1 equals 8, then Race of Co-Applicant or Co-Borrower
			Collected on the Basis of Visual Observation or Surname must equal 4, and the reverse must be true."""
		if row["co_app_race_1"] == "8":
			row["co_app_race_basis"] = "4"
		if row["co_app_race_basis"] == "4":
			row["co_app_race_1"] = "8"
		return row

	def v643_const(self, row):
		"""If Sex of Applicant or Borrower Collected on the Basis of Visual Observation or Surname equals 1, then
			Sex of Applicant or Borrower must equal 1 or 2.
		"""
		if row["app_sex_basis"] =="1" and row["app_sex"] not in ("1", "2"):
			row["app_sex"] = random.choice(("1","2"))
		return row

	def v644_const(self, row):
		"""1) If Sex of Applicant or Borrower Collected on the Basis of Visual Observation or Surname equals 2,
			then Sex of Applicant or Borrower must equal 1, 2, 3, or 6.
		2) If Sex of Applicant or Borrower equals 6, then Sex of Applicant or Borrower Collected on the Basis of
			Visual Observation or Surname must equal 2 or 3.

			Inclusion of value, 3 is from cfpb/hmda-platform#2771."""
		if row["app_sex_basis"] == "2" and row["app_sex"] not in ("1", "2", "3", "6"):
			row["app_sex"] = random.choice(("1", "2", "3", "6"))
		if row["app_sex"] == "6":
			row["app_sex_basis"] = random.choice(("2", "3"))
		return row

	def v645_const(self, row):
		"""
		If Sex of Applicant or Borrower equals 4, then Sex of Applicant or Borrower Collected on the Basis of
			Visual Observation or Surname must equal 3.
		"""
		if row["app_sex"] == "4":
			row["app_sex_basis"] = "3"
		return row

	def v647_const(self, row):
		"""If Sex of Co-Applicant or Co-Borrower Collected on the Basis of Visual Observation or Surname equals 1,
			then Sex of Co-Applicant or Co-Borrower must equal 1 or 2.
		"""
		if row["co_app_sex_basis"] == "1" and row["co_app_sex"] not in ("1", "2"):
			row["co_app_sex"] = random.choice(("1", "2"))
		return row

	def v648_const(self, row):
		"""1) If Sex of Co-Applicant or Co-Borrower Collected on the Basis of Visual Observation or Surname equals 2,
			then Sex of Co-Applicant or Co-Borrower must equal 1, 2, 3 or 6.
		2) If Sex of Co-Applicant or Co-Borrower equals 6, then Sex of Co-Applicant or Co-Borrower Collected on the
			Basis of Visual Observation or Surname must equal 2 or 3.

			Inclusion of value, 3 is from cfpb/hmda-platform#2774.
			"""
		if row["co_app_sex_basis"] == "2" and row["co_app_sex"] not in ("1", "2", "3", "6"):
			row["co_app_sex"] = random.choice(("1", "2", "3", "6"))
		if row["co_app_sex"] == "6":
			row["co_app_sex_basis"] = random.choice(("2","3"))
		return row

	def v649_const(self, row):
		"""If Sex of Co-Applicant or Co-Borrower equals 4, then Sex of Co-Applicant or Co-Borrower Collected
			on the Basis of Visual Observation or Surname must equal 3."""
		if row["co_app_sex"] == "4":
			row["co_app_sex_basis"] = "3"
		return row

	def v650_const(self, row):
		"""1) If Sex of Co-Applicant or Co-Borrower Collected on the Basis of Visual Observation or Surname equals 4, 
			then Sex of Co-Applicant or Co-Borrower must equal 5, and the reverse must be true."""
		if row["co_app_sex_basis"] == "4":
			row["co_app_sex"] = "5"
		if row["co_app_sex"] == "5":
			row["co_app_sex_basis"] = "4"
		return row

	def v651_const(self, row):
		"""1) If the Ethnicity of Applicant or Borrower: 1 equals 4; and Race of Applicant or Borrower: 1 equals 7;
			and Sex of Applicant or Borrower equals 4 indicating the applicant or borrower is a non-natural person,
			then Age of Applicant or Borrower must equal 8888."""
		if row["app_eth_1"] == "4" and row["app_race_1"] == "7" and row["app_sex"] == "4":
			row["app_age"] = "8888"
		return row

	def v652_const(self, row): 
		"""1) If the Ethnicity of Co-Applicant or Co-Borrower: 1 equals 4; and Race of Co-Applicant or Co-Borrower: 1 equals 7; 
			and Sex of Co-Applicant or Co-Borrower: 1 equals 4 indicating that the co-applicant or coborrower
			is a non-natural person, then Age of CoApplicant or Co-Borrower must equal 8888."""
		if row["co_app_eth_1"] == "4" and row["co_app_race_1"] == "7" and row["co_app_sex"] == "4":
			row["co_app_age"] = "8888"
		return row

	def v654_const(self,row):
		"""1) If Multifamily Affordable Units is a number, then Income must be NA."""
		if row["affordable_units"] != "NA" and row["affordable_units"] !="":
			row["income"] = "NA"
		return row

	def v655_const(self, row):
		"""1) If Ethnicity of Applicant or Borrower: 1 equals 4; and Race of Applicant or Borrower: 1 equals 7; and
			Sex of Applicant or Borrower: 1 equals 4 indicating the applicant is a non-natural person, then Income must be NA.
		2) If Ethnicity of Co-Applicant or Co-Borrower: 1 equals 4; and Race of Co-Applicant or Co-Borrower: 1 equals 7;
			and Sex of Co-Applicant or Co-Borrower: 1 equals 4 indicating that the co-applicant or coborrower is a non-natural person,
			then Income must be NA. """
		if row["app_eth_1"] == "4" and row["app_race_1"] == "7" and row["app_sex"] == "4":
			row["income"] = "NA"
		if row["co_app_eth_1"] == "4" and row["co_app_race_1"] == "7" and row["co_app_sex"] == "4":
			row["income"] = "NA"
		return row

	def v656_const(self, row): 
		"""2) If Action Taken equals 2, 3, 4, 5, 7 or 8, then Type of Purchaser must equal 0."""
		if row["action_taken"] in ("2", "3", "4", "5", "7", "8"):
			row["purchaser_type"] = "0"
		return row

	def v657_const(self, row):
		"""1) If Action Taken equals 3, 4, 5, 6, or 7, then Rate Spread must be NA.
		3) If Reverse Mortgage equals 1, then Rate Spread must be NA."""
		if row["action_taken"] in ("3", "4", "5", "6", "7") or row["reverse_mortgage"] == "1":
			row["rate_spread"] = "NA"
		return row

	def v658_const(self, row): 
		"""1) If Action Taken equals 2, 3, 4, 5, 7, or 8, then HOEPA Status must be 3."""
		if row["action_taken"] in ("2", "3", "4", "5", "7", "8"):
			row["hoepa"] = "3"
		return row

	def v661_const(self, row): 
		"""1) If Credit Score of Applicant or Borrower equals 8888 indicating not applicable, then Applicant or
			Borrower, Name and Version of Credit Scoring Model must equal 9, and the reverse must be true."""
		if row["app_credit_score"] == "8888":
			row["app_score_name"] = "9"
		if row["app_score_name"] == "9":
			row["app_credit_score"] ="8888"
		return row

	def v662_const(self, row): 
		"""1) If Applicant or Borrower, Name and Version of Credit Scoring Model equals 1, 2, 3, 4, 5, 6, 7, or 9,
			then Applicant or Borrower, Name and Version of Credit Scoring Model: Conditional Free Form Text
			Field for Code 8 must be left blank, and the reverse must be true.
		2) If Applicant or Borrower, Name and Version of Credit Scoring Model equals 8, then Applicant or
			Borrower, Name and Version of Credit Scoring Model: Conditional Free Form Text Field for Code 8
			must not be blank, and the reverse must be true."""

		if row["app_score_name"] in ("1", "2", "3", "4", "5", "6", "7", "9"):
			row["app_score_code_8"] = ""
		elif row["app_score_code_8"] =="" and row["app_score_name"] not in ("1", "2", "3", "4", "5", "6", "7", "9"):
			row["app_score_name"] = random.choice(("1", "2", "3", "4", "5", "6", "7", "9"))
		elif row["app_score_name"] == "8" and row["app_score_code_8"] =="":
			row["app_score_code_8"] = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(25))
		elif row["app_score_code_8"] != "" and row["app_score_name"] != "8":
			row["app_score_name"] = "8"
		return row

	def v663_const(self, row): 
		"""1) If Action Taken equals 4, 5, or 6, then Credit Score of Applicant or Borrower must equal 8888; and
			Applicant or Borrower, Name and Version of Credit Scoring Model must equal 9; and Applicant or
			Borrower, Name and Version of Credit Scoring Model: Conditional Free Form Text Field for Code 8
			must be left blank."""
		if row["action_taken"] in ("4", "5", "6"):
			row["app_credit_score"] = "8888"
			row["app_score_name"] = "9"
			row["app_score_code_8"] = ""
		return row

	def v664_const(self, row): 
		"""1) If Action Taken equals 4, 5, or 6, then Credit Score of Co-Applicant or Co-Borrower must equal 8888;
			and Co-Applicant or Co-Borrower, Name and Version
			of Credit Scoring Model must equal 9; and CoApplicant or Co-Borrower, Name and Version of
			Credit Scoring Model: Conditional Free Form Text Field for Code 8 must be left blank."""
		if row["action_taken"] in ("4", "5", "6"):
			row["co_app_credit_score"] = "8888"
			row["co_app_score_name"] = "9"
			row["co_app_score_code_8"] = ""
		return row

	def v666_const(self,row):
		"""1) If Credit Score of Co-Applicant or Co-Borrower equals 8888 indicating not applicable, then CoApplicant
			or Co-Borrower, Name and Version of Credit Scoring Model must equal 9, and the reverse must be true.
		2) If Credit Score of Co-Applicant or Co-Borrower equals 9999 indicating no co-applicant, then CoApplicant
			or Co-Borrower, Name and Version of Credit Scoring Model must equal 10, and the reverse must be true."""
		if row["co_app_credit_score"] == "8888":
			row["co_app_score_name"] = "9"
		if row["co_app_score_name"] == "9":
			row["co_app_credit_score"] = "8888"
		if row["co_app_credit_score"] == "9999":
			row["co_app_score_name"] = "10"
		if row["co_app_score_name"] == "10":
			row["co_app_credit_score"] = "9999"
		return row

	def v667_const(self, row): 
		"""1) If Co-Applicant or Co-Borrower, Name and Version of Credit Scoring Model equals 1, 2, 3, 4, 5, 6, 7, 9, or
			10, then Co-Applicant or Co-Borrower, Name and Version of Credit Scoring Model: Conditional Free
			Form Text Field for Code 8 must be left blank, and the reverse must be true.
		2) If Co-Applicant or Co-Borrower, Name and Version of Credit Scoring Model equals 8, then Co-Applicant
			or Co-Borrower, Name and Version of Credit Scoring Model: Conditional Free Form Text Field for Code 8
			must not be left blank, and the reverse must be true."""
		if row["co_app_score_name"] in ("1", "2", "3", "4", "5", "6", "7", "9", "10"):
			row["co_app_score_code_8"] = ""
		elif row["co_app_score_code_8"] == "" and row["co_app_score_name"] not in ("1", "2", "3", "4", "5", "6", "7", "9", "10"):
			row["co_app_score_name"] = random.choice(("1", "2", "3", "4", "5", "6", "7", "9", "10"))
		elif row["co_app_score_name"] == "8" and row["co_app_score_code_8"] =="":
			row["co_app_score_code_8"] = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(25))
		elif row["co_app_score_code_8"] != "" and row["co_app_score_name"] != "8":
			row["co_app_score_name"] = "8"
		return row

	def v668_const(self, row):
		"""1) If Ethnicity of Applicant or Borrower: 1 equals 4; and Race of Applicant or Borrower: 1 equals 7; and
			Sex of Applicant or Borrower equals 4 indicating the applicant is a non-natural person then Credit Score of
			Applicant or Borrower must equal 8888 indicating not applicable.
		2) If Ethnicity of Co-Applicant or Co-Borrower: 1 equals 4; and Race of Co-Applicant or Co-Borrower:
			1 equals 7; and Sex of Co-Applicant or Co-Borrower equals 4 indicating that the co-applicant is a nonnatural
			person, then Credit Score of Co-Applicant or Co-Borrower must equal 8888 indicating not applicable."""

		if row["app_eth_1"]  == "4" and row["app_race_1"] == "7" and row["app_sex"] == "4":
			row["app_credit_score"] = "8888"
		if row["co_app_eth_1"] == "4" and row["co_app_race_1"] == "7" and row["co_app_sex"] == "4":
			row["co_app_credit_score"] = "8888"
		return row

	def v669_const(self,row):
		"""1) Reason for Denial: 1 must equal 1, 2, 3, 4, 5, 6, 7, 8, 9, or 10, and cannot be left blank.
		2) Reason for Denial: 2; Reason for Denial: 3; and Reason for Denial: 4 must equal 1, 2, 3, 4, 5, 6, 7, 8,
			9, or be left blank.
		3) Each Reason for Denial code can only be reported once.
		4) If Reason for Denial: 1 equals 10, then Reason for Denial: 2; Reason for Denial: 3; and Reason for Denial: 4 must all be left blank."""
		denial_fields = [row["denial_1"], row["denial_2"], row["denial_3"], row["denial_4"]]
		denial_enums = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

		if row["denial_1"] not in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10"):
			row["denial_1"] = random.choice(("1", "2", "3", "4", "5", "6", "7", "8", "9", "10"))
		denial_vals = set(denial_fields) #get distinct values
		denial_vals.discard("") #remove blanks
		blanks = 0
		for field in denial_fields:
			if field == "":
				blanks +=1
		if len(denial_vals) + blanks < 5: #check if blanks and distinct values are correct
			row["denial_1"], row["denial_2"], row["denial_3"], row["denial_4"] = \
			self.no_enum_dupes(fields=denial_fields, enum_list=denial_enums)

		if row["denial_1"] == "10":
			row["denial_2"] = ""
			row["denial_3"] = ""
			row["denial_4"] = ""
		return row

	def v670_const(self, row): 
		"""1) If Action Taken equals 3 or 7, then the Reason for Denial: 1 must equal 1, 2, 3, 4, 5, 6, 7, 8, or 9, and the reverse must be true.
		2) If Action Taken equals 1, 2, 4, 5, 6, or 8, then Reason for Denial: 1 must equal 10, and the reverse must be true."""
		if row["action_taken"] in ("3", "7") and row["denial_1"] not in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
			row["denial_1"] = random.choice(("1", "2", "3", "4", "5", "6", "7", "8", "9"))
		#elif row["denial_1"] in ("1", "2", "3", "4", "5", "6", "7", "8", "9") and row["action_taken"] not in ("3", "7"):
		#	row["action_taken"] = random.choice(("3", "7"))
		elif row["action_taken"] in ("1", "2", "4", "5", "6", "8") and row["denial_1"] != "10":
			row["denial_1"] = "10"
		#elif row["denial_1"] =="10" and row["action_taken"] not in ("1", "2", "4", "5", "6", "8"):
		#	row["action_taken"] = random.choice(("1", "2", "4", "5", "6", "8"))
		return row

	def v671_const(self, row):
		""" 1) Reason for Denial: 1; Reason for Denial: 2; Reason for Denial: 3; or Reason for Denial: 4 was
			reported Code 9: Other; however, the Reason for Denial: Conditional Free Form Text Field for Code 9
			was left blank; or
		2) The Reason for Denial: Conditional Free Form Text Field for Code 9 was reported, but Code 9 was
			not reported in Reason for Denial: 1; Reason for Denial: 2; Reason for Denial: 3; or Reason for Denial: 4."""
		if (row["denial_1"] == "9" or row["denial_2"] == "9" or row["denial_3"] == "9" or row["denial_4"]=="9") and row["denial_code_9"] =="":
			row["denial_code_9"] = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(25))
		elif row["denial_code_9"] !="" and (row["denial_1"] != "9" and row["denial_2"] !="9" and row["denial_3"]!="9" and row["denial_4"] !="9"):
			row["denial_code_9"] = ""
		return row

	def v672_const(self, row):
		"""1) Total Loan Costs must be a number greater than or equal to 0 or NA, and cannot be left blank.
		2) If Total Points and Fees is a number greater than or equal to 0, then Total Loan Costs must be NA.
		3) If Reverse Mortgage equals 1, then Total Loan Costs must be NA.
		4) If Open-End Line of Credit equals 1, then Total Loan Costs must be NA.
		5) If Business or Commercial Purpose equals 1, then Total Loan Costs must be NA.
		6) If Action Taken equals 2, 3, 4, 5, 7 or 8, then Total Loan Costs must be NA."""
		if row["loan_costs"] !="NA":
			if float(row["loan_costs"]) <0:
				row["loan_costs"] = "10"
		if row["points_fees"] != "NA":
			if float(row["points_fees"] )>=0:
				row["loan_costs"] = "NA"
		if row["reverse_mortgage"] == "1":
			row["loan_costs"] = "NA"
		if row["open_end_credit"] == "1":
			row["loan_costs"] = "NA"
		if row["business_purpose"] == "1":
			row["loan_costs"] = "NA"
		if row["action_taken"] in ("2", "3", "4", "5", "7", "8"):
			row["loan_costs"] = "NA"
		return row

	def v673_const(self, row): 
		"""1) Total Points and Fees must be a number greater than or equal to 0 or NA, and cannot be left blank.
		2) If Action Taken equals 2, 3, 4, 5, 6, 7 or 8 then Total Points and Fees must be NA.
		3) If Reverse Mortgage equals 1, then Total Points and Fees must be NA.
		4) If Business or Commercial Purpose equals 1, then Total Points and Fees must be NA.
		5) If Total Loan Costs is a number greater than or equal to 0, then Total Points and Fees must be NA."""
		if row["action_taken"] in ("2", "3", "4", "5", "6", "7", "8"):
			row["points_fees"] = "NA"
		if row["reverse_mortgage"] == "1":
			row["points_fees"] = "NA"
		if row["business_purpose"] == "1":
			row["points_fees"] = "NA"
		if row["loan_costs"] != "NA":
			if float(row["loan_costs"]) >=0:
				row["points_fees"] = "NA"
		return row

	def v674_const(self, row):
		"""1) Origination Charges must be a number greater than or equal to 0 or NA, and cannot be left blank.
		2) If Reverse Mortgage equals 1, then Origination Charges must be NA.
		3) If Open-End Line of Credit equals 1, then Origination Charges must be NA.
		4) If Business or Commercial Purpose equals 1, then Origination Charges must be NA.
		5) If Action Taken equals 2, 3, 4, 5, 7 or 8, then Origination Charges must be NA."""
		if row["reverse_mortgage"] == "1":
			row["origination_fee"] = "NA"
		if row["open_end_credit"] == "1":
			row["origination_fee"] = "NA"
		if row["business_purpose"] == "1":
			row["origination_fee"] = "NA"
		if row["action_taken"] in ("2", "3", "4", "5", "7", "8"):
			row["origination_fee"] = "NA"
		return row

	def v675_const(self, row):
		"""1) Discount Points must be a number greater than 0, blank, or NA.
		2) If Reverse Mortgage equals 1, then Discount Points must be NA.
		3) If Open-End Line of Credit equals 1, then Discount Points must be NA.
		4) If Business or Commercial Purpose equals 1, then Discount Points must be NA.
		5) If Action Taken equals 2, 3, 4, 5, 7 or 8, then Discount Points must be NA."""
		if row["reverse_mortgage"] == "1":
			row["discount_points"] = "NA"
		if row["open_end_credit"] =="1":
			row["discount_points"] = "NA"
		if row["business_purpose"] == "1":
			row["discount_points"] = "NA"
		if row["action_taken"] in ("2", "3", "4", "5", "7", "8"):
			row["discount_points"] = "NA"
		return row

	def v676_const(self, row):
		"""1) Lender Credits must be a number greater than 0, blank, or NA.
		2) If Reverse Mortgage equals 1, then Lender Credits must be NA.
		3) If Open-End Line of Credit equals 1, then Lender Credits must be NA.
		4) If Business or Commercial Purpose equals 1, then Lender Credits must be NA.
		5) If Action Taken equals 2, 3, 4, 5, 7 or 8, then Lender Credits must be NA."""
		if row["reverse_mortgage"] == "1":
			row["lender_credits"] = "NA"
		if row["open_end_credit"] == "1":
			row["lender_credits"] = "NA"
		if row["business_purpose"] == "1":
			row["lender_credits"] = "NA"
		if row["action_taken"] in ("2", "3", "4", "5", "7", "8"):
			row["lender_credits"] = "NA"
		return row

	def v677_const(self, row):
		"""1) Interest Rate must be a number greater than or equal to 0, NA or Exempt, and cannot be left blank.
		2) If Action Taken equals 3, 4, 5, or 7; then Interest Rate must be NA."""
		if row["action_taken"] in ("3", "4", "5", "7"):
			row["interest_rate"] = "NA"
		return row

	def v678_const(self, row): 
		"""1) Prepayment Penalty Term must be a whole number greater than 0 or NA, and cannot be left blank.
		2) If Action Taken equals 6, then Prepayment Penalty Term must be NA.
		3) If Reverse Mortgage equals 1, then Prepayment Penalty Term must be NA.
		4) If Business or Commercial Purpose equals 1, then Prepayment Penalty Term must be NA.
		5) If both Prepayment Penalty Term and Loan Term are numbers, then Prepayment Penalty Term must
		be less than or equal to Loan Term."""
		if row["action_taken"] == "6":
			row["prepayment_penalty"] = "NA"
		if row["reverse_mortgage"] == "1":
			row["prepayment_penalty"] = "NA"
		if row["business_purpose"] == "1":
			row["prepayment_penalty"] = "NA"
		if row["loan_term"] != "NA" and row["loan_term"] != "Exempt" and row["prepayment_penalty"] !="NA" \
			and row["prepayment_penalty"] != "Exempt":
			if int(row["loan_term"]) >=0 and int(row["prepayment_penalty"]) > int(row["loan_term"]):
				row["prepayment_penalty"] = row["loan_term"]
		return row

	def v679_const(self, row): 
		"""1) Debt-to-Income Ratio must be either a number or NA, and cannot be left blank.
		2) If Action Taken equals 4, 5 or 6, then Debt-to-Income Ratio must be NA.
		3) If Multifamily Affordable Units is a number, then Debt-to-Income Ratio must be NA."""
		if row["action_taken"] in ("4", "5", "6"):
			row["dti"] = "NA"
		if row["affordable_units"] !="NA":
			row["dti"] = "NA"
		return row

	def v680_const(self, row): 
		"""1) If Ethnicity of Applicant or Borrower: 1 equals 4; and Race of Applicant or Borrower: 1 equals 7; and
 			Sex of Applicant or Borrower: 1 equals 4 indicating the applicant or borrower is a non-natural person;
			and the Ethnicity of Co-Applicant or Co-Borrower: 1 equals 5; and Race of Co-Applicant or Co-Borrower:
			1 equals 8; and Sex of Co-Applicant or Co-Borrower: 1 equals 5 indicating that there is no co-applicant or
			co-borrower, then Debt-to-Income Ratio must be NA.
		2) If Ethnicity of Applicant or Borrower: 1 equals 4; and Race of Applicant or Borrower: 1 equals 7; and
			Sex of Applicant or Borrower: 1 equals 4 indicating the applicant or borrower is a non-natural person;
			and the Ethnicity of Co-Applicant or Co-Borrower: 1 equals 4; and Race of Co-Applicant or Co-Borrower:
			1 equals 7; and Sex of Co-Applicant or Co-Borrower: 1 equals 4 indicating that the co-applicant or coborrower
			is also a non-natural person, then Debt-toIncome Ratio must be NA."""
		if row["app_eth_1"] == "4" and row["app_race_1"] == "7" and row ["app_sex"] == "4" and \
		row["co_app_eth_1"] == "5" and row["co_app_race_1"] == "8" and row["co_app_sex"] == "5":
			row["dti"] = "NA"
		if row["app_eth_1"] == "4" and row["app_race_1"] == "7" and row ["app_sex"] == "4" and \
		row["co_app_eth_1"] == "4" and row["co_app_race_1"] == "7" and row["co_app_sex"] == "4":
			row["dti"] = "NA"
		return row

	def v681_const(self, row): 
		"""1) Combined Loan-to-Value Ratio must be either a number greater than 0 or NA, and cannot be left blank.
		2) If Action Taken equals 4, 5, or 6, then Combined Loan-to-Value ratio must be NA."""
		if row["action_taken"] in ("4", "5", "6"):
			row["cltv"] = "NA"
		return row

	def v682_const(self, row): 
		"""1) Loan Term must be either a whole number greater than zero or NA, and cannot be left blank.
		2) If Reverse Mortgage equals 1, then Loan Term must be NA."""
		if row["reverse_mortgage"] == "1":
			row["loan_term"] = "NA"
		return row

	def v688_const(self, row):
		"""1) Property Value must be either a number greater than 0 or NA, and cannot be left blank.
		2) If Action Taken equals 4 or 5, then Property Value must be NA."""
		if row["action_taken"] in ("4", "5"):
			row["property_value"] = "NA"
		return row

	def v689_const(self, row): 
		"""1) Manufactured Home Secured Property Type must equal 1, 2 or 3, and cannot be left blank.
		2) If Multifamily Affordable Units is a number, then Manufactured Home Secured Property Type must equal 3.
		3) If Construction Method equals 1, then Manufactured Home Secured Property Type must equal 3."""
		if row["affordable_units"] not in  ["NA", "Exempt"]:
			row["manufactured_type"] = "3"
		if row["const_method"] == "1":
			row["manufactured_type"] = "3"
		return row

	def v690_const(self, row): 
		"""1) Manufactured Home Land Property Interest must equal 1, 2, 3, 4, or 5, and cannot be left blank.
		2) If Multifamily Affordable Units is a number, then Manufactured Home Land Property Interest must equal 5.
		3) If Construction Method equals 1, then Manufactured Home Land Property Interest must equal 5."""
		if row["affordable_units"] not in  ["NA", "Exempt"]:
			row["manufactured_interest"] = "5"
		if row["const_method"] == "1":
			row["manufactured_interest"] = "5"
		return row

	def v692_const(self, row): 
		"""2) If Total Units is less than 5, then Multifamily Affordable Units must be NA.
		3) If Total Units is greater than or equal to 5, then Multifamily Affordable Units must be less than or
		equal to Total Units. """
		if int(row["total_units"]) < 5:
			row["affordable_units"] = random.choice(["NA", "Exempt"])
		if row["affordable_units"] not in ["NA", "Exempt"] and int(row["affordable_units"]) > int(row["total_units"]):
			row["affordable_units"] = row["total_units"]
		return row

	def v693_const(self, row):
		"""1) If Action Taken equals 6, then Submission of Application must equal 3, and the reverse must be true."""
		if row["action_taken"] == "6":
			row["app_submission"] = "3"
		if row["app_submission"] == "3":
			row["action_taken"] = "6"
		return row

	def v694_const(self, row): 
		"""1) Initially Payable to Your Institution must equal 1, 2 or 3, and cannot be left blank.
		2) If Action Taken equals 6, then Initially Payable to Your Institution must equal 3.
		3) If Action Taken equals 1, then Initially Payable to Your Institution must equal 1 or 2."""
		if row["action_taken"] == "6":
			row["initially_payable"] = "3"
		if row["action_taken"] == "1" and row["initially_payable"] not in ("1", "2"):
			row["initially_payable"] = random.choice(("1", "2"))
		return row
        
	def v695_const(self, row):
		"""1) NMLSR Identifier must be a valid NMLSR ID in integer format, NA, or Exempt, and cannot be left blank.
		2) NMLSR Identifier must not contain only the number zero (0) as a value."""
		row["mlo_id"] = "NA"
            
		return row

	def v696_const(self, row):
		"""1) Automated Underwriting System: 1 must equal
            1111, 1, 2, 3, 4, 5, 6, or 7 and cannot be left blank.
            Automated Underwriting System: 2; Automated
            Underwriting System: 3; Automated Underwriting
            System: 4; and Automated Underwriting System: 5
            must equal 1, 2, 3, 4, 5, 7 or be left blank.

            2) Automated Underwriting System Result: 1 must
            equal 1111, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
            15, 16, 17, 18, 19, 20, 21, 22, 23, or 24 and cannot
            be left blank. Automated Underwriting System
            Result: 2; Automated Underwriting System Result: 3;
            Automated Underwriting System Result: 4; and
            Automated Underwriting System Result: 5 must
            equal 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
            16, 18, 19, 20, 21, 22, 23, 24 or be left blank.
            
            3) The number of reported Automated Underwriting
            Systems must equal the number of reported
            Automated Underwriting System Results."""
            
		aus_sys = [row["aus_1"], row["aus_2"], row["aus_3"], row["aus_4"], row["aus_5"]]
		aus_results = [row["aus_result_1"], row["aus_result_2"], row["aus_result_3"], row["aus_result_4"], row["aus_result_5"]]

		#set Not applicable and blanks correctly
		if row["aus_1"] == "6":
			row["aus_result_1"] ="17"
		if row["aus_2"] == "":
			row["aus_result_2"] =""
		if row["aus_3"] == "":
			row["aus_result_3"] =""
		if row["aus_4"] == "":
			row["aus_result_4"] =""
		if row["aus_5"] == "":
			row["aus_result_5"] =""

		#Ensure AUS system and AUS result are both exempt if either is exempt and that all other AUS or results fields are blank
		if row["aus_1"] == "1111" or row["aus_result_1"] == "1111":
			row["aus_result_1"] = "1111"
			row["aus_result_2"] = ""
			row["aus_result_3"] = ""
			row["aus_result_4"] = ""
			row["aus_result_5"] = ""

			row["aus_1"] = "1111"
			row["aus_2"] = ""
			row["aus_3"] = ""
			row["aus_4"] = ""
			row["aus_5"] = ""

		#number of reported systems must match the number of reported results
		result_enums = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", 
			"17", "18", "19", "20", "21", "22", "23", "24", "16")

		aus_1_vals = ['1', '2', '3', '4', '5', '6', '7']

		if (row["aus_1"] in aus_1_vals and row['aus_result_1'] == '') or (row["aus_1"] == '' and row['aus_result_1'] in aus_results): 

			row["aus_1"] = random.choice(aus_1_vals)
			row["aus_result_1"] = random.choice(result_enums)

		
		for i in range(1, len(aus_sys)):
			if aus_sys[i] in ("1", "2", "3", "4", "5", "7") and aus_results[i] not in result_enums:
				aus_sys[i] = random.choice(result_enums[:-1])
			
		#Ensure code 5 free form text is marked if the text field is populated
		if (row["aus_1"]  != "5" and row["aus_2"] != "5" and row["aus_3"] != "5" and row["aus_4"] != "5" and row["aus_5"] != "5") and \
		row["aus_code_5"] != "":
			row["aus_code_5"] = ""

		#Ensure code 16 free form text is marked if the text field is populated
		if row["aus_result_1"] != "16" and row["aus_result_2"] != "16" and row["aus_result_3"] != "16" and row["aus_result_4"] !="16" \
		and row["aus_result_5"] != "16" and row["aus_code_16"] !="":
			row["aus_code_16"] = ""

		return row

	def v699_const(self, row): 
		"""1) If Automated Underwriting System: 1; Automated Underwriting System: 2; Automated Underwriting
			System: 3; Automated Underwriting System: 4; or Automated Underwriting System: 5 equals 5,
			then the corresponding Automated Underwriting System Result: 1; Automated Underwriting System Result: 2;
			Automated Underwriting System Result: 3; Automated Underwriting System Result: 4; or
			Automated Underwriting System Result: 5 must equal 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, or 16."""
		aus_sys = [row["aus_1"], row["aus_2"], row["aus_3"], row["aus_4"], row["aus_5"]]
		aus_results = [row["aus_result_1"], row["aus_result_2"], row["aus_result_3"], row["aus_result_4"], row["aus_result_5"]]

		for i in range(len(aus_sys)):
			if aus_sys[i] == "5":
				if aus_results[i] not in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", 
					"14", "15", "16", "18", "19", "20", "21", "22", "23", "24"):
					row["aus_result_"+str(i+1)] = random.choice(("1", "2", "3", "4", "5", "6", 
						"7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "18", "19",
						"20", "21", "22", "23", "24"))
		return row

	def v700_const(self, row):
		"""1) If Automated Underwriting System: 1 equals 6, then the corresponding Automated Underwriting
			System Result: 1 must equal 17; 
			and the Automated Underwriting System: 2; Automated UnderwritingSystem: 3; Automated Underwriting System: 4; 
			Automated Underwriting System: 5;vAutomated Underwriting System Result: 2; Automated Underwriting System Result: 3; Automated
			Underwriting System Result: 4; and Automated Underwriting System Result: 5 must all be left blank.
		2) If Automated Underwriting System Result: 1 equals 17, then the corresponding
			Automated Underwriting System: 1 must equal 6; and the Automated Underwriting System: 2; Automated
			Underwriting System: 3; Automated Underwriting System: 4; Automated Underwriting System: 5;
			Automated Underwriting System Result: 2; Automated Underwriting System Result: 3;
			Automated Underwriting System Result: 4; and Automated Underwriting System Result: 5 must all be left blank."""
		if row["aus_1"] == "6":
			row["aus_2"] = ""
			row["aus_3"] = ""
			row["aus_4"] = ""
			row["aus_5"] = ""
			row["aus_result_1"] = "17"
			row["aus_result_2"] = ""
			row["aus_result_3"] = ""
			row["aus_result_4"] = ""
			row["aus_result_5"] = ""
		if row["aus_result_1"] == "17":
			row["aus_1"] = "6"
			row["aus_2"] = ""
			row["aus_3"] = ""
			row["aus_4"] = ""
			row["aus_5"] = ""
			row["aus_result_2"] = ""
			row["aus_result_3"] = ""
			row["aus_result_4"] = ""
			row["aus_result_5"] = ""
		return row


	def v701_const(self, row): 
		"""1) If Automated Underwriting System: 2; Automated Underwriting System: 3; Automated Underwriting
			System: 4; or Automated Underwriting System: 5 was left blank, then the corresponding reported
			Automated Underwriting System Result: 2; Automated Underwriting System Result: 3;
			Automated Underwriting System Result: 4; or Automated Underwriting System Result: 5 must be left blank."""
		aus_sys = [row["aus_1"], row["aus_2"], row["aus_3"], row["aus_4"], row["aus_5"]]
		aus_results = [row["aus_result_1"], row["aus_result_2"], row["aus_result_3"], row["aus_result_4"], row["aus_result_5"]]

		for i in range(len(aus_sys)):
			if aus_sys[i] != "":
				if aus_results[i] =="":
					row["aus_result_"+str(i+1)] = random.choice(("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"))
		return row

	def v702_const(self, row): 
		"""1) Automated Underwriting System: 1; Automated Underwriting System: 2; Automated Underwriting
			System: 3; Automated Underwriting System: 4; or Automated Underwriting System: 5 was reported
			Code 5: Other. However, the Automated Underwriting System: Conditional Free Form Text Field for Code 5
			was left blank; or
		2) The Automated Underwriting System: Conditional Free Form Text Field for Code 5 was reported, but
			Code 5 was not reported in Automated Underwriting System: 1; Automated Underwriting System: 2;
			Automated Underwriting System: 3; Automated Underwriting System: 4; or Automated Underwriting System: 5."""
		aus_sys = [row["aus_1"], row["aus_2"], row["aus_3"], row["aus_4"], row["aus_5"]]
		aus_results = [row["aus_result_1"], row["aus_result_2"], row["aus_result_3"], row["aus_result_4"], row["aus_result_5"]]
		for i in range(len(aus_sys)):
			if aus_sys[i] == "5":
				if row["aus_code_5"] == "":
					row["aus_code_5"] = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(25))
		if row["aus_code_5"] != "" and row["aus_1"] !="5" and row["aus_2"] !="5" and row["aus_3"] !="5" and row["aus_4"] !="5" and row["aus_5"] !="5":
			row["aus_code_5"] = ""
		return row

	def v703_const(self, row):
		"""1) Automated Underwriting System Result: 1; Automated Underwriting System Result: 2;
			Automated Underwriting System Result: 3; Automated Underwriting System Result: 4; or
			Automated Underwriting System Result: 5 was reported Code 16: Other. However, the Automated
			Underwriting System Result: Conditional Free Form Text Field for Code 16 was left blank; or
		2) The Automated Underwriting System Result : Conditional Free Form Text Field for Code 16 was
			reported, but Code 16 was not reported in Automated Underwriting System Result: 1; Automated
			Underwriting System Result: 2; Automated Underwriting System Result: 3; Automated
			Underwriting System Result: 4; or Automated Underwriting System Result: 5."""
		#code 16 field is blank but code 16 was reported
		aus_results = [row["aus_result_1"], row["aus_result_2"], row["aus_result_3"], row["aus_result_4"], row["aus_result_5"]]
		for i in range(len(aus_results)):
			if aus_results[i] == "16":
				if row["aus_code_16"] == "":
					row["aus_code_16"] = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(25))
		#code 16 field is populated but code 16 was not reported
		if row["aus_code_16"] != "" and row["aus_result_1"] !="16" and row["aus_result_2"] !="16" and row["aus_result_3"] !="16" and row["aus_result_4"] !="16" \
		and row["aus_result_5"] !="16":
			row["aus_code_16"] = ""
		return row

	def v704_const(self, row): 
		"""1) If Action Taken equals 6, then Automated Underwriting System: 1 must equal 6.
		2) If Action Taken equals 6, then Automated Underwriting System Result: 1 must equal 17."""
		if row["action_taken"] == "6":
			row["aus_1"] = "6"
			row["aus_result_1"] = "17"
		return row
	def v705_const(self, row): 
		"""1) If Ethnicity of Applicant or Borrower: 1 equals 4; and Race of Applicant or Borrower: 1 equals 7; and
			Sex of Applicant or Borrower: 1 equals 4 indicating the applicant is a non-natural person; and the
			Ethnicity of Co-Applicant or Co-Borrower: 1 equals 5; and Race of Co-Applicant or Co-Borrower: 1 equals
			8; and Sex of Co-Applicant or Co-Borrower: 1 equals 5 indicating that there is no co-applicant or coborrower,
			then Automated Underwriting System: 1 must equal 6; and Automated Underwriting System Result: 1 must equal 17.
		2) If the Ethnicity of Applicant or Borrower: 1 equals 4; and Race of Applicant or Borrower: 1 equals 7;
			and Sex of Applicant or Borrower: 1 equals 4 indicating the applicant or borrower is a non-natural
			person; and Ethnicity of Co-Applicant or CoBorrower: 1 equals 4; and Race of Co-Applicant or
			Co-Borrower: 1 equals 7; and Sex of Co-Applicant or Co-Borrower: 1 equals 4 indicating that the coapplicant
			or co-borrower is also a non-natural person, then Automated Underwriting System: 1 must equal
			6; and Automated Underwriting System Result: 1 must equal 17."""
		if row["app_eth_1"] =="4" and row["app_race_1"] == "7" and row["app_sex"] == "4" and \
		row["co_app_eth_1"] == "5" and row["co_app_race_1"] =="8" and row["co_app_sex"] == "5":
			row["aus_1"] = "6"
			row["aus_result_1"] = "17"
		if row["app_eth_1"] =="4" and row["app_race_1"] == "7" and row["app_sex"] == "4" and \
		row["co_app_eth_1"] == "4" and row["co_app_race_1"] =="7" and row["co_app_sex"] == "4":
			row["aus_1"] = "6"
			row["aus_result_1"] = "17"
		return row
	
	def v709_const(self, row):
		"""1) If Street Address, City, and Zip Code is reported Exempt, then all three
			 must be reported Exempt."""
		if (row["street_address"] == "Exempt" or row["city"] == "Exempt" or row["zip_code"] == "Exempt"):
			row["street_address"] = "Exempt"
			row["city"] = "Exempt"
			row["zip_code"] = "Exempt"
		return row
	
	def v710_const(self, row):
		
		"""If the Credit Score exemption election is taken,"""
		"""1) Credit Score of Applicant or Borrower, Credit
			Score of Co-Applicant or Co-Borrower, Applicant or
			Borrower, Name and Version of Credit Scoring
			Model, and Co-Applicant or Co-Borrower, Name and
			Version of Credit Scoring Model must be reported
			1111; and
		   2) Applicant or Borrower, Name and Version of
			Credit Scoring Model: Conditional Free Form Text
			Field for Code 8 and Co-Applicant or Co-Borrower,
			Name and Version of Credit Scoring Model:
			Conditional Free Form Text Field for Code 8 must be
			left blank."""
		if row["app_credit_score"] == "1111":
			row["co_app_credit_score"] = "1111"
			row["app_score_name"] = "1111"
			row["co_app_score_name"] = "1111"
			row["app_score_name"] = ""
			row["app_score_code_8"] = ""
			row["co_app_score_name"] = ""
			row["co_app_score_code_8"] = ""
		return row


	def v711_const(self, row):

		"""1) If the Reason for Denial exemption election is
			taken, Reason for Denial: 1 must be reported 1111;
			and
		   2) Reason for Denial: 2, Reason for Denial: 3,
			Reason for Denial: 4, and Reason for Denial:
			Conditional Free Form Text Field for Code 9 must be
			left blank."""
		if row["denial_1"] == "1111":
			row["denial_1"] = "1111"
			row["denial_1"] = "1111" 
			row["denial_2"] = ""
			row["denial_3"] = ""
			row["denial_4"] = ""
			row["denial_code_9"] = ""
		return row


	def v712_const(self, row):
		"""1) If the Total Loan Costs or Total Points and Fees
			  exemption election is taken, Total Loan Costs and
			  Total Points and Fees must be reported Exempt."""
		if (row["loan_costs"] == "Exempt" or row["points_fees"] == "Exempt"):
			row["loan_costs"] = "Exempt"
			row["points_fees"] = "Exempt"

		return row

	def v713_const(self, row):
		"""If the Automated Underwriting exemption election is taken,
		1) Automated Underwriting System: 1 and
			  Automated Underwriting System Result: 1 must be
              reported 1111; and
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
		if row["aus_1"] == "1111":
			row["aus_1"] = "1111" 
			row["aus_result_1"] = "1111"
			row["aus_2"] = "" 
			row["aus_3"] = ""
			row["aus_4"] = "" 
			row["aus_5"] = ""
			row["aus_code_5"] = ""
			row["aus_result_2"] = ""
			row["aus_result_3"] = "" 
			row["aus_result_4"] = ""
			row["aus_result_5"] = ""
			row["aus_code_16"] = ""

		return row
		
	def v714_const(self, row):
		"""1) If the Application Channel exemption election is
			taken, Submission of Application and Initially Payable
			to Your Institution must be reported 1111."""
		if (row["app_submission"] == "1111" or 
			row["initially_payable"] == "1111"):
			row["app_submission"] = "1111"
			row["initially_payable"] = "1111"
		return row
		
	def v715_const(self, row):
		"""1) If the Non-Amortizing Features exemption election
				is taken, Balloon Payment, Interest-Only Payments,
				Negative Amortization and Other Non-amortizing
				Features must be reported 1111."""
		if (row["non_amort_features"] == "1111" or row["balloon"] == "1111" or row["int_only_pmts"] == "1111" or row["neg_amort"] == "1111"):
			row["balloon"] = "1111" 
			row["int_only_pmts"] = "1111" 
			row['neg_amort'] = "1111" 
			row["non_amort_features"] = "1111"

		return row

