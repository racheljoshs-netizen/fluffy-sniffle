import asyncio
import edge_tts
import os

async def test_save():
    communicate = edge_tts.Communicate("Test message", "en-US-AndrewNeural")
    await communicate.save("E:/0x/test_edge.mp3")
    print(f"File exists: {os.path.exists('E:/0x/test_edge.mp3')}")

if __name__ == "__main__":
    asyncio.run(test_save())
