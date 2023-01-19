import requests
from py2neo import Graph

def add_to_named(nid,name):
	with open("symptom_named.txt", "a") as f:
		f.write(nid + "\t" + name + "\n")
def add_to_skipped(nid):
	with open("symptom_skipped.txt", "a") as f:
		f.write(nid + "\n")
def get_WSL_name(symptom_id):
	nih_url = "http://cdek.wustl.edu/mesh/{}/"
	page = requests.get(nih_url.format(symptom_id))
	page = page.text
	start_index = page.find("<title>")
	name = page[start_index:]
	start_index = name.find("|")
	end_index = name.find("(")
	name = name[start_index+1:end_index].strip()
	return name
def get_symptom_name(symptom_id):
	drugbank_atc_url = "https://www.ncbi.nlm.nih.gov/medgen/?term={}"
	page = requests.get(drugbank_atc_url.format(symptom_id))
	page = page.text
	start_index = page.find("<title>")
	name = page[start_index:]
	start_index = name.find(">")
	end_index = name.find("(")
	name = name[start_index+1:end_index].strip()
	if name.find("<")==-1:
		return name
	else: 
		return ""
#with open("temp.txt") as f:
#	for line in f:
#		nid = line.strip()		
#		try:
#			id_name = get_WSL_name(nid)
#			if id_name == "":
#				add_to_skipped(nid)
#			else:
#				add_to_named(nid,get_WSL_name(nid))
#		except:
#			pass
graph = Graph(host='34.86.195.172', port=7687, user='neo4j', password='drkg')
with open("symptom_named.txt") as f:
	for line in f:
		nid,name = line.strip().split("\t")
		graph.run('MATCH (e:Symptom) WHERE e.id="{}" SET e.name="{}" RETURN e.name'.format(nid, name))