import random
import string

import pandas as pd
import yaml

import utils

class quality_lar_data_constraints(object):

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
			if func[:1] in ("q") and func[1:4].isdigit()==True:
				self.constraints.append(func)

	#constraint functions
	#these functions will be used to re-generate data for a specific LAR row so that the data row is valid 
	#For example, preapproval code 2 limits the valid entries for action taken


	def q605_const(self, row):
		"""
		1) If Type of Purchaser equals 1 or 3, then Loan Type generally should equal 1.

		2) If Type of Purchaser equals 2, then Loan Type generally should equal 2, 3, or 4.
		"""

		if row["purchaser_type"] in ("1", "3") and row["loan_type"] != "1":
			row["loan_type"] = "1"

		if row["purchaser_type"] in ("2") and row["loan_type"] not in ("2", "3", "4"):
			row["loan_type"] = random.choice(["2", "3", "4"])

		return row


	def q607_const(self, row):
		"""
		1) If Lien Status equals 2, then Loan Amount generally should be less than or equal to $250 thousand (entered as 250000).
		"""
		if row["lien"] == "2" and float(row["loan_amount"]) > 250000:
			row["loan_amount"] = str(random.choice(range(50000, 250000)))

		return row


	def q608_const(self, row):
		"""
		1) If Action Taken equals 1, then the Action Taken Date generally should occur after the Application Date
		"""

		if row["action_taken"] == "1":
			if row["action_date"] <= row["app_date"]:
				row["action_date"] = "20201231" #set to last day of collection year

		return row


	def q609_const(self, row):
		"""
		1) If Type of Purchaser equals 1, 2, 3, or 4, 
		then Rate Spread generally should be less than or equal to 10%, Exempt, or NA.
		"""

		if row["purchaser_type"] in ("1", "2", "3", "4") and row["rate_spread"] not in ("Exempt", "NA"):
			if float(row["rate_spread"]) > 10.0:
				row["rate_spread"] = str(random.choice(range(0, 9)))

		return row


	def q610_const(self, row):
		"""
		1) If Action Taken equals 1, 
		Lien Status equals 1, and 
		Rate Spread is greater than 6.5%, 
		then HOEPA Status generally should be 1.
		"""

		if row["action_taken"] == "1" and row["lien"] == "1" and row["rate_spread"] not in ("NA", "Exempt") \
		and row["hoepa"] != "1":

			if float(row["rate_spread"]) > 6.5:
				row["hoepa"] = "1"

		return row

	def q611_const(self, row):
		"""
		1) If Action Taken equals 1, Lien Status equals 2, and Rate Spread is greater than 8.5%, 
		then HOEPA Status generally should be 1.
		"""

		if row["hoepa"] != "1" and row["total_units"] not in ("1", "2", "3", "4"):
			if row["action_taken"] == "1" and row["lien"] == "2" and row["rate_spread"] not in ("NA", "Exempt"):
					if float(row["rate_spread"]) > 8.5:
						row["hoepa"] = "1"

		return row

	def q612_const(self, row):
		"""
		1) If Type of Purchaser equals 1 or 3, then HOEPA Status generally should be 2 or 3
		"""

		if row["purchaser_type"] in ("1", "3") and row["hoepa"] not in ("2", "3"):
			row["hoepa"] = random.choice(["2", "3"])

		return row


	def q613_const(self, row):
		"""
		1) If Business or Commercial Purpose equals 1, then Loan Purpose generally should equal 1, 2, 31, 32, or 5.
		"""

		loan_purpose_choices = ("1", "2", "31", "32", "5")
		if row["business_purpose"] == "1" and row["loan_purpose"] not in loan_purpose_choices:
			row["loan_purpose"] = random.choice(loan_purpose_choices)

		return row

	def q614_const(self, row):
		"""
		2) The Age of Co-Applicant or Co-Borrower generally should be between 18 and 100 
		unless the Age of Co-Applicant or Co-Borrower is reported 8888 indicating NA or 9999 
			indicating no co-applicant or co-borrower. 
		"""
		if row["capp_age"] not in ("NA", "9999", "8888"):
			if int(row["app_age"]) < 18 or int(row["app_age"]) > 100:
				row["app_age"] = random.choice(range(18, 100))

		if row["co_app_age"] not in ("NA", "9999", "8888"):
			if int(row["co_app_age"]) < 18 or int(row["co_app_age"]) > 100:
				row["co_app_age"] = random.choice(range(18, 100))

		return row

	def q615_const(self, row):
		"""
		2) If Total Points and Fees and Origination Charges are not reported NA or Exempt, 
		and are both nonzero numbers, 
		then Total Points and Fees generally should be greater than Origination Charges.
		"""

		if row["points_fees"] not in ("NA", "Exempt") and row["origination_fee"] not in ("NA", "Exempt"):
			if float(row["points_fees"]) < float(row["origination_fee"]):
				row["points_fees"] = random.choice(range(int(row["origination_fee"]), int(float(row["origination_fee"])*1.2)))

		return row

	def q616_const(self, row):
		"""
		2) If Total Points and Fees and Discount Points are not reported NA or Exempt, 
		and are both nonzero numbers, 
		then Total Points and Fees generally should be greater than Discount Points.
		"""

		if row["points_fees"] not in ("NA", "Exempt", "0") and row["discount_points"] not in ("NA", "Exempt", "0"):
			if float(row["points_fees"]) < float(row["discount_points"]):

				#row["points_fees"] = str(float(row["discount_points"]) + 100)
				switch = row["points_fees"]
				row["points_fees"] = row["discount_points"]
				row["discount_points"] = switch

		return row

	def q617_const(self, row):

		"""
		1) If Loan Type equals 1 
		and Combined Loan-to-Value Ratio and Property Value are not reported NA or Exempt, 
		then the Combined Loan-to Value Ratio generally should be greater than or equal to the Loan to-Value Ratio 

		(calculated Property Value divided by the Loan Amount)
		"""

		if row["loan_type"] == "1" and row["cltv"] not in ("Exempt", "NA") and row["property_value"] not in ("Exempt", "NA"):
			#check if cltv >= ltv, if not, fix it

			ltv = float(row["loan_amount"]) / float(row["property_value"]) * 100

			while float(row["cltv"]) < ltv:
				row["loan_amount"] = float(row["loan_amount"]) * .80
				print(row["loan_amount"])
				ltv = float(row["loan_amount"]) / float(row["property_value"]) * 100
				row["cltv"] = str(random.choice(range(ltv, int(ltv * 1.5))))

		return row


	def q618_const(self, row):
		"""
		1) If Construction Method equals 2, then Manufactured Home Secured Property Type generally should not be 3.

		"""

		if row["const_method"] == "2" and row["manufactured_type"] == "3":
			row["manufactured_type"] = random.choice(["2", "1", "1111"])

		return row
		

	def q619_const(self, row):
		"""
		1) If Construction Method equals 2, then Manufactured Home Land Property Interest generally should not be 5
		"""
		if row["const_method"] == "2" and row["manufactured_interest"] == "5":
			row["manufactured_interest"] = random.choice(["1", "2", "3", "4"])

		return row

	def q620_const(self, row):
		"""
		1) If Business or Commercial Purpose equals 2, then NMLSR ID generally should not be NA.
		"""
		if row["business_purpose"] == "2" and row["mlo_id"] == "NA":
			row["mlo_id"] = "123456"

		return row

	def q622_const(self, row):
		"""
		1) If Reverse Mortgage equals 1, 
		then the Age of Applicant or Borrower generally should be greater than or equal to 62. 
		Your data indicates a number outside this range.
		"""
		if float(row["app_age"]) < 62:
			row["app_age"] = random.choice(range(62, 100))
		return row


	def q624_const(self, row):
		"""
		1) If Loan Type equals 2 and Total Units equals 1, 
		then Loan Amount generally should be less than or equal to $637,000 (reported as 637000).
		"""
		max_amount = 467000
		if row["loan_type"] == "2" and row["total_units"] == "1" and int(row["loan_amount"]) > max_amount:
			row["loan_amount"] = random.choice(range(50000, int(max_amount)))

		return row


	def q625_const(self, row):
		"""
		1) If Loan Type equals 3 and Total Units is less than or equal to 4, 
		then Loan Amount generally should be less than or equal to $1,050,000 (reported as 1050000).
		"""

		if row["loan_type"] == "3" and int(row["total_units"]) < 5 and float(row["loan_amount"]) >= 1050000:
			row["loan_amount"] = random.choice(range(40000, 467000))

		return row


	def q627_const(self, row):
		"""
		1) If Total Units is greater than or equal to 5, 
		then Loan Amount generally should be between $100,000 (reported as 100000) 
		and $10,000,000 (reported as 10000000)
		"""
		if int(row["total_units"]) >= 5 and not (100000 <= float(row["loan_amount"]) <= 10000000):
			row["loan_amount"] = random.choice(range(100000, 467000))

		return row

	def q629_const(self, row):
		"""
		1) If Action Taken equals 1, 2, 3, 4, 5, 7, or 8; Total Units is less than or equal to 4; 
		and Loan Purpose equals 1, 2, or 4, then Income generally should not be NA.
		"""

		if row["action_taken"] in ("1", "2", "3", "4", "5", "7", "8") and int(row["total_units"]) < 5 \
			and row["loan_purpose"] in ("1", "2", "4") and row["income"] == "NA":

			row["income"] = str(random.choice(range(50,500)))

		return row


	def q630_const(self, row):
		"""
		1) If Total Units is greater than or equal to 5, then HOEPA Status generally should equal 3.
		"""

		if row["total_units"] not in ("1", "2", "3", "4") and row["hoepa"] != "3":
			row["hoepa"] = "3"
			row["rate_spread"] = "NA"

		return row


	def q633_const(self, row):
		"""
		1) If Automated Underwriting System: 1; 
			Automated Underwriting System: 2; 
			Automated Underwriting System: 3;  
			Automated Underwriting System: 4; or 
			Automated Underwriting System: 5 equals 4, 

			then the corresponding 

			Automated Underwriting System Result: 1; 
			Automated Underwriting System Result: 2; 
			Automated Underwriting System Result: 3; 
			Automated Underwriting System Result: 4; or 
			Automated Underwriting System Result: 5 

			should equal 3, 4, 10, 15, 18, 19, 20, 21, 22, 23, 24 or 16.
		"""
		valid_aus_results = ["3", "4", "10", "15", "18", "19", "20", "21", "22", "23", "24", "16"]

		if row["aus_1"] == "4" and row["aus_result_1"] not in valid_aus_results:
			row["aus_result_1"] = random.choice(valid_aus_results)

		if row["aus_2"] == "4" and row["aus_result_2"] not in valid_aus_results:
			row["aus_result_2"] = random.choice(valid_aus_results)

		if row["aus_3"] == "4" and row["aus_result_3"] not in valid_aus_results:
			row["aus_result_3"] = random.choice(valid_aus_results)

		if row["aus_4"] == "4" and row["aus_result_4"] not in valid_aus_results:
			row["aus_result_4"] = random.choice(valid_aus_results)

		if row["aus_5"] == "4" and row["aus_result_5"] not in valid_aus_results:
			row["aus_result_5"] = random.choice(valid_aus_results)

		return row


	def q631_const(self, row):
		"""
		1) If Loan Type equals 2, 3, or 4, then Total Units generally should be less than or equal to 4.
		"""

		if row["loan_type"] in ("2", "3", "4") and row["total_units"] not in ("1", "2", "3", "4"):
			row["total_units"] = random.choice(["1", "2", "3", "4"])

		return row

	def q632_const(self, row):
		"""
		1) If aus 1; aus: 2; aus: 3; aus: 4; or aus: 5 equals 3, 
		then the corresponding aus Result: 1; aus Result: 2; aus Result: 3; aus Result: 4; or aus: 5 
		should equal 1, 2, 3, 4, 8, 13, 18, 19 or 16.
		"""
		
		if row["aus_1"] == "3" and row["aus_result_1"] not in ("1", "2", "3", "4", "8", "13", "18", "19", "16"):
			row["aus_result_1"] = random.choice(("1", "2", "3", "4", "8", "13", "18", "19", "16"))
		
		if row["aus_2"] == "3" and row["aus_result_2"] not in ("1", "2", "3", "4", "8", "13", "18", "19", "16"):
			row["aus_result_2"] = random.choice(("1", "2", "3", "4", "8", "13", "18", "19", "16"))
		
		if row["aus_3"] == "3" and row["aus_result_3"] not in ("1", "2", "3", "4", "8", "13", "18", "19", "16"):
			row["aus_result_3"] = random.choice(("1", "2", "3", "4", "8", "13", "18", "19", "16"))
		
		if row["aus_4"] == "3" and row["aus_result_4"] not in ("1", "2", "3", "4", "8", "13", "18", "19", "16"):
			row["aus_result_4"] = random.choice(("1", "2", "3", "4", "8", "13", "18", "19", "16"))
		
		if row["aus_5"] == "3" and row["aus_result_5"] not in ("1", "2", "3", "4", "8", "13", "18", "19", "16"):
			row["aus_result_5"] = random.choice(("1", "2", "3", "4", "8", "13", "18", "19", "16"))

		return row


	def q643_const(self, row):
		"""
		1) If Automated Underwriting System: 1; 
			Automated Underwriting System: 2; 
			Automated Underwriting System: 3; 
			Automated Underwriting System: 4; or
			Automated Underwriting System: 5 
		equals 1, then the corresponding 

		Automated Underwriting System Result: 1; 
		Automated Underwriting System Result: 2; 
		Automated Underwriting System Result: 3; 
		Automated Underwriting System Result: 4; or 
		Automated Underwriting System Result: 5 

		should equal 1, 2, 3, 4, 5, 6, 7, 15, or 16.
		"""
		aus_choices = ("1", "2", "3", "4", "5", "6", "7", "15", "16")

		if row["aus_1"] == "1" and row["aus_result_1"] not in aus_choices:
			row["aus_result_1"] = random.choice(aus_choices)
		
		if row["aus_2"] == "1" and row["aus_result_2"] not in aus_choices:
			row["aus_result_2"] = random.choice(aus_choices)
		
		if row["aus_3"] == "1" and row["aus_result_3"] not in aus_choices:
			row["aus_result_3"] = random.choice(aus_choices)
		
		if row["aus_4"] == "1" and row["aus_result_4"] not in aus_choices:
			row["aus_result_4"] = random.choice(aus_choices)
		
		if row["aus_5"] == "1" and row["aus_result_5"] not in aus_choices:
			row["aus_result_5"] = random.choice(aus_choices)

		return row


	def q644_const(self, row):
		"""
		1) If Automated Underwriting System: 1; 
			Automated Underwriting System: 2; 
			Automated Underwriting System: 3; 
			Automated Underwriting System: 4; or 
			Automated Underwriting System: 5 
		equals 2, 

		then the corresponding 
		
		Automated Underwriting System Result: 1; 
		Automated Underwriting System Result: 2;
		Automated Underwriting System Result: 3; 
		Automated Underwriting System Result: 4; or 
		Automated Underwriting System Result: 5 

		should equal 8, 9, 10, 11, 12, 13, or 16.

		"""
		aus_choices = ("8", "9", "10", "11", "12", "13", "16")

		if row["aus_1"] == "2" and row["aus_result_1"] not in aus_choices:
			row["aus_result_1"] = random.choice(aus_choices)
		
		if row["aus_2"] == "2" and row["aus_result_2"] not in aus_choices:
			row["aus_result_2"] = random.choice(aus_choices)
		
		if row["aus_3"] == "2" and row["aus_result_3"] not in aus_choices:
			row["aus_result_3"] = random.choice(aus_choices)
		
		if row["aus_4"] == "2" and row["aus_result_4"] not in aus_choices:
			row["aus_result_4"] = random.choice(aus_choices)
		
		if row["aus_5"] == "2" and row["aus_result_5"] not in aus_choices:
			row["aus_result_5"] = random.choice(aus_choices)

		return row


	def q648_const(self, row):
		"""
		1) If Action Taken equals 1, 2, 3, 4, 5, 7, or 8, the first 20 characters of the ULI should match the reported LEI.
		"""
		if row["action_taken"] in ("1", "2", "3", "4", "5", "7", "8") and row["uli"][:20] != row["lei"]:
			row["uli"] = row["lei"] + utils.char_string_gen(23)
			row["uli"] = row["uli"] + utils.check_digit_gen(ULI=row["uli"])

		return row


	def q650_2_const(self, row):
		"""
		2) The Interest Rate reported is greater than 20, which may indicate a misplaced decimal point.
		"""

		if row["interest_rate"] not in ("NA", "Exempt") and float(row["interest_rate"]) > 20:
			row["interest_rate"] = random.choice(range(1,15))

		return row

	def q651_1_const(self, row):
		"""
		1) The CLTV reported is greater than 0 but less than 1, which may indicate a misplaced decimal point.
		"""

		if row["cltv"] != "NA" and 0 < float(row["cltv"]) < 1:
			row["cltv"] = random.choice(range(50, 110))

		return row

	def q653_1_const(self, row):
		"""
		1) If Action Taken equals 1, 2, or 8, 
		and the value for CLTV is not NA or Exempt, 
		the CLTV should generally be between 0 and 250.
		"""
		if row["cltv"] != "NA" and float(row["cltv"]) > 120:
			print("*"*100)
			print(row["cltv"])

		return row
	
	def q654_const(self, row):
		"""
		1) If Income is greater than $5,000 (reported as 5) and Action Taken equals 1, 2, or 8, 
		the DTI should generally be between 0 and 80.

		Note: DTI accepts NA and Exempt
		"""

		if row["dti"] not in ["NA", "Exempt"] and row["income"] != "NA":

			if int(row["income"]) > 5 and row["action_taken"] in ["1","2","8"]:
				if float(row["dti"]) < 0 or float(row["dti"]) > 80:
					row["dti"] = random.choice(range(30, 70))

		return row


	def q655_const(self, row):
		"""
		1) If Total Units is greater than or equal to 5 
		and the record relates to a multifamily property, 
		then Multifamily Affordable Units should generally be 0 or an integer
		"""

		if int(row["total_units"]) > 4 and row["affordable_units"] in ("NA"):
			row["affordable_units"] = random.choice(["0", "Exempt"])

		return row




