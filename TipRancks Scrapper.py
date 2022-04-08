import pandas as pd
import requests
import urllib3
from bs4 import BeautifulSoup
from selenium import webdriver

USER = "jiztastamablastamarang@gmail.com"
PASSWORD = "6pnpd7pG"
url = 'https://www.tipranks.com/sign-in'
queries = ['analysts', 'bloggers', 'insiders']
path = "d:/etf/NER_market_analyst.xlsx"

DRIVER_PATH="d:/Documents/chromedriver.exe"
driver = webdriver.Chrome(executable_path=DRIVER_PATH)

driver.get(url)
user = driver.find_element_by_xpath("//input[@type='email']").send_keys(USER)
password = driver.find_element_by_xpath("//input[@type='password']").send_keys(PASSWORD)
submit = driver.find_element_by_class_name("client-templates-loginPage-styles__submitButton").click()


driver.get(url)
#soup = BeautifulSoup(driver.page_source, 'lxml')

data = pd.ExcelFile(path).parse(sheet_name="Sheet1")


for i in range(2):
    for query in queries:
        name = str(data.loc[i, "person"]).lower().split()
        print(name)
        driver.get("https://www.tipranks.com/" + query + "/" + name[0] + "-" + name[1])
        print(query)
        print(driver.title)
        if driver.title == 'Page Not Found :(':
            pass
        else:
           print(driver.page_source)
           #data['worksFor'] = driver.find_element_by_xpath("//span[@itemprop='worksFor']").text
           #data['jobTitle'] = driver.find_element_by_xpath("//span[@itemprop = 'jobTitle']").text
           #data['rank'] = driver.find_element_by_class_name("client-components-experts-styles__ranking")
           break




USER = "jiztastamablastamarang@gmail.com"
PASSWORD = "6pnpd7pG"
url = 'https://www.tipranks.com/sign-in'
DRIVER_PATH="d:/Documents/chromedriver.exe"
driver = webdriver.Chrome(executable_path=DRIVER_PATH)
driver.get(url)
user = driver.find_element_by_xpath("//input[@type='email']").send_keys(USER)
password = driver.find_element_by_xpath("//input[@type='password']").send_keys(PASSWORD)
submit = driver.find_element_by_class_name("client-templates-loginPage-styles__submitButton").click()

for i in range(3):
    url = data.loc[i, "url"]
    driver.get(url)

    print(data.loc[i, "url"])
    if driver.title == 'Page Not Found :(':
        pass
    else:
        data.loc[i, 'name'] = driver.find_element_by_xpath("//span[@itemprop='name']").text
        data.loc[i, 'worksFor'] = driver.find_element_by_xpath("//span[@itemprop='worksFor']").text
        data.loc[i, 'jobTitle'] = driver.find_element_by_xpath("//span[@itemprop = 'jobTitle']").text
        data.loc[i, 'rate'] = driver.find_element_by_class_name("client-components-experts-styles__profitableRatingsLabel").text
        data.loc[i, 'sector'] = driver.find_element_by_class_name("client-components-experts-styles__mainSectorName").text
        data.loc[i, 'location'] = driver.find_element_by_class_name("client-components-experts-styles__flagCountry").text
        data.loc[i, 'ratings'] = driver.find_element_by_class_name("client-components-experts-styles__ratingsUpper").text
        data.loc[i, 'buy'] = driver.find_elements_by_class_name("client-components-experts-styles__legendPercent")[0].text
        data.loc[i, 'hold'] = driver.find_elements_by_class_name("client-components-experts-styles__legendPercent")[1].text
        data.loc[i, 'sell'] = driver.find_elements_by_class_name("client-components-experts-styles__legendPercent")[2].text




#data.to_excel("d:/etf/TipRanks.xlsx", index=False, header=True)

