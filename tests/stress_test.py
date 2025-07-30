import time
import requests
import concurrent.futures
from pathlib import Path

ENDPOINT = "http://localhost:8000/v1/audio/transcriptions"
ENDPOINT = "http://localhost:8000/v1/audio/transcriptions_batch"
AUDIO_PATH = "./audio/bonjour.m4a"

# Number of total requests to send
NUM_REQUESTS = 100

# Number of requests to send concurrently
CONCURRENCY = 2

def transcribe(audio_bytes):
    start = time.perf_counter()
    try:
        response = requests.post(ENDPOINT, files={"file": audio_bytes})
        latency = time.perf_counter() - start
        response.raise_for_status()
        return {"latency": latency, "status": "ok"}
    except Exception as e:
        return {"latency": None, "status": f"error: {e}"}


def run_stress_test():
    audio_bytes = Path(AUDIO_PATH).read_bytes()
    results = []

    print(f"🚀 Launching {NUM_REQUESTS} requests with concurrency={CONCURRENCY}...")

    start_global = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = [executor.submit(transcribe, audio_bytes) for _ in range(NUM_REQUESTS)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    duration = time.perf_counter() - start_global

    success = [r for r in results if r["status"] == "ok"]
    failures = [r for r in results if r["status"] != "ok"]
    latencies = [r["latency"] for r in success]

    print(f"\n✅ Success: {len(success)} / {NUM_REQUESTS}")
    print(f"❌ Failures: {len(failures)}")
    if failures:
        print(f"Examples: {[r['status'] for r in failures[:3]]}")
    if latencies:
        print(f"\n📊 Latency stats (s) for {len(latencies)} successful requests:")
        print(f"  min:  {min(latencies):.2f}")
        print(f"  max:  {max(latencies):.2f}")
        print(f"  mean: {sum(latencies)/len(latencies):.2f}")
        print(f"\n⚡ Throughput: {len(success)/duration:.2f} req/s over {duration:.2f} seconds")

if __name__ == "__main__":
    run_stress_test()
