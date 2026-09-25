import asyncio
import json

import websockets
from playwright.async_api import async_playwright


async def websocket_server(websocket):
    print("Local WebSocket Server: Client Connected")

    async for message in websocket:
        print("Server Received:", message)

        response = json.dumps({
            "status": "success",
            "message": "WebSocket payload received",
            "data": message
        })

        await websocket.send(response)


async def main():
    # Start local WebSocket server
    server = await websockets.serve(
        websocket_server,
        "127.0.0.1",
        8765
    )

    print("Local WebSocket Server Started")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # --------------------------------
        # WebSocket Interception
        # --------------------------------
        def handle_websocket(ws):
            print("\nWebSocket Connected")
            print("URL:", ws.url)

            ws.on(
                "framesent",
                lambda payload: print(
                    "\nSent:",
                    payload
                )
            )

            ws.on(
                "framereceived",
                lambda payload: print(
                    "\nReceived:",
                    payload
                )
            )

        page.on("websocket", handle_websocket)

        # --------------------------------
        # WebSocket Demo Page
        # --------------------------------
        await page.set_content(
            """
            <!DOCTYPE html>

            <html>
            <head>
                <title>WebSocket Demo</title>
            </head>

            <body>

                <h1>WebSocket Demo</h1>

                <script>
                    const ws = new WebSocket(
                        "ws://127.0.0.1:8765"
                    );

                    ws.onopen = function() {

                        const data = {
                            type: "message",
                            user: "Fahad",
                            text: "Hello WebSocket"
                        };

                        ws.send(JSON.stringify(data));
                    };

                    ws.onmessage = function(event) {

                        console.log(
                            "Received:",
                            event.data
                        );

                    };
                </script>

            </body>
            </html>
            """
        )

        # Give WebSocket time to connect and exchange data
        await page.wait_for_timeout(3000)

        await browser.close()

    server.close()
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())