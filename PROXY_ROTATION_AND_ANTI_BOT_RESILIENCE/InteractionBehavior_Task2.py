import random
import time

from playwright.sync_api import sync_playwright


class HumanLikeInteraction:

    def __init__(self):
        self.min_delay = 0.8
        self.max_delay = 2.5

    def delay_jitter(self):
        """Wait for a randomized amount of time."""
        delay = random.uniform(
            self.min_delay,
            self.max_delay
        )

        print(f"Delay: {delay:.2f} seconds")
        time.sleep(delay)

    def move_mouse(self, page, start_x, start_y, end_x, end_y):
        """Move mouse through multiple intermediate points."""

        steps = random.randint(8, 15)

        print(f"Mouse movement steps: {steps}")

        for step in range(1, steps + 1):

            progress = step / steps

            current_x = (
                start_x
                + (end_x - start_x) * progress
            )

            current_y = (
                start_y
                + (end_y - start_y) * progress
            )

            # Small random variation
            current_x += random.uniform(-3, 3)
            current_y += random.uniform(-3, 3)

            page.mouse.move(
                current_x,
                current_y
            )

            time.sleep(
                random.uniform(0.02, 0.08)
            )

    def run(self):

        with sync_playwright() as p:

            print("Launching Chromium...")

            browser = p.chromium.launch(
                headless=False
            )

            page = browser.new_page()

            print("Opening website...")

            page.goto("https://example.com")

            print("Page loaded.")

            self.delay_jitter()

            print("Starting mouse movement...")

            self.move_mouse(
                page,
                100,
                100,
                600,
                400
            )

            print("Mouse movement completed.")

            self.delay_jitter()

            print("Task 2 completed.")

            browser.close()


if __name__ == "__main__":

    interaction = HumanLikeInteraction()

    interaction.run()