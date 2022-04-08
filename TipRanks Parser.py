from xml.etree.ElementTree import fromstring, ElementTree
import requests
import pandas
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import fuckit
from bs4 import BeautifulSoup

# Parse site
sitemap = [
    "https://www.tipranks.com/sitemap-analysts.xml",
    #"https://www.tipranks.com/sitemap-bloggers.xml",
    #"https://www.tipranks.com/sitemap-insiders-1.xml",
    #"https://www.tipranks.com/sitemap-insiders-2.xml",
    #"https://www.tipranks.com/sitemap-insiders-3.xml",
    #"https://www.tipranks.com/sitemap-insiders-4.xml",
    #"https://www.tipranks.com/sitemap-insiders-5.xml"
]

items = []
sources = []
for xml in sitemap:
    tree = ElementTree(fromstring(requests.get(xml).text))
    root = tree.getroot()
    for url in root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
        items.append(url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text)
        xml = re.search("-[a-z]+", xml).group(0)
        sources.append(xml[1:len(xml)])

data = pandas.DataFrame(list(zip(items, sources)), columns=['url', 'source'])


# Scraping info
USER = "jiztastamablastamarang@gmail.com"
PASSWORD = "6pnpd7pG"
url = 'https://www.tipranks.com/sign-in'
DRIVER_PATH = "d:/Documents/chromedriver.exe"
opt = webdriver.ChromeOptions()
prefs = {'profile.default_content_setting_values': {'images': 2}}
opt.add_experimental_option('prefs', prefs)

driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=opt)
#driver.get(url)
#user = driver.find_element_by_xpath("//input[@type='email']").send_keys(USER)
#password = driver.find_element_by_xpath("//input[@type='password']").send_keys(PASSWORD)
#submit = driver.find_element_by_class_name("client-templates-loginPage-styles__submitButton").click()

for i in range(len(data)):
    url = data.loc[i, "url"]
    driver.get(url)
    source = driver.page_source
    with fuckit:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@itemprop='name']")))
    #with fuckit:
    #    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@itemprop='worksFor']")))
    with fuckit:
        data.loc[i, 'name'] = driver.find_element_by_xpath("//span[@itemprop='name']").text
    with fuckit:
        data.loc[i, 'worksFor'] = driver.find_element_by_xpath("//span[@itemprop='worksFor']").text
    with fuckit:
        data.loc[i, 'worksFor'] = driver.find_element_by_xpath("//div[@itemprop='worksFor']").text
    with fuckit:
        data.loc[i, 'jobTitle'] = driver.find_element_by_xpath("//span[@itemprop = 'jobTitle']").text
    with fuckit:
        data.loc[i, 'jobTitle'] = driver.find_elements_by_class_name("client-components-insiders-styles__insiderPosition client-components-insiders-mixins__elipsify").text
    #with fuckit:
    #    soup = BeautifulSoup(source, "html.parser")
    #    y = soup.select_one("script[type='application/ld+json']")
    with fuckit:
        data.loc[i, 'sector'] = driver.find_element_by_class_name("client-components-experts-styles__mainSectorName").text
        data.loc[i, 'location'] = driver.find_element_by_class_name("client-components-experts-styles__flagCountry").text
    with fuckit:
        data.loc[i, 'rank'] = driver.find_elements_by_class_name("client-components-insiders-styles__ranking")[1].text.split()[1]
    with fuckit:
        data.loc[i, 'rank'] = driver.find_elements_by_class_name("client-components-experts-styles__ranking")[1].text.split()[1]
    with fuckit:
        data.loc[i, 'succsessRate'] = driver.find_element_by_class_name("client-components-experts-styles__profitableRatingsLabel").text
        data.loc[i, 'ratings'] = driver.find_element_by_class_name("client-components-experts-styles__ratingsUpper").text
    with fuckit:
        data.loc[i, 'buy'] = driver.find_elements_by_class_name("client-components-experts-styles__legendPercent")[0].text
        data.loc[i, 'hold'] = driver.find_elements_by_class_name("client-components-experts-styles__legendPercent")[1].text
        data.loc[i, 'sell'] = driver.find_elements_by_class_name("client-components-experts-styles__legendPercent")[2].text


data["url"] = data["url"].str.replace("https://www.tipranks.com", "")
data["rank"] = data["rank"].str.replace(",", "").str.replace("#", "")

data.to_excel("d:/etf/Analysts_.xlsx", index=False, header=True)

