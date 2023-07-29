import cv2
import pytesseract
import re
import Python.loadDB as db

path = "Samples/"

medicines = db.loadMedicines()
products = [x['prod_name'] for x in medicines]

compounds = db.loadCompounds()

def getStrings(image):
	if (type(image) == str):
		image = path + image
		image = cv2.imread(image)

	raw_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	return pytesseract.image_to_string(raw_image)

def getProduct(image):
	texts = getStrings(image).lower()
	# print(texts)
	pred_product = None
	contents = []
	for product in products:
		if (product.lower() in texts):
			pred_product = product
			break

	for line in texts.split("\n"):
		comp = None
		#print(line)
		for word in line.split(" "):
			if (word in compounds):
				comp = word
		q = None
		if (comp):
			x = re.search("(\d)+( mg|mg)?", line)
			if (x):
				q = x.group(0)

		if (comp):
			contents.append((comp, q))

	return {"prod_name": pred_product, "compounds": contents}
				

if __name__ == "__main__":
	#print(getStrings('4.jpeg'))
	path = "../Samples"
	print(getProduct('4.jpeg'))
	
