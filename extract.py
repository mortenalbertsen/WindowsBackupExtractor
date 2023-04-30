import os
import uuid
from zipfile import ZipFile

def main():
	sourceFolder = "/Volumes/MOR_BACKUP"
	destionationFolder = "/Volumes/BIG-PEN/MOR_BACKUP"
	conflicts_folder = "/Volumes/BIG-PEN/MOR_BACKUP/Conflicts"
	checksums = {};
	# Traverse volumes (start with oldest entry)
	count = 0
	for root, dirs, files in os.walk(sourceFolder, True, False):
		for file in files:
			path_to_file = f"{root}/{file}"
			if file.endswith("zip"):
				#print(f"Opening {path_to_file}")			
				with ZipFile(path_to_file, mode='r') as zip_file:
					for zip_file_info in zip_file.infolist():
						crc_value = zip_file_info.CRC
						entry_name = zip_file_info.filename
						flag_bits = zip_file_info.flag_bits
						#print(f"{path_to_file} contains {entry_name} with checksum: {crc_value} and flag-bits: {flag_bits}")
						entry_name_chopped = entry_name[24:].replace('\\','/')
						entry_name_chopped = replace_characters(entry_name_chopped)
						(parent_folder, filename) = determine_parent_folder_and_filename(entry_name_chopped)
						write_destination = f"{destionationFolder}/{parent_folder}{filename.encode('utf_8').decode('utf_8')}"
						byte_payload = zip_file.read(zip_file_info)
						if entry_name not in checksums: # We haven't come across this file before
							# Write file to destinationFolder	
							os.makedirs(os.path.dirname(write_destination), exist_ok=True) # Make sure directory exists
							with open(write_destination, 'wb') as output_file:
								output_file.write(byte_payload)
							# Update checksums map
							checksums[entry_name] = crc_value
							count = count + 1
						elif we_dont_care_about_it(entry_name_chopped):
							continue
						elif entry_name in checksums and checksums[entry_name] != crc_value: # We've found a different version of the same file
							print(f"Found different version of {entry_name}. Writing to conflicts_folder")
							filename = filename + str(uuid.uuid4())
							write_destination = f"{conflicts_folder}/{parent_folder}{filename.encode('utf_8').decode('utf_8')}"
							os.makedirs(os.path.dirname(write_destination), exist_ok=True) # Make sure directory exists
							with open(write_destination, 'wb') as output_file:
								output_file.write(byte_payload)
			else:
				print(f"Ignoring file {path_to_file}")


def we_dont_care_about_it(input):
	ignorables = ['AppData']
	for ignorable in ignorables:
		if ignorable in input:
			return True

	return False


def determine_parent_folder_and_filename(input: str):
	#print(f"Reciving {input}")
	if '/' not in input:
		return ('', input)
	index = input.rindex('/')

	# Determine parent folder
	parent_folder = input[:index]

	# Determine filename
	filename = input[index:]
	return (parent_folder, filename)

def replace_characters(input):
	replacements = {}
	replacements['¥'] = 'Ø'
	replacements['¢'] = 'ø'
	fixed = input
	for (actual, replacement) in replacements.items():
		fixed = fixed.replace(actual,replacement)
	return fixed

if __name__ == '__main__':
	main()