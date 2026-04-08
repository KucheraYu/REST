import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def scrape_frontend():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    data = []

    try:
        driver.get("http://localhost:3000/login")
        time.sleep(1)

        register_btn = driver.find_element(By.XPATH, "//button[text()='Register']")
        register_btn.click()
        time.sleep(0.3)

        driver.find_element(By.CSS_SELECTOR, "input[type='text']").send_keys("Scraper")
        email_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='email']")
        email_inputs[0].send_keys("scraper@test.com")
        password_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
        password_inputs[0].send_keys("123456")

        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(1)

        table_rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        for row in table_rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 3:
                data.append({
                    "id": cells[0].text,
                    "name": cells[1].text,
                    "email": cells[2].text,
                })

        driver.find_element(By.LINK_TEXT, "Posts").click()
        time.sleep(1)

        post_rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        post_count = len(post_rows)

        print(f"[Scraper] Users found: {len(data)}")
        for u in data:
            print(f"  {u['id']}: {u['name']} <{u['email']}>")
        print(f"[Scraper] Posts on page: {post_count}")

    finally:
        driver.quit()

    return data, post_count


if __name__ == "__main__":
    scrape_frontend()
