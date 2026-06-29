has_high_income = True
has_good_credit = True

if has_high_income and has_good_credit:
    print("Eligible for Loan")
else:
    print("Not Eligible for Loan")


has_high_income = False
has_good_credit = True

if has_high_income and has_good_credit:
    print("Eligible for Loan")
else:
    print("Not Eligible for Loan")


has_high_income = False
has_good_credit = True

if has_high_income or has_good_credit:
    print("Eligible for Loan")
else:
    print("Not Eligible for Loan")


has_high_income = False
has_good_credit = False

if has_high_income or has_good_credit:
    print("Eligible for Loan")
else:
    print("Not Eligible for Loan")

has_high_income = True
has_criminal_record = False

if has_high_income and not has_criminal_record:
    print("Eligible for Loan")
else:
    print("Not Eligible for Loan")

has_high_income = True
has_criminal_record = True

if has_high_income and not has_criminal_record:
    print("Eligible for Loan")
else:
    print("Not Eligible for Loan")

has_high_income = False
has_criminal_record = False

if has_high_income or not has_criminal_record:
    print("Eligible for Loan")
else:
    print("Not Eligible for Loan")


has_high_income = False
has_criminal_record = True

if has_high_income or not has_criminal_record:
    print("Eligible for Loan")
else:
    print("Not Eligible for Loan")

