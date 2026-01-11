import requests
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, vfx
import os

def process_video_dubbing(job, job_id):
    # 1. تحميل الفيديو الأصلي
    video_path = f"input_{job_id}.mp4"
    with open(video_path, "wb") as f:
        f.write(requests.get(job.video_url).content)
    
    video = VideoFileClip(video_path)
    audio_segments = []

    for edit in job.edits:
        # 2. تحميل الصوت العربي المولد من AI Studio
        audio_tmp = f"audio_{job_id}_{edit.start}.mp3"
        with open(audio_tmp, "wb") as f:
            f.write(requests.get(edit.audio_url).content)
        
        # 3. معالجة المزامنة: وضع الصوت في وقته وتعديل السرعة
        audio_clip = AudioFileClip(audio_tmp).set_start(edit.start)
        
        # تطبيق العمليات الرياضية لتناسب مدة الصوت مع الفيديو إذا لزم الأمر
        # هنا يتم وضع الصوت فوق الفيديو الأصلي
        audio_segments.append(audio_clip)

    # 4. الدمج النهائي (كتم صوت الفيديو الأصلي ووضع الدبلجة)
    final_audio = CompositeAudioClip(audio_segments)
    final_video = video.set_audio(final_audio)
    
    output_path = f"final_{job_id}.mp4"
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
    
    # تنظيف الملفات المؤقتة
    print(f"تم الانتهاء من العمل: {output_path}")
