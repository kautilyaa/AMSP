import nltk
from nltk.metrics import edit_distance
# import loadDB as db

def getDistance(x, y):
	return edit_distance(x, y)

def getMatch(word, wordList, thresh=5):
	min_dist = 50
	min_word = ''
	for w in wordList:
		d = getDistance(word, w)
		if (d < min_dist):
			min_dist = d
			min_word = w

	if (min_dist < thresh):
		return min_word
	return False

def searchMedicine(query, list_meds):
	print(query)
	results, count = [], 0
	if (not query):
		# print("Empty Query")
		return []
	for med in list_meds:
		if (count > 10):
			return results
		if query in med['prod_name']:
			results.append(med)
			count += 1
	for med in list_meds:
		if (count > 10):
			return results
		for comp, __ in med['compounds']:
			if query in comp:
				if (not med in results):
					results.append(med)
					count += 1
					break

	if (results):
		return results
	elif (len(query.split()) > 1):
		for q in query.split():
			if (len(results) > 10):
				return results
			results.append(searchMedicine(q, list_meds))
		return results
	else:
		return results
	


if __name__ == '__main__':
	x = "ciprofloxacin"
	y = "iprortoxacin"

	print(getDistance(x, y))

