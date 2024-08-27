import time
import re
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as Soup

def save_emails_to_txt(emails):
    with open('emails.txt', 'a', encoding='utf-8') as file:
        for email in emails:
            file.write(f"{email}\n")

def save_page_source(driver, filename):
    """ Save the page source HTML to a file """
    with open(filename, "w", encoding="utf-8") as file:
        file.write(driver.page_source)

def extract_emails_from_html(html_content):
    """ Extract emails from the HTML content """
    soup = Soup(html_content, 'html.parser')
    text_content = soup.get_text()
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = set(re.findall(email_pattern, text_content))
    return emails

def load_all_comments(driver, button_text):
    loadmore = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        try:
            load_more_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[contains(@class, 'comments-comments-list__load-more-comments-button') and .//span[text()='{button_text}']]"))
            )
            if load_more_button:
                print("Clicking 'Load more comments' button...")
                load_more_button.click()
                loadmore += 1
                print(f"Emails collected: {loadmore * 10}")
                time.sleep(4) #adjust based on browser speed/rate limit of site scraped
            else:
                print("No button found.")
                break
        except Exception as e:
            print(f"Error: {e}")
            break
    return loadmore

def main():
    with open("config.json") as f:
        config = json.load(f)
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get("https://www.linkedin.com/checkpoint/rm/sign-in-another-account?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin")
        driver.find_element(By.NAME, config["username_name"]).send_keys(config["linkedin_username"])
        driver.find_element(By.NAME, config["password_name"]).send_keys(config["linkedin_password"])
        driver.find_element(By.XPATH, config["sign_in_button_xpath"]).click()
        
        urls = [] #TODO: input urls from other scraper
        total = 0
        for url in urls:
            driver.get(url)

            emailnum = load_all_comments(driver, "Load more comments")
            total+= emailnum
            save_page_source(driver, "page_source.html")
            html_content = driver.page_source
            emails = extract_emails_from_html(html_content)

            save_emails_to_txt(emails)
            emails.clear()
            print(total)
                

        input("Press Enter to close chrome")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
