from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import librosa
import shutil
import os
from tempfile import NamedTemporaryFile

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def analyze_track(file_path):
    y, sr = librosa.load(file_path, sr=None)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    energy = sum(abs(y)) / len(y)
    return {"tempo": round(tempo, 2), "energy": round(energy, 4)}

@app.post("/battle")
async def battle(track1: UploadFile = File(...), track2: UploadFile = File(...)):
    def save_upload(upload):
        temp = NamedTemporaryFile(delete=False, suffix=".wav")
        with temp as out_file:
            shutil.copyfileobj(upload.file, out_file)
        return temp.name

    file1_path = save_upload(track1)
    file2_path = save_upload(track2)

    stats1 = analyze_track(file1_path)
    stats2 = analyze_track(file2_path)

    lit_score_1 = stats1["tempo"] * stats1["energy"]
    lit_score_2 = stats2["tempo"] * stats2["energy"]

    winner = "Track 1" if lit_score_1 > lit_score_2 else "Track 2"

    os.remove(file1_path)
    os.remove(file2_path)

    return {
        "winner": winner,
        "track1": stats1,
        "track2": stats2,
        "score1": round(lit_score_1, 2),
        "score2": round(lit_score_2, 2)
    }
