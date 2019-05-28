#This script will generate a file that will fail a specific edit (though others may also fail)
#This script relies on the presence of a clean data file

from file_generator import FileGenerator 

#Instantiating the file generator. 
file = FileGenerator()

file.create_files(kind='error_files')
