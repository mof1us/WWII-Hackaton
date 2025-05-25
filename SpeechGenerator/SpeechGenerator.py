import requests
from speechkit import Session, SpeechSynthesis
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

class SpeechGenerator:
    def __init__(self, speech_text: str, sex: int):
        self.speech_text = speech_text
        self.speaker_voice = "jane" if sex == 1  else "ermil"
        self.logger = logging.getLogger("SpeechGenerationMain")
        self.oauth_session = Session.from_yandex_passport_oauth_token(os.getenv("YANDEX_OATH_TOKEN"),
                                                                      os.getenv("YANDEX_CATALOG_ID"))
        if os.getenv("YANDEX_OATH_TOKEN") is None or os.getenv("YANDEX_CATALOG_ID") is None:
            self.logger.warning("check .env file setup")
        self.synthesizeAudio = SpeechSynthesis(self.oauth_session)
        self.logger.info("End of setupping Speech gen")

        self.result_voice: bytes = None

    def generate_voice(self) -> bytes:
        if self.result_voice:
            return self.result_voice
        self.result_voice = self.synthesizeAudio.synthesize_stream(
            text=self.speech_text,
            voice=self.speaker_voice, format='oggopus', sampleRateHertz='16000'
        )
        return self.result_voice


if __name__ == "__main__":
    test = SpeechGenerator('''Дорогая Мария! Пишу из госпиталя под Смоленском. Осколок снаряда задел плечо, но врач говорит – жить буду. В бою за деревню мы отбили три атаки, танки горели, земля дрожала. Рука слаба, но врач сулит силу скоро. Держусь мыслью о встрече. Обнимаю. Иван.''', sex=0)
    with open("voice.mp3", "wb") as f:
        f.write(test.generate_voice())
