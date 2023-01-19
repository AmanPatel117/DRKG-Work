import requests

def find_DOID_mappings(nid):
	page = requests.get('https://www.ebi.ac.uk/ols/ontologies/doid/terms?obo_id={}'.format(nid)).text
	page = page[page.find('database cross reference'):]
	page = page[page.find('<ul>'):page.find('</ul')]
	temp_page = page[page.find('<li')+1:]
	temp_page = temp_page + '<li'
	mappings = []
	while temp_page.find('<li') != -1:
		page = temp_page[temp_page.find('<span>')+1:]
		mapping = page[page.find('>')+1:page.find('</span')]
		mappings.append(mapping)
		temp_page = page[temp_page.find('<li')+1:]
	for i in range(0,len(mappings)):
		mappings[i] = mappings[i].strip()
		if mappings[i].find('<span>')!=-1:
			mappings[i] = mappings[i][6:]
	return mappings
def get_DOID_id(nid):
	page = requests.get('https://www.ebi.ac.uk/ols/search?q=MESH%3A{}&ontology=doid'.format(nid))
	print(page.json())

get_DOID_id('D012220')




#with open("C:\\Users\\Aman\\Documents\\DRKG_Work\\Text Files\\Attributes\\Node Attributes\\diseases.txt") as f, open('C:\\Users\\Aman\\Documents\\DRKG_Work\\Text Files\\Attributes\\Node Attributes\\mappings_found.txt','a') as maps, open('C:\\Users\\Aman\\Documents\\DRKG_Work\\Text Files\\Attributes\\Node Attributes\\mappings_skipped.txt','a') as skips:
	#for line in f:
		#nid = line.split("\t")[0].split('::')[1]
		#if find_DOID_mappings(nid) != []:
		#	maps