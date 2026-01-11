from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List
import utils
import uuid

app = FastAPI()

class EditOrder(BaseModel):
    start: float
    end: float
    audio_url: str
    speed_factor: float

class DubbingJob(BaseModel):
    video_url: str
    edits: List[EditOrder]

@app.post("/render")
async def create_render(job: DubbingJob, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    # تشغيل المهمة في الخلفية حتى لا يتوقف المتصفح
    background_tasks.add_task(utils.process_video_dubbing, job, job_id)
    return {"status": "started", "job_id": job_id, "message": "المعالجة بدأت في الخلفية"}

@app.get("/status/{job_id}")
async def check_status(job_id: str):
    # هنا يمكنك إضافة منطق للتأكد من انتهاء الملف
    return {"message": "هذه الميزة تتطلب قاعدة بيانات بسيطة لتتبع الحالة"}
