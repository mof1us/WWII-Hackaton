import asyncio
import os
import tempfile

from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips


class MovieMaker:
    def __init__(self):
        self.final = None
        self.video_files: list[str] = []
        self.transition_duration = 2

    async def start_generation(self):
        base_video = VideoFileClip(self.video_files[0])
        target_size = base_video.size
        target_fps = 24
        clips = [
            VideoFileClip(path).resized(target_size).with_fps(target_fps)
            for path in self.video_files
        ]

        self.final = concatenate_videoclips(
            clips,
            method="compose",
            padding=-self.transition_duration,
        )

    async def get_video_binary(self) -> bytes:
        if self.final is None:
            raise ValueError("Video generation has not been started yet.")
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            self.final.write_videofile(temp_file.name, codec="libx264", audio_codec="aac")
            temp_file.seek(0)
            video_binary = temp_file.read()
        return video_binary

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
    maker = MovieMaker()
    await maker.start_generation()
    await maker.get_video_binary()

if __name__ == "__main__":
    asyncio.run(main())
