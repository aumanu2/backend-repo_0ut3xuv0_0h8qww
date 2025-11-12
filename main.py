import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

# Import defensively to avoid crash when DB isn't configured
try:
    from database import db, create_document, get_documents
except Exception:
    db, create_document, get_documents = None, None, None

from schemas import Student, Marksheet, AdmitCard, Attendance

app = FastAPI(title="School Helper API", version="1.0.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "School Helper Backend running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set",
        "database_name": os.getenv("DATABASE_NAME") or "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "❌ Not Available"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Helpers

def ensure_db_available():
    if db is None or create_document is None or get_documents is None:
        raise HTTPException(status_code=503, detail="Database not configured. Set DATABASE_URL and DATABASE_NAME.")

# ---------------- Students ----------------

@app.post("/students", status_code=201)
def create_student(student: Student):
    ensure_db_available()
    exists = db["student"].find_one({"roll_no": student.roll_no}) if db else None
    if exists:
        raise HTTPException(status_code=409, detail="Roll number already exists")
    new_id = create_document("student", student)
    return {"id": new_id}

@app.get("/students")
def list_students(class_name: Optional[str] = None, section: Optional[str] = None):
    ensure_db_available()
    query = {}
    if class_name:
        query["class_name"] = class_name
    if section:
        query["section"] = section
    docs = get_documents("student", query)
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs

@app.get("/students/{student_id}")
def get_student(student_id: str):
    ensure_db_available()
    # Attempt ObjectId lookup then fallback
    doc = None
    try:
        from bson import ObjectId
        doc = db["student"].find_one({"_id": ObjectId(student_id)})
    except Exception:
        doc = db["student"].find_one({"id": student_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Student not found")
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc

# ---------------- Marksheet ----------------

@app.post("/marksheets", status_code=201)
def create_marksheet(sheet: Marksheet):
    ensure_db_available()
    if sheet.subjects:
        total_obt = sum(s.marks for s in sheet.subjects)
        total_max = sum(s.max_marks for s in sheet.subjects)
        percentage = (total_obt / total_max * 100) if total_max > 0 else 0
        grade = (
            "A+" if percentage >= 90 else
            "A" if percentage >= 80 else
            "B" if percentage >= 70 else
            "C" if percentage >= 60 else
            "D" if percentage >= 50 else
            "E"
        )
        sheet.total_obtained = total_obt
        sheet.total_max = total_max
        sheet.percentage = round(percentage, 2)
        sheet.grade = grade
    new_id = create_document("marksheet", sheet)
    return {"id": new_id}

@app.get("/marksheets")
def list_marksheets(student_id: Optional[str] = None, exam_name: Optional[str] = None):
    ensure_db_available()
    q = {}
    if student_id:
        q["student_id"] = student_id
    if exam_name:
        q["exam_name"] = exam_name
    docs = get_documents("marksheet", q)
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs

# ---------------- Admit Cards ----------------

@app.post("/admit-cards", status_code=201)
def create_admit_card(card: AdmitCard):
    ensure_db_available()
    new_id = create_document("admitcard", card)
    return {"id": new_id}

@app.get("/admit-cards")
def list_admit_cards(student_id: Optional[str] = None, exam_name: Optional[str] = None):
    ensure_db_available()
    q = {}
    if student_id:
        q["student_id"] = student_id
    if exam_name:
        q["exam_name"] = exam_name
    docs = get_documents("admitcard", q)
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs

# ---------------- Attendance ----------------

@app.post("/attendance", status_code=201)
def mark_attendance(record: Attendance):
    ensure_db_available()
    new_id = create_document("attendance", record)
    return {"id": new_id}

@app.get("/attendance")
def list_attendance(student_id: Optional[str] = None, date: Optional[str] = None, status: Optional[str] = None):
    ensure_db_available()
    q: dict = {}
    if student_id:
        q["student_id"] = student_id
    if date:
        q["date"] = date
    if status:
        q["status"] = status
    docs = get_documents("attendance", q)
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
