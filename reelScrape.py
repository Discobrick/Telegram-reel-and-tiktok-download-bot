import os
import re
import requests
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def goToSnapSave(downloadUrl, browser):
    browser.get("https://snapsave.app")
    url = browser.find_element(value="url")
    url.send_keys(downloadUrl)
    url.send_keys(Keys.RETURN)


def downloadReel(downloadUrl,fromUser):
    options = Options()
    options.enable_mobile
    options.add_argument('--no-sandbox')

    browser = webdriver.Remote(command_executor="http://127.0.0.1:4444/wd/hub",options=options)
    addon_id = webdriver.Firefox.install_addon(browser,os.path.dirname(os.path.realpath(__file__))+'/Ublock.xpi', temporary=True)
    videoUrl = ""

    if (re.search(r"(.*www.facebook\.com\/reel.*)|(.*fb.watch\/.*)", downloadUrl)):
        goToSnapSave(downloadUrl, browser)
        WebDriverWait(browser,10000).until(EC.presence_of_element_located((By.XPATH,"(//*[contains(@href,'https://video')])[1]")))
        videoUrl = browser.find_element(By.XPATH,"(//*[contains(@href,'https://video')])[1]").get_attribute('href')
    elif(re.search(r".*9gag\.com\/gag\/.*",downloadUrl)):
        browser.get(downloadUrl)
        WebDriverWait(browser,10000).until(EC.presence_of_element_located((By.XPATH,"//*[@type='video/mp4']")))
        videoUrl = browser.find_element(By.XPATH,"//*[@type='video/mp4']").get_attribute('src')
    else:
        goToSnapSave(downloadUrl, browser)
        WebDriverWait(browser,10000).until(EC.presence_of_element_located((By.XPATH,"//*[contains(@href,'https://snapxcdn.com')]")))
        videoUrl = browser.find_element(By.XPATH,"//*[contains(@href,'https://snapxcdn.com')]").get_attribute('href')


    r = requests.get(videoUrl)
    filePath = '/app/downloads' + fromUser + datetime.now().strftime("%d%m%Y%H%M%S") +  '.mp4'
    open(filePath,'wb').write(r.content)

    browser.quit()
    return filePath

