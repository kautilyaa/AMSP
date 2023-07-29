import cv2
import pytesseract
import re
import pandas as pd
import statistics
import sys

import Python.searchOps as SOPS
import Python.loadDB as db

path = "Samples/"

''' compounds = ["penicillin", "penicillin g", "ticarcilin", "meziocillin", "cefalotin", "cefazolin", "cefotaxime", "azireonam", "imipenem", "cefepime", "ampicillin", "cefotetan", "levofloxacin", "ampicillin", "vancomycin"] '''

compounds = db.loadCompounds()

bacterias = ['e. coli', 'e coli', 'p. mirabilis', 'msra', 'escherichia coli']

def getData(image):
	# Removing Non-text Areas
	raw_image = cv2.cvtColor(cv2.imread(path + image), cv2.COLOR_BGR2RGB)
	data = pytesseract.image_to_data(raw_image, output_type='data.frame')
	return data

def getStrings(image):
	if (type(image) == str):
		image = path + image
		image = cv2.imread(path + image)
	raw_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	return pytesseract.image_to_string(raw_image)

def getResistanceData(image):
	if (type(image) == str):
		image = cv2.cvtColor(cv2.imread(path + image), cv2.COLOR_BGR2RGB)
	
	data = pytesseract.image_to_data(image, output_type='data.frame')
	data['text'] = data['text'].fillna("")
	data['text'] = data['text'].apply(lambda x: x.lower())
	# salt_data = data.loc[data['text'].isin(compounds)]

	salt_data = data
	
	bacts = detectBacts(getStrings(image).lower())

	resist_data = {}

	for index, row in salt_data.iterrows():
		#cv2.imshow(row['text'],raw_image[int(row['top']-row['height']):int(row['top']+row['height']*2), :])
		#tmp = raw_image[int(row['top']-row['height']):int(row['top']+row['height']*2), :].resize()
		curr_comp =  SOPS.getMatch(row['text'], compounds)

		if (not curr_comp):
			continue

		bounds = (int(row['top'] - row['height']* 0.5), int(row['top'] + row['height'] * 0.75))
		cap_str = ''
		curr_data = data.loc[(data['top'] > bounds[0]) & (data['top'] < bounds[1])]
		for __, word in curr_data.iterrows():
			cap_str += word['text'] + ' '
		#cap_str = pytesseract.image_to_string(raw_image[int(row['top']-row['height']):int(row['top']+row['height']*2), :])

		print(cap_str)
		c, r = getResistance(cap_str, curr_comp)
		try:
			resist_data[c].extend(r)
		except:
			resist_data[c] = r

	return {'bacts': bacts, 'resist_data': resist_data}

def getResistance(cap_str, compound):
	regex = "(?:\s|\W)(r|s|i|5|a|1|\$)(?:\s|\W)"
	resistance_val = []
	replace = {'r':3, 'i':2, 's':1, 'resistant':3, 'intermediate':2, 'sensitive':1, 'lactamase':3, '5':1, 'a':3, '1':2, '$':1}
	for x in re.finditer(regex, cap_str):
		#resistance_val.append(x.group(1))
	# if (resistance_val):
		return (compound, replace[x.group(1)])

	regex = "(?:\s)(resistant|sensitive|intermediate|lactamse)(?:\s)"
	
	for x in re.finditer(regex, cap_str):
		#resistance_val.append(x.group(1))
	#if (resistance_val):
		return (compound, replace[x.group(1)] )

	return (compound, None)

def detectBacts(cap_str):
	print(cap_str)
	bacts = []
	for bact in bacterias:
		if (bact in cap_str):
			bacts.append(bact)

	return bacts

def getResistanceFromInhZone(cap_str):
	# When Numerical Data
	regex = "(?:<|>)?(\d+)(?:-|_|:|;)?(\d+)?"
	resistance_val = []
	
	for x in re.finditer(regex, cap_str):
		p1 = int(x.group(1))
		if (x.group(2)):
			p2 = int(x.group(2))
			if (p1 + p2 >= 20):
				resistance_val.append((p1 + p2) / 2)
			elif (p1 >= 10):
				resistance_val.append(p1)
			elif (p2 >= 10):
				resistance_val.append(p2)
		else:
			if (p1 >= 10):
				resistance_val.append(p1)

		print(x.group(0))
		cap_str = cap_str.replace(x.group(0), "", 1)

	compound = cap_str.strip()

	if (resistance_val):
		resistance = sum(resistance_val) / len(resistance_val)
		if (statistics.stdev(resistance_val) > 17):
			resistance_val.sort()
			resistance = resistance_val[-1]
		resistance = 3 - int(resistance * (3/51))
	else:
		# TO:DO IMPLEMENT FOR TRUE/FALSE VALUES
		resistance = 0

	return (compound, resistance)
	
if __name__ == "__main__":
	try:
		image = sys.argv[1]
	except:
		image = 'R4.png'

	#print(getStrings('R1.jpeg'))
	data = getData(image)
	print(getResistanceData(image))
	#print(getProduct('R1.jpeg'))
