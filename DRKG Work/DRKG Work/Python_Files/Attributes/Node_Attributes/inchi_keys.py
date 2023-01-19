import requests
def add_to_named(nid,key,smiles):
	with open("C:\\Users\\Aman\\Documents\\DRKG_Work\\Text Files\\Attributes\\Node Attributes\\inchi_keys_found.txt", "a") as f:
		f.write(nid + "\t" + key + "\t" + smiles + "\n")
def add_to_skipped(nid):
	with open("C:\\Users\\Aman\\Documents\\DRKG_Work\\Text Files\\Attributes\\Node Attributes\\inchi_keys_skipped.txt", "a") as f:
		f.write(nid + "\n")
def get_chebi_key_and_smiles(nid):
	url = 'https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:{}'.format(nid)
	page = requests.get(url).text
	page1 = page
	key = ""
	page = page[page.find('InChIKey'):]
	page = page[page.find("<td>"):]
	key = page[page.find(">")+1:page.find("</td>")]
	smiles = ""
	page1 = page1[page1.find('SMILES'):]
	page1 = page1[page1.find("<td>"):]
	smiles = page1[page1.find(">")+1:page1.find("</td>")]
	if smiles.find("<") != -1:
		smiles = ""
	return key,smiles
def get_chembl_key_and_smiles(nid):
	url = 'https://www.ebi.ac.uk/chembl/compound_report_card/{}/'.format(nid)
	key = ""
	page = requests.get(url).text
	page1 = page
	page = page[page.find("@context"):]
	page = page[page.find("inChIKey"):]
	key = page[page.find(": \"")+3:page.find("\",")]

	smiles = ""
	page1 = page1[page1.find('@context'):]
	page1 = page1[page1.find('smiles'):]
	page1 = page1[page1.find("\"")+1:]
	page1 = page1[page1.find("\"")+1:]
	smiles = page1[:page1.find("\"")]
	return key, smiles
def get_molport_key_and_smiles(nid):
	nid = nid[nid.find('-'):]
	nid = nid.replace('-','')
	nid = nid[2:]
	url = 'https://www.molport.com/shop/moleculelink/2-difluoromethoxy-1-1-1-2-tetrafluoroethane/{}'.format(nid)
	print(url)
	page = requests.get(url).text
	page = page[page.find("InChI key:"):]
	page = page[page.find("div class"):]
	key = page[page.find(">")+1:page.find("<")]
	page = requests.get(url).text
	page = page[page.find("SMILES:"):]

def get_bindingdb_key_and_smiles(nid):
	url = 'http://www.bindingdb.org/bind/chemsearch/marvin/MolStructure.jsp?monomerid={}'.format(nid.split(':')[1])
	key = ""
	smiles = ""
	page = requests.get(url).text
	page1 = page
	page1 = page1[page1.find('InChI Key'):]
	page1 = page1[page1.find('=')+1:]
	page1 = page1[page1.find('=')+1:]
	key = page1[:page1.find('<')]
	
	page = requests.get(url).text
	page = page[page.find('SMILES:'):]
	page = page[page.find('>')+1:]
	page = page[page.find('>')+1:]
	smiles = page[:page.find('<')]
	return key, smiles
def get_brenda_key_and_smiles(nid):
	url = 'https://www.brenda-enzymes.org/ligand.php?brenda_ligand_id={}'.format(nid.split(':')[1])
	page = requests.get(url).text
	print(page)

def get_drugbank_key_and_smiles(nid):
	url = 'https://go.drugbank.com/drugs/{}'.format(nid)
	page = requests.get(url).text
	page1 = page
	page = page[page.find("InChI Key</dt>")+14:]
	page = page[page.find(">"):]
	key = page[1:page.find("<")]
	page1 = page1[page1.find("SMILES</dt>")+11:]
	page1 = page1[page1.find(">")+1:]
	page1 = page1[page1.find(">")+1:]
	smiles = page1[:page1.find("<")]
	return key, smiles
def get_mesh_key_and_smiles(nid):
	url = 'https://www.ncbi.nlm.nih.gov/pccompound?LinkName=mesh_pccompound&from_uid='.format("67"+nid.split(':')[1])
	page = requests.get(url).text
	print(page.find('46184986'))
	print(page[page.find('46184986'):])
def get_key_and_smiles(nid):
	chebi_key_and_smiles = get_chebi_key_and_smiles(nid)
	if chebi_key_and_smiles[0] != "" and chebi_key_and_smiles[1] != "":
		return chebi_key_and_smiles
	chembl_key_and_smiles = get_chembl_key_and_smiles(nid)
	if chembl_key_and_smiles[0] != "" and chembl_key_and_smiles[1] != "":
		return chembl_key_and_smiles
	drugbank_key_and_smiles = get_drugbank_key_and_smiles(nid)
	if drugbank_key_and_smiles[0] != "" and drugbank_key_and_smiles[1] != "":
		return drugbank_key_and_smiles
	bindingdb_key_and_smiles = get_bindingdb_key_and_smiles(nid)
	if bindingdb_key_and_smiles[0] != "" and bindingdb_key_and_smiles[1] != "":
		return bindingdb_key_and_smiles
	else:
		return ("","")
#	if "CHEBI" in nid:
#		return get_chebi_key_and_smiles(nid)
#	elif "CHEMBL" in nid:
#		return get_chembl_key_and_smiles(nid)
#	elif "DB" in nid:
#		get_drugbank_key_and_smiles(nid)
#	else:
#		return ("","")	

with open("C:\\Users\\Aman\\Documents\\DRKG_Work\\Text Files\\Naming\\Node_Naming\\entity2src.tsv") as f:
	for line in f:
		if line.split('::')[0] == "Compound":
			nid = line.split("\t")[0].split('::')[1]
			try:
				key_smiles = get_key_and_smiles(nid)
				if key_smiles[0] == "" or key_smiles[1] == "":
					add_to_skipped(nid)
				else:
					add_to_named(nid, key_smiles[0],key_smiles[1])
			except:
				add_to_skipped(nid)