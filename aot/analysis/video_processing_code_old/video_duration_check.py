import os
import aot
import yaml
from pathlib import Path
import ffmpeg


video_path = "/tank/shared/2024/visual/AOT/derivatives/stimuli/rescaled_final"

#check whether all videos are 2.5 seconds long
invalide_videos = []
for video in os.listdir(video_path):
    if video.endswith(".mp4"):
        video_file = os.path.join(video_path, video)
        video_duration = round(float(ffmpeg.probe(video_file)['format']['duration']), 1)
        if video_duration != 2.5:
            print("invalid video")
            print(video, video_duration)
            invalide_videos.append(video)

print(invalide_videos)


