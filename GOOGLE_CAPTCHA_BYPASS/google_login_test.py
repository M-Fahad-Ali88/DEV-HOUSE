import asyncio
import os
import re
import sys
import io
from urllib.parse import urlparse, parse_qs

import aiohttp
import cv2
import numpy as np
import pytesseract
from PIL import Image
from playwright.async_api import async_playwright
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception
from dotenv import load_dotenv

# --- UNCOMMENT THE LINE BELOW IF TESSERACT IS NOT IN YOUR PATH ---
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

load_dotenv()

EMAIL = os.getenv("GOOGLE_EMAIL")
PASSWORD = os.getenv("GOOGLE_PASSWORD")
TWO_CAPTCHA_API_KEY = os.getenv("TWO_CAPTCHA_API_KEY")
DEMO_MODE = False   # Set to True to test on reCAPTCHA demo page

# -------------------- STEALTH (optional) --------------------
try:
    from playwright_stealth import stealth
    HAS_STEALTH = True
except (ImportError, TypeError):
    try:
        from playwright_stealth import Stealth
        stealth = Stealth()
        HAS_STEALTH = True
    except ImportError:
        HAS_STEALTH = False

async def apply_stealth(page):
    if HAS_STEALTH:
        try:
            if isinstance(stealth, Stealth):
                await stealth.apply_stealth(page)
            else:
                await stealth(page)
        except Exception:
            pass

class CaptchaDetected(Exception):
    pass

# -------------------- IMPROVED OCR SOLVER --------------------
async def solve_image_captcha(page):
    print("🔍 Attempting to solve image CAPTCHA using OCR...")
    try:
        await page.wait_for_selector("iframe[src*='recaptcha']", timeout=15000)
        print("✅ Found reCAPTCHA iframe.")

        # Try multiple selectors for the image
        img_element = None
        selectors = [
            "iframe[src*='recaptcha'] >> img.rc-image",
            "iframe[src*='recaptcha'] >> img[role='img']",
            "iframe[src*='recaptcha'] >> img#captcha-image",
            "iframe[src*='recaptcha'] >> img[alt*='captcha']",
            "iframe[src*='recaptcha'] >> img"
        ]
        for sel in selectors:
            temp = page.locator(sel)
            count = await temp.count()
            print(f"Selector '{sel}' count: {count}")
            if count > 0:
                img_element = temp
                print(f"✅ Found image using selector: {sel}")
                break
        if img_element is None:
            raise Exception("Could not find any CAPTCHA image element.")

        # Screenshot and save
        img_bytes = await img_element.screenshot(type="png")
        img = Image.open(io.BytesIO(img_bytes))
        img.save('captcha_debug.png')
        print("📸 Screenshot saved as 'captcha_debug.png'.")

        # Preprocess
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        # Try Otsu and adaptive; pick the one with more white pixels
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        if np.mean(otsu) > np.mean(adaptive):
            thresh = otsu
            print("Using Otsu threshold.")
        else:
            thresh = adaptive
            print("Using adaptive threshold.")

        # Invert if needed (text light on dark)
        if np.mean(thresh) < 128:
            thresh = cv2.bitwise_not(thresh)
            print("Inverted image.")

        thresh = cv2.medianBlur(thresh, 3)
        kernel = np.ones((1, 1), np.uint8)
        thresh = cv2.dilate(thresh, kernel, iterations=1)
        thresh = cv2.erode(thresh, kernel, iterations=1)

        # Try multiple OCR configs
        texts = []
        configs = [
            r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
            r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
            r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
            '--oem 3 --psm 8',
            '--oem 3 --psm 7'
        ]
        for cfg in configs:
            t = pytesseract.image_to_string(thresh, config=cfg).strip()
            if t:
                texts.append(t)
                print(f"OCR with config '{cfg}': '{t}'")
        if not texts:
            raise Exception("No OCR result.")

        # Choose longest (most likely correct)
        text = max(texts, key=len)
        print(f"📝 Best OCR result: '{text}'")

        # Locate input field inside the iframe using frame_locator
        captcha_frame = page.frame_locator("iframe[src*='recaptcha']")
        input_box = None
        input_selectors = [
            "input[id='captcha-input']",
            "input[type='text']",
            "input[aria-label='Type the text you see']",
            "input[placeholder='Type the text']"
        ]
        for sel in input_selectors:
            temp = captcha_frame.locator(sel)
            if await temp.count() > 0:
                input_box = temp
                print(f"✅ Found input using selector: {sel}")
                break
        if input_box is None:
            raise Exception("Could not find CAPTCHA input box.")

        await input_box.fill(text)
        print(f"✅ Filled CAPTCHA with: '{text}'")

        # Click verify button
        verify_selectors = [
            "button[type='submit']",
            "text=Verify",
            "text=Submit"
        ]
        verify_btn = None
        for sel in verify_selectors:
            temp = captcha_frame.locator(sel)
            if await temp.count() > 0:
                verify_btn = temp
                break
        if verify_btn:
            await verify_btn.click()
            await page.wait_for_timeout(2000)
            print("✅ Verify button clicked.")
        return True
    except Exception as e:
        print(f"❌ OCR solving failed: {e}")
        return False

# -------------------- 2CAPTCHA SOLVER (fallback) --------------------
async def solve_recaptcha_v2(sitekey: str, page_url: str) -> str:
    if TWO_CAPTCHA_API_KEY:
        async with aiohttp.ClientSession() as session:
            payload = {
                'key': TWO_CAPTCHA_API_KEY,
                'method': 'userrecaptcha',
                'googlekey': sitekey,
                'pageurl': page_url,
                'json': 1
            }
            async with session.post('http://2captcha.com/in.php', data=payload) as resp:
                result = await resp.json()
                if result.get('status') != 1:
                    raise Exception(f"2Captcha error: {result.get('request')}")
                captcha_id = result['request']
            for _ in range(30):
                await asyncio.sleep(2)
                async with session.get(
                    f'http://2captcha.com/res.php?key={TWO_CAPTCHA_API_KEY}&action=get&id={captcha_id}&json=1'
                ) as poll_resp:
                    poll_result = await poll_resp.json()
                    if poll_result.get('status') == 1:
                        return poll_result['request']
                    elif poll_result.get('request') == 'CAPCHA_NOT_READY':
                        continue
                    else:
                        raise Exception(f"2Captcha polling error: {poll_result.get('request')}")
            raise TimeoutError("2Captcha timed out.")
    else:
        return "MANUAL"

# -------------------- CAPTCHA HANDLER --------------------
async def handle_captcha(page):
    if await page.locator('text=Type the text you see').count() > 0 or \
       await page.locator('text=Type the text you hear').count() > 0:
        print("📌 CAPTCHA challenge detected.")
        if await page.locator('text=Type the text you see').count() > 0:
            success = await solve_image_captcha(page)
            if success:
                return True
        print("⏳ OCR failed or audio challenge. You have 60 seconds to solve manually in the browser.")
        await page.wait_for_timeout(60000)
        return True
    return False

# -------------------- LOGIN WITH RETRY --------------------
@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(8),
    retry=retry_if_exception(lambda e: isinstance(e, CaptchaDetected))
)
async def perform_login(page):
    if DEMO_MODE:
        # ---------- Test on reCAPTCHA demo page ----------
        print("🧪 Testing on reCAPTCHA demo page...")
        await page.goto("https://www.google.com/recaptcha/api2/demo")
        await page.wait_for_load_state("networkidle")

        # Click the checkbox inside the iframe to trigger the challenge
        checkbox_frame = page.frame_locator("iframe[src*='recaptcha']")
        checkbox = checkbox_frame.locator('.recaptcha-checkbox-border')
        if await checkbox.count() > 0:
            await checkbox.click()
            await page.wait_for_timeout(2000)
        else:
            anchor = checkbox_frame.locator('#recaptcha-anchor')
            if await anchor.count() > 0:
                await anchor.click()
                await page.wait_for_timeout(2000)

        # Wait for the challenge to appear
        await page.wait_for_selector("iframe[src*='recaptcha']:not([style*='display: none'])", timeout=10000)
        await page.wait_for_timeout(2000)

        # Extract sitekey (for 2Captcha fallback)
        sitekey = await page.locator('.g-recaptcha').get_attribute('data-sitekey')
        if not sitekey:
            iframe_src = await page.locator("iframe[src*='recaptcha']").get_attribute('src')
            if iframe_src:
                parsed = urlparse(iframe_src)
                params = parse_qs(parsed.query)
                sitekey = params.get('k', [None])[0]
        if not sitekey:
            raise Exception("Could not find sitekey on demo page")
        print(f"Demo sitekey: {sitekey}")

        token = await solve_recaptcha_v2(sitekey, page.url)
        if token != "MANUAL" and token.startswith("03"):
            await page.evaluate(f'document.getElementById("g-recaptcha-response").innerHTML="{token}";')
            await page.evaluate('if (typeof ___grecaptcha_cfg !== "undefined") { ___grecaptcha_cfg.clients[0].callback("' + token + '"); }')
            await page.click('input[type="submit"]')
        else:
            await handle_captcha(page)
            await page.click('input[type="submit"]')

        await page.wait_for_load_state("networkidle")
        if await page.locator('text=Success').count() > 0:
            print("✅ Demo CAPTCHA solved successfully!")
        else:
            raise CaptchaDetected("Demo CAPTCHA solving failed")
        return

    # ---------- Google Login ----------
    print("🔐 Starting Google login...")
    await page.goto("https://accounts.google.com/")
    await page.wait_for_load_state("networkidle")

    email_input = page.locator('input[type="email"]')
    await email_input.fill(EMAIL)
    await page.click('button:has-text("Next")')
    await page.wait_for_load_state("networkidle")

    password_input = page.locator('input[type="password"]')
    await password_input.fill(PASSWORD)
    await page.click('button:has-text("Next")')
    await page.wait_for_load_state("networkidle")

    await page.wait_for_timeout(3000)
    if await page.locator("iframe[src*='recaptcha']").count() > 0:
        print("🛡️ CAPTCHA iframe detected.")
        handled = await handle_captcha(page)
        if not handled:
            raise CaptchaDetected("CAPTCHA not solved")
        await page.click('button:has-text("Next")')
        await page.wait_for_load_state("networkidle")

    if await page.locator('a[href*="mail.google.com"]').count() > 0 or \
       await page.locator('[aria-label="Google Account"]').count() > 0:
        print("✅ Google login successful!")
    else:
        raise CaptchaDetected("Login failed – possible CAPTCHA loop, wrong credentials, or 2FA.")

# -------------------- MAIN --------------------
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        await apply_stealth(page)

        try:
            await asyncio.wait_for(perform_login(page), timeout=120)
        except asyncio.TimeoutError:
            print("⏰ Operation timed out.")
        except CaptchaDetected as e:
            print(f"❌ CAPTCHA error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        finally:
            input("Press Enter to close browser...")
            try:
                await browser.close()
            except:
                pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⏹️ Interrupted by user.")
        sys.exit(0)