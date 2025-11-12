"""
Database Schemas for School Helper App

Each Pydantic model below represents a MongoDB collection. The collection name
is the lowercase of the class name. Example: class Student -> collection "student".

These schemas are used for validation at the API layer and for the built-in
DB helper utilities.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import date

# Core domain models

class Student(BaseModel):
    full_name: str = Field(..., description="Student full name")
    roll_no: str = Field(..., description="Unique roll number")
    class_name: str = Field(..., description="Class/Grade, e.g., '10' or 'Grade 5'")
    section: Optional[str] = Field(None, description="Section, e.g., A/B/C")
    dob: Optional[date] = Field(None, description="Date of birth")
    guardian_name: Optional[str] = Field(None, description="Parent/Guardian name")
    contact: Optional[str] = Field(None, description="Contact number")
    address: Optional[str] = Field(None, description="Postal address")

class SubjectMark(BaseModel):
    name: str = Field(..., description="Subject name")
    marks: float = Field(..., ge=0, description="Obtained marks")
    max_marks: float = Field(..., gt=0, description="Maximum marks")

class Marksheet(BaseModel):
    student_id: str = Field(..., description="ID of the student (stringified ObjectId)")
    exam_name: str = Field(..., description="Exam name, e.g., Half-Yearly")
    class_name: str = Field(..., description="Class for which the exam was taken")
    year: int = Field(..., ge=1900, le=3000, description="Academic year")
    subjects: List[SubjectMark] = Field(..., description="List of subject marks")
    total_obtained: Optional[float] = Field(None, ge=0, description="Total obtained marks")
    total_max: Optional[float] = Field(None, ge=0, description="Total maximum marks")
    percentage: Optional[float] = Field(None, ge=0, le=100, description="Overall percentage")
    grade: Optional[str] = Field(None, description="Overall grade")
    remarks: Optional[str] = Field(None, description="General remarks")

class AdmitCard(BaseModel):
    student_id: str = Field(..., description="ID of the student (stringified ObjectId)")
    roll_no: str = Field(..., description="Roll number to show on card")
    class_name: str = Field(..., description="Class")
    exam_name: str = Field(..., description="Exam name")
    exam_date: Optional[date] = Field(None, description="Date of exam")
    center: Optional[str] = Field(None, description="Exam center/room")
    issued_on: Optional[date] = Field(None, description="Issue date")

class Attendance(BaseModel):
    student_id: str = Field(..., description="ID of the student (stringified ObjectId)")
    date: date = Field(..., description="Attendance date")
    status: Literal['Present','Absent','Late'] = Field(..., description="Attendance status")
    remarks: Optional[str] = Field(None, description="Optional remarks")

# Read-only response helpers
class IdResponse(BaseModel):
    id: str
