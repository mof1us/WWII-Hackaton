import asyncio
import base64

import uvicorn
from fastapi import FastAPI, Body
from starlette.requests import Request
from starlette.responses import FileResponse, HTMLResponse, PlainTextResponse, JSONResponse
from starlette.templating import Jinja2Templates

from FastApiApplication.LetterProcess import LetterProcess
from TextGenerator.TextGenerator import TextGenerator


class Application:
    def __init__(self):
        self.app = FastAPI()
        self.setup_routing()
        self.running_processes: dict[int, LetterProcess] = {}
        self.text_analizer = TextGenerator()


    async def add_new_letter(self, data=Body()) -> JSONResponse:
        # body format: {“letter”: “Текст введённого пользователем письма”}
        if self.running_processes.keys():
            user_id = max(self.running_processes.keys()) + 1
        else:
            user_id = 0
        current_process = LetterProcess(data['letter'], user_id, self.text_analizer)
        self.running_processes[user_id] = current_process
        await current_process.start_text_scenes_generation()

        return JSONResponse({
            "status_code": 0,
            "user_id": user_id,
        })

    async def get_text_generation_result(self, user_id: int) -> JSONResponse:
        # body format: {"user_id": 0}
        if user_id not in self.running_processes:
            return JSONResponse({
                "status_code": -2,
                "message": "generation prcess not finded"
            })

        result = await self.running_processes[user_id].get_text_generation_result()
        if result:
            return JSONResponse({
                "status_code": 0,
                "result": result
            })
        else:
            return JSONResponse({
                "status_code": 1,
                "message": "text generation in process"
            })

    async def init_img_generation(self, data=Body()) -> JSONResponse:
        # body format: {"user_id": 0}
        if "user_id" not in data:
            return JSONResponse(
                {"status_code": -1,
                 "message": "wrong body"}
            )
        if data["user_id"] not in self.running_processes:
            return JSONResponse({
                JSONResponse(
                    {"status_code": -2,
                     "message": "generation prcess not finded"}
                )
            })

        user_id = data["user_id"]
        await self.running_processes[user_id].start_image_generation()
        return JSONResponse({
            "status_code": 0
        })

    async def get_images(self, user_id: int) -> JSONResponse:
        if user_id not in self.running_processes:
            return JSONResponse({
                JSONResponse(
                    {"status_code": -2,
                     "message": "generation prcess not finded"}
                )
            })
        images = await self.running_processes[user_id].get_images_base_64()
        if images:
            return JSONResponse({
                "status_code": 0,
                "images": images
            })
        else:
            return JSONResponse({
                "status_code": 1,
                "message": "images in generation process"
            })

    async def get_voice(self, user_id: int) -> JSONResponse:
        if user_id not in self.running_processes:
            return  JSONResponse(
                    {"status_code": -2,
                     "message": "generation prcess not finded"}
                )
        voice_bin = await self.running_processes[user_id].get_speech()
        return JSONResponse({
            "status_code": 0,
            "voice": base64.b64encode(voice_bin).decode("ascii")
        })

    async def start_animation_generation(self, data=Body()) -> JSONResponse:
        if "user_id" not in data:
            return JSONResponse(
                {"status_code": -1,
                 "message": "wrong body"}
            )
        if data["user_id"] not in self.running_processes:
            return JSONResponse({
                "status_code": -2,
                "message": "generation prcess not finded"
            })
        user_id = data["user_id"]
        await self.running_processes[user_id].start_animation_generation()
        return JSONResponse({
            "status_code": 0
        })

    async def get_animation_result(self, user_id: int) -> JSONResponse:
        if user_id not in self.running_processes:
            return JSONResponse({
                "status_code": -2,
                "message": "generation prcess not finded"
            })
        result_videos = await self.running_processes[user_id].get_animation_result()
        if result_videos is None:
            return JSONResponse({
                "status_code": 1,
                "message": "animation generation in process"
            })
        return JSONResponse({
            "status_code": 0,
            "result_videos": [base64.b64encode(video).decode("ascii") for video in result_videos]
        })

    async def start_video_montage(self, data=Body()) -> JSONResponse:
        if "user_id" not in data:
            return JSONResponse(
                {"status_code": -1,
                 "message": "wrong body"}
            )
        if data["user_id"] not in self.running_processes:
            return JSONResponse({
                "status_code": -2,
                "message": "generation prcess not finded"
            })
        user_id = data["user_id"]
        await self.running_processes[user_id].start_video_montage()
        return JSONResponse({
            "status_code": 0
        })

    async def get_montage_result(self, user_id: int) -> JSONResponse:
        if user_id not in self.running_processes:
            return JSONResponse({
                "status_code": -2,
                "message": "generation prcess not finded"
            })
        video_binary = await self.running_processes[user_id].get_montage_video()
        if video_binary is None:
            return JSONResponse({
                "status_code": 1,
                "message": "video montage in process"
            })
        return JSONResponse({
            "status_code": 0,
            "video": base64.b64encode(video_binary).decode("ascii")
        })

    def setup_routing(self):
        self.app.add_api_route(
            f"/api/init_text_generation",
            methods=["POST"],
            endpoint=self.add_new_letter,
            response_class=JSONResponse,
            name=f"get_main"
        )

        self.app.add_api_route(
            f"/api/init_img_generation",
            methods=["POST"],
            endpoint=self.init_img_generation,
            response_class=JSONResponse,
            name=f"start_img_gen"
        )
        self.app.add_api_route(
            f"/api/get_images",
            methods=["GET"],
            endpoint=self.get_images,
            response_class=JSONResponse,
            name=f"start_img_gen"
        )
        self.app.add_api_route(
            f"/api/get_voice",
            methods=["GET"],
            endpoint=self.get_voice,
            response_class=JSONResponse,
            name=f"get_voice"
        )
        self.app.add_api_route(
            f"/api/get_text_generation_result",
            methods=["GET"],
            endpoint=self.get_text_generation_result,
            response_class=JSONResponse,
            name=f"get_text_gen_result"
        )
        self.app.add_api_route(
            f"/api/start_animation_generation",
            methods=["POST"],
            endpoint=self.start_animation_generation,
            response_class=JSONResponse,
            name=f"start_animation_gen"
        )
        self.app.add_api_route(
            f"/api/get_animation_result",
            methods=["GET"],
            endpoint=self.get_animation_result,
            response_class=JSONResponse,
            name=f"get_animation_result"
        )
        self.app.add_api_route(
            f"/api/start_video_montage",
            methods=["POST"],
            endpoint=self.start_video_montage,
            response_class=JSONResponse,
            name=f"start_video_montage"
        )
        self.app.add_api_route(
            f"/api/get_montage_result",
            methods=["GET"],
            endpoint=self.get_montage_result,
            response_class=JSONResponse,
            name=f"get_montage_result"
        )




