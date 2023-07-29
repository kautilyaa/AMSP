import pandas as pd
import json

path = 'DB/'

def loadJSON(filepath):
	with open(path + filepath, 'r') as f:
		return json.load(f)

def loadCompounds(filepath = "Compounds/standard_compounds.json"):
	return loadJSON(filepath)

def loadMedicines(filepath = "Drugs/full_details.json"):
	return loadJSON(filepath)
