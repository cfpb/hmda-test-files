import os
import pandas as pd
import utils
from file_generator import FileGenerator

class RaceCategorization(object):
	"""
	Creates test files and answer keys that test FFIEC 
	Race Categorization Logic. 

	The logic for race categorization can be found here:
	https://github.com/cfpb/hmda-platform/wiki/Race-Categorization-2018.
	"""
	def __init__(self):
		#Instantiating the file generator class. 
		self.new_file = FileGenerator()

		#Creates an empty dictionary for storing answer key results with
		#each row generation. 
		self.answer_key_dict = {'Row': [],
						   'Answer': [], 
						   'app_race_1': [],
						   'app_race_2': [],
						   'app_race_3': [],
						   'app_race_4': [],
						   'app_race_5': [],
						   'co_app_race_1': [],
						   'co_app_race_2': [],
						   'co_app_race_3': [],
						   'co_app_race_4': [],
						   'co_app_race_5': []
						}

		#Storing minority race codes. 
		self.minority_race_codes = ['1', '2', '21','22','23','24','25','26','27','3','4','41','42','43','44']

		#Creating the output file directory and storing the directory name in a global variable. 
		self.output_directory = '../custom_files/ffiec_logic/output/'
		if not os.path.exists(self.output_directory):
			os.makedirs(self.output_directory)

		#Creating the answer key directory and storing the directory name in a global variable. 
		self.answer_key_directory = '../custom_files/ffiec_logic/answers/'
		if not os.path.exists(self.answer_key_directory):
			os.makedirs(self.answer_key_directory)

		#Storing the name for the clean file path used to generate the race categorization test files.
		self.clean_filepath = "../edits_files/clean_files/Bank1/"

		#Storing the clean file name that points to a file with more than 1000 original rows. 
		self.clean_filename_1000_rows = "clean_file_1000_rows_Bank1.txt"

		#Reads in a TS and LAR dataframe from the clean filepath and filename. 
		self.ts_data, self.lar_data = utils.read_data_file(path=self.clean_filepath, 
			data_file=self.clean_filename_1000_rows)

	def run_answer_key(self, lar_row_df, answer_response, row_number):
		"""
		Creates an answer key row given details from the generated row..
		"""

		answer_key_dict = self.answer_key_dict

		answer_key_dict['Row'].append(str(row_number))
		answer_key_dict['Answer'].append(answer_response)

		answer_key_dict['app_race_1'].append(lar_row_df['app_race_1'].iloc[0])
		answer_key_dict['app_race_2'].append(lar_row_df['app_race_2'].iloc[0])
		answer_key_dict['app_race_3'].append(lar_row_df['app_race_3'].iloc[0])
		answer_key_dict['app_race_4'].append(lar_row_df['app_race_4'].iloc[0])
		answer_key_dict['app_race_5'].append(lar_row_df['app_race_5'].iloc[0])
		
		answer_key_dict['co_app_race_1'].append(lar_row_df['co_app_race_1'].iloc[0])
		answer_key_dict['co_app_race_2'].append(lar_row_df['co_app_race_2'].iloc[0])
		answer_key_dict['co_app_race_3'].append(lar_row_df['co_app_race_3'].iloc[0])
		answer_key_dict['co_app_race_4'].append(lar_row_df['co_app_race_4'].iloc[0])
		answer_key_dict['co_app_race_5'].append(lar_row_df['co_app_race_5'].iloc[0])

		return answer_key_dict

	def run_row_generator(self, changed_value_dictionary, lar_list, answer_response, counter):
		"""
		A helper function that takes a dictionary of columns and new values, and creates a new
		row that validates against syntax and validity edits. The new row is then appended to
		a running list of custom rows, and an answer key dictionary is produced.  
		"""

		#Uses a FileGenerator method to create a new custom row, given a dictionary of columns
		#and new values, a clean filepath and a clean filename with at least 1000 original rows.
		df = self.new_file.validate_custom_row(dictionary=changed_value_dictionary, 
			clean_filepath=self.clean_filepath, clean_filename=self.clean_filename_1000_rows)
		
		#Appends the row to a running list of custom rows.  
		lar_list.append(df)

		#Creates an answer key dictionary that is returned using the counter that keeps track of which
		#row is being added. 
		answer_key_dict = self.run_answer_key(lar_row_df=df, answer_response=answer_response, row_number=counter)

		#Prints the counter. 
		print(counter)

		#Returns the answer key response. 
		return (answer_key_dict)

	def package_file_and_answer_key(self, lar_list, answer_key_dict, answer_response):
		#Creates a lar dataframe from the running custom row list. 
		lar_df = pd.concat(lar_list)

		#Modifies TS data for the new number of LAR entries.
		self.ts_data["lar_entries"] = len(lar_df)

		#Applies unique ULIs to the new dataframe. 
		lar_df = utils.unique_uli(new_lar_df=lar_df, 
			lei=self.ts_data.iloc[0][14])

		#Writes the file to the output directory. 
		utils.write_file(path=self.output_directory, 
			ts_input=self.ts_data, lar_input=lar_df, name=answer_response+".txt")

		#Creates a dataframe from the answer key dictionary. 
		answer_key_dataframe = pd.DataFrame(answer_key_dict)

		#Writes the answer key to the answer key directory. 
		answer_key_dataframe.to_csv(self.answer_key_directory + answer_response + ".csv", index=False)

	def joint_condition_1(self):
		"""
		If Applicant Race 1, 2, 3, 4, or 5 has one or more minority race (1, 2, 21, 
		22, 23, 24, 25, 26, 27, 3, 4, 41, 42, 43, 44) 
		AND Co-Applicant Race: 1, 2, 3, 4, or 5 equals White (5)

		THEN
		Categorize as Joint

		"""
		#Stores a counter for keeping track of row numbers. 
		counter = 0
		#Stores a running list of rows created.
		lar_list = []
		#Stores the answer response for the answer key. 
		answer_response = 'Joint_Race_1'

		#For each combination of codes specified above, a new row is created and added to the running list.  
		for applicant_race in ['1','2','3','4','5']:
				for race_code in self.minority_race_codes:
					for coapplicant_race in ['1','2','3','4','5']:
						#Creates a dictionary of LAR column to changed value. 
						new_dict = {
						"app_race_{applicant_race}".format(applicant_race=applicant_race): race_code,
						"co_app_race_{coapplicant_race}".format(coapplicant_race=coapplicant_race): '5'
						}
						
						#Passes in the dictionary and running list to the row generator method. 
						answer_key_dict = self.run_row_generator(changed_value_dictionary=new_dict, lar_list=lar_list, 
							answer_response=answer_response, counter=counter)

						#Increases the counter by one for the next row. 
						counter = counter + 1
		
		#Packages the LAR dataframe created and the TS sheet into a submission file, storing
		#that and an answer key file in the appropriate directories. 				
		self.package_file_and_answer_key(lar_list=lar_list, answer_key_dict=answer_key_dict, 
			answer_response=answer_response)

	def joint_condition_2(self):
		"""
		If Co-Applicant Race 1, 2, 3, 4, or 5 has one or more minority race (1, 2, 21, 
		22, 23, 24, 25, 26, 27, 3, 4, 41, 42, 43, 44) 
		AND Applicant Race: 1, 2, 3, 4, or 5 equals White (5)

		THEN
		Categorize as Joint

		"""

		#Stores a counter for keeping track of row numbers. 
		counter = 0
		#Stores a running list of rows created.
		lar_list = []
		#Stores the answer response for the answer key. 
		answer_response = 'Joint_Race_2'
		
		#For each combination of codes specified above, a new row is created and added to the running list.
		for race_code in self.minority_race_codes:
			for coapplicant_race in ['1','2','3','4','5']:
				
				#Creates a dictionary of LAR column to changed value. 
				new_dict = {
				"co_app_race_{coapplicant_race}".format(coapplicant_race=coapplicant_race): race_code,
				"app_race_1": "5",
				"app_race_2": "",
				"app_race_3": "",
				"app_race_4": "",
				"app_race_5": ""
				}
				
				#Passes in the dictionary and running list to the row generator method. 
				answer_key_dict = self.run_row_generator(changed_value_dictionary=new_dict, lar_list=lar_list, 
							answer_response=answer_response, counter=counter)

				#Increases the counter by one for the next row.
				counter = counter + 1
		
		#Packages the LAR dataframe created and the TS sheet into a submission file, storing
		#that and an answer key file in the appropriate directories.				
		self.package_file_and_answer_key(lar_list=lar_list, answer_key_dict=answer_key_dict, 
			answer_response=answer_response)









