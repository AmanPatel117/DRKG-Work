import requests
def add_to_named(nid,name):
	with open("tax_named.txt", "a") as f:
		f.write(nid + "\t" + name + "\n")
def add_to_skipped(nid):
	with open("tax_named.txt", "a") as f:
		f.write(nid + "\n")
def get_tax_name(tax_id):
	ncbi_tax_url = "https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id={}"
	page = requests.get(ncbi_tax_url.format(tax_id))
	page = page.content.decode("utf-8")
	page = page.lower()
	start_index = page.find("<title>")
	end_index = page.find("</title>")
	name = page[start_index:end_index+1]
	start_index = name.find("(")
	name = name[start_index:end_index]
	name = name[1:len(name)-2]
	return name

with open("entity2src.tsv") as f:
	for line in f:
		ntype, nid = line.split("\t")[0].split("::")
		if ntype=="Tax":			
			try:
				id_name = get_tax_name(nid)
				if id_name == "":
					add_to_skipped(nid)
				else:
					add_to_named(nid,get_tax_name(nid))
			except:
				add_to_skipped(nid)
		