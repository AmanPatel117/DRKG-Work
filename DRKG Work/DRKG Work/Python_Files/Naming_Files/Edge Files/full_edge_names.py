with open("C:\\Users\\Aman\\Documents\\DRKG_Work\\Text Files\\Edge_Naming\\relation_glossary.tsv") as f, open("C:\\Users\\Aman\\Documents\\DRKG_Work\\Text Files\\Edge_Naming\\full_edge_names.txt", 'a') as full_name_file, open("C:\\Users\\Aman\\Documents\\DRKG_Work\\Text Files\\Edge_Naming\\het_edges.tsv") as het_edges:
	for line in f:
		if line.split("\t")[0].split("::")[0]=="GNBR":
			edge_id = line.split("\t")[0].split("::")[1]
			full_name = line.split("\t")[3]
			interaction_type = line.split("\t")[2]
			if full_name.find(",") != -1:
				full_name = full_name.split(",")[0]
			full_name_file.write("GNBR" + "\t" + edge_id + "\t" + full_name + "\t" + interaction_type + "\n")
	for line in het_edges:
		edge_id = line.split("\t")[1]
		full_name = line.split("\t")[0]
		full_name = full_name.replace(" - ", "_")
		full_name = full_name.replace(" > ", "_")
		full_name_file.write("Hetionet" + "\t" + edge_id + "\t" + full_name + "\n")
