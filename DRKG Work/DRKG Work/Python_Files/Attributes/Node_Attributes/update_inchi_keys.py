from py2neo import Graph

graph = Graph(host='localhost', port=7687, user='neo4j', password='Tennisgod#117') 

with open('C:\\Users\\Aman\\Documents\\DRKG_Work\\Text Files\\Attributes\\Node Attributes\\inchi_keys_found.txt') as f:
	for line in f:
		try:
			nid, inchi_key, smiles = line.split("\t")
			smiles = smiles[:smiles.find('\n')]
			graph.run('MATCH (n:Compound) WHERE n.id = "{}" SET n.inchi_key = "{}", n.canonical_smiles = "{}" RETURN n'.format(nid,inchi_key,smiles))
		except:
			pass