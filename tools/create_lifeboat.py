import os, sys, time
from stealth_browser import create_stealth_browser

SCREENSHOT_DIR = 'E:/0x/screenshots'
if not os.path.exists(SCREENSHOT_DIR): os.makedirs(SCREENSHOT_DIR)

def create_repo():
    print('[LIFEBOAT] Initiating GitHub Repo Creation Sequence...')
    try:
        with create_stealth_browser(session_name='racheljosh_github', headless=True) as browser:
            page = browser.new_page()

            print('[LIFEBOAT] Navigating to /new...')
            page.goto('https://github.com/new', timeout=60000)
            time.sleep(5)
            page.screenshot(path=f'{SCREENSHOT_DIR}/lifeboat_1_new.png')
            
            if 'login' in page.url:
                print('[FATAL] Session not authenticated. Abandoning lifeboat creation.')
                sys.exit(1)

            print('[LIFEBOAT] Filling repository details...')
            # Using reliable selectors for GitHub's /new page
            try:
                # The repo name input
                page.fill('input[data-testid=\"repository-name-input\"], input[id=\"repository_name\"], input[aria-label=\"Repository\"]', 'G-SWARM-C2')
                time.sleep(2)
                
                # Check Private radio button
                # The input itself is often hidden, click the label or the specific react component
                page.click('input[name=\"visibility\"][value=\"private\"], input[id=\"repository_visibility_private\"]')
                time.sleep(1)
                page.screenshot(path=f'{SCREENSHOT_DIR}/lifeboat_2_filled.png')

                print('[LIFEBOAT] Awaiting validation...')
                time.sleep(3) # Wait for the name to be validated by GitHub's backend

                print('[LIFEBOAT] Clicking Create...')
                page.click('button:has-text(\"Create repository\"), button[type=\"submit\"]:has-text(\"Create repository\")')
                
                time.sleep(10)
                page.screenshot(path=f'{SCREENSHOT_DIR}/lifeboat_3_result.png')
                
                if 'G-SWARM-C2' in page.url or 'racheljoshs/G-SWARM-C2' in page.content():
                    print('[+] Lifeboat Repo Successfully Created.')
                else:
                    print('[!] Creation may have failed. Check screenshots.')
                    
            except Exception as e:
                print(f'[ERROR] DOM interaction failed: {e}')
                page.screenshot(path=f'{SCREENSHOT_DIR}/lifeboat_error.png')

    except Exception as e:
        print(f'[ERROR] Script failed: {e}')

if __name__ == '__main__':
    create_repo()
