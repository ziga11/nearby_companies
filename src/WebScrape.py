from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json
import time
import os
import pandas as pd
import numpy as np
from pathlib import Path

session = requests.Session()


def fetch_content(url, retries=3):
    try:
        response = session.get(url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        if retries > 0:
            print(f"Error fetching page {url}: {str(e)}. Retrying...")
            time.sleep(5)
            return fetch_content(url, retries - 1)
        else:
            print(f"Max retries exceeded for {url}. Error: {str(e)}")
            raise


class Recruitly:
    def __init__(self, driver):
        self.driver = driver

    def login(self):
        LOGIN_URL = "https://secure.recruitly.io/login"
        USERNAME = "it@kariera.si"
        PASSWORD = os.getenv("recruitlyPW")

        self.driver.get(LOGIN_URL)

        time.sleep(2)

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        ).send_keys(USERNAME)

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        ).send_keys(PASSWORD)

        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    def xlsx_to_json(self, xlsx_file):
        df = pd.read_excel(xlsx_file)
        data_dict = df.to_dict(orient="records")

        os.remove(xlsx_file)

        def replace_nan_with_none(obj):
            if isinstance(obj, list):
                return [replace_nan_with_none(i) for i in obj]
            elif isinstance(obj, dict):
                return {k: replace_nan_with_none(v) for k, v in obj.items()}
            elif isinstance(obj, float) and np.isnan(obj):
                return None
            else:
                return obj

        data_dict = replace_nan_with_none(data_dict)
        json_file = "../data/proaktivna_prodaja_candidates.json"

        with open(
            "../data/places_coordinates.json", "r", encoding="utf-8"
        ) as coordinate_file:
            coordinate_dict = json.load(coordinate_file)

        for entry in data_dict:
            try:
                entry["Coordinates"] = coordinate_dict[entry["Address City"].lower()]
            except Exception:
                entry["Coordinates"] = None

        with open(json_file, "w", encoding="utf-8") as file:
            json.dump(data_dict, file, ensure_ascii=False, indent=4)

    def find_xlsx_file(self):
        downloads_path = Path.home() / "Downloads"

        latest_file = None
        latest_creation_time = 0

        for file in downloads_path.iterdir():
            if not file.is_file():
                continue

            creation_time = file.stat().st_ctime
            if creation_time > latest_creation_time:
                latest_creation_time = creation_time
                latest_file = file

        return latest_file

    def fetch_candidates(self):
        self.driver.get("https://secure.recruitly.io/candidate")

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "candidate-filter-btn"))
        )

        self.driver.find_element(By.ID, "candidate-filter-btn").click()

        self.driver.find_element(
            By.CSS_SELECTOR, "a.nav-link[href='#candidate-custom-filters']"
        ).click()

        desired_filter = self.driver.find_element(
            By.XPATH,
            "//a[contains(@class, 'hand') and contains(text(), 'Proaktivna_prodaja')]",
        )

        parent_element = desired_filter.find_element(By.XPATH, "../..")

        next_sibling = parent_element.find_element(By.XPATH, "following-sibling::*[1]")
        next_sibling.find_element(By.TAG_NAME, "a").click()
        tags = self.driver.find_elements(By.CSS_SELECTOR, "li.ms-elem-selectable")
        for tag in tags:
            tag.click()
        self.driver.find_element(
            By.CSS_SELECTOR, "button.btn.btn-blue.btn-candidate-export"
        ).click()
        time.sleep(2)
        self.xlsx_to_json(self.find_xlsx_file())


class WebScrape:
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.default_content_setting_values.notifications": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        self.session = session
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(15)
        self.driver.maximize_window()
        self.recruitly = Recruitly(self.driver)

    def fetch_candidates(self):
        self.recruitly.login()
        self.recruitly.fetch_candidates()
