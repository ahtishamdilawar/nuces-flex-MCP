import os
import re
import sys
import time
from typing import Optional

import httpx
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://flexstudent.nu.edu.pk"


def _log(msg: str):
    print(msg, file=sys.stderr)


def _find_chrome_binary() -> Optional[str]:
    """Find Chrome binary path on Windows."""
    if sys.platform != "win32":
        return None  # Let Selenium find it on other platforms
    
    # Common Chrome installation paths on Windows
    possible_paths = [
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            _log(f"Found Chrome at: {path}")
            return path
    
    return None


class FlexSession:
    
    def __init__(self):
        self.client: Optional[httpx.Client] = None
        self.cookies: dict = {}
        self.page_dumps: dict = {}
        self._logged_in = False
    
    def login(self) -> bool:
        roll_no = os.getenv("FLEX_ROLL_NO")
        password = os.getenv("FLEX_PASSWORD")
        
        if not roll_no or not password:
            raise ValueError("FLEX_ROLL_NO and FLEX_PASSWORD must be set in environment")
        
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option("useAutomationExtension", False)
        
        chrome_path = _find_chrome_binary()
        if chrome_path:
            options.binary_location = chrome_path
        
        os.environ['WDM_LOG_LEVEL'] = '0'
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        try:
            driver.get(f"{BASE_URL}/Login")
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "m_inputmask_4"))
            )
            
            username_field = driver.find_element(By.ID, "m_inputmask_4")
            password_field = driver.find_element(By.ID, "pass")
            
            username_field.clear()
            username_field.send_keys(roll_no)
            password_field.clear()
            password_field.send_keys(password)
            
            time.sleep(2)
            
            recaptcha_iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='recaptcha']"))
            )
            driver.switch_to.frame(recaptcha_iframe)
            
            checkbox = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".recaptcha-checkbox-border"))
            )
            checkbox.click()
            
            driver.switch_to.default_content()
            
            # Wait for CAPTCHA to be solved (either auto-pass or human solves image challenge)
            _log("Waiting for CAPTCHA to be solved...")
            _log("If an image challenge appears, please solve it manually.")
            
            captcha_timeout = 120  # 2 minutes for human to solve if needed
            captcha_solved = False
            start_time = time.time()
            
            while time.time() - start_time < captcha_timeout:
                try:
                    # Check if g-recaptcha-response has a value (means CAPTCHA is solved)
                    recaptcha_response = driver.execute_script(
                        "return document.getElementById('g-recaptcha-response')?.value || '';"
                    )
                    if recaptcha_response:
                        _log("CAPTCHA solved successfully!")
                        captcha_solved = True
                        break
                except Exception:
                    pass
                time.sleep(1)
            
            if not captcha_solved:
                raise Exception("CAPTCHA was not solved within the timeout period")
            
            sign_in_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "m_login_signin_submit"))
            )
            sign_in_button.click()
            
            WebDriverWait(driver, 30).until(
                lambda d: "/Login" not in d.current_url
            )
            
            page_source = driver.page_source
            dump_links = re.findall(r'href="(/[^"]*\?[^"]*dump=([^"&]+)[^"]*)"', page_source)
            
            for full_url, dump_value in dump_links:
                path = re.sub(r'\?.*', '', full_url)
                self.page_dumps[path] = dump_value
            
            dump_patterns = re.findall(r'(/[A-Za-z][^"\'?]*)\?[^"\']*dump=([^"\'&]+)', page_source)
            for path, dump_value in dump_patterns:
                if path not in self.page_dumps:
                    self.page_dumps[path] = dump_value
            
            selenium_cookies = driver.get_cookies()
            for cookie in selenium_cookies:
                self.cookies[cookie["name"]] = cookie["value"]
            
            self.client = httpx.Client(
                base_url=BASE_URL,
                cookies=self.cookies,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
                },
                follow_redirects=True,
                timeout=30.0
            )
            
            self._logged_in = True
            return True
            
        except Exception as e:
            _log(f"Login error: {e}")
            return False
        finally:
            driver.quit()
    
    def get(self, path: str) -> httpx.Response:
        if not self._logged_in or not self.client:
            raise RuntimeError("Not logged in. Call login() first.")
        return self.client.get(path)
    
    def get_html(self, path: str, append_dump: bool = True) -> str:
        if append_dump and "dump=" not in path:
            base_path = path.split("?")[0]
            dump_token = self.page_dumps.get(base_path)
            
            if dump_token:
                separator = "&" if "?" in path else "?"
                path = f"{path}{separator}dump={dump_token}"
        
        response = self.get(path)
        response.raise_for_status()
        return response.text
    
    def is_logged_in(self) -> bool:
        return self._logged_in
    
    def close(self):
        if self.client:
            self.client.close()


_session: Optional[FlexSession] = None

def get_session() -> FlexSession:
    global _session
    if _session is None:
        _session = FlexSession()
    return _session


def ensure_logged_in() -> FlexSession:
    session = get_session()
    if not session.is_logged_in():
        if not session.login():
            raise RuntimeError("Failed to login to FLEX portal")
    return session
