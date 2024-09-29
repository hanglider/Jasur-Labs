from functools import reduce

users = [
    {"name": "Alice", "expenses": [100, 50, 75, 200]},
    {"name": "Bob", "expenses": [50, 75, 80, 100]},
    {"name": "Charlie", "expenses": [200, 300, 50, 150]},
    {"name": "David", "expenses": [100, 200, 300, 400]},
    {"name": "Eve", "expenses": [150, 60, 90, 120]},
    {"name": "Frank", "expenses": [80, 200, 150, 100]},
    {"name": "Grace", "expenses": [300, 400, 250, 500]},
    {"name": "Hannah", "expenses": [120, 60, 70, 90]},
    {"name": "Ivy", "expenses": [500, 300, 250, 150]},
    {"name": "Jack", "expenses": [75, 100, 50, 150]},
    {"name": "Kim", "expenses": [100, 90, 80, 60]},
    {"name": "Liam", "expenses": [120, 200, 180, 160]},
    {"name": "Mia", "expenses": [400, 500, 450, 300]},
    {"name": "Noah", "expenses": [90, 80, 100, 150]},
    {"name": "Olivia", "expenses": [60, 90, 110, 140]},
    {"name": "Paul", "expenses": [200, 300, 150, 100]},
    {"name": "Quincy", "expenses": [100, 120, 130, 140]},
    {"name": "Rachel", "expenses": [90, 60, 50, 80]},
    {"name": "Sam", "expenses": [500, 400, 350, 600]},
    {"name": "Tina", "expenses": [150, 200, 300, 250]},
]

def filter_users(users, min_expenses, max_expenses):
    return list(filter(
        lambda user: (sum(user["expenses"]) >= min_expenses) and 
                     (sum(user["expenses"]) <= max_expenses),
        users
    ))

def calculate_total_expenses(user):
    return sum(user["expenses"])

def main(users, min_expenses, max_expenses):
    filtered_users = filter_users(users, min_expenses, max_expenses)

    total_expenses_per_user = list(map(
        lambda user: {"name": user["name"], "total_expenses": calculate_total_expenses(user)},
        filtered_users
    ))

    overall_total_expenses = reduce(
        lambda acc, user: acc + user["total_expenses"],
        total_expenses_per_user, 0
    )

    print("Отфильтрованные пользователи с общей суммой расходов:", total_expenses_per_user)
    print("Общая сумма расходов всех отфильтрованных пользователей:", overall_total_expenses)

main(users, min_expenses=400, max_expenses=500)