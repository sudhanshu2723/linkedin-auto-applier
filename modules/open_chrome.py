'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

Support me: https://github.com/sponsors/GodsScion

version:    26.01.20.5.08
'''

from modules.helpers import get_default_temp_profile, make_directories
from config.settings import run_in_background, stealth_mode, disable_extensions, safe_mode, file_name, failed_file_name, logs_folder_path, generated_resume_path
from config.questions import default_resume_path
if stealth_mode:
    import undetected_chromedriver as uc
else: 
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    # from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from modules.helpers import find_default_profile_directory, critical_error_log, print_lg
from selenium.common.exceptions import SessionNotCreatedException

def createChromeSession(isRetry: bool = False):
    make_directories([file_name,failed_file_name,logs_folder_path+"/screenshots",default_resume_path,generated_resume_path+"/temp"])
    # Set up WebDriver with Chrome Profile
    options = uc.ChromeOptions() if stealth_mode else Options()
    if run_in_background:   options.add_argument("--headless")
    if disable_extensions:  options.add_argument("--disable-extensions")

    print_lg("IF YOU HAVE MORE THAN 10 TABS OPENED, PLEASE CLOSE OR BOOKMARK THEM! Or it's highly likely that application will just open browser and not do anything!")
    profile_dir = find_default_profile_directory()
    if isRetry:
        print_lg("Will login with a guest profile, browsing history will not be saved in the browser!")
    elif profile_dir and not safe_mode:
        options.add_argument(f"--user-data-dir={profile_dir}")
    else:
        print_lg("Logging in with a guest profile, Web history will not be saved!")
        options.add_argument(f"--user-data-dir={get_default_temp_profile()}")
    if stealth_mode:
        import os, glob, subprocess, re
        # Auto-detect Chrome version
        def get_chrome_version():
            try:
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                ]
                for path in chrome_paths:
                    if os.path.exists(path):
                        result = subprocess.run(['powershell', '-command', f'(Get-Item "{path}").VersionInfo.FileVersion'], capture_output=True, text=True)
                        match = re.search(r'(\d+)\.', result.stdout.strip())
                        if match:
                            return int(match.group(1))
            except:
                pass
            return None

        chrome_version = get_chrome_version()
        print_lg(f"Detected Chrome version: {chrome_version}")

        # Find a cached chromedriver to avoid re-downloading every run
        uc_cache = os.path.join(os.path.expanduser("~"), "appdata", "roaming", "undetected_chromedriver")
        cached = glob.glob(os.path.join(uc_cache, "*.exe"))
        common = [
            r"C:\Program Files\Google\Chrome\chromedriver-win64\chromedriver.exe",
            r"C:\Program Files (x86)\Google\Chrome\chromedriver-win64\chromedriver.exe",
        ]
        local_driver = next((p for p in common if os.path.exists(p)), None) or (cached[0] if cached else None)
        if local_driver:
            try:
                print_lg(f"Using cached ChromeDriver: {local_driver}")
                driver = uc.Chrome(driver_executable_path=local_driver, options=options)
            except Exception as e:
                print_lg(f"Cached driver failed ({type(e).__name__}), downloading...")
                fresh_options = uc.ChromeOptions()
                for arg in options.arguments:
                    fresh_options.add_argument(arg)
                if chrome_version:
                    driver = uc.Chrome(options=fresh_options, version_main=chrome_version)
                else:
                    driver = uc.Chrome(options=fresh_options)
        else:
            print_lg("Downloading Chrome Driver... This may take some time.")
            if chrome_version:
                driver = uc.Chrome(options=options, version_main=chrome_version)
            else:
                driver = uc.Chrome(options=options)
    else: driver = webdriver.Chrome(options=options) #, service=Service(executable_path="C:\\Program Files\\Google\\Chrome\\chromedriver-win64\\chromedriver.exe"))
    driver.maximize_window()
    wait = WebDriverWait(driver, 15)
    actions = ActionChains(driver)
    return options, driver, actions, wait

try:
    options, driver, actions, wait = None, None, None, None
    options, driver, actions, wait = createChromeSession()
except SessionNotCreatedException as e:
    critical_error_log("Failed to create Chrome Session, retrying with guest profile", e)
    options, driver, actions, wait = createChromeSession(True)
except Exception as e:
    msg = 'Seems like Google Chrome is out dated. Update browser and try again! \n\n\nIf issue persists, try Safe Mode. Set, safe_mode = True in config.py \n\nPlease check GitHub discussions/support for solutions https://github.com/GodsScion/Auto_job_applier_linkedIn \n                                   OR \nReach out in discord ( https://discord.gg/fFp7uUzWCY )'
    if isinstance(e,TimeoutError): msg = "Couldn't download Chrome-driver. Set stealth_mode = False in config!"
    print_lg(msg)
    critical_error_log("In Opening Chrome", e)
    print_lg("CRITICAL: Chrome failed to open. Exiting.")
    try: driver.quit()
    except (NameError, AttributeError): exit()
