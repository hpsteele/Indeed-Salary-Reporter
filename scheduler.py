import schedule
import time	
import subprocess

def scraping():
    subprocess.Popen("C:\\Users\\Administrateur\\Desktop\\firsy_prog\\Scrapping.bat", shell=True)

def import_and_preprocessing():
    subprocess.Popen("C:\\Users\\Administrateur\\Desktop\\firsy_prog\\import_and_preprocessing.bat", shell=True)
	
def additionnal_companies_preprocessing():
    subprocess.Popen("C:\\Users\\Administrateur\\Desktop\\firsy_prog\\additionnal_companies_preprocessing.bat", shell=True)	

def scrapping_companies():
    subprocess.Popen("C:\\Users\\Administrateur\\Desktop\\firsy_prog\\scrapping_companies.bat", shell=True)
	
def Prediction():
    subprocess.Popen("C:\\Users\\Administrateur\\Desktop\\firsy_prog\\Prediction.bat", shell=True)

def viz_guillaume():
    subprocess.Popen("C:\\Users\\Administrateur\\Desktop\\firsy_prog\\viz_guillaume.bat", shell=True)
	
def soukeye_graphs():
    subprocess.Popen("C:\\Users\\Administrateur\\Desktop\\firsy_prog\\soukeye_graphs.bat", shell=True)
	
def hugh_graphs():
    subprocess.Popen("C:\\Users\\Administrateur\\Desktop\\firsy_prog\\hugh-graphs.bat", shell=True)

def rapport_automatise_envoye():
    subprocess.Popen("C:\\Users\\Administrateur\\Desktop\\firsy_prog\\rapport_automatise_envoye.bat", shell=True)


	
schedule.every().day.at("13:22").do(scraping)
schedule.every().day.at("13:21").do(import_and_preprocessing)
schedule.every().day.at("13:23").do(scrapping_companies)
schedule.every().day.at("13:34").do(additionnal_companies_preprocessing)
schedule.every().day.at("13:38").do(Prediction)
schedule.every().day.at("13:45").do(viz_guillaume)
schedule.every().day.at("13:04").do(soukeye_graphs)
schedule.every().day.at("13:56").do(hugh_graphs)
schedule.every().day.at("13:56").do(rapport_automatise_envoye)

while True:
    schedule.run_pending()
    time.sleep(1)
	

