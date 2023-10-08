import os
import re
import requests
from datetime import datetime
import logging as log

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def go_to_snap_save(download_url, browser):
    """Navigates to snapsave.app"""
    browser.get("https://snapsave.app")
    url = browser.find_element(value="url")
    url.send_keys(download_url)
    url.send_keys(Keys.RETURN)


def download_reel(download_url,from_user):
    """Downloads a video from one of the supported sites"""
    options = Options()
    options.enable_mobile
    options.add_argument('--no-sandbox')

    browser = webdriver.Remote(command_executor="http://127.0.0.1:4444/wd/hub",options=options)
    addon_id = webdriver.Firefox.install_addon(browser,os.path.dirname(os.path.realpath(__file__))+'/Ublock.xpi', temporary=True)
    video_url = get_video_url(download_url, browser)

    r = requests.get(video_url,timeout=240)
    file_path = '/app/downloads' + from_user + datetime.now().strftime("%d%m%Y%H%M%S") +  '.mp4'
    open(file_path,'wb').write(r.content)

    browser.quit()
    return file_path

def get_video_url(download_url, browser):
    try:
        if (re.search(r"(.*www.facebook\.com\/reel.*)|(.*fb.watch\/.*)", download_url)):
            go_to_snap_save(download_url, browser)
            FB_VIDEO_XPATH = "(//*[contains(@onClick,'showAd')])[1]"
            WebDriverWait(browser,120).until(EC.presence_of_element_located((By.XPATH,FB_VIDEO_XPATH)))
            video_url = browser.find_element(By.XPATH,FB_VIDEO_XPATH).get_attribute('href')
        elif(re.search(r".*9gag\.com\/gag\/.*",download_url)):
            browser.get(download_url)
            NEINGAG_VIDEO_XPATH = "//*[@type='video/mp4']"
            WebDriverWait(browser,120).until(EC.presence_of_element_located((By.XPATH,NEINGAG_VIDEO_XPATH)))
            video_url = browser.find_element(By.XPATH,NEINGAG_VIDEO_XPATH).get_attribute('src')
        else:
            go_to_snap_save(download_url, browser)
            TIKTOK_INSTA_VIDEO_XPATH = "//*[contains(@onClick,'showAd')]"
            WebDriverWait(browser,120).until(EC.presence_of_element_located((By.XPATH,TIKTOK_INSTA_VIDEO_XPATH)))
            video_url = browser.find_element(By.XPATH,TIKTOK_INSTA_VIDEO_XPATH).get_attribute('href')
    except Exception as e:
        log.error(e)
        browser.quit()

    return video_url

