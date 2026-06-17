from models import Student, Lecturer, Course, CA, Semester, CourseResult





def calculate_ca(ca):
    return (
        (ca.assignment or 0) +
        (ca.attendance or 0) +
        (ca.mid_semester or 0) +
        (ca.quiz or 0)
    )
    
def validate_ca(ca):
    if ca.assignment < 0 or ca.assignment > 10:
        raise ValueError("Assignment score must be between 0 and 10")
    if ca.attendance < 0 or ca.attendance > 5:
        raise ValueError("Attendance score must be between 0 and 5")
    if ca.mid_semester < 0 or ca.mid_semester > 15:
        raise ValueError("Mid-semester score must be between 0 and 15")
    if ca.quiz < 0 or ca.quiz > 10:
        raise ValueError("Quiz score must be between 0 and 10")
    
def calculate_total_score(ca, exam_score):
    total_ca = calculate_ca(ca)
    return total_ca + (exam_score or 0)

def validate_exam_score(exam_score):
    if exam_score < 0 or exam_score > 60:
        raise ValueError("Exam score must be between 0 and 60")

def calculate_grade(total_score):
    if total_score < 0 or total_score > 100:
        raise ValueError("Total score must be between 0 and 100")
    
    if total_score >= 80:
        return 'A', 5.0
    elif total_score >= 60:
        return 'B', 4.0
    elif total_score >= 50:
        return 'C', 3.0
    elif total_score >= 45:
        return 'D', 2.0
    elif total_score >= 40:
        return 'E', 1.0
    else:
        return 'F', 0.0

def calculate_gpa(semester):
    total_points = 0
    total_units = 0

    for result in semester.course_results:
        total_score = calculate_total_score(result.ca, result.exam_score)
        _, point = calculate_grade(total_score)
        total_points += point * result.course.credit_unit
        total_units += result.course.credit_unit

    if total_units == 0:
        return 0.0

    return round(total_points / total_units, 2)

def calculate_cgpa(student):
    total_weighted_points = 0
    total_units = 0

    for semester in student.semesters:
        for result in semester.course_results:
            total_score = calculate_total_score(result.ca, result.exam_score)
            _, point = calculate_grade(total_score)
            total_weighted_points += point * result.course.credit_unit
            total_units += result.course.credit_unit

    if total_units == 0:
        return 0.0

    return round(total_weighted_points / total_units, 2)

def carry_over_risk(ca, predicted_exam):
    
    if calculate_ca(ca) == 0:
        return "CA not entered by lecturer yet. Calm down boss."
    
    total = calculate_total_score(ca, predicted_exam)
    
    if total < 45:
        return f"Your total is {total} High risk (wrap it up gng...)"
    elif total < 50:
        return f"Your total is {total} Moderate risk (just pray lol...)"
    else:
        return f"Your total is {total} Low risk (you came here so youre not better than you think nigg)"
    
def course_impact_current_semester(semester):

    gpa = calculate_gpa(semester)
    impact_list = []

    for result in semester.course_results:
        total_score = calculate_total_score(result.ca, result.exam_score)
        grade, point = calculate_grade(total_score)
        impact = point * result.course.credit_unit
        impact_list.append({
            "course_code": result.course.course_code,
            "course_title": result.course.course_title,
            "credit_unit": result.course.credit_unit,
            "grade": grade,
            "impact_score": impact,
            "semester_gpa": gpa
        })

    return impact_list

def what_if_simulator_current_semester(semester, simulated_scores_dict):
    simulated_results = []
    
    for result in semester.course_results:
        expected_exam = simulated_scores_dict.get(result.course.course_code, result.exam_score)
        total = calculate_total_score(result.ca, expected_exam)
        grade, point = calculate_grade(total)
        simulated_results.append({
            "course": result.course.course_code,
            "simulated_total": total,
            "simulated_grade": grade,
            "grade_point": point
        })
        
    total_points = sum(r["grade_point"] * next(c.credit_unit for c in semester.course_results if c.course.course_code == r["course"]) for r in simulated_results)
    total_units = sum(c.credit_unit for c in semester.course_results)
    simulated_gpa = round(total_points / total_units, 2) if total_units > 0 else 0.0
    return simulated_results, simulated_gpa



