named_files = {"Anatomy":"anatomy_named.txt","Biological Process":"bio_process_named.txt","Cellular Component":"cell_comp_named.txt","Molecular Function":"mol_function_named.txt","Pathway":"pathway_named.txt","Pharmacologic Class":"pharm_class_named.txt","Side Effect":"side_effect_named.txt"}
skipped_files = {"Anatomy":"anatomy_skipped.txt","Biological Process":"bio_process_skipped.txt","Cellular Component":"cell_comp_skipped.txt","Molecular Function":"mol_function_skipped.txt","Pathway":"pathway_skipped.txt","Pharmacologic Class":"pharm_class_skipped.txt","Side Effect":"side_effect_skipped.txt"}
def add_to_named(nid,name,ntype):
	with open(named_files[ntype], 'a') as f:
		f.write(('{}\t{}\n'.format(nid, name)))
def add_to_skipped(nid,ntype):
	with open(skipped_files[ntype], 'a') as f:
		f.write('{}\n'.format(nid))
def create_temp_array(ntype):
	with open("entity2src.tsv") as f:
		for line in f:
			n_type, nid = line.split("\t")[0].split('::')
			if n_type == ntype:
				temp_array.append(line.split("\t")[0].split("::")[1])
def create_het_ids_dict(ntype):
	with open("hetionet-v1.0-nodes.tsv.txt") as f:
		for line in f:
			n_type, nid = line.split("\t")[0].split('::')
			if n_type == ntype:
				het_ids.update({line.split("\t")[0].split("::")[1]:line.split("\t")[1]})
for ntype in named_files.keys():
	f = open(named_files[ntype], "a")
	f.truncate(0)
	temp_array = []
	het_ids = {}
	create_temp_array(ntype)
	create_het_ids_dict(ntype)
	for nid in temp_array:
		try:
			add_to_named(nid,het_ids[nid],ntype)
		except:
			add_to_skipped(nid,ntype)

