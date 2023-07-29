import pandas as pd
import numpy as np
import json
import re

path = "../DB/"
filename = "Medicinal Data CURR.csv"

data = pd.read_csv(path + filename)

data = data.drop(["Timestamp"], axis=1)
data = data.fillna("")

def extractCompounds(filepath="Compounds/compounds_list.json"):
	compSet = set()

	compounds = np.array(data['Compounds (salts)'])
	
	for block in compounds:
		for sent in block.split("\n"):
			comp = sent.split('-')[0].strip()
			if (comp):
				compSet.add(comp.lower())

	# print(compSet)
	with open(path + filepath, 'w+') as f:
		json.dump(list(compSet), f)

def productsToJSON(filepath="Drugs/full_details.json"):
	products = []
	index = 0
	for index, row in data.iterrows():
		tmp = {"index": index, "prod_name": row['Medicine Name'].lower(), "diseases": row['Disease'].lower().split("\n")}
		index += 1

		tmp["search_word"] = re.sub("\(.*\)", "", tmp['prod_name'])

		tmp['compounds'] = []
		for comp in row["Compounds (salts)"].split("\n"):
			c_u = comp.lower().split("-")
			c = c_u[0].strip()
			try:
				u = c_u[1].strip()
			except:
				u = None

			tmp['compounds'].append((c, u))
	
		tmp['side_effects'] = [x for x in row["Side Effects"].lower().split("\n") if x]
		tmp['safety_advice'] = [x for x in row["Safety Advice"].lower().split("\n") if x]

		if (not tmp['side_effects']):
			tmp['side_effects'].append("No common side effects seen")

		if (not tmp['safety_advice']):
			tmp['safety_advice'].append("Safe to use")

		tmp["type"] = row['Type'].lower()

		products.append(tmp)

	with open(path + filepath, 'w+') as f:
		json.dump(products, f)


if __name__ == '__main__':
	# extractCompounds()
	productsToJSON()
