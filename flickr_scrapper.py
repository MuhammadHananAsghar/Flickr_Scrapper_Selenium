from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time
import pickle
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent

ua = UserAgent()
opts = Options()
opts.add_argument(f"user-agent={ua.random}")

driver_path = "drivers/geckodriver"
service = Service(driver_path)
driver = webdriver.Firefox(service=service, options=opts)

seed_query = "turtle"
seed_url = "https://flickr.com"
driver.get("https://flickr.com/search/?text={}".format(seed_query))
time.sleep(1)
print("Page is Loaded!")

def scroll():
	SCROLL_PAUSE_TIME = 10
	last_height = driver.execute_script("return document.body.scrollHeight")
	while True:
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(SCROLL_PAUSE_TIME)
		new_height = driver.execute_script("return document.body.scrollHeight")
		if new_height == last_height:
			break
		last_height = new_height
scroll()
time.sleep(5)
id_button = 1
while True:
	try:
		load_more = driver.find_element(By.CLASS_NAME,"infinite-scroll-load-more")
		load_more_button = load_more.find_element(By.TAG_NAME,"button")
		load_more_button.click()
		time.sleep(5)
		scroll()
		id_button += 1
	except:
		break
	if id_button == 5:
		break

img_anchors = []
image_anchors = driver.find_elements(By.CLASS_NAME,"overlay")
for image_anchor in image_anchors:
	img_anchors.append(image_anchor.get_attribute("href")+"in/photostream/")
print("Data is Scrapped!")
print(f"Total {len(img_anchors)} Images Scrapped.")

with open(f"data/{seed_query}.pkl", "wb") as fp:
	pickle.dump(img_anchors, fp)
# To Download
def download_image_flickr(url):
	directory = ""
	page = requests.get(url)
	contents = page.content
	soup = BeautifulSoup(contents, 'html.parser')
	image = soup.find_all("img", {"class": "main-photo"})[0]
	url_of_image = "https:"+image.get("src")
	name = url_of_image.split("/")[-1]
	response = requests.get(url)
	with open(f"{directory}/{name}", 'wb') as handle:
		handle.write(response.content)
	print(f"Saved: {name}")

with ThreadPoolExecutor(max_workers=8) as executor:
	executor.map(download_image_flickr, img_anchors)
driver.quit()
