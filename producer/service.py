from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, Query, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
import uuid
import os
import time
from threading import Thread
from celery_app import celery_app

UPLOAD_FOLDER = '/files'
FILE_TIME_LIMIT = 24 * 60 * 60


def delete_old_files():
    current_time = time.time()
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(file_path):
            file_mtime = os.path.getmtime(file_path)
            if current_time - file_mtime > FILE_TIME_LIMIT:
                print(f"Deleting old file: {file_path}")
                os.remove(file_path)


def run_cleanup_scheduler(interval=3600):
    while True:
        delete_old_files()
        time.sleep(interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    cleanup_thread = Thread(target=run_cleanup_scheduler, daemon=True)
    cleanup_thread.start()
    yield


app = FastAPI(title="Producer Service", lifespan=lifespan)


@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No selected file")

    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return {"file_url": file_path}


@app.get("/get_file")
async def get_file(file_url: str = Query(...)):
    if not os.path.isfile(file_url):
        raise HTTPException(status_code=404, detail=f"File not found {file_url}")
    return FileResponse(file_url)


@app.post("/submit_task")
async def submit_task(task_data: dict):
    task_id = str(uuid.uuid4())
    task_data["task_id"] = task_id
    task_type = task_data.get("type", "default")

    try:
        celery_app.send_task(f"workers.{task_type}", args=[task_data], task_id=task_id)
        print(f"Task {task_id} added to Celery queue")
    except Exception as e:
        print(f"Error adding task to Celery queue: {e}")
        raise HTTPException(status_code=500, detail="Failed to add task to Celery queue")

    return JSONResponse(content={"task_id": task_id}, status_code=202)


@app.get("/get_result/{task_id}")
async def get_result(task_id: str):
    result = celery_app.AsyncResult(task_id)
    if result.ready():
        return {"task_id": task_id, "result": result.result}
    else:
        return JSONResponse(content={"task_id": task_id, "status": "processing"}, status_code=202)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5050)
