
import datetime

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

print('hello world')

server_url = 'http://localhost:5000'

t1 = datetime.datetime.now()
print('Performance test started: ' + str(t1))

browser = webdriver.Firefox()
browser.get(server_url)
print(browser.current_url)
elem = browser.find_element_by_name("login")
elem.clear()
elem.send_keys("admin")
elem.send_keys(Keys.RETURN)
print(browser.current_url)

elem = WebDriverWait(browser, 20).until(
         EC.element_to_be_clickable((By.ID, "proddate-save")))

print(browser.title)
browser.implicitly_wait(15)
elem = browser.find_element_by_id("proddate-input")
elem.clear()
elem.send_keys("201501")
elem.send_keys(Keys.RETURN)
print(browser.current_url)

browser.get(server_url + '/leases')
elem = WebDriverWait(browser, 20).until(
         EC.element_to_be_clickable((By.ID, "search-basic")))
elem.click()
print(browser.current_url)

browser.get(server_url + '/wells')
elem = WebDriverWait(browser, 20).until(
         EC.element_to_be_clickable((By.ID, "search-basic")))
elem.click()
print(browser.current_url)

browser.get(server_url + '/wellevents')
elem = WebDriverWait(browser, 20).until(
         EC.element_to_be_clickable((By.ID, "search-basic-button")))
elem.click()
print(browser.current_url)

browser.get(server_url + '/facility/search')
elem = WebDriverWait(browser, 20).until(
         EC.element_to_be_clickable((By.ID, "search-basic")))
elem.click()
print(browser.current_url)

browser.get(server_url + '/reports/royalties')
print(browser.current_url)

browser.get(server_url + '/reports/calclist')
print(browser.current_url)

urls = []
all_options = browser.find_elements_by_id("worksheet")

for option in all_options:
    urls.append(option.get_attribute("href"))
#    print("Value is: %s" % option.get_attribute("href"))
#   option.click()
#    print('   ', browser.current_url)

for u in urls:
    browser.get(u)
    a = u.split('?')
    f = a[1].replace('&',' ')
    file_name = 'html/' + f + '.html'
    with open(file_name, 'w', encoding='utf-8') as out:
        out.write(browser.page_source + '\n')
    print('   ', browser.current_url)

t2 = datetime.datetime.now()
print('Ended: ' + str(t2))

t3 = t2 - t1
print('Took: ' + str(t3))

with open('$Performance Log.txt', 'a') as out:
        out.write(str(t1) + ' ' + str(t3) + ' ' + server_url + '\n')
