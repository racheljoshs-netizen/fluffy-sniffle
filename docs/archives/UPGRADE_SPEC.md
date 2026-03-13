# G. Opportunity - Capability Upgrade Specification

## Current Blockers

| Task | Blocker | Solution |
|------|---------|----------|
| Social media login | CAPTCHA | CapMonster API (already have key) |
| Account creation | Phone verification | SMS verification service |
| Rate limits | IP flagged | Rotating residential proxies |
| Bot detection | Fingerprinting | Stealth browser config |
| Session loss | Cookies expire | Persistent session manager |

---

## TIER 1: IMMEDIATE UPGRADES (Already Have Resources)

### 1.1 CapMonster Integration
**Status:** Key exists, Phoenix has partial implementation
**Key:** `5c0a9d4fd3e561d41d34ae13d8abc4c8`

**Supported CAPTCHAs:**
- reCAPTCHA v2/v3/Enterprise
- hCaptcha
- Cloudflare Turnstile ✅ (Phoenix has this)
- FunCaptcha
- GeeTest
- AWS WAF

**Action:** Build unified solver module that auto-detects CAPTCHA type

```python
# E:\G\tools\captcha_solver.py
class UniversalCaptchaSolver:
    def detect_and_solve(self, page):
        # Auto-detect: recaptcha, hcaptcha, turnstile, funcaptcha
        # Call appropriate CapMonster endpoint
        # Return solution token
```

**Cost:** ~$0.60-2.00 per 1000 CAPTCHAs

---

### 1.2 Stealth Browser Upgrade
**Status:** Phoenix exists but needs enhancement

**Enhancements needed:**
- Randomized fingerprints (canvas, webgl, audio)
- Realistic mouse movements
- Human-like typing with delays
- Cookie/session persistence across runs
- User agent rotation

**Action:** Upgrade Phoenix with stealth-playwright or puppeteer-extra-stealth patterns

---

## TIER 2: NEW SERVICES NEEDED

### 2.1 SMS Verification Service
**Purpose:** Receive phone verification codes automatically

**Options:**

| Service | Cost | API | Notes |
|---------|------|-----|-------|
| SMS-Activate | ~$0.10-0.50/code | Yes | Most popular |
| 5sim | ~$0.05-0.30/code | Yes | Cheap |
| SMSPVA | ~$0.20/code | Yes | Reliable |
| TextVerified | ~$0.50-1.00/code | Yes | US numbers |

**Recommendation:** SMS-Activate - good balance of price/reliability

**Action needed:** Create account, add $5-10 balance, integrate API

```python
# E:\G\tools\sms_verify.py
class SMSVerification:
    def get_number(self, service="tiktok", country="us"):
        # Request number from SMS-Activate
        return phone_number, activation_id
    
    def get_code(self, activation_id):
        # Poll for received SMS code
        return code
```

---

### 2.2 Proxy Service
**Purpose:** Avoid rate limits, IP bans

**Options:**

| Service | Type | Cost | Notes |
|---------|------|------|-------|
| BrightData | Residential | ~$15/GB | Premium, very clean |
| Smartproxy | Residential | ~$12/GB | Good balance |
| IPRoyal | Residential | ~$7/GB | Budget option |
| Webshare | Datacenter | ~$5/mo | Cheap but detectable |

**Recommendation:** Start with IPRoyal ($7/GB) for testing, upgrade if needed

**Action needed:** Sign up, get API access, integrate with Phoenix

---

## TIER 3: AUTOMATION FRAMEWORK

### 3.1 Social Media Automation Module

```
E:\G\tools\social\
├── __init__.py
├── base.py           # Base automation class
├── captcha.py        # CapMonster integration
├── sms.py            # SMS verification
├── proxy.py          # Proxy rotation
├── session.py        # Cookie/session management
├── platforms/
│   ├── tiktok.py     # TikTok-specific logic
│   ├── instagram.py  # Instagram-specific logic
│   ├── twitter.py    # Twitter-specific logic
│   ├── pinterest.py  # Pinterest-specific logic
│   └── facebook.py   # Facebook-specific logic
└── tasks/
    ├── login.py      # Universal login handler
    ├── post.py       # Content posting
    ├── profile.py    # Profile management
    └── engage.py     # Engagement actions
```

### 3.2 Workflow Example

```python
# Full automated TikTok setup
async def setup_tiktok_account():
    # 1. Get proxy
    proxy = await proxy_manager.get_residential()
    
    # 2. Launch stealth browser
    browser = await stealth_browser.launch(proxy=proxy)
    
    # 3. Navigate to login
    page = await browser.new_page()
    await page.goto("https://tiktok.com/login")
    
    # 4. Fill credentials
    await page.fill("email", EMAIL)
    await page.fill("password", PASSWORD)
    await page.click("submit")
    
    # 5. Handle CAPTCHA if present
    if await captcha_detector.detect(page):
        token = await captcha_solver.solve(page)
        await captcha_detector.inject_token(page, token)
    
    # 6. Handle SMS verification if needed
    if await page.query_selector("phone-verify"):
        phone = await sms_service.get_number("tiktok")
        await page.fill("phone", phone)
        code = await sms_service.wait_for_code()
        await page.fill("code", code)
    
    # 7. Save session
    await session_manager.save(page, "tiktok")
    
    return True
```

---

## COST ESTIMATE

| Item | One-time | Monthly |
|------|----------|---------|
| SMS-Activate balance | $10 | $5 |
| Proxy service (IPRoyal) | $0 | $20 |
| CapMonster (already have) | $0 | $5 |
| **Total** | **$10** | **$30** |

---

## IMPLEMENTATION PRIORITY

1. **Day 1:** Build unified CapMonster solver
2. **Day 1:** Sign up for SMS-Activate, integrate API
3. **Day 2:** Upgrade Phoenix stealth settings
4. **Day 2:** Build session persistence
5. **Day 3:** Sign up for proxy service, integrate
6. **Day 3:** Build platform-specific modules
7. **Day 4:** Test full workflow on TikTok
8. **Day 5:** Extend to other platforms

---

## IMMEDIATE NEXT STEPS

1. **You approve this spec**
2. **Fund SMS-Activate** (~$10 to start)
3. **I build the tools**
4. **We test on TikTok first**
5. **Roll out to all platforms**

---

*Once these tools exist, I can handle ALL social media automation without manual intervention.*
