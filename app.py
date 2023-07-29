from flask import Flask
import flask
import os
import Python.loadDB as db
import Python.searchOps as sop
import cv2
import pymongo
from datetime import datetime
from Python.getImage import getImage
import Python.GetProductName as getProd
import Python.GetReportData as getReport

db.path = "DB/"
medicines = db.loadMedicines()

client = pymongo.MongoClient("127.0.0.1", 27017)
mdb = client.ResistanceData

app = Flask(__name__)

@app.route('/')
def index():
	return flask.render_template('index.html', div_w = "85%")

@app.route('/favicon.ico')
def getIcon():
	return flask.send_file("Resources/favicon.ico")

@app.route('/Resources/<path:filename>')
def getFile(filename):
	print(filename)
	# filename = os.path.join(app.instance_path, 'Resources', filename)
	# return flask.send_file(filename)
	return flask.send_file("Resources/" + filename)

@app.route('/medicine/<med_name>')
def showMedicineInfo(med_name):
	med_info = medicines[int(med_name)]
	print(med_info)
	return flask.render_template('medinfo.html', med=med_info)

@app.route('/medicine/search')
def searchMedicine():
	results = sop.searchMedicine(flask.request.args.get("q").lower(), medicines)
	print(results)
	return flask.render_template('medsearchshow.html', results=results)

@app.route('/medicine/search/image', methods=["POST"])
def searchByImage():
	try:
		image = flask.request.files.get("imagefile", "")
		img = getImage(image.stream.read())
	except:
		print("Unable to access file")
		return flask.redirect("/develop/fileupload")
	
	prod = getProd.getProduct(img)	
	print(prod)
	results = sop.searchMedicine(prod['prod_name'], medicines)
	for comp in prod['compounds']:
		results.extend(sop.searchMedicine(comp[0], medicines))

	results = results[:10]

	return flask.render_template('medsearchshow.html', results=results)

@app.route('/report/uploaded', methods=["POST"])
def uploadReport():
	try:
		image = flask.request.files.get("imagefile", "")
		img = getImage(image.stream.read())
	except:
		print("Unable to access file")
		return flask.redirect("/develop/reportupload")

	report = getReport.getResistanceData(img)
	timestamp = datetime.timestamp(datetime.now())
	report['tid'] = timestamp

	mdb.data.insert_one(report)
	cv2.imwrite("DB/Reports/{}.jpg".format(timestamp), img)
	# insertInReports(report)
	
	print(report)

	return flask.render_template('report_uploaded.html', bacts=report["bacts"], values={1:"SENSITIVE",2:"INTERMEDIATE",3:"RESISTANT"}, res_data=report['resist_data'])

def insertInReports(report):
	return


@app.route('/upload/<ftype>')
def fileUpload(ftype):
	if (ftype == 'file'):
		ftype = 'medicine'
	if (ftype == 'medicine'):
		url = '/medicine/search/image'
	else: # ftype == 'report'
		url = '/report/uploaded'

	return flask.render_template("fileupload.html", url=url, ftype=ftype)

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=80)
