import requests
from py2neo import Graph
#with open("atc_named.txt",'a') as f: 
#	f.truncate(0)
#with open("atc_skipped.txt",'a') as s:
#	s.truncate(0)
def add_to_named(nid,name):
	with open("atc_named.txt", "a") as f:
		f.write(nid + "\t" + name + "\n")
def add_to_skipped(nid):
	with open("atc_skipped.txt", "a") as f:
		f.write(nid + "\n")
def get_atc_name(atc_id):
	drugbank_atc_url = "https://www.whocc.no/atc_ddd_index/?code={}&showdescription=no"
	page = requests.get(drugbank_atc_url.format(atc_id))
	page = page.text	
	tag1 = page.find("code="+atc_id+"&showdescription=no")
	tag2 = page.find("code="+atc_id+"&showdescription=yes")
	name = ""
	if tag1 != -1:
		name = page[tag1:]
		start_index = name.find(">")
		end_index = name.find("</a>")
		name = name[start_index+1:end_index]
	elif tag2 != -1:
		name = page[tag2+1:]
		name = name[name.find("code="+atc_id+"&showdescription=yes"):]
		name = name[name.find(">")+1:name.find("</a>")]
	return name
def backup_atc_name(atc_id):
	hipaaspace_atc_url = "https://www.hipaaspace.com/medical_billing/coding/anatomical_therapeutic_chemical_classification_system/{}"
	page = requests.get(hipaaspace_atc_url.format(atc_id))
	page=page.text
	name = ""
	name = page[page.find("<title>"):]
	name = name[name.find("|")+1:]
	name = name[:name.find("|")].strip()
	return name

#with open("entity2src.tsv") as f:
#	for line in f:
#		ntype, nid = line.split("\t")[0].split("::")
#		if ntype=="Atc":			
#			try:
#				id_name = get_atc_name(nid)
#				if id_name == "":
#					add_to_skipped(nid)
#				else:
#					add_to_named(nid,get_atc_name(nid))
#			except:
#				add_to_skipped(nid)
#with open("atc_skipped.txt") as f:
#	for line in f:
#		print(line.strip() + "\t" + backup_atc_name(line.strip()))
#with open("atc_named.txt") as f:
#	lines = f.readlines()
#	new_lines = []
#	ids = []
#	for line in lines:
#		line = line.replace("\t"," ")
#		line = line.replace("\n","")
#		ids.append(line.split(" ")[0].strip())
#		new_lines.append(line[line.find(" "):].strip())
#	with open("atc_named_copy.txt", 'a') as f:
#		f.truncate(0) 
#		for i in range(0,len(new_lines)):
#			new_lines[i] = new_lines[i].lower()
#			new_lines[i] = new_lines[i][0].upper() + new_lines[i][1:]
#			f.write(ids[i] + "\t" + new_lines[i] +"\n")
graph = Graph(host='34.86.195.172', port=7687, user='neo4j', password='drkg')
with open("atc_named.txt") as f:
	for line in f:
		nid, name = line.strip().split("\t")
		graph.run('MATCH (e:Atc) WHERE e.id="{}" SET e.name="{}" RETURN e.name'.format(nid, name))
