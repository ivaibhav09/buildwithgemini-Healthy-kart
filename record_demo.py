import os
import glob
import time
import subprocess
import asyncio
import imageio_ffmpeg
from playwright.async_api import async_playwright

FRONTEND_URL = "http://localhost:8080"
RAW_VIDEO_DIR = "/tmp/demo_raw"
OUTPUT_MP4 = "/config/.gemini/antigravity/brain/445b9a7a-c7d0-4d53-abee-ebe49104f7b2/healthy_kart_demo.mp4"
LOFI_AUDIO = "/tmp/lofi_bg.mp3"


async def main():
    os.makedirs(RAW_VIDEO_DIR, exist_ok=True)
    
    # 1. Synthesize upbeat lo-fi audio track if not present
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    if not os.path.exists(LOFI_AUDIO):
        print("Synthesizing upbeat lo-fi audio track...")
        cmd_audio = [
            ffmpeg, "-y", "-f", "lavfi",
            "-i", "aevalsrc=0.1*sin(2*PI*261.63*t)+0.08*sin(2*PI*329.63*t)+0.08*sin(2*PI*392.00*t)+0.06*sin(2*PI*493.88*t):s=44100:d=60",
            "-af", "lowpass=f=1500,volume=0.5",
            LOFI_AUDIO
        ]
        subprocess.run(cmd_audio, check=True)

    print("Launching Playwright Chromium browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=RAW_VIDEO_DIR,
            record_video_size={"width": 1280, "height": 720}
        )
        page = await context.new_page()

        print(f"Navigating to Healthy-Kart UI: {FRONTEND_URL}")
        await page.goto(FRONTEND_URL, wait_until="networkidle")
        await asyncio.sleep(2)

        # -------------------------------------------------------------
        # Scene 1: First Prompt - Dairy-Free Recipe Recommendation
        # -------------------------------------------------------------
        print("Executing Scene 1: Dairy-Free Recipe Prompt...")
        prompt1 = "What dinner can I make with chicken, garlic, and spinach given my dairy allergy?"
        
        input_box = page.locator("#input")
        await input_box.fill(prompt1)
        await asyncio.sleep(1)
        
        form = page.locator("#form")
        await form.evaluate("form => form.dispatchEvent(new Event('submit', {cancelable: true, bubbles: true}))")
        
        # Wait for assistant response to stream in and display the structured A2UI recipe card
        print("Waiting for response to Scene 1...")
        await page.wait_for_selector(".msg-row.agent", timeout=45000)
        await asyncio.sleep(12)  # Pause to show off response & card UI

        # -------------------------------------------------------------
        # Scene 2: Richer Prompt - Image Generation & Nutrition Tool Call
        # -------------------------------------------------------------
        print("Executing Scene 2: Quinoa Bowl Image & Nutrition Prompt...")
        prompt2 = "Generate a photo and calculate nutrition breakdown for a healthy quinoa bowl."
        await input_box.fill(prompt2)
        await asyncio.sleep(1)
        await form.evaluate("form => form.dispatchEvent(new Event('submit', {cancelable: true, bubbles: true}))")

        print("Waiting for response to Scene 2...")
        # Wait until loading spinner disappears and assistant message completes
        await asyncio.sleep(25)  # Wait for image generation & python calculation

        # Scroll to bottom smoothly to highlight final output
        await page.evaluate("document.querySelector('#log').scrollTop = document.querySelector('#log').scrollHeight")
        await asyncio.sleep(5)

        print("Closing browser context to finalize video file...")
        await context.close()
        await browser.close()

    # Find recorded raw video
    video_files = glob.glob(os.path.join(RAW_VIDEO_DIR, "*.webm"))
    if not video_files:
        raise RuntimeError("No raw video recorded by Playwright.")
    
    # Sort by modification time to get latest
    video_files.sort(key=os.path.getmtime, reverse=True)
    raw_video = video_files[0]
    print(f"Recorded raw video: {raw_video}")

    # 2. Merge video with upbeat lo-fi audio track using FFmpeg
    print("Combining video with lo-fi background music track into MP4...")
    cmd_merge = [
        ffmpeg, "-y",
        "-i", raw_video,
        "-i", LOFI_AUDIO,
        "-c:v", "libx264",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        OUTPUT_MP4
    ]
    subprocess.run(cmd_merge, check=True)
    print(f"Demo video saved successfully to: {OUTPUT_MP4}")

if __name__ == "__main__":
    asyncio.run(main())
