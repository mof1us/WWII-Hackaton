import asyncio
import os
import tempfile
import time

from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips


class MovieMaker:
    def __init__(self, video_files: list[bytes], audio_file: bytes):
        self.final = None
        self.video_files: list[bytes] = video_files
        self.transition_duration = 2
        self.result_video: bytes = None
        self.audio_file = audio_file

    async def start_generation(self):
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            temp_file.write(self.video_files[0])
            base_video = VideoFileClip(temp_file.name)
        target_size = base_video.size
        target_fps = 24
        clips = []
        for path in self.video_files:
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
                temp_file.write(path)
                video_clip = VideoFileClip(temp_file.name)
                if video_clip.size != target_size:
                    video_clip = video_clip.resized(target_size)
                if video_clip.fps != target_fps:
                    video_clip = video_clip.with_fps(target_fps)
                clips.append(video_clip)

        self.final = concatenate_videoclips(
            clips,
            method="compose",
            padding=-self.transition_duration,
        )
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as audio_temp:
            audio_temp.write(self.audio_file)
            audio_temp.flush()
            audio_clip = AudioFileClip(audio_temp.name)
            self.final = self.final.with_audio(audio_clip)

    async def get_video_binary(self) -> bytes | None:
        if self.result_video is None:
            return None
        return self.result_video

    def generate_video(self):
        if self.final is None:
            raise ValueError("Video generation has not been started yet.")
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            self.final.write_videofile(temp_file.name, codec="libx264", audio_codec="aac")
            temp_file.seek(0)
            video_binary = temp_file.read()
        self.result_video = video_binary

    async def save_video_to_file(self):
        print(f"count of threads: {os.cpu_count()}")
        self.final.write_videofile(
            "final.mp4",
            fps=24,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            threads=os.cpu_count(),
        )


async def main():
    files = [open("test3.mp4", "rb").read(), open("test2.mp4", "rb").read(), open("test1.mp4", "rb").read()]
    audio = open("voice.mp3", "rb").read()
    maker = MovieMaker(files, audio)
    await maker.start_generation()
    asyncio.create_task(asyncio.to_thread(maker.generate_video))
    for i in range(100):
        if await maker.get_video_binary():
            print("Video generation completed")
            break
        else:
            print("in progress")
        await asyncio.sleep(5)
    await maker.save_video_to_file()

if __name__ == "__main__":
    asyncio.run(main())
