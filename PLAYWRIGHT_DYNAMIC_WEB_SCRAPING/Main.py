import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto("https://quotes.toscrape.com/js/", wait_until="networkidle")

        print("Page Title:", await page.title())

        previous_height = 0

        for _ in range(5):
            current_height = await page.evaluate(
                "document.body.scrollHeight"
            )

            if current_height == previous_height:
                break

            previous_height = current_height

            await page.evaluate(
                "window.scrollTo(0, document.body.scrollHeight)"
            )

            await page.wait_for_timeout(1000)

        print("\nDynamic content loaded.")

        quotes = page.locator(".quote")

        count = await quotes.count()

        print(f"\nQuotes Found: {count}")

        for i in range(count):
            quote = quotes.nth(i)

            text = await quote.locator(".text").inner_text()
            author = await quote.locator(".author").inner_text()

            print(f"{i + 1}. {text} — {author}")

        await page.set_content(
            """
            <custom-card></custom-card>

            <script>
                class CustomCard extends HTMLElement {
                    constructor() {
                        super();

                        const shadow = this.attachShadow({
                            mode: "open"
                        });

                        shadow.innerHTML = `
                            <div>
                                <h2>Shadow DOM Content</h2>
                                <button>Load Data</button>
                            </div>
                        `;
                    }
                }

                customElements.define("custom-card", CustomCard);
            </script>
            """
        )

        shadow_text = await page.locator(
            "custom-card"
        ).locator("h2").inner_text()

        print("\nShadow DOM:", shadow_text)

        button = page.locator(
            "custom-card"
        ).get_by_role("button", name="Load Data")

        await button.click()

        print("Shadow DOM button clicked.")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main()) 