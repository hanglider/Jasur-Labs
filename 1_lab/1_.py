from functools import reduce

students = [
    {"name": "Alice", "age": 20, "grades": [85, 90, 88, 92]},
    {"name": "Bob", "age": 22, "grades": [78, 89, 76, 85]},
    {"name": "Charlie", "age": 21, "grades": [92, 95, 88, 94]},
    {"name": "David", "age": 23, "grades": [65, 75, 70, 68]},
    {"name": "Eve", "age": 20, "grades": [88, 91, 87, 90]},
    {"name": "Frank", "age": 22, "grades": [72, 85, 80, 77]},
    {"name": "Grace", "age": 21, "grades": [93, 90, 89, 92]},
    {"name": "Hannah", "age": 23, "grades": [80, 85, 88, 84]},
    {"name": "Ivy", "age": 19, "grades": [95, 97, 93, 96]},
    {"name": "Jack", "age": 24, "grades": [60, 65, 62, 68]},
    {"name": "Kim", "age": 20, "grades": [89, 91, 87, 92]},
    {"name": "Liam", "age": 22, "grades": [79, 82, 85, 80]},
    {"name": "Mia", "age": 21, "grades": [91, 92, 93, 94]},
    {"name": "Noah", "age": 23, "grades": [67, 72, 70, 68]},
    {"name": "Olivia", "age": 20, "grades": [87, 89, 85, 88]},
    {"name": "Paul", "age": 22, "grades": [82, 85, 79, 83]},
    {"name": "Quincy", "age": 21, "grades": [90, 92, 89, 91]},
    {"name": "Rachel", "age": 23, "grades": [75, 80, 78, 82]},
    {"name": "Sam", "age": 19, "grades": [98, 95, 96, 99]},
    {"name": "Tina", "age": 24, "grades": [63, 68, 65, 66]},
]


def filter_students(students, min_age, max_age):
    return list(filter(
        lambda student: (student["age"] >= min_age) and
                        (student["age"] <= max_age) ,
        students
    ))

def calculate_average_grade(student):
    return sum(student["grades"]) / len(student["grades"])

def main(students):
    filtered_students = filter_students(students, min_age=23, max_age=25)

    students_with_averages = list(map(
        lambda student: {**student, "average": calculate_average_grade(student)},
        filtered_students
    ))

    overall_avg = reduce(
        lambda acc, student: acc + sum(student["grades"]),
        students_with_averages, 0
    ) / reduce(lambda acc, student: acc + len(student["grades"]), students_with_averages, 0)

    max_average = reduce(
        lambda acc, student: max(acc, student["average"]),
        students_with_averages, 0
    )

    top_students = list(filter(lambda student: student["average"] == max_average, students_with_averages))

    print("Отфильтрованные студенты:", filtered_students)
    print("Общий средний балл:", overall_avg)
    print("Лучшие студенты:", top_students)

main(students)