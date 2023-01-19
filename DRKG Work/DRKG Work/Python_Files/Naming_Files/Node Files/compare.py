from py2neo import Graph
graph = Graph(host='34.86.195.172', port=7687, user='neo4j', password='drkg') 
diseases = list(graph.run('MATCH (e:Disease) RETURN e.name'))
het_diseases = []
graph_diseases = []
count = 0
with open("hetionet-v1.0-nodes.tsv.txt") as f, open("diseases_hetionet.txt", 'a') as b:
	for line in f:
		ntype = line.split("\t")[0].split("::")[0]
		name = line.split("\t")[1]
		if ntype == "Disease":
			#b.write(name + "\n")
			het_diseases.append(name.lower().strip())
with open("diseases_graph.txt") as f:
	for line in f:
		graph_diseases.append(line.lower().strip())
for disease in het_diseases:
	if disease in graph_diseases:
		count +=1
	else:
		print(disease)
print(count)
