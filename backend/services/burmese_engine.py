import asyncio
import os
try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None
try:
    import ollama
except ImportError:
    ollama = None

class PlaywrightRunner:
    def __init__(self):
        self.screenshots_dir = "screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)

    async def ask_ai_vision(self, image_path, question):
        print(f"🤖 AI is analyzing... ({question})")
        if not os.path.exists(image_path):
            return "Error: Screenshot image not found!"

        try:
            with open(image_path, "rb") as file:
                image_bytes = file.read()

            response = ollama.chat(
                model="llava",
                messages=[
                    {
                        "role": "user",
                        "content": question,
                        "images": [image_bytes],
                    }
                ],
            )
            return response["message"]["content"]
        except Exception as e:
            return f"AI Error: {e}"

    async def run_script(self, script: str):
        """
        Parses and runs the Burmese DSL script.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            lines = script.strip().split("\n")
            results = []

            for line in lines:
                if not line or line.startswith("#"):
                    continue
                
                parts = line.split(" ", 1)
                command = parts[0]
                content = parts[1] if len(parts) > 1 else ""

                if command == "ဖွင့်":
                    print(f"🌐 Opening: {content}")
                    await page.goto(content)
                elif command == "နှိပ်":
                    await page.wait_for_selector(content)
                    await page.click(content)
                    print(f"👆 Clicked: {content}")
                elif command == "ရိုက်ထည့်":
                    inputs = content.split(" ", 1)
                    if len(inputs) == 2:
                        await page.wait_for_selector(inputs[0])
                        await page.fill(inputs[0], inputs[1])
                elif command == "ကြည့်ပေးပါ":
                    screenshot_path = os.path.join(self.screenshots_dir, "latest.png")
                    await page.screenshot(path=screenshot_path)
                    ai_reply = await self.ask_ai_vision(screenshot_path, content)
                    results.append(ai_reply)
                elif command == "စောင့်":
                    await asyncio.sleep(int(content))
                elif command == "stop":
                    break
            
            await browser.close()
            return True, "\n".join(results) if results else "Executed successfully"

if __name__ == "__main__":
    # Test script
    script = """
    ဖွင့် https://www.google.com
    ကြည့်ပေးပါ What do you see?
    stop
    """
    runner = PlaywrightRunner()
    asyncio.run(runner.run_script(script))
