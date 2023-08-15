import glob
import os
import re
import time
import urllib.request

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def enterUrl(downloadUrl, browser):
    url = browser.find_element(value="url")
    url.send_keys(downloadUrl)
    url.send_keys(Keys.RETURN)



def downloadReel(downloadUrl):
    options = Options()
    options.enable_mobile
    downloadDir = "/home/seluser/Downloads/"
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", downloadDir)
    options.add_argument('--no-sandbox')

    browser = webdriver.Remote(command_executor="http://127.0.0.1:4444/wd/hub",options=options)
    addon_id = webdriver.Firefox.install_addon(browser,os.path.dirname(os.path.realpath(__file__))+'/Ublock.xpi', temporary=True)
    if(re.search(r".*9gag\.com\/gag\/.*",downloadUrl)):
        browser.get(downloadUrl)
        enterUrl(downloadUrl, browser)
        time.sleep(2)
        if(browser.find_element(By.XPATH,"//*[@class='notification is-warning']")):
            enterUrl(downloadUrl, browser)
        time.sleep(5)
    else:
        browser.get("https://snapsave.app")

    if (re.search(r"(.*www.facebook\.com\/reel.*)|(.*fb.watch\/.*)", downloadUrl)):
        # Removes giant ad div that remains empty and pushes download button out of view
        browser.execute_script(
            "document.getElementById(\"ad-slot\").remove();")
        time.sleep(1)
        WebDriverWait(browser, 1000000).until(EC.element_to_be_clickable(
            (By.XPATH, "//*[@class = 'table is-fullwidth']/tbody/tr[1]/td[3]/a"))).click()
    
    elif(re.search(r".*9gag\.com\/gag\/.*",downloadUrl)):
        videoUrl = browser.find_element(By.XPATH,"//*[@type=\"video/mp4\"]/@src")
        urllib.request.urlretrieve(videoUrl,'/home/seluser/Downloads/' + downloadUrl +'.mp4')
        time.sleep(5)
    else:
        # Removes giant ad div that remains empty and pushes download button out of view
        browser.execute_script(
            "document.getElementById(\"ad-slot\").remove();")
        try:
         # Changes the element height so that it is rendered into view   
            browser.execute_script(
                "document.getElementsByClassName(\"download-items__thumb video\")[0].style.height = \"100px\"")
        except Exception:
            pass
        time.sleep(1)
        WebDriverWait(browser, 1000000).until(EC.element_to_be_clickable(
            (By.XPATH, "//*[@title = 'Download Photo'] | //*[@title = 'Download Video']"))).click()

    # Prevent Firefox from closing if the download is taking too long.
    while (glob.glob(downloadDir + '/*.part')):
        time.sleep(1)
    browser.quit()

