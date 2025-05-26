import asyncio
import base64
import os
import time
from collections.abc import Coroutine
import asyncio

import aiohttp
from runwayml import RunwayML
from dotenv import load_dotenv

load_dotenv()

def bytes_to_datauri(bin_data: bytes, mime="image/png") -> str:
    if len(bin_data) > 3_300_000:         # ~3.3 MB ≈ 5 MB в base64
        raise ValueError("Слишком большой файл для data-URI")
    b64 = base64.b64encode(bin_data).decode()
    return f"data:{mime};base64,{b64}"

class ImageAnimator:
    def __init__(self, images_for_generation: list[bytes]):
        self.client = RunwayML()
        self.images_for_generation: list[bytes] = images_for_generation

        self.tasks: list[id] = ["1a346514-a312-4cc5-8763-3a0b26ae6cf9"]
        self.result_videos: list[bytes] = []


    async def start_tasks(self):
        for image in self.images_for_generation:
            asyncio.create_task(self.start_generation_task(bytes_to_datauri(image)))


    async def get_result_videos(self) -> list[bytes] | None:
        # print(self.tasks)
        # for task_id in self.tasks:
        #     task = self.client.tasks.retrieve(task_id)
        #     print(task.status)
        #     if task.status not in ("SUCCEEDED", "FAILED"):
        #         return None
        #     video_url = task.output[0]
        #     async with aiohttp.ClientSession() as session:
        #         async with session.get(video_url) as resp:
        #             video_bytes = await resp.read()
        #     self.result_videos.append(video_bytes)
        #  TODO Потом раскоментировать
        if self.result_videos:
            return self.result_videos
        else:
            for i in range(5):
                self.result_videos.append(open("tmp.mp4", "rb").read())
            return self.result_videos


    async def start_generation_task(self, image: str):
        # task = self.client.image_to_video.create(
        #     model='gen3a_turbo',
        #     # Point this at your own image file
        #     prompt_image=image,
        #     prompt_text='Generate a video',
        #     ratio='1280:768',
        #     duration=5,
        # )
        # self.tasks.append(task.id)
        # print('Task started:', task.id)
        pass


async def main():
    img_list = [open("img.png", "rb").read(), open("img.png", "rb").read(), open("img.png", "rb").read(), open("img.png", "rb").read(), open("img.png", "rb").read()]
    animator = ImageAnimator(img_list)
    await animator.start_tasks()

if __name__ == "__main__":
    asyncio.run(main())
