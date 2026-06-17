from flask import Flask, render_template, flash, redirect, url_for, session, request
from forms import StudentLoginForm, LecturerLoginForm, NewSemesterForm
from database import *
from models import *
from logic import *
from collections import defaultdict
import os


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/lecturer_login', methods=['GET', 'POST'])
def lecturer_login():
    form = LecturerLoginForm()
    session.pop('_flashes', None)
    
    if form.validate_on_submit():
        lecturer = get_lecturer_by_email(form.email.data)
        if lecturer is None:
            flash('No account found with that email.', 'danger')
        
        elif lecturer and lecturer['password_hash'] == form.password.data:
            session['lecturer_id'] = lecturer['lecturer_id']
            session['lecturer_name'] = lecturer['name']
            flash('Login successful!', 'success')
            return redirect(url_for('lecturer_dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    
    
    
    return render_template('lecturer_login.html', form=form, )

    

@app.route('/student_login', methods=["GET", "POST"])
def student_login():
    form = StudentLoginForm()
    session.pop('_flashes', None)
    
    if form.validate_on_submit():
        student = get_student_by_email(form.email.data)
        
        if student is None:
            flash('No account found with that email.', 'danger')
        elif student and student['password_hash'] == form.password.data:
            session['student_id'] = student['student_id']
            session['student_name'] = student['name']
            flash('Login successful!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    
    return render_template('student_login.html', form=form)


@app.route('/lecturer_dashboard')
def lecturer_dashboard():
    semesters = db_get_semesters()
    selected_semester_id = request.args.get('semester_id')
    selected_course_id = request.args.get('course_id')
    lecturer_id = session.get('lecturer_id')
    semester_selected = selected_semester_id is not None
    students_in_course = []
    active_semester = get_active_semester()
    courses = []
    existing_scores = {}
    
    if not session.get('lecturer_id'):
        return redirect(url_for('lecturer_login'))
    
    if selected_course_id and selected_semester_id:
        scores = get_existing_scores(course_id = selected_course_id, semester_id= selected_semester_id)
        existing_scores = {s['student_id']: s for s in scores}

    if not semester_selected:
        active = get_active_semester()
        if active:
            selected_semester_id = str(active['semester_id'])

    if semester_selected:
        courses = get_lecturer_courses(lecturer_id)
        
    
    if selected_course_id and selected_semester_id:
        students_in_course = get_students_in_course(selected_course_id, selected_semester_id)
    
        

    return render_template('lecturer_dashboard.html',
                        form=NewSemesterForm(),
                        semesters=semesters,
                        selected_semester_id=selected_semester_id,
                        semester_selected=semester_selected,
                        courses=courses,
                        selected_course_id=selected_course_id,
                        students_in_course=students_in_course,
                        active_semester=active_semester,  
                        existing_scores = existing_scores)



''' @app.route('/create_semester', methods=['GET', 'POST'])
def create_semester():
    form = NewSemesterForm()
    
    if form.validate_on_submit():
        semester_name = form.semester_name.data
        academic_year = form.academic_year.data
        db_create_semester(semester_name, academic_year)
        
        flash(f'Semester "{semester_name}" created successfully!', 'success')
    return redirect(url_for('lecturer_dashboard')) '''

@app.route('/save_score', methods=['POST'])
def save_score_route():
    student_id = request.form.get('student_id')
    course_id = request.form.get('course_id')
    semester_id = request.form.get('semester_id')
    assignment = float(request.form.get('assignment')) if request.form.get('assignment') != '' else None
    attendance = float(request.form.get('attendance')) if request.form.get('attendance') != '' else None
    mid_semester = float(request.form.get('mid_semester')) if request.form.get('mid_semester') != '' else None
    quiz = float(request.form.get('quiz')) if request.form.get('quiz') != '' else None
    exam_score = float(request.form.get('exam_score')) if request.form.get('exam_score') != '' else None

    total = None
    grade = None
    grade_point = None

    if all(v is not None for v in [assignment, attendance, mid_semester, quiz, exam_score]):
        ca = CA(assignment, attendance, mid_semester, quiz)
        total = calculate_total_score(ca, exam_score)
        grade, grade_point = calculate_grade(total)

    save_score(student_id, course_id, semester_id, assignment, attendance, mid_semester, quiz, exam_score, total, grade, grade_point)
    flash('Score saved successfully!', 'success')
    return redirect(url_for('lecturer_dashboard', semester_id=semester_id, course_id=course_id))
    

@app.route('/student_dashboard')
def student_dashboard():
    student_id = session.get('student_id')
    selected_semester_id = request.args.get('semester_id')
    semester_selected = selected_semester_id is not None
    semesters = get_enrolled_semesters(student_id)
    
    if not session.get('student_id'):
        return redirect(url_for('student_login'))

    if not semester_selected:
        active = get_active_semester()
        if active:
            selected_semester_id = str(active['semester_id'])

    course_results_display = []
    gpa = 0.0
    cgpa = 0.0
    total_units = 0

    if selected_semester_id:
        raw_results = get_student_results(student_id, selected_semester_id)


        semester_obj = Semester(selected_semester_id, '')
        for r in raw_results:
            exam = r['exam_score'] or 0
            ca = CA(r['assignment'] or 0, r['attendance'] or 0, r['mid_semester'] or 0, r['quiz'] or 0)
            course = Course(r['courses']['course_id'], r['courses']['course_code'],
                        r['courses']['course_title'], r['courses']['credit_unit'],
                        r['courses']['lecturer_id'])
            cr = CourseResult(student_id, selected_semester_id, course, ca, r['exam_score'])
            semester_obj.course_results.append(cr)
            all_scores_entered = all([
                            r['assignment'] is not None,
                            r['attendance'] is not None,
                            r['mid_semester'] is not None,
                            r['quiz'] is not None,
                            r['exam_score'] is not None
                        ])
            total = calculate_total_score(ca, exam)
            grade, _ = calculate_grade(total)
            course_results_display.append({
                "course_code": course.course_code,
                "course_title": course.course_title,
                "assignment": r['assignment'] or 0,
                "attendance": r['attendance'] or 0,
                "mid_semester": r['mid_semester'] or 0,
                "quiz": r['quiz'] or 0,
                "ca": calculate_ca(ca),
                "exam_score": r['exam_score'] or 0,
                "raw_assignment": r['assignment'],
                "raw_attendance": r['attendance'],
                "raw_mid_semester": r['mid_semester'],
                "raw_quiz": r['quiz'],
                "total": total if all_scores_entered else None,
                "grade": grade if all_scores_entered else None,
                "credit_unit": course.credit_unit,
                "student_id": student_id,
                "course_id": course.course_id,
                "semester_id": selected_semester_id
            })

        gpa = calculate_gpa(semester_obj)
        total_units = sum(r['courses']['credit_unit'] for r in raw_results)
        
        all_results = get_student_results(student_id, selected_semester_id)
        semester_groups = defaultdict(list)
        for r in all_results:
            semester_groups[r['semester_id']].append(r)

        student_obj = Student(student_id, '', '', '', '')
        for sem_id, results in semester_groups.items():
            sem_obj = Semester(sem_id, '')
            for r in results:
                ca = CA(r['assignment'] or 0, r['attendance'] or 0, r['mid_semester'] or 0, r['quiz'] or 0)
                total = calculate_total_score(ca, r['exam_score'] or 0)
                course = Course(r['courses']['course_id'], r['courses']['course_code'],
                            r['courses']['course_title'], r['courses']['credit_unit'],
                            r['courses']['lecturer_id'])
                sem_obj.course_results.append(CourseResult(student_id, sem_id, course, ca, r['exam_score']))
            student_obj.semesters.append(sem_obj)

        cgpa = calculate_cgpa(student_obj)

    return render_template('student_dashboard.html',
                        semesters=semesters,
                        results=course_results_display,
                        gpa=gpa,
                        cgpa=cgpa,
                        total_units=total_units,
                        selected_semester_id=selected_semester_id,
                        semester_selected=semester_selected,
                        active_semester=get_active_semester()
                        )

@app.route('/simulator', methods = ['GET', 'POST'])
def simulator():
    student_id = session.get('student_id')
    enrollments, active_semester = get_student_enrolled_courses_active(student_id)
    
    simulated_gpa = None
    simulated_cgpa = None
    simulated_results = []
    
    if not session.get('student_id'):
        return redirect(url_for('student_login'))

    if request.method == 'POST':
        semester_obj = Semester(active_semester['semester_id'], '')
        
        for enrollment in enrollments:
            course = enrollment['courses']
            course_id = str(course['course_id'])
            
            assignment = float(request.form.get(f'assignment_{course_id}', 0))
            attendance = float(request.form.get(f'attendance_{course_id}', 0))
            mid_semester = float(request.form.get(f'mid_semester_{course_id}', 0))
            quiz = float(request.form.get(f'quiz_{course_id}', 0))
            exam = float(request.form.get(f'exam_{course_id}', 0))

            ca = CA(assignment, attendance, mid_semester, quiz)
            course_obj = Course(course['course_id'], course['course_code'],
                            course['course_title'], course['credit_unit'],
                            course['lecturer_id'])
            cr = CourseResult(student_id, active_semester['semester_id'], course_obj, ca, exam)
            semester_obj.course_results.append(cr)

            total = calculate_total_score(ca, exam)
            grade, point = calculate_grade(total)
            simulated_results.append({
                "course_code": course['course_code'],
                "course_title": course['course_title'],
                "total": total,
                "grade": grade,
                "credit_unit": course['credit_unit']
            })

        simulated_gpa = calculate_gpa(semester_obj)

        prev_results = get_previous_semester_results(student_id, active_semester['semester_id'])
        total_weighted = sum(
            calculate_grade(calculate_total_score(
                CA(r['assignment'], r['attendance'], r['mid_semester'], r['quiz']),
                r['exam_score']
            ))[1] * r['courses']['credit_unit']
            for r in prev_results
        )
        total_weighted += simulated_gpa * sum(c['courses']['credit_unit'] for c in enrollments)
        total_units = sum(r['courses']['credit_unit'] for r in prev_results) + \
                    sum(c['courses']['credit_unit'] for c in enrollments)
        simulated_cgpa = round(total_weighted / total_units, 2) if total_units > 0 else simulated_gpa
        
        if total > 100:
            flash('One or more scores exceed the maximum. Check your inputs.', 'danger')

    return render_template('simulator.html',
                        enrollments=enrollments,
                        active_semester=active_semester,
                        simulated_results=simulated_results,
                        simulated_gpa=simulated_gpa,
                        simulated_cgpa=simulated_cgpa)
    
if __name__ == '__main__':
    app.run(debug=True)
