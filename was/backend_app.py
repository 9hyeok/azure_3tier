from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from datetime import datetime
import os

app = FastAPI()

DATA_FILE = 'account_requests.csv'

# CSV 초기화
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["name", "department", "email", "phone", "requested_at", "status", "note"])
    df.to_csv(DATA_FILE, index=False)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_data():
    return pd.read_csv(DATA_FILE)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

@app.post("/request")
async def submit_request(data: dict):
    df = load_data()
    new_row = {
        "name": [data["name"]],
        "department": [data["department"]],
        "email": [data["email"]],
        "phone": [data["phone"]],
        "requested_at": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "status": ["pending"],
        "note": ["  "]
    }
    df = pd.concat([df,pd.DataFrame(new_row)])
    save_data(df)
    return {"message": "신청이 완료되었습니다."}

@app.get("/status")
async def check_status(name: str, department: str):
    df = load_data()
    matched = df[(df["name"] == name) & (df["department"] == department)]
    print(matched)
    if matched.empty:
        raise HTTPException(status_code=404, detail="신청 정보를 찾을 수 없습니다.")
    
    return matched.to_dict(orient="list")

@app.get("/admin")
async def get_all():
    df = load_data()
    return df.to_dict(orient="list")


@app.post("/admin/delete")
async def delete_rows(rows:list[dict]):
    df = load_data()
    initial_len = len(df)   
    for row in rows:
        df = df[
            ~((df["name"] == row["name"]) &
              (df["email"] == row["email"]) &
              (df["department"] == row["department"]))
        ]

    if len(df) == initial_len:
        raise HTTPException(status_code=404, detail="삭제된 항목 없음")

    save_data(df)
    return {"message": f"{initial_len - len(df)}개 항목 삭제 완료"}