import concurrent.futures  # Importing concurrent.futures for thread-based parallelism
import requests  # Importing requests for HTTP requests
from bs4 import BeautifulSoup  # Importing BeautifulSoup for HTML parsing
from selenium import webdriver  # Importing webdriver from Selenium for web automation
from selenium.webdriver.common.keys import Keys  # Importing Keys for keyboard actions
from selenium.webdriver.common.by import By  # Importing By for locating elements
from selenium.webdriver.support import expected_conditions as EC  # Importing EC for expected conditions
from selenium.webdriver.support.ui import WebDriverWait  # Importing WebDriverWait for waiting for elements to load
import threading  # Importing threading for managing threads
import time  # Importing time for adding delays

# Lock for thread-safe printing
print_lock = threading.Lock()

# List to store numbers that didn't work
NumsThatDidntWork = []

# arrays for past papers
MMME1ARRAY = []
ENGFFARRAY = []
MMME2ARRAY = []
COMP2ARRAY = []
CHEM1ARRAY = []
LIFE1ARRAY = []
ECON1ARRAY = []
PSGY1ARRAY = []
counter = False

def if_page(driver, url):
    global counter
    usernametext = ''
    passwordtext = ''
    driver.execute_script("window.open('" + url + "');")  # Open page in new tab using Selenium
    driver.switch_to.window(driver.window_handles[-1])  # Switch to newly opened tab
    if not counter:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'searchinput')))
        input_element = driver.find_element(By.ID, 'searchinput')
        input_element.clear()
        for char in "University of Nottingham":
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'searchinput')))
            input_element.send_keys(char)
            time.sleep(0.1)
        input_element.send_keys(Keys.ENTER)
        time.sleep(1)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'primary'))) 
        input_element2 = driver.find_elements(By.CLASS_NAME, 'primary')
        input_element2[1].click()
        counter = True     
    else:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'primary'))) 
        input_element2 = driver.find_element(By.CLASS_NAME, 'primary')
        input_element2.click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'username')))
    username = driver.find_element(By.ID, 'username')
    username.send_keys(usernametext)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'password')))
    password = driver.find_element(By.ID, 'password')
    password.send_keys(passwordtext)
    password.send_keys(Keys.ENTER)
    # Wait for the page to load after login
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'main-container')))
    # Scrape the page content after login
    source = driver.page_source
    html_source = BeautifulSoup(source, 'html.parser')
    code = html_source.find_all('div', attrs={'class':'simple-item-view-description item-page-field-wrapper table'})
    if len(code) > 1 and str(code[1].text[16:21]) == 'MMME1':
        MMME1ARRAY.append(url)
    elif len(code) > 1 and str(code[1].text[16:21]) == 'ENGFF':
        ENGFFARRAY.append(url)
    elif len(code) > 1 and str(code[1].text[16:21]) == 'MMME2':
        MMME2ARRAY.append(url)
    elif len(code) > 1 and str(code[1].text[16:21]) == 'COMP2':
        COMP2ARRAY.append(url)
    elif len(code) > 1 and str(code[1].text[16:21]) == 'CHEM1':
        CHEM1ARRAY.append(url)
    elif len(code) > 1 and str(code[1].text[16:21]) == 'LIFE1':
        LIFE1ARRAY.append(url)
    elif len(code) > 1 and str(code[1].text[16:21]) == 'ECON1':
        ECON1ARRAY.append(url)
    elif len(code) > 1 and str(code[1].text[16:21]) == 'PSGY1':
        PSGY1ARRAY.append(url)
    driver.close()  # Close the current tab
    driver.switch_to.window(driver.window_handles[-1])
def scrape_page(i, driver):
    try:
        index = str(i)
        url = 'https://rdmc.nottingham.ac.uk/handle/internal/' + index
        page_to_scrape = requests.get(url, timeout=5)  # Sending HTTP GET request
        soup = BeautifulSoup(page_to_scrape.text, 'html.parser')  # Parsing HTML content
        exampaper = soup.find('h1', attrs={'data-i18n': 'ds-search-heading'})  # Finding exam paper heading
        with print_lock:
            # Handling different types of pages
            if exampaper is not None and exampaper.text == 'Find Your Institution': 
                print(index, 'is a page')
                if_page(driver, url)
                tabs = driver.window_handles
                for tab in tabs[:-1]:  # Keep the last tab open
                    driver.switch_to.window(tab)
                    driver.close()
                driver.switch_to.window(driver.window_handles[-1])           
            else:
                print(index, 'not a page')
    except Exception as e:
        with print_lock:
            NumsThatDidntWork.append(index)
            print("Error occurred while accessing page", index, ":", e)

# Function to handle errors
def errors(index, driver):
    try:
        url = 'https://rdmc.nottingham.ac.uk/handle/internal/' + str(NumsThatDidntWork[index])
        page_to_scrape = requests.get(url, timeout=5)  # Sending HTTP GET request
        soup = BeautifulSoup(page_to_scrape.text, 'html.parser')  # Parsing HTML content
        exampaper = soup.find('h1', attrs={'data-i18n': 'ds-search-heading'})  # Finding exam paper heading
        
        with print_lock:
            # Handling different types of pages
            if exampaper is not None and exampaper.text == 'Find Your Institution': 
                print(NumsThatDidntWork[index], 'is a page, length of errors is: ', len(NumsThatDidntWork))
                if_page(driver, url)
                tabs = driver.window_handles
                for tab in tabs[:-1]:  # Keep the last tab open
                    driver.switch_to.window(tab)
                    driver.close()
                del NumsThatDidntWork[index]
                driver.switch_to.window(driver.window_handles[-1])
            else:
                print(NumsThatDidntWork[index], 'not a page, length of errors is: ', len(NumsThatDidntWork))
                del NumsThatDidntWork[index]
    except Exception as e:
        with print_lock:
            print("Error occurred while accessing page", NumsThatDidntWork[index], ":", e)

# Main function
def main():
    # Create a Firefox webdriver
    driver = webdriver.Firefox()
    # Scraping pages with ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(scrape_page, range(9000, 12000), [driver]*99999999)
    # Handling errors
    while len(NumsThatDidntWork) > 0:
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            executor.map(errors, range(len(NumsThatDidntWork)), [driver]*999999999)

if __name__ == "__main__":
    main()
    print('mecanical year 1 array is:',MMME1ARRAY)
    print('FFEBS array is:', ENGFFARRAY)
    print('mech year 2 is:', MMME2ARRAY)
    print('comp sci second year is:', COMP2ARRAY)
    print('chem first year is:', CHEM1ARRAY)
    print('boi chem first year is:', LIFE1ARRAY)
    print('math and econ first year is:', ECON1ARRAY)
    print('psychology first year is:', PSGY1ARRAY)
    print('END')