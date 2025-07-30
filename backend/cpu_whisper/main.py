from fastapi import FastAPI, UploadFile, File
from faster_whisper import WhisperModel
import tempfile
import asyncio
import time
from typing import List

model_size = "tiny"
app = FastAPI()
model = WhisperModel(model_size, device="cpu", compute_type="int8")

@app.get("/")
async def root():
    return {"message": "Welcome to the Whisper API!"}

@app.post("/v1/audio/transcriptions")
async def transcribe(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        segments, info = model.transcribe(tmp.name, beam_size=5)
        print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
        text = ""
        for segment in segments:
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

            text += segment.text
    return {"text": text}

# ---------- DYNAMIC BATCHING ROUTE ----------

queue: List[tuple[UploadFile, asyncio.Future]] = []
condition = asyncio.Condition()

max_batch_size = 4
max_wait_time = 0.1  # seconds

@app.post("/v1/audio/transcriptions_batch")
async def transcribe_batch(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    loop = asyncio.get_event_loop()
    future = loop.create_future()

    async with condition:
        queue.append((audio_bytes, future))
        condition.notify_all()

    return await future

async def batch_worker():
    while True:
        async with condition:
            await condition.wait()
            start_time = time.time()

            while len(queue) < max_batch_size and (time.time() - start_time) < max_wait_time:
                await asyncio.sleep(0.01)

            batch = []
            while queue and len(batch) < max_batch_size:
                batch.append(queue.pop(0))

        for audio_bytes, future in batch:
            try:
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp.write(audio_bytes)
                    segments, info = model.transcribe(tmp.name, beam_size=5)
                    text = "".join([s.text for s in segments])
                    future.set_result({"text": text})
            except Exception as e:
                future.set_exception(e)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(batch_worker())