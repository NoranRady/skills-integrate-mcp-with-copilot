"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
from pathlib import Path

from .database import init_db, get_db, engine
from .models import Base, Activity, Student

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


@app.on_event("startup")
def startup_event():
    """Initialize database on application startup"""
    print("Initializing database...")
    init_db()
    
    # Load sample data if database is empty
    db = next(get_db())
    
    # Check if activities already exist
    existing_activities = db.query(Activity).count()
    if existing_activities == 0:
        print("Loading sample activities...")
        _load_sample_data(db)
    
    db.close()


def _load_sample_data(db: Session):
    """Load sample activities and students into the database"""
    sample_activities = [
        {
            "name": "Chess Club",
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "students": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        {
            "name": "Programming Class",
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "students": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        {
            "name": "Gym Class",
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "students": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        {
            "name": "Soccer Team",
            "description": "Join the school soccer team and compete in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "students": ["liam@mergington.edu", "noah@mergington.edu"]
        },
        {
            "name": "Basketball Team",
            "description": "Practice and play basketball with the school team",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "students": ["ava@mergington.edu", "mia@mergington.edu"]
        },
        {
            "name": "Art Club",
            "description": "Explore your creativity through painting and drawing",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "students": ["amelia@mergington.edu", "harper@mergington.edu"]
        },
        {
            "name": "Drama Club",
            "description": "Act, direct, and produce plays and performances",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "students": ["ella@mergington.edu", "scarlett@mergington.edu"]
        },
        {
            "name": "Math Club",
            "description": "Solve challenging problems and participate in math competitions",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "max_participants": 10,
            "students": ["james@mergington.edu", "benjamin@mergington.edu"]
        },
        {
            "name": "Debate Team",
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 12,
            "students": ["charlotte@mergington.edu", "henry@mergington.edu"]
        }
    ]
    
    # Create activities with students
    for activity_data in sample_activities:
        students_emails = activity_data.pop("students", [])
        
        # Create or get students
        students = []
        for email in students_emails:
            student = db.query(Student).filter(Student.email == email).first()
            if not student:
                student = Student(email=email, name=email.split("@")[0].title())
                db.add(student)
            students.append(student)
        
        db.flush()  # Ensure students are inserted
        
        # Create activity
        activity = Activity(**activity_data, participants=students)
        db.add(activity)
    
    db.commit()
    print("Sample data loaded successfully!")


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(db: Session = Depends(get_db)):
    """Get all activities with their current participants"""
    activities = db.query(Activity).all()
    
    result = {}
    for activity in activities:
        result[activity.name] = {
            "description": activity.description,
            "schedule": activity.schedule,
            "max_participants": activity.max_participants,
            "participants": [p.email for p in activity.participants]
        }
    
    return result


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Sign up a student for an activity"""
    # Find the activity
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Check if student is already signed up
    existing_student = db.query(Student).filter(Student.email == email).first()
    if existing_student and existing_student in activity.participants:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )
    
    # Check capacity
    if len(activity.participants) >= activity.max_participants:
        raise HTTPException(
            status_code=400,
            detail=f"Activity is full (max {activity.max_participants})"
        )
    
    # Create or get student
    if not existing_student:
        existing_student = Student(email=email, name=email.split("@")[0].title())
        db.add(existing_student)
        db.flush()
    
    # Add student to activity
    activity.participants.append(existing_student)
    db.commit()
    
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Unregister a student from an activity"""
    # Find the activity
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Find the student
    student = db.query(Student).filter(Student.email == email).first()
    if not student or student not in activity.participants:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )
    
    # Remove student from activity
    activity.participants.remove(student)
    db.commit()
    
    return {"message": f"Unregistered {email} from {activity_name}"}

