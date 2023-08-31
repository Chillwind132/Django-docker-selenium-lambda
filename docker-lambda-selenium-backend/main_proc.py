import os
import time
import boto3
import logging
from datetime import datetime

from selenium import webdriver
from tempfile import mkdtemp
from selenium.webdriver.common.by import By

s3_bucket = "stg-uploaded-screenshots-lambda"
s3_client = boto3.client('s3')




def generate_screenshot(chrome, output_path):
    time.sleep(0.5)

    today = datetime.now()  # Generate current time for file naming
    file_name = "Picture" + today.strftime('%Y_%m_%d_%H_%M_%S') + ".png"
    file_path_full = os.path.join(output_path, file_name)

    chrome.find_element(By.TAG_NAME, 'body').screenshot(file_path_full)  # Take screenshot of data inside the <body> tag and save
    return file_path_full, file_name


def handler(event="None", context=None):  # sls invoke --function screenshot_proc --raw --data https://www.example.com/

    options = webdriver.ChromeOptions()
    service = webdriver.ChromeService("/opt/chromedriver")

    options.binary_location = '/opt/chrome/chrome'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument(f"--user-data-dir={mkdtemp()}")
    options.add_argument(f"--data-path={mkdtemp()}")
    options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    options.add_argument("--remote-debugging-port=9222")

    chrome = webdriver.Chrome(options=options, service=service)

    #chrome = Browser(options=options)
    chrome.get(event)

    # Set up output directory
    output_path = os.path.join('/tmp', 'output')
    os.makedirs(output_path, exist_ok=True)

    try:
        file_path_full, file_name = generate_screenshot(chrome, output_path)
        s3_client.upload_file(file_path_full, s3_bucket, file_name)

    except Exception as e:
        logging.error(f"Screenshot generation error: {str(e)}")
        chrome.quit()
        return str(e)

    # Remove file after upload to s3
    os.remove(file_path_full)

    chrome.quit()
    return file_name