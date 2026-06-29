print("===== Salary Calculator =====")
employee_name = input("\n\nEnter Employee Name: ")
monthly_salary = float(input("Enter Monthly Salary: "))
yrs_of_experience = int(input("Enter Years of Experience: "))
annual_salary = monthly_salary * 12
bonus = annual_salary * 0.15
total_income = annual_salary + bonus

print(f"\n\n------SALARY REPORT------\nEmployee: {employee_name.upper()}\nLength of Name: {len(employee_name)}\nTitle: {employee_name.title()}\nMonthly Salary: {monthly_salary}\nYears of Experience: {yrs_of_experience}\nAnnual Salary: {int(annual_salary)}\nBonus: {int(bonus)}\nTotal Income: {int(total_income)}")
