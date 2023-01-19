from py2neo import Graph
graph = Graph(host='34.86.195.172', port=7687, user='neo4j', password='drkg')
#graph.run('MATCH p=()-[r:`A_`]->() WHERE r.connected_entity_types="Compound:Gene" SET r.old_name="A_" RETURN r')
with open("C:\\Users\\Aman\\Documents\\DRKG_Work\\Text Files\\Edge_Naming\\full_edge_names.txt") as f:
	for line in f:
		new_name = line.split("\t")[2]
		old_name = line.split("\t")[1]
		if line.split("\t")[0] == "GNBR":
			interacting_types = line.split("\t")[3]
			interacting_types = interacting_types[:interacting_types.find("\n")]
			query1 = 'CALL apoc.refactor.rename.type("{}","{}")'.format(old_name,new_name)
			graph.run(query1)
			#graph.run(query)
		elif line.split("\t")[0] == "Hetionet":
			query2 = 'CALL apoc.refactor.rename.type("{}","{}")'.format(old_name,new_name)
			graph.run(query2)
		#query = 'CALL apoc.refactor.rename.type("{}","{}")'.format(old_name,new_name)
		#query2 = 'MATCH p=()-[r:"{}"]->() SET r.old_name="{}" RETURN r'.format(newest_name,old_name)
		#graph.run(query1)
		#graph.run(query2)