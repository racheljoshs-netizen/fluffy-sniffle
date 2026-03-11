from core import PhoenixController
import time

def login_google():
    print("==========================================")
    print("   PHOENIX LOGIN: AUTONOMOUS")
    print("==========================================")
    
    phoenix = PhoenixController()
    phoenix.launch()
    
    email = "catboxxxr@gmail.com"
    passwords = ["Saqqara2006!", "!X32pz456?"]
    
    try:
        # 1. Nav
        if not phoenix.goto("https://accounts.google.com/signin"): return
        phoenix.wait_for_stable(2)

        # 2. Email
        print("[Google] Entering Email...")
        if not phoenix.smart_type("Email", email, ["input[type='email']"]):
             print("[Google] Email fail.")
             return
             
        phoenix.page.keyboard.press("Enter")
        phoenix.wait_for_stable(4) # Google animation

        # 3. Password Loop
        for i, password in enumerate(passwords):
            print(f"[Google] Password Try {i+1}...")
            
            # Check if we are on password screen
            if not phoenix.page.is_visible("input[type='password']"):
                print("[Google] Waiting for password field...")
                time.sleep(2)
            
            if not phoenix.smart_type("Password", password, ["input[type='password']", "input[name='password']"]):
                 continue

            phoenix.page.keyboard.press("Enter")
            phoenix.wait_for_stable(5)
            
            # 4. Success Check
            if "myaccount.google.com" in phoenix.page.url or phoenix.page.is_visible("a[href*='SignOut']"):
                print("[Google] LOGIN SUCCESSFUL.")
                # CRITICAL: Wait for cookie flush before closing
                print("[Google] Saving Session (Hold 10s)...")
                time.sleep(10)
                phoenix.close()
                print("[Google] Session Saved. Browser Closed.")
                return

            if phoenix.page.is_visible("text=Wrong password"):
                print("[Google] Wrong Pwd.")
                phoenix.page.keyboard.press("Control+A")
                phoenix.page.keyboard.press("Backspace")
                continue
            
            # Edge Case: Immediate 2FA (Even if user says none, Google might force it)
            if "challenge" in phoenix.page.url:
                print("[Google] 2FA Challenge Detected.")
                # We wait a bit to see if it auto-resolves (e.g. trusted dev)
                time.sleep(5)
                # If still there, we can't solve it autonomously without phone.
                # But we abide by "User does nothing". We'll just wait and see.
                
    except Exception as e:
        print(f"[Google] Error: {e}")
    finally:
        # Emergency cleanup if not closed
        if phoenix.active:
            print("[Google] Script ending. Closing browser.")
            phoenix.close()

if __name__ == "__main__":
    login_google()
