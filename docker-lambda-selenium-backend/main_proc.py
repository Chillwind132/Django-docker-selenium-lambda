from selenium import webdriver
from tempfile import mkdtemp
from selenium.webdriver.common.by import By
from botocore.exceptions import ClientError
from datetime import datetime
import boto3
import os
import logging
import time

format = ".jpg"
s3_bucket = "stg-uploaded-screenshots-lambda"
s3_client = boto3.client('s3')

def handler(event=None, context=None): # sls invoke --function screenshot_proc --raw --data https://www.example.com/
    options = webdriver.ChromeOptions()
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
    chrome = webdriver.Chrome("/opt/chromedriver",
                              options=options)
    chrome.get(event)

    time.sleep(0.5)

    try:
        today = datetime.now() # Generate current time for file naming
        file_name = "Picture" + str(today)
        file_name = file_name.replace(" ","_") + ".png"
        path = "/tmp"
        output_path = path + "/output/"
        file_path_full = output_path + file_name

        if os.path.exists(output_path):
            pass
        else:
            os.makedirs(output_path)

        chrome.find_element(By.TAG_NAME, 'body').screenshot(file_path_full) #Take screenshot of data inside the <body> tag and save
        upload = s3_client.upload_file(file_path_full, s3_bucket, file_name)

    except Exception as e:
        chrome.close()
        return str(e)

    os.remove(file_path_full) # Remove file after upload to s3

    chrome.close()
    return file_name
