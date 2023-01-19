import re
import requests
import time
from py2neo import Graph
from chembl_webresource_client.new_client import new_client

### GENES AND DISEASES ARE DONE!! ###

# source file with entity ids and sources
entity_info = "src/entity2src.tsv" 
# files where any found names will be written
named_files = {"Gene": "named_genes.txt", "Compound": "named_compounds.txt", "Disease": "named_diseases.txt"} 
# files where any ids that the program couldn't find a name for will be written
skipped_files = {"Gene": "skipped_genes.txt", "Compound": "skipped_compounds.txt", "Disease": "skipped_diseases.txt"} 

# pharmgkb source file with some names to be extracted
pharmgkb_entity_file = "pharmgkbDrugLabels.tsv" 

# connection to the graph database on the cloud
graph = Graph(host='34.86.195.172', port=7687, user='neo4j', password='drkg') 

#####################
### DRIVER METHOD ###
#####################
def get_all_entity_names(update_kg=True):
	'''Names all entities in the graph (or at least attempts to). Extracts any entity names that it can based on the entity id and source database. 
	Currently, this only covers most compounds, diseases, and genes.
	:param update_kg: (boolean) True if the extracted names should be used to modifiy the KG, False otherwise
	'''
	# read in the entities that we have already named
	named_entities = read_from_named_entities_files()
	# read in the entities that we attempted and failed
	skipped_entities = read_from_skipped_entities_files()

	count = 0
	total = 39220 + 24313 + 5103 - len(named_entities) - len(skipped_entities)  # 97238
	with open(entity_info, 'r') as f:
		# parse each line to determine the entity type and id
		for line in f: 
			nid, ntype, nsources, nrefs = process_entity_line(line)

			# entity already named or skipped; either way, let's not waste time on it
			if nid in named_entities or nid in skipped_entities:
				continue

			# entity not one of the currently handled types
			if ntype not in ["Gene", "Compound", "Disease"]:
				continue

			# attempt to extract the entity name
			try: 
				name = get_entity_name(nid, ntype)

				# case: we want to update the KG with the name we found
				if update_kg: ## WHEN WOULD WE NOT WANT TO UPDATE THE KG?
					# case: there was a non-empty name found for this entity
					if name is not None:
						success = add_name_to_kg(nid, name, ntype)

						# track if we were able to update this entity in the KG or not
						if success: 
							write_to_named_entities_file(ntype, nid, name)
						else:
							write_to_skipped_entities_file(ntype, nid, name)
					# case: the name was empty :(
					else:
						write_to_skipped_entities_file(ntype, nid)

					# keep track of how many entities we've done so far
					count += 1
					if count % 10 == 0:
						print('{}/{}'.format(count, total)) ##WHAT IS THE PURPOSE OF THIS IF BLOCK?

					# let the computer/database rest so that nothing freezes
					if count % 500 == 0:
						time.sleep(30)
			# we failed when trying to extract the entity name
			except:
				write_to_skipped_entities_file(ntype, nid)

#####################
### FILE HANDLERS ###
#####################
def read_from_named_entities_files():
	'''Reads in the list of entities that we have already named.
	:return: (list) the list of ids of entity which are already named
	'''
	named_entities = []

	for file in named_files.values():
		with open(file, 'r', encoding="utf-8") as f:
			for line in f:
				try:
					nid, name = line.strip().split('\t')
				except:
					nid = line.strip()
					name = ""         #WHEN WOULD THE EXCEPT BLOCK RUN? IF YOU ARE EXTRACTING FROM THE NAMED_FILE, WHY WOULD YOU HAVE AN EMPTY STRING AS NAME
				named_entities.append(nid)

	return named_entities

def write_to_named_entities_file(ntype, nid, name):
	'''Adds an entry to the appropriate named entities file to track that we found the given name for the given id.
	:param ntype: (str) the type of the entity
	:param nid: (str) the id of the entity
	:param name: (str) the name we found for the entity
	'''
	with open(named_files[ntype], 'a', encoding="utf-8") as f:
		f.write('{}\t{}\n'.format(nid, name))

def read_from_skipped_entities_files():
	'''Reads in the list of entities that we previously skipped.
	:return: (list) the list of ids of entity which were skipped
	'''
	skipped_entities = []

	for file in skipped_files.values():
		with open(file, 'r', encoding="utf-8") as f:
			for line in f:
				try:
					nid, name = line.strip().split('\t')
				except:
					nid = line.strip()
				skipped_entities.append(nid)

	return skipped_entities

def write_to_skipped_entities_file(ntype, nid, name=None):
	'''Adds an entry to the appropriate skipped entities file to track that we failed to name the entity.
	:param ntype: (str) the type of the entity
	:param nid: (str) the id of the entity
	:param name: (str, optional) the name we found for the entity, if one was found; otherwise None (default None)
	'''
	with open(skipped_files[ntype], 'a', encoding="utf-8") as f:
		if name is None:
			f.write('{}\n'.format(nid))
		else:
			f.write('{}\t{}\n'.format(nid, name))

def process_entity_line(line):
	'''Parses a single line from the source file which contains information about the entity. 
	Extracts the id, type, sources, and any references.
	:param line: (str) the line from the source file
	:return: (tuple) a tuple which contains all the extracted information about the entity
	'''
	parts = line.strip().split('\t') #I AM NOT FAMILIAR WITH TSV FILES, IT LOOKS LIKE A SPREADSHEET. WHERE ARE THE TABS YOU USED TO SEPARATE THE DATA INTO THE VARIABLES?
	nid, other = parts[0], parts[1:]
	ntype, nid = nid.split('::')
	ntype = ntype.replace(' ', '')
	if len(other) == 1:
		nsources = other[0]  #WHAT IS NSOURCES? 
		i = nsources.find(']')
		nsources = nsources[:i+1]
		nrefs = nsources[i+2:] if i+2 < len(nsources) else ''
	else:
		nsources = [s[:s.find(']')+1] for s in other]
		nrefs = [s[s.find(']')+2:] for s in other if s.find(']')+2 < len(s)]

	return nid, ntype, nsources, nrefs

########################
### DATABASE UPDATER ###
########################
def add_name_to_kg(nid, name, ntype):
	'''Adds the given name as an attribute for the given entity.
	:param nid: (str) the entity id
	:param name: (str) the extracted entity name
	:param ntype: (str) the entity type
	:return: (boolean) True if the name was successfully added, False otherwise
	'''
	update_name_query = 'MATCH (e:{}) WHERE e.id="{}" SET e.name="{}" RETURN e.name'.format(ntype, nid, name)
	result = list(graph.run(update_name_query))

	return len(result) > 0

###########################
### ACTUAL NAME GETTERS ###
###########################
def get_entity_name(nid, ntype):
	'''Extracts a name for the given entity id.
	Currently handles only genes, compounds, and diseases.
	:param nid: (str) the entity id
	:param ntype: (str) the entity type
	:return: (str) the extracted name or None if a name could not be found
	'''
	if ntype == "Gene":
		name = get_gene_name(nid)
	elif ntype == "Compound":
		name = get_compound_name(nid)
	elif ntype == "Disease":
		name = get_disease_name(nid)
	else:
		name = None

	return name

#########################
### ALL GENE HANDLERS ###
#########################
def get_gene_name(gene_id):
	'''Handles the extraction of gene names for various gene sources. 
	:param gene_id: (str) the entity id
	:return: (str) the extracted name or None if a name could not be found
	'''
	# case: the gene's id is actually it's name
	if gene_id.startswith("N"): #DOES A GENEID STARTING WITH N MEAN THAT THE ID IS ITS REAL NAME?
		return gene_id

	# case: the gene has multiple ids, so let's pull off just the first one
	if ";" in gene_id:
		gene_id = gene_id[:gene_id.find(";")]

	if not gene_id.startswith("drugbank"):  # if nsources != "[Drugbank]":
		name = get_ncbi_gene_name(gene_id)
	else:
		name = get_drugbank_gene_name(gene_id)	

	return name		

'''The next two methods are the two handlers for extracting gene names: 
	- one connects to NCBI 
	- one connects to DrugBank
Each one does a couple steps:
	- access and "GET" the correct webpage which corresponds to the entity
	- find the common tags that indicate the name is going to follow
	- see which tag was actually in the file and extract the name which follows it
'''

def get_ncbi_gene_name(gene_id):
	# get the webpage which corresponds to the given gene id
	ncbi_gene_url = "https://www.ncbi.nlm.nih.gov/gene/{}"
	result = requests.get(ncbi_gene_url.format(gene_id)) #IS THIS LINE WHERE THE SPECIFIC PAGE FOR THE GENE_ID IS PULLED UP? IS THE RETURNED FILE A STRING OF HTML?
	result = result.content.decode("utf-8")

	# find each of the common tags that indicate where the name is
	tag1 = result.find("<dt> Official\n                         Full Name</dt>")  # ("<dt> Official\s* Full Name</dt>")
	tag2 = result.find("<dt> Gene description </dt>")
	tag3 = result.find("<dt> Full Name</dt>")
	tag4 = result.find("<title>") #I WOULD PROBABLY UNDERSTAND THIS BETTER WITH A SAMPLE HTML FILE SO I GET AN IDEA OF WHAT A PATTERN LOOKS LIKE

	name = None
	
	# check which tag is in the webpage and do some ugly string parsing to get the name following the tag
	if tag1 != -1:
		result = result[tag1:]
		name_start = result.find("<dd>") + len("<dd>")
		result = result[name_start:]
		name_end = result.find("<")
		name = result[:name_end].strip()
	elif tag2 != -1:
		result = result[tag2:]
		name_start = result.find("<dd>") + len("<dd>")
		result = result[name_start:]
		name_end = result.find("<")
		name = result[:name_end].strip()
	elif tag3 != -1:
		result = result[tag3:]
		name_start = result.find("<dd>") + len("<dd>")
		result = result[name_start:]
		name_end = result.find("<")
		name = result[:name_end].strip()
	elif tag4 != 1:
		result = result[tag4:]
		name_start = len("<title>")
		name_end = result.find("</title>")
		name = result[name_start:name_end]
		if " - Gene - NCBI" in name:
			name = name[:name.find(" - Gene - NCBI")]

	return name

def get_drugbank_gene_name(gene_id):
	# split the gene id because we only want the number part
	_, gene_id = gene_id.split(':')

	# get the webpage which corresponds to the given gene id
	drugbank_gene_url = "https://go.drugbank.com/bio_entities/{}"
	result = requests.get(drugbank_gene_url.format(gene_id))
	result = result.content.decode("utf-8")

	# find each of the common tags that indicate where the name is
	tag1 = result.find("ID</th><th></th></tr></thead><tbody><tr>")
	tag2 = result.find("Name</dt>")

	name = None

	# check which tag is in the webpage and do some ugly string parsing to get the name following the tag
	if tag1 != -1:
		result = result[tag1:]
		name_start = result.find("<td>") + len("<td>")
		name_end = result.find("</td>")
		name = result[name_start:name_end].strip()
	elif tag2 != -1:
		result = result[tag2+len("Name</dt>"):]
		name_start = result.find(">") + len(">")
		name_end = result.find("</dd>")
		name = result[name_start:name_end].strip()

	return name

#############################
### ALL COMPOUND HANDLERS ###
#############################
def get_compound_name(compound_id):
	'''Handles the extraction of compound names for various compound sources. 
	:param compound: (str) the entity id
	:return: (str) the extracted name or None if a name could not be found
	'''
	# case: the compound has multiple ids, so let's try each one
	if "|" in compound_id:
		compound_id = compound_id.split("|")
		for i in compound_id:
			name = get_compound_name(i)
			if name is not None:
				return name
	elif compound_id.upper().startswith("CHEBI"):
		name = get_chebi_compound_name(compound_id)
	elif compound_id.startswith("CHEMBL"):
		name = get_chembl_compound_name(compound_id)
	elif compound_id.startswith("DB"):
		name = get_drugbank_compound_name(compound_id)
	elif compound_id.startswith("MESH"):
		name = get_mesh_compound_name(compound_id)
	elif compound_id.startswith("bindingdb"):
		name = get_bindingdb_compound_name(compound_id)
	elif compound_id.startswith("brenda"):
		name = get_brenda_compound_name(compound_id)
	elif compound_id.startswith("drugcentral"):
		name = get_drugcentral_compound_name(compound_id)
	elif compound_id.startswith("fdasrs"):
		name = get_fdasrs_compound_name(compound_id)
	elif compound_id.startswith("gtopdb"):
		name = get_gtopdb_compound_name(compound_id)
	elif compound_id.startswith("hmdb"):
		name = get_hmdb_compound_name(compound_id)
	elif compound_id.startswith("molport"):
		name = get_molport_compound_name(compound_id)
	elif compound_id.startswith("pharmgkb"):
		name = get_pharmgkb_compound_name(compound_id)
	elif compound_id.startswith("pubchem"):
		name = get_pubchem_compound_name(compound_id)
	elif compound_id.startswith("rhea"):
		name = get_rhea_compound_name(compound_id)
	elif compound_id.startswith("zinc"):
		name = get_zinc_compound_name(compound_id)
	# case: we couldn't find the compound in any of the sources, so let's try ROBOKOP: another KG
	else:
		return find_compound_in_robokop(compound_id)

	if name == "":
		name = find_compound_in_robokop(compound_id)
		if name is None:
			name = ""

	return name

'''The next 15 methods are the 15 handlers for extracting compound names: one for each source aka url. 
Most of them do the same steps as the gene handlers, and they are, for the most part, very similar methods just with different urls and different tags.
There are a couple which are unique in that they use an external file or package instead of getting a url.
'''

def get_chebi_compound_name(compound_id):
	# split the compound id because we only want the number part
	_, compound_id = compound_id.split(":")

	# get the webpage which corresponds to the given compound id
	chebi_url = "https://www.ebi.ac.uk/chebi/searchId.do?chebiId={}"  # "https://pubchem.ncbi.nlm.nih.gov/#query={}&tab=compound"
	result = requests.get(chebi_url.format(compound_id))
	result = result.content.decode("utf-8")

	# find each of the common tags that indicate where the name is
	tag1 = result.find("ChEBI ASCII Name")
	tag2 = result.find("ChEBI Name")

	name = None

	# check which tag is in the webpage and do some ugly string parsing to get the name following the tag
	if tag1 != -1:
		result = result[tag1:]
		name_start = result.find("<td>") + len("<td>")
		result = result[name_start:]
		name_end = result.find("</td>")
		name = clean_out_brackets(result[:name_end]).strip()
	elif tag2 != -1:
		result = result[tag2:]
		name_start = result.find("<td>") + len("<td>")
		result = result[name_start:]
		name_end = result.find("</td>")
		name = result[:name_end]
		name = clean_out_brackets(name).strip()

	return name

def get_chembl_compound_name(compound_id):
	# extract the name via the chembl_webresource_client.new_client python package
	molecule = new_client.molecule
	m = molecule.get(compound_id)
	name = m['pref_name'] if m['pref_name'] is not None else ""

	return name

def get_drugbank_compound_name(compound_id):
	# get the webpage which corresponds to the given compound id
	drugbank_url = "https://go.drugbank.com/drugs/{}"
	result = requests.get(drugbank_url.format(compound_id))
	result = result.content.decode("utf-8")

	# find each of the common tags that indicate where the name is
	tag1 = result.find("Generic Name</dt>")
	tag2 = result.find("Name</dt>")

	name = None

	# check which tag is in the webpage and do some ugly string parsing to get the name following the tag
	if tag1 != -1:
		result = result[tag1+len("Generic Name</dt>"):]
		name_start = result.find(">") + len(">")
		name_end = result.find("</dd>")
		name = result[name_start:name_end].strip()
	elif tag2 != -1:
		result = result[tag2+len("Name</dt>"):]
		name_start = result.find(">") + len(">")
		name_end = result.find("</dd>")
		name = result[name_start:name_end].strip()

	return name

def get_mesh_compound_name(compound_id):
	# split the compound id because we only want the number part
	_, compound_id = compound_id.split(":")

	# get the webpage which corresponds to the given compound id
	mesh_url = "https://id.nlm.nih.gov/mesh/lookup/label?resource={}"
	result = requests.get(mesh_url.format(compound_id))
	result = result.content.decode("utf-8")

	name = str(result)[2:-2].strip()

	return name

def get_bindingdb_compound_name(compound_id):
	# split the compound id because we only want the number part
	_, compound_id = compound_id.split(":")

	# get the webpage which corresponds to the given compound id
	result = requests.get("https://www.bindingdb.org/bind/BindingDB_CHEMBL_ID.txt")
	result = result.content.decode("utf-8")

	# find each of the common tags that indicate where the name is
	tag1 = result.find(compound_id + '\t')

	name = None

	# check which tag is in the webpage and do some ugly string parsing to get the name following the tag
	if tag1 != -1:
		result = result[tag1:]
		name_start = result.find('\t') + len('\t')
		name_end = result.find('\n')
		name = result[name_start:name_end].strip()
		name = get_chembl_compound_name(name)

	return name

def get_brenda_compound_name(compound_id):
	# split the compound id because we only want the number part
	_, compound_id = compound_id.split(":")

	# get the webpage which corresponds to the given compound id
	brenda_url = "https://www.brenda-enzymes.org/ligand.php?brenda_ligand_id={}"
	result = requests.get(brenda_url.format(compound_id), headers={'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"})
	result = result.content.decode("utf-8")

	# find each of the common tags that indicate where the name is
	tag1 = result.find("<h1>Ligand ")

	name = None

	# check which tag is in the webpage and do some ugly string parsing to get the name following the tag
	if tag1 != -1:
		result = result[tag1:]
		name_start = len("<h1>Ligand ")
		name_end = result.find("</h1>")
		name = result[name_start:name_end].strip()

	return name

def get_drugcentral_compound_name(compound_id):
	# split the compound id because we only want the number part
	_, compound_id = compound_id.split(":")

	# get the webpage which corresponds to the given compound id
	drugcentral_url = "https://drugcentral.org/drugcard/{}?q=lipitor"
	result = requests.get(drugcentral_url.format(compound_id), headers={'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"})
	result = result.content.decode("utf-8")

	# find each of the common tags that indicate where the name is
	tag1 = result.find('<h1 class="starfont">')

	name = None

	# check which tag is in the webpage and do some ugly string parsing to get the name following the tag
	if tag1 != -1:
		result = result[tag1:]
		name_start = len('<h1 class="starfont">')
		name_end = result.find(' <a style="font-size: 15px; color: #f0db4f" href="#druguse">')
		name = result[name_start:name_end].strip()

	return name

def get_fdasrs_compound_name(compound_id):
	# split the compound id because we only want the number part
	_, compound_id = compound_id.split(":")

	# get the webpage which corresponds to the given compound id
	fdasrs_url = "https://fdasis.nlm.nih.gov/srs/auto/startswith/{}"
	result = requests.get(fdasrs_url.format(compound_id))
	result = result.content.decode("utf-8")

	# find each of the common tags that indicate where the name is
	tag1 = result.find("Preferred Substance Name:</td>")

	name = None

	# check which tag is in the webpage and do some ugly string parsing to get the name following the tag
	if tag1 != -1:
		result = result[tag1:]
		name_start = result.find("<td>") + len("<td>")
		result = result[name_start:]
		name_end = result.find("</td>")
		name = result[:name_end].strip()

	return name

def get_gtopdb_compound_name(compound_id):
	# split the compound id because we only want the number part
	_, compound_id = compound_id.split(":")

	# get the webpage which corresponds to the given compound id
	gtopdb_url = "https://www.guidetopharmacology.org/GRAC/LigandDisplayForward?ligandId={}"
	result = requests.get(gtopdb_url.format(compound_id))
	result = result.content.decode("utf-8")

	# find each of the common tags that indicate where the name is
	tag1 = result.find("<title>")

	name = None

	# check which tag is in the webpage and do some ugly string parsing to get the name following the tag
	if tag1 != -1:
		result = result[tag1:]
		name_start = len("<title>")
		name_end = result.find(" | ")
		name = result[name_start:name_end].strip()

	return name

def get_hmdb_compound_name(compound_id):
	# split the compound id because we only want the number part
	_, compound_id = compound_id.split(":")

	# get the webpage which corresponds to the given compound id
	hmdb_url = "https://hmdb.ca/metabolites/{}"
	result = requests.get(hmdb_url.format(compound_id))
	result = result.content.decode("utf-8")

	# find each of the common tags that indicate where the name is
	tag1 = result.find("<th>Common Name</th>")

	name = None

	# check which tag is in the webpage and do some ugly string parsing to get the name following the tag
	if tag1 != -1:
		result = result[tag1:]
		name_start = result.find("<td><strong>") + len("<td><strong>")
		name_end = result.find("</strong></td>")
		name = result[name_start:name_end].strip()

	return name

def get_molport_compound_name(compound_id):
	# parse the id into the correct format for the url
	_, compound_id = compound_id.split(":")
	compound_id = compound_id[len("Molport-"):]
	compound_id = compound_id.replace('-', '')

	# get the webpage which corresponds to the given compound id
	molport_url = "https://www.molport.com/shop/moleculelink//{}?searchtype=text-search"
	result = requests.get(molport_url.format(compound_id))
	result = result.content.decode("utf-8")

	# find each of the common tags that indicate where the name is
	tag1 = result.find("IUPAC:")

	name = None

	# check which tag is in the webpage and do some ugly string parsing to get the name following the tag
	if tag1 != -1:
		result = result[tag1:]
		name_start = result.find('<div class="wrappable">') + len('<div class="wrappable">')
		name_end = result.find("</div>")
		name = result[name_start:name_end].strip()

	return name

def get_pharmgkb_compound_name(compound_id):
	# split the compound id because we only want the number part
	_, compound_id = compound_id.split(":")

	name = None

	# search the pharmgkb file for the compound id and extract its name
	with open(pharmgkb_entity_file, 'r') as f:
		for line in f:
			line_parts = line.split('\t')
			nid, name = line_parts[0], line_parts[1]

			if compound_id == nid:
				name_start = name.find("Label for ") + len("Label for ")
				name = name[name_start:]

	return name

def get_pubchem_compound_name(compound_id):
	# split the compound id because we only want the number part
	_, compound_id = compound_id.split(":")

	# get the webpage which corresponds to the given compound id
	pubchem_url = "https://pubchem.ncbi.nlm.nih.gov/compound/{}"
	result = requests.get(pubchem_url.format(compound_id))
	result = result.content.decode("utf-8")

	# find each of the common tags that indicate where the name is
	tag1 = result.find('<title>')

	name = None

	# check which tag is in the webpage and do some ugly string parsing to get the name following the tag
	if tag1 != -1:
		result = result[tag1:]
		name_start = len('<title>')
		name_end = result.find(" | ")
		name = result[name_start:name_end].strip()

	return name

# not sure how to interpret these ones yet, so skip them
def get_rhea_compound_name(compound_id):
	# skip
	return 
	_, compound_id = compound_id.split(":")

	rhea_url = None
	result = requests.get(rhea_url.format(compound_id))
	result = result.content.decode("utf-8")

	tag1 = result.find('<title>')

	name = None
	if tag1 != -1:
		result = result[tag1:]
		name_start = len('<title>')
		name_end = result.find(" | ")
		name = result[name_start:name_end].strip()

	return name

def get_zinc_compound_name(compound_id):
	# split the compound id because we only want the number part
	_, compound_id = compound_id.split(":")

	# get the webpage which corresponds to the given compound id
	zinc_url = "https://zinc.docking.org/substances/{}/"
	result = requests.get(zinc_url.format(compound_id))
	result = result.content.decode("utf-8")

	# find each of the common tags that indicate where the name is
	tag1 = result.find('<title>')

	name = None

	# check which tag is in the webpage and do some ugly string parsing to get the name following the tag
	if tag1 != -1:
		result = result[tag1:]
		name_start = result.find('(')
		name_end = result.find("</title")
		name = result[name_start:name_end].strip()[1:-1]

	return name

def find_compound_in_robokop(compound_id):
	'''Searches for the given compound id in another KG called ROBOKOP to see if it has the name there.
	:param compound_id: (str) the compound's id
	:return: (str) the name of the compound, if one was found; otherwise None
	'''
	robokop = Graph(host='localhost', port=7687, user='neo4j', password='password')

	chem_equiv_ids = list(robokop.run("MATCH (e:chemical_substance) RETURN DISTINCT e.id, e.name, e.equivalent_identifiers"))

	for ids in chem_equiv_ids:
		e_id, e_name, other_ids = ids
		for i in other_ids:
			if compound_id in i:
				return e_name

	return None	

############################
### ALL DISEASE HANDLERS ###
############################
def get_disease_name(disease_id):
	if disease_id.startswith("DOID"):
		name = get_doid_disease_name(disease_id)
	elif disease_id.startswith("MESH"):
		name = get_mesh_disease_name(disease_id)
	elif disease_id.startswith("OMIM"):
		name = get_omim_disease_name(disease_id)
	elif disease_id.startswith("SARS-CoV2"):
		name = disease_id
	# case: we could not find the disease name in any of the sources above, so let's check for it in ROBOKOP
	else:
		name = find_disease_in_robokop(disease_id)

	return name

'''The next 4 methods are the 4 handlers for extracting disease names: one for each source.
They perform the same basic steps as the gene and compound handlers for their unique url and tags. 
'''

def get_doid_disease_name(disease_id):
	# split the disease id because we only want the number part
	_, disease_id = disease_id.split(":")

	# get the webpage which corresponds to the given disease id
	doid_url = "https://www.ebi.ac.uk/ols/ontologies/doid/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FDOID_{}"
	result = requests.get(doid_url.format(disease_id))
	result = result.content.decode("utf-8")

	# find each of the common tags that indicate where the name is
	tag1 = result.find('<title id="pageTitle">')

	name = None

	# check which tag is in the webpage and do some ugly string parsing to get the name following the tag
	if tag1 != -1:
		result = result[tag1:]
		name_start = len('<title id="pageTitle">')
		name_end = result.find("</title")
		name = result[name_start:name_end].strip()
	else:
		print(disease_id)

	return name

def get_mesh_disease_name(disease_id):
	# split the disease id because we only want the number part
	_, disease_id = disease_id.split(":")

	# get the webpage which corresponds to the given disease id
	mesh_url = "https://id.nlm.nih.gov/mesh/lookup/label?resource={}"
	result = requests.get(mesh_url.format(disease_id))
	result = result.content.decode("utf-8")

	# parse the response to extract the name
	name = str(result)[1:-1].split(",")[0][1:-1].strip()

	return name

def get_ncbi_disease_name(disease_id):
	# get the webpage which corresponds to the given disease id
	ncbi_url = "https://www.ncbi.nlm.nih.gov/medgen/?term={}"
	result = requests.get(ncbi_url.format(disease_id))
	result = result.content.decode("utf-8")

	# find each of the common tags that indicate where the name is
	tag1 = result.find('<div class="MedGenTitleText">')

	name = None

	# check which tag is in the webpage and do some ugly string parsing to get the name following the tag
	if tag1 != -1:
		result = result[tag1:]
		name_start = len('<div class="MedGenTitleText">')
		name_end = result.find("</div>")
		name = result[name_start:name_end]
		name = clean_out_brackets(name).strip()
	else:
		print(disease_id)

	return name

def get_omim_disease_name(disease_id):
	# split the disease id because we only want the number part
	_, disease_id = disease_id.split(":")

	# get the webpage which corresponds to the given disease id
	omim_url = "https://api.omim.org/api/entry?mimNumber={}&format=xml"
	result = requests.get(omim_url.format(disease_id), headers={'ApiKey': 'yMqWv8EfQiW-oDl1tWvl8g'})
	result = result.content.decode("utf-8")

	# find each of the common tags that indicate where the name is
	tag1 = result.find('<preferredTitle>')

	name = None

	# check which tag is in the webpage and do some ugly string parsing to get the name following the tag
	if tag1 != -1:
		result = result[tag1:]
		name_start = len('<preferredTitle>')
		# name_end = result.find(";") 
		name_end = result.find("</preferredTitle>")
		name = result[name_start:name_end].strip()
	else:
		print(disease_id)

	if name.startswith("MOVED TO "):
		new_id = name[name.find("MOVED TO ") + len("MOVED TO "):]
		name = get_omim_disease_name("OMIM:{}".format(new_id))

	return name

def find_disease_in_robokop(disease_id):
	'''Searches for the given disease id in another KG called ROBOKOP to see if it has the name there.
	:param compound_id: (str) the disease's id
	:return: (str) the name of the disease, if one was found; otherwise None
	'''
	robokop = Graph(host='localhost', port=7687, user='neo4j', password='password')
	disease_equiv_ids = list(robokop.run("MATCH (e:disease) RETURN DISTINCT e.id, e.name, e.equivalent_identifiers"))

	for ids in disease_equiv_ids:
		e_id, e_name, other_ids = ids
		if disease_id in other_ids:
			return e_name

	return None

def clean_out_brackets(string):
	'''Cleans out all the leftover html tags <{}>.
	:param string: (str) the string to clean
	:return: (str) the cleaned str
	'''
	i = string.find("<")
	result = string[:i]
	while i != -1:
		j = string.find(">")
		string = string[j+1:]
		i = string.find("<")
		result += string[:i]

	return result


if __name__ == '__main__':
	get_all_entity_names(update_kg=True)
