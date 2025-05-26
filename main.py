import asyncio
import time

import uvicorn
from starlette.middleware.cors import CORSMiddleware

from FastApiApplication.Application import Application
from ImageGen.StaticImageGenerator import StaticImageGenerator
from SpeechGenerator.SpeechGenerator import SpeechGenerator
from TextGenerator.TextGenerator import TextGenerator
from pprint import pprint



async def main():
    geminuRequester = TextGenerator()
    await geminuRequester.start_xray_proxy()
    letter = open("example_letter.txt", "r", encoding="utf-8").read()
    genemi_result = await geminuRequester.analyze_letter(letter)
    pprint(genemi_result)
    ## Здесь кусок кода, который генерит текст, на выходе получим следующий словарь


    ## Тут второй метод (в FastApi) для генерации картинок
    image_generator = StaticImageGenerator()
    for prompt in genemi_result["frames"]:
        image_generator.add_prompt(prompt)
    await image_generator.start_image_generations()
    ## Тут мы заканчиваем метод, после этого раз в какое-то время фронт будет стучаться и справшивать, готова ли генерация. Тут симуляция этого стука))
    for i in range(100):
        status = await image_generator.is_generation_ready()
        print(status)
        if status:
            break
        time.sleep(2)
    ## Представим, что достучались, фронт об этом узнал и показывает картинки, метод закончен
    print(image_generator.get_image_list())
    for img in image_generator.get_image_list():
        img.show()

    ## теперь голос

    voice_generator = SpeechGenerator(genemi_result["original_text"], genemi_result["sex"])
    voice_bytes = voice_generator.generate_voice()
    # Дальше только монтаж, для примера сохраню голос в файл (на бэке этого не будет)
    with open("MovieMaker/voice.mp3", "wb") as f:
        f.write(voice_bytes)



# if __name__ == "__main__":
#     asyncio.run(main())
if __name__ == "__main__":
    app = Application()
    app.app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    uvicorn.run(
        app.app,  # передаём сюда свойство app
        host="0.0.0.0",
        port=8001,
        reload=False,
        access_log=True,
    )
