from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.action_chains import ActionChains
import re
import mysql.connector

details = {
    "Business Name": [],
    "Address": [],
    "Category": [],
    "Review Average": [],
    "Review Count": [],
    "Website": [],
    "Phone Number": [],
}

browser = webdriver.Chrome()
browser.get('https://www.google.com/maps/search/dentist+near+me/@28.9925063,76.9931886,14z/data=!3m1!4b1?entry=ttu')
time.sleep(2)

shop_element = browser.find_elements(By.XPATH, "//a[contains(@class, 'hfpxzc')]")
saturation = True

while saturation:
    current_length = len(shop_element)
    element = shop_element[current_length - 1]
    actions = ActionChains(browser)
    actions.move_to_element(element).perform()
    try:
        end_of_scroll = browser.find_element(By.XPATH, "//span[contains(@class, 'HlvSq')]")
        saturation = False
        break
    except:
        try:
            end = browser.find_element(By.XPATH, "//div[contains(@class, 'njRcn')]")
            if end:
                saturation = False
                break
        except:
            pass
    if shop_element.index(element) == len(shop_element) - 1:
        browser.execute_script("arguments[0].scrollIntoView();", element)
    shop_element = browser.find_elements(By.XPATH, "//a[contains(@class, 'hfpxzc')]")

def shop_url(f_element=shop_element):
    """Extracts url to details about shop"""
    shopurl = []
    for element in f_element:
        shopurl.append(element.get_attribute('href'))
    return shopurl

def extractor(browser):
    # shop name
    try:
        business_name = browser.find_element(By.XPATH, "//h1[contains(@class, 'DUwDvf')]").text
    except:
        business_name = "N/A"
    # review
    try:
        review = browser.find_element(By.XPATH, "//div[contains(@class, 'F7nice')]").text.strip()
        review = review.split('\n')
        try:
            review_average = review[0].strip()
        except:
            review_average = "N/A"
        try:
            review_count = review[1].replace('(', '').replace(')', '').strip()
        except:
            review_count = "N/A"
    except:
        review_average = "No reviews"
        review_count = "No reviewer"
    try:
        category = browser.find_element(By.XPATH, "//button[contains(@class, 'DkEaL')]").text.strip()
    except:
        category = "N/A"

    # regex
    add_num_web_element = browser.find_elements(By.XPATH, "//div-[contains(@class, 'rogA2c')]")
    phone_pattern_regex = r'\b(?:\+?\d{1,3})?[-.\s]??(?:\d{10}|\d{5}[-.\s]?\d{5})\b'
    website_pattern_regex = r'\b(?!facebook\.com\b)(?!instagram\.com\b)(?!swiggy\.com\b)(?!zomato\.com\b)([a-zA-Z0-9.-]+\.[a-zA-Z]{2,7})\b'
    complete_string = ""
    for element in add_num_web_element:
        complete_string = complete_string + " " + element.text
    phone_num_t = re.findall(phone_pattern_regex, complete_string)
    if phone_num_t == []:
        phone_num = "N/A"
    else:
        phone_num = phone_num_t[0]
    website_t = re.findall(website_pattern_regex, "hey there i am here aptechfatehabad.com")
    if website_t == []:
        website = "N/A"
    elif website_t == [('', '')]:
        website = "N/A"
    else:
        website = website_t[0]
    try:
        address = add_num_web_element[0].text
    except:
        address = "N/A"

    data = [business_name, address, category, review_average, review_count, website, phone_num]
    return data

def visit_url(f_shopurl=shop_url()):
    for url in f_shopurl:
        browser.get(url)
        detail = extractor(browser)
        details["Business Name"].append(detail[0])
        details["Address"].append(detail[1])
        details["Category"].append(detail[2])
        details["Review Average"].append(detail[3])
        details["Review Count"].append(detail[4])
        details["Website"].append(detail[5])
        details['Phone Number'].append(detail[6])

visit_url()

# MySQL database connection
conn = mysql.connector.connect(
    host="your_host",
    user="your_username",
    password="your_pass",
    database="business_data",
    
)
cursor = conn.cursor()

# Insert data into MySQL
for i in range(len(details["Business Name"])):
    sql = "INSERT INTO businesses (business_name, address, category, review_average, review_count, website, phone_number) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    val = (
        details["Business Name"][i],
        details["Address"][i],
        details["Category"][i],
        details["Review Average"][i],
        details["Review Count"][i],
        details["Website"][i],
        details["Phone Number"][i]
    )
    cursor.execute(sql, val)

conn.commit()
print(" successful..")
cursor.close()
conn.close()

browser.quit()
