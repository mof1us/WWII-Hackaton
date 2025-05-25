import asyncio
import logging
from idlelib.window import add_windows_to_menu

from FastApiApplication.ProcessStatuses import ProcessStatuses
from ImageGen.StaticImageGenerator import StaticImageGenerator
from SpeechGenerator.SpeechGenerator import SpeechGenerator
from TextGenerator.TextGenerator import TextGenerator


class LetterProcess:
    def __init__(self, letter_text: str, user_id: int, text_gen: TextGenerator):
        self.logger = logging.getLogger(__name__)
        self.letter_text = letter_text
        self.user_id = user_id
        self.logger.info(f"Process for user {user_id} inited")
        self.status: ProcessStatuses = ProcessStatuses.LETTER_LOADED
        self.text_gen_result: dict = {}

        self.text_gen: TextGenerator = text_gen
        self.img_gen: StaticImageGenerator = StaticImageGenerator()
        self.anim_gen = None
        self.speech_gen: SpeechGenerator = None

    async def start_text_scenes_generation(self) -> None:
        asyncio.create_task(self.text_gen.analyze_letter(self.letter_text))
        self.status = ProcessStatuses.LETTER_PARSING_FOR_SCENES

    async def get_text_generation_result(self) -> dict | None:
        if not self.text_gen.text_generation_result:
            return None
        self.speech_gen = SpeechGenerator(self.text_gen.text_generation_result["original_text"], self.text_gen.text_generation_result["sex"])
        self.text_gen_result = self.text_gen.text_generation_result
        self.status = ProcessStatuses.LETTER_READY_FOR_IMAGE_GENERATING
        return self.text_gen.text_generation_result

    async def start_image_generation(self) -> None:
        for prompt in self.text_gen_result["frames"]:
            self.img_gen.add_prompt(prompt)
        await self.img_gen.start_image_generations()
        self.status = ProcessStatuses.LETTER_IN_IMAGE_GENERATION_PROCESS

    async def get_speech(self) -> bytes:
        return self.speech_gen.generate_voice()

    async def get_images_base_64(self) -> list[str] | None:
        is_ready = await self.img_gen.is_generation_ready()
        if is_ready:
            return self.img_gen.get_image_list_base_64()
        else:
            return None

