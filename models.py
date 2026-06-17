class Student:
    def __init__(self, student_id, name, email, matric_no, level):
        self.student_id = student_id
        self.name = name
        self.email = email
        self.matric_no = matric_no
        self.level = level
        self.semesters = []

class Lecturer:
    def __init__(self, lecturer_id, name, email, staff_id, department):
        self.lecturer_id = lecturer_id
        self.name = name
        self.email = email
        self.staff_id = staff_id
        self.department = department

class Course:
    def __init__(self, course_id, course_code, course_title, credit_unit, lecturer_id):
        self.course_id = course_id
        self.course_code = course_code
        self.course_title = course_title
        self.credit_unit = credit_unit
        self.lecturer_id = lecturer_id

class CA:
    def __init__(self, assignment, attendance, mid_semester, quiz):
        self.assignment = assignment
        self.attendance = attendance
        self.mid_semester = mid_semester
        self.quiz = quiz

class CourseResult:
    def __init__(self, student_id, semester_id, course, ca, exam_score):
        self.student_id = student_id
        self.semester_id = semester_id
        self.course = course
        self.ca = ca
        self.exam_score = exam_score

class Semester:
    def __init__(self, semester_id, semester_name):
        self.semester_id = semester_id
        self.semester_name = semester_name
        self.course_results = []
