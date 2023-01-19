types = ["Gene", "Compound", "Atc", "Disease", "Tax", "Biological Process", "Molecular Function", "Cellular Component", "Pathway", "Side Effect", "Pharmacologic Class"]

def find_matches(ntype):
	total_entities = 0
	matches = 0
	entity_array = []
	het_ids = []
	with open("entity2src.tsv") as f:
		for line in f:
			n_type, nid = (line.split("\t")[0].split('::'))
			if n_type==ntype:
				entity_array.append(nid)
				total_entities += 1
	with open("hetionet-v1.0-nodes.tsv.txt") as f:
		for line in f:
			n_type, nid = (line.split("\t")[0].split('::'))
			if n_type==ntype:
				het_ids.append(nid)
	for entity in entity_array:
		if entity in het_ids:
			matches += 1
	print(str(matches) + " " + ntype + " entity matches")
	print(str(round(matches/total_entities*100)) + " percent of the original " + ntype + " entites had matches in the hetionet file." + "\n")
for type in types:
	find_matches(type)