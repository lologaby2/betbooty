from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
import requests
# استيراد مكتبة المونتاج
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, vfx

app = FastAPI()

# 1. حل مشكلة "Failed to fetch" - إضافة تصريح CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # يسمح لـ Google AI Studio بالوصول للبوت
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# نماذج البيانات لاستقبال الطلبات من AI Studio
class EditInstruction(BaseModel):
    start: float
    end: float
    audio_url: str
    speed_factor: float

class DubbingJob(BaseModel):
    video_url: str
    instructions: List[EditInstruction]

# --- الوظائف الأساسية ---

@app.get("/")
async def root():
    """نقطة فحص الاتصال (Bot Ping)"""
    return {
        "status": "online",
        "message": "MoviePy & FastAPI Server is running!",
        "capabilities": ["trim", "speed_sync", "audio_overlay", "dubbing"]
    }

def run_video_processing(job_id: str, video_url: str, instructions: List[EditInstruction]):
    """وحدة المعالجة الثقيلة (تعمل في الخلفية)"""
    try:
        # تحميل الفيديو الأصلي
        video_input_path = f"input_{job_id}.mp4"
        with open(video_input_path, "wb") as f:
            f.write(requests.get(video_url).content)
        
        video = VideoFileClip(video_input_path)
        audio_clips = []

        for idx, ins in enumerate(instructions):
            # تحميل ملف الصوت العربي
            audio_tmp_path = f"audio_{job_id}_{idx}.mp3"
            with open(audio_tmp_path, "wb") as f:
                f.write(requests.get(ins.audio_url).content)
            
            # معالجة الصوت: ضبط وقت البدء
            new_audio = AudioFileClip(audio_tmp_path).set_start(ins.start)
            
            # ملاحظة: يمكنك هنا إضافة منطق vfx.speedx للفيديو إذا أردت تطويل المشهد
            audio_clips.append(new_audio)

        # دمج الأصوات فوق الفيديو (مع كتم الصوت الأصلي)
        final_audio = CompositeAudioClip(audio_clips)
        final_video = video.set_audio(final_audio)
        
        output_path = f"final_dubbed_{job_id}.mp4"
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
        
        print(f"Success: Video {job_id} is ready at {output_path}")
        # هنا يمكن إضافة كود لرفع النتيجة إلى سحابة أو إرسال إشعار
        
    except Exception as e:
        print(f"Error during processing: {str(e)}")

@app.post("/render")
async def start_dubbing(job: DubbingJob, background_tasks: BackgroundTasks):
    """استقبال طلب المونتاج وتشغيله في الخلفية"""
    job_id = str(uuid.uuid4())
    background_tasks.add_task(run_video_processing, job_id, job.video_url, job.instructions)
    
    return {
        "status": "processing",
        "job_id": job_id,
        "message": "بدأت عملية المونتاج، سيستغرق الأمر دقائق بناءً على حجم الفيديو"
    }
