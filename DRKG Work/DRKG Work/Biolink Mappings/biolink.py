import yaml
mapping_types = ["broad_mappings", "exact_mappings", "close_mappings", "narrow_mappings"]
with open("big-biolink-model.yaml", "r") as biolink_file:
	biolink_dict = yaml.safe_load(biolink_file)
def find_link(edge_id, database_id):
	for biolink_type in biolink_dict["slots"].keys():
		for mapping_type in mapping_types:
			if mapping_type in biolink_dict["slots"][biolink_type].keys():
				for edge_type in biolink_dict["slots"][biolink_type][mapping_type]:
					if edge_id in edge_type and database_id in edge_type:
						print(edge_type)
						return edge_type, mapping_type, biolink_type, edge_id
print(biolink_dict["slots"].keys())
#with open("C:\\Users\\Aman\\Documents\\DRKG_Work\\Text Files\\Naming\\Edge_Naming\\full_edge_names.txt") as f, open("biolink_mapping_info.txt", 'a') as file:
#	info_lines = []
#	for line in f:
#		func_value = find_link(line.split("\t")[1],line.split("\t")[0])
#		if func_value is not None:
#			info_line = func_value[3] + "\t" + func_value[1] + "\t" + func_value[2]
#			info_lines.append(info_line)
#	for info_line in info_lines:
#		file.write(info_line + "\n")
