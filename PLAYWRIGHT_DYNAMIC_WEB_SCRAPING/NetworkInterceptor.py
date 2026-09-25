import asyncio
import json

from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # --------------------------------
        # 1. Intercept API Response
        # --------------------------------
        async def handle_response(response):
            if "/api/products" in response.url:
                print("\nAPI Response Detected")
                print("URL:", response.url)
                print("Status:", response.status)

                try:
                    payload = await response.json()

                    print("\nRaw API Payload:")
                    print(json.dumps(payload, indent=4))

                except Exception as error:
                    print("Could not read JSON:", error)

        page.on("response", handle_response)

        # --------------------------------
        # 2. Mock API Response
        # --------------------------------
        async def api_route(route):
            payload = {
                "products": [
                    {
                        "id": 1,
                        "name": "Laptop",
                        "price": 120000
                    },
                    {
                        "id": 2,
                        "name": "Keyboard",
                        "price": 5000
                    },
                    {
                        "id": 3,
                        "name": "Mouse",
                        "price": 2500
                    }
                ]
            }

            await route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(payload)
            )

        # IMPORTANT:
        # Register route BEFORE page JavaScript runs.
        await page.route("**/api/products", api_route)

        # --------------------------------
        # 3. Create Dynamic Webpage
        # --------------------------------
        await page.set_content(
            """
            <!DOCTYPE html>

            <html>
            <head>
                <base href="http://demo.local/">
                <title>API Interception Demo</title>
            </head>

            <body>

                <h1>Products</h1>

                <div id="products"></div>

                <script>
                    async function loadProducts() {
                        const response =
                            await fetch("/api/products");

                        const data =
                            await response.json();

                        const container =
                            document.getElementById("products");

                        data.products.forEach(product => {
                            const item =
                                document.createElement("p");

                            item.textContent =
                                product.name +
                                " - " +
                                product.price;

                            container.appendChild(item);
                        });
                    }

                    loadProducts();
                </script>

            </body>
            </html>
            """
        )

        # --------------------------------
        # 4. Wait for Rendered Data
        # --------------------------------
        await page.wait_for_selector("#products p")

        # --------------------------------
        # 5. Display Rendered DOM
        # --------------------------------
        print("\nRendered DOM:")

        print(
            await page.locator("#products").inner_text()
        )

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())