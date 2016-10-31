# head_file.py

# fix scanning in the same block (after a successful search and find) for another file_type
# make this a stable version
# research fastest way to read a file in hex

import binascii, re, os, math
from init_drive import getDriveTotal

def getReadProgress(block_num, block_total, file_ctr):                    # give value to view
	#print("Examining Block: ", block_num, " out of ", block_total)       # @to_GUI
	#print("[+] Recovered ", file_ctr, " files.")                         # @to_GUI
	cur_block = block_num*1.0 / block_total * 100
	return(str("{0:.2f}".format(cur_block)), file_ctr)

def fastReadImage(file_name, output_path, lst_srt, lst_end, lst_types, lst_buf, **item_opt):   # improve this by recovering recently deleted files
	file_ctr = 0
	block_size = 131072
	block_num = 0
	output_path = os.path.normcase(output_path)
	
	try:
		file_hndle = open(file_name, 'rb')
	except (OSError, IOError) as e:
		#print("Error: " + file_name + " cannot be read.")               ################## DISPLAY ERROR MESSAGE @to_GUI
		exit(-1)
	
	if re.match(r'/dev/s', file_name) or re.match(r'\\\\.\\', file_name):
		raw_total = getDriveTotal(file_name)
	else:
		raw_total = os.path.getsize(file_name)
	block_total = int(math.ceil(raw_total / block_size))
	unparsed = file_hndle.read(block_size)
	hex_data = binascii.hexlify(unparsed).decode('utf-8')

	srt_pos = 0
	end_pos = 0
	type_ctr = len(lst_types)
	lst_dump = []

	while block_num <= block_total:
		#prog, file_ctr = getReadProgress(block_num, block_total, file_ctr)     # @to_GUI
		
		for i in range(0, type_ctr):
			match = lst_srt[i].search(hex_data)
			if match:
				srt_pos = match.start()
				match = lst_end[i].search(hex_data[srt_pos:])
				
				if match:
					end_pos = match.end()
					file_data = hex_data[srt_pos:end_pos]
					if file_data:
						lst_dump.append(file_data)
				else:
					file_data = hex_data[srt_pos:]
					
					while hex_data and not match:
						if block_num == block_total:
							return
						block_num = block_num + 1
						file_hndle.seek((block_size) * block_num)
						unparsed = file_hndle.read(block_size)
						hex_data = binascii.hexlify(unparsed).decode('utf-8')
						
						match = lst_end[i].search(hex_data)
						if match:
							end_pos = match.end()
							file_data = file_data + hex_data[:end_pos]
							if file_data:
								lst_dump.append(file_data)
						elif len(file_data) > lst_buf[i]:
							end_pos = 0
							match = True
							
							file_data = file_data + hex_data + str(lst_end[i]).replace("re.compile('", "").replace("')", "")      # add replacing regex chars here soon
							lst_dump.append(file_data)
						else:
							file_data = file_data + hex_data
				
				end_pos = end_pos - (end_pos % 2)
				hex_data = hex_data[end_pos:]
						
				if not hex_data and block_num < block_total:
					block_num = block_num + 1
					file_hndle.seek((block_size) * block_num)
					unparsed = file_hndle.read(block_size)
					hex_data = binascii.hexlify(unparsed).decode('utf-8')
				
				#continue                                                 # check if this is even needed
			
			for item in lst_dump:
				if len(item.encode('utf-8')) % 2 != 0:
					item = item + '0'
				file_ctr = file_ctr + 1
				writeImage(item, output_path, lst_types[i], file_ctr)
		
			lst_dump = []
		
		block_num = block_num + 1
		file_hndle.seek((block_size) * block_num)
		unparsed = file_hndle.read(block_size)
		hex_data = binascii.hexlify(unparsed).decode('utf-8')
	
	file_hndle.close()
	
def writeImage(item, output_path, file_type, file_ctr):
	item = item.encode('utf-8')
	file_name = output_path + str(file_ctr) + '].' + file_type
		
	item = binascii.unhexlify(item)
	with open(file_name, 'wb') as f_out:
		f_out.write(item)
