"""
under construction 
"""

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome

import os
import speech_recognition as sr
from time import sleep
from typing import Type

from pypasser.exceptions import IpBlock
from pypasser.utils import download_audio, convert_to_wav

class reCaptchaV2(object):
    """
    reCaptchaV2 bypass
    -----------------
    Solving reCaptcha V2 using speech to text
    
    Attributes
    ----------
    driver: webdriver
    
    play: bool
        default is True
    
    attempts: int
        default is 3 times

    Returns
    ----------
    bool: result of solver
    """
    def __new__(cls, *args, **kwargs) -> bool:
        instance = super(reCaptchaV2, cls).__new__(cls)
        instance.__init__(*args,**kwargs)

        remaining_attempts = instance.attempts
        file_path = None

        try:
            cls.__click_check_box__(instance.driver)

            if cls.__is_checked__(instance.driver):
                return True

            cls.__click_audio_button__(instance.driver)

            while remaining_attempts:
                remaining_attempts -= 1

                link = cls.__get_audio_link__(instance.driver, instance.play)
                file_path = convert_to_wav(download_audio(link))
                cls.__type_text__(instance.driver, cls.speech_to_text(file_path))
                os.remove(file_path)

                checked = cls.__is_checked__(instance.driver)
                if checked or not remaining_attempts:
                    return checked

        except Exception as e:
            if file_path:
                os.remove(file_path)

            if 'rc-doscaptcha-header' in instance.driver.page_source:
                raise IpBlock()
            else:
                raise e
        
    def __init__(self, driver: Type[Chrome], play: bool = True, attempts: int = 3):
        self.driver   = driver
        self.play     = play
        self.attempts = attempts
      
    def __click_check_box__(self):
        self.switch_to.frame(self.find_element(By.TAG_NAME, "iframe"))
        check_box = WebDriverWait(self, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#recaptcha-anchor"))
        )

        check_box.click()
        self.switch_to.default_content()
        
    def __click_audio_button__(self):
        self.switch_to.frame(self.find_elements(By.TAG_NAME, "iframe")[2])
        audio_btn = WebDriverWait(self, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#recaptcha-audio-button")
            )
        )

        audio_btn.click()
        self.switch_to.default_content()

    def __get_audio_link__(self, play):
        voice = self.find_elements(By.TAG_NAME, "iframe")[2]
        self.switch_to.frame(voice)
        download_btn = WebDriverWait(self, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".rc-audiochallenge-tdownload-link")
            )
        )

        link = download_btn.get_attribute('href')
        if play:
            play_button = WebDriverWait(self, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".rc-audiochallenge-play-button > button")
                )
            )

            play_button.click()
        return link
    
    def __type_text__(self, text):
        text_field = WebDriverWait(self, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#audio-response"))
        )

        text_field.send_keys(text , Keys.ENTER)
        self.switch_to.default_content()
        
    def __is_checked__(self):
        sleep(3)
        self.switch_to.frame(
            WebDriverWait(self, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'iframe[name^=a]')
                )
            )
        )

        try:
            self.find_element(By.CSS_SELECTOR, '.recaptcha-checkbox-checked')
            self.switch_to.default_content()
            return True
        except NoSuchElementException:
            self.switch_to.default_content()
            return False
        
    def speech_to_text(self) -> str:   
        r = sr.Recognizer()
        with sr.AudioFile(self) as source:
            audio = r.record(source)

        return r.recognize_sphinx(audio)
