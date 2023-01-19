from py2neo import Graph
graph = Graph(host='34.86.195.172', port=7687, user='neo4j', password='drkg') 
named_files = {"Anatomy":"anatomy_named.txt","BiologicalProcess":"bio_process_named.txt","CellularComponent":"cell_comp_named.txt","MolecularFunction":"mol_function_named.txt","Pathway":"pathway_named.txt","PharmacologicClass":"pharm_class_named.txt","SideEffect":"side_effect_named.txt", "Tax":"tax_named.txt", "Atc":"atc_named.txt"}
for key in named_files.keys():
	ntype = key
	with open(named_files[key]) as f:
		for line in f:
			nid, name = line.split("\t")
			query = 'MATCH (e:{}) WHERE e.id="{}" SET e.name="{}" RETURN e.name'.format(ntype, nid, name)
			result = list(graph.run(query))