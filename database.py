from supabase import create_client, Client
import os

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

supabase: Client = create_client(
    SUPABASE_URL, SUPABASE_KEY
    )

def get_lecturer_by_email(email):
    response = supabase.table('lecturers').select('*').eq('email', email).execute()
    if response.data:
        return response.data[0]
    return None

def get_student_by_email(email):
    response = supabase.table('students').select('*').eq('email', email).execute()
    if response.data:
        return response.data[0]
    return None

def db_create_semester(semester_name, academic_year):
    response = supabase.table('semesters').insert({
        "semester_name": semester_name,
        "academic_year": academic_year,
    }).execute()
    return response.data

def db_get_semesters():
    response = supabase.table('semesters').select('*').execute()
    return response.data

def get_lecturer_courses(lecturer_id):
    response = supabase.table('courses')\
        .select('course_id, course_title, course_code')\
        .eq('lecturer_id', int(lecturer_id))\
        .execute()
    return response.data

def get_active_semester():
    response = supabase.table('semesters')\
        .select('*', 'semester_name')\
        .eq('is_active', True)\
        .execute()
    return response.data[0] if response.data else None

def get_students_in_course(course_id, semester_id):
    response = supabase.table('enrollments')\
        .select('*, students(*)')\
        .eq('course_id', int(course_id))\
        .eq('semester_id', int(semester_id))\
        .execute()
    return response.data

def save_score(student_id, course_id, semester_id, assignment, attendance, mid_semester, quiz, exam_score, total_score, grade, grade_point):
    response = supabase.table('course_results').upsert({
        "student_id": int(student_id),
        "course_id": int(course_id),
        "semester_id": int(semester_id),
        "assignment": float(assignment) if assignment is not None else None,
        "attendance": float(attendance) if attendance is not None else None,
        "mid_semester": float(mid_semester) if mid_semester is not None else None,
        "quiz": float(quiz) if quiz is not None else None,
        "exam_score": float(exam_score) if exam_score is not None else None,
        "total_score": float(total_score) if total_score is not None else None,
        "grade": grade,
        "grade_point": float(grade_point) if grade_point is not None else None
    }, on_conflict = "student_id, semester_id, course_id").execute()
    return response.data

def get_existing_scores(course_id, semester_id):
    response = supabase.table('course_results')\
        .select('*')\
        .eq('course_id', int(course_id))\
        .eq('semester_id', int(semester_id))\
        .execute()
    return response.data

def get_student_results(student_id, semester_id):
    response = supabase.table('course_results')\
        .select('*, courses(*)')\
        .eq('student_id', int(student_id))\
        .eq('semester_id', int(semester_id))\
        .execute()
    return response.data

def get_enrolled_semesters(student_id):
    response = supabase.table('enrollments')\
        .select('semesters(*)')\
        .eq('student_id', int(student_id))\
        .execute()
    semesters = []
    seen = set()
    for e in response.data:
        sid = e['semesters']['semester_id']
        if sid not in seen:
            seen.add(sid)
            semesters.append(e['semesters'])
    return semesters

def get_student_enrolled_courses_active(student_id):
    active = get_active_semester()
    if not active:
        return[], None
    
    response = supabase.table('enrollments')\
        .select('*,courses(*)')\
        .eq('student_id', int(student_id))\
        .execute()
    return response.data, active

def get_previous_semester_results(student_id, current_semester_id):
    response = supabase.table('course_results')\
        .select('*, courses(*)')\
        .eq('student_id', int(student_id))\
        .neq('semester_id', int(current_semester_id))\
        .execute()
    return response.data
