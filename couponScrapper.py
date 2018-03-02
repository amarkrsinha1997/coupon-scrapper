#!python3
try:
	import pygsheets
except Exception as e:
	raise e

import bs4, requests, datetime, time
from selenium import webdriver

#Activating the selenium module for use in chrome headless browser
#so that the module can run in background
try:
	options = webdriver.ChromeOptions()
	options.add_argument('headless')
	driver = webdriver.Chrome('./chromedriver',chrome_options=options)
except:
	try:
		options = webdriver.ChromeOptions()
		options.add_argument('headless')
		driver = webdriver.Chrome(chrome_options=options)
	except Exception as e:
		raise e


jsonFile = open('coupon-scrapper.json')
email = json.load(jsonFile.read())['client_email']
print('\n\n\n'+email + ' \nPlease share your sheet with this email\n\n\n')



#authorizing and connecting to the sheet name couponScrapper using the jsonfile
#couponScrapper
try: 
	googleCloud = pygsheets.authorize(service_file='coupon-scrapper.json')

	sheetName = input('Enter the name of workSheet that you have created and gave the access : ')
	workSheet = googleCloud.open(sheetName or 'couponScrapper').sheet1
except Exception as e:
	url= 'https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html'
	print('''Include the service account file you can watch the tutorial here ({0}) to create service file
			and save it as coupon-scrappr.json 
			Give access to you Worksheet using it email-id
		 '''.format(url))
 
#getting the page as soup module using request and bs4
def getRequestSoup(url):
	return bs4.BeautifulSoup(requests.get(url).text,'html.parser')

#getting the page as soup module using selenium and bs4
def getDriverSoup(url):
	driver.get(url)
	return bs4.BeautifulSoup(driver.page_source, 'html.parser')

def getCode(url, offerId):
	url = url+'?modal=getCodeModal&offer={0}'.format(offerId)
	couponCodePage = getDriverSoup(url)
	return couponCodePage.find(class_= 'code-txt').text

def appendRow(row):
	workSheet.append_table(values=row)
	print('row saved!')

def loadMorePage(url):
	driver.get(url)
	loadMoreButton = driver.find_element_by_class_name('load-more-offers')
	print('Wait while loading all the offer in the page.....', end='')
	while True:
		print('.', end='')
		try:
			loadMoreButton.click()
		except Exception as e:
			break
		time.sleep(2)
	print('\nOffer loaded....')
	return bs4.BeautifulSoup(driver.page_source, 'html.parser')


def getCategory(url):
	offerCategory = ' '.join(url.split('/')[-1].split('-'))
	print('Extracting from  : ' + offerCategory)

	categoryPage = loadMorePage(url)  

	#get the all the offers
	offers = categoryPage.find_all(class_='offer-card-holder')
	for offer in offers:
		row = []
		#extract the title, store, code, offerDetails
		storeName = offer.find(class_='store-name').text.strip()
		offerTitle = offer.find(class_='offer-title offer-get-code-link').get('data-offer-value')
		print('Extracting the offer : ' + offerTitle)

		offerDetail = []
		for li in offer.find_all('li'):
			offerDetail.append(li.text)
		offerDetail = '\n'.join(offerDetail)

		offerId = offer.find(class_='get-codebtn-holder').get('data-offer-value')

		#Getting the offer code
		offerCode = getCode(url, offerId)
		if offerCode == '':
			offerCode = "Not Available"


		row.append(storeName)
		row.append(offerTitle)
		row.append(offerDetail)
		row.append(offerCode)
		row.append(offerCategory)

		print('Appending offer {0} to the sheet couponScrapper'.format(offerTitle))
		appendRow(row)




def start():
	startTime = datetime.datetime.now()
	header= ['Store Name', 'Offer Title', 'Offer Detail', 'Offer Code', 'Offer Category']
	print('Adding the heading')
	appendRow(header)
	url = 'https://www.coupondunia.in/categories'
	categoriesPage = getRequestSoup(url)
	categoriesUrl = [ 'https://www.coupondunia.in' + category.parent.get('href') for category in categoriesPage.find_all(class_='sub-category')]
	for url in categoriesUrl:
		getCategory(url)

	print("Done!")
	endTime = datetime.datetime.now()
	print('Total time taken for scrapping' + (startTime - endTime).total_seconds())
start()

