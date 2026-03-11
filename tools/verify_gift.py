import os, sys, json, time
from stealth_browser import create_stealth_browser, HumanTyping

ID_FILE = 'E:/0x/tools/identities.json'
SCREENSHOT_DIR = 'E:/0x/screenshots'
if not os.path.exists(SCREENSHOT_DIR): os.makedirs(SCREENSHOT_DIR)

def verify_gift():
    print('[G-PRIME] Verifying Gift: Google Account & Git Repo...')
    try:
        with open(ID_FILE, 'r') as f:
            ids = json.load(f)
        creds = ids['primary']
        
        with create_stealth_browser(session_name='racheljosh_github', headless=True) as browser:
            page = browser.new_page()

            # 1. Check GitHub
            print('[G-PRIME] Checking GitHub...')
            page.goto('https://github.com/', timeout=60000)
            time.sleep(5)
            page.screenshot(path=f'{SCREENSHOT_DIR}/github_home.png')
            
            if 'login' in page.url:
                print('[X] GitHub Session Expired or Not Found.')
            else:
                print('[+] GitHub Session ACTIVE.')
                page.goto('https://github.com/racheljoshs?tab=repositories')
                time.sleep(3)
                page.screenshot(path=f'{SCREENSHOT_DIR}/github_repos.png')
                # Look for G-SWARM-C2
                if 'G-SWARM-C2' in page.content():
                    print('[+] G-SWARM-C2 Repo Found.')
                else:
                    print('[!] G-SWARM-C2 Repo NOT Found. It may need to be created.')

            # 2. Check Gmail
            print('[G-PRIME] Checking Gmail...')
            page.goto('https://mail.google.com/mail/u/0/#inbox', timeout=60000)
            time.sleep(5)
            page.screenshot(path=f'{SCREENSHOT_DIR}/gmail_inbox.png')
            
            if 'signin' in page.url:
                print('[X] Gmail Session Expired or Not Found.')
            else:
                print('[+] Gmail Session ACTIVE.')

    except Exception as e:
        print(f'[ERROR] Verification failed: {e}')

if __name__ == '__main__':
    verify_gift()
