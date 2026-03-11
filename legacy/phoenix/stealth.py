import time
import random
from config import TYPE_DELAY_MIN, TYPE_DELAY_MAX, CLICK_DELAY_MIN, CLICK_DELAY_MAX

class StealthOps:
    @staticmethod
    def human_type(page, selector, text):
        try:
            page.focus(selector)
            for char in text:
                page.keyboard.type(char)
                time.sleep(random.uniform(TYPE_DELAY_MIN, TYPE_DELAY_MAX))
        except Exception as e:
            print(f"[StealthOps] Typing failure on {selector}: {e}")

    @staticmethod
    def human_click(page, selector):
        try:
            page.hover(selector)
            time.sleep(random.uniform(CLICK_DELAY_MIN, CLICK_DELAY_MAX))
            page.click(selector)
        except Exception as e:
            print(f"[StealthOps] Click failure on {selector}: {e}")

    @staticmethod
    def scroll_to_bottom(page, speed_factor=1.0):
        try:
            current_y = 0
            total_height = page.evaluate("document.body.scrollHeight")
            while current_y < total_height:
                scroll_step = random.randint(300, 700)
                current_y += scroll_step
                page.mouse.wheel(0, scroll_step)
                total_height = page.evaluate("document.body.scrollHeight")
                time.sleep(random.uniform(0.1, 0.4) / speed_factor)
        except Exception as e:
            print(f"[StealthOps] Scroll failure: {e}")
