anatomy_file = open("all_anatomy.txt", 'r')
list_of_names_file = open("hetionet-v1.0-nodes.tsv.txt", "r")
named_file = open("anatomy_named.txt", 'a')
skipped_file = open("anatomy_skipped.txt", 'a')
count = 0
het_ids = {}
anatomy_ids = []
named_file.truncate(0)
def add_to_named(nid, name):
	named_file.write('{}\t{}\n'.format(nid, name))
def add_to_skipped(nid):
	skipped_file.write('{}\n'.format(nid))
for line in anatomy_file:
	anatomy_ids.append(line.split("\t")[0].split("::")[1])
for line in list_of_names_file:
	het_ids.update({line.split("\t")[0].split("::")[1]:line.split("\t")[1]})
for nid in anatomy_ids:
	try:
		add_to_named(nid,het_ids[nid])
	except:
		add_to_skipped(nid)

