import csv
import os
from flask import Flask, render_template, request
from datetime import *
import pandas as pd
app = Flask(__name__) 
def details_check(Student_number, Password):
    count= int()
    for row in open('Student.csv'):
        count+= 1
    test = []
    with open('Student.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            test.append(row)
        tries = 0
        row_search = 0
        number_check = test[row_search].get('Student Number', '').strip() 
        while number_check != Student_number and tries <=3 and row_search < len(test):              
            row_search +=1
            number_check = test[row_search].get('Student Number').strip()
        else:
            password_check = test[row_search].get('Password').strip()
            if password_check == Password and number_check == Student_number:
                return True
            else:
                return False
    tries += 1

def details_check_staff(Name, Password):
    test = []
    with open('Staff.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            test.append(row)
        tries = 0
        row_search = 0
        name_check = test[row_search].get('Name', '').strip()
        while name_check != Name and tries <=3 and row_search < len(test):
            row_search +=1
            name_check = test[row_search].get('Name', '').strip()
        else:
            password_check = test[row_search].get('Password').strip()
            if password_check == Password and name_check == Name:
                return True
            else:
                return False
    tries += 1

equipment_log = pd.read_csv('Equipment.csv')
booking_log = pd.read_csv('Bookings.csv')
student_log = pd.read_csv('Student.csv')

def CSV_check():
    equipment_log.to_html('Equipment_log.html')

def CSV_check_staff():
    equipment_log.to_html('Equipment_log.html')
    booking_log.to_html('Booking_log.html')
    student_log.to_html('Student_log.html')

@app.route('/')
def first_page():
   return render_template('index.html')

@app.route('/sign_in', methods = ['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        Student_number = request.form.get('student_number', type=str)
        if len(Student_number) != 8:
            return render_template('index.html') 
        if Student_number.__contains__('E'):
            return render_template('index.html') 
        Password = request.form.get('password', type=str)
        print(Student_number, Password)
        pass_check = details_check(Student_number, Password)
        if pass_check == True:
            CSV_check()
            os.replace('C:/Users/phant/Documents/FOL/Equipment_log.html', 'C:/Users/phant/Documents/FOL/templates/Equipment_log.html')
            return render_template('Homepage.html')
    return render_template('index.html')

@app.route('/Staff_sign_in', methods = ['GET', 'POST'])
def Staff_sign_in():
    if request.method == 'POST':
        Name = request.form.get('name', type=str)
        Password = request.form.get('password', type=str)
        pass_check = details_check_staff(Name, Password)
        if pass_check == True:
            CSV_check_staff()
            os.replace('C:/Users/phant/Documents/FOL/Equipment_log.html', 'C:/Users/phant/Documents/FOL/templates/Equipment_log.html')
            os.replace('C:/Users/phant/Documents/FOL/Booking_log.html', 'C:/Users/phant/Documents/FOL/templates/Booking_log.html')
            os.replace('C:/Users/phant/Documents/FOL/Student_log.html', 'C:/Users/phant/Documents/FOL/templates/Student_log.html')
            return render_template('Staff_homepage.html')
    return render_template('Staff_sign_in.html')

@app.route('/Homepage')
def Homepage():
    return render_template('Homepage.html')
@app.route('/Register', methods = ['GET', 'POST'])
def Register():
    if request.method == 'POST':
        Student_number = request.form.get('student number')
        if len(Student_number) != 8:
            return render_template('Register.html')
        Password = request.form.get('password')
        Email = request.form.get('email')
        add_user = os.path.isfile('Student.csv')
        with open('Student.csv', 'a', newline = '' ) as file:
            writer = csv.writer(file)
            if not add_user:
                writer.writerow(['Student Number', 'Password', 'Email' ])
                writer.writerow([  Student_number, Password, Email  ])
            else:
                writer.writerow([ Student_number, Password, Email ])
            return render_template('Homepage.html')
    return render_template('Register.html')

def past_date(Date_of_booking):
    Date_hold = datetime.fromisoformat(Date_of_booking)
    Todays_date = datetime.now()
    if Date_hold <= Todays_date:
        return False
    else:
        return True

def selected_date(Date_of_booking, Date_of_return):
    Date_hold_for_booking = datetime.fromisoformat(Date_of_booking)
    Todays_date = datetime.now()
    Date_hold_for_return = datetime.fromisoformat(Date_of_return)
    if Date_hold_for_booking <= Todays_date or Date_hold_for_return <= Date_hold_for_booking:
        return False
    else:
        return True

@app.route('/Booking', methods = ['GET', 'POST'])
def Booking():
    if request.method == 'POST':
        Name = request.form.get('name')
        Email= request.form.get('email')
        Date_of_booking = request.form.get('date of booking')
        date_of_booking_check = past_date(Date_of_booking)
        if date_of_booking_check == False:
            return render_template('Error_page.html')
        elif date_of_booking_check == True:
            Date_of_return = request.form.get('date of return')
            date_of_return_check = selected_date(Date_of_booking,Date_of_return)
            if date_of_return_check == False:
                return render_template('Error_page.html')
            elif date_of_return_check == True:
                Equipment = request.form.get('equipment')
                pass_check = Equipment_check(Equipment)
                if pass_check == True:
                    add_booking = os.path.isfile('Bookings.csv')
                    with open('Bookings.csv', 'a', newline = '' ) as file:
                        writer = csv.writer(file)
                        if not add_booking:
                            writer.writerow(['Name', 'Email', 'Date of Booking', 'Date of Return', 'Equipment' ])
                            writer.writerow([ Name, Email, Date_of_booking, Date_of_return, Equipment ])
                            return render_template('Conformation.html')
                        writer.writerow([ Name, Email, Date_of_booking, Date_of_return, Equipment ])
                        return render_template('Conformation.html')
                elif pass_check == False:
                    return render_template('Error_page.html')
    return render_template('Booking.html')

@app.route('/Confirmation')
def Confirmation():
    return render_template('Confirmation.html')

@app.route('/Staff')
def Staff():
    return render_template('Staff_homepage.html')

@app.route('/Staff_error')
def Staff_error():
    return render_template('Staff_error.html')

@app.route('/Staff_booking', methods = ['GET', 'POST'])
def Staff_booking():
    if request.method == 'POST':
        Name = request.form.get('name')
        Email= request.form.get('email')
        Date_of_booking = request.form.get('date of booking')
        date_of_booking_check = past_date(Date_of_booking)
        if date_of_booking_check == False:
            return render_template('Error_page.html')
        elif date_of_booking_check == True:
            Date_of_return = request.form.get('date of return')
            date_of_return_check = selected_date(Date_of_booking,Date_of_return)
            if date_of_return_check == False:
                return render_template('Error_page.html')
            elif date_of_return_check == True:
                Equipment = request.form.get('equipment')
                pass_check = Equipment_check(Equipment)
                if pass_check == True:
                    add_booking = os.path.isfile('Bookings.csv')
                    with open('Bookings.csv', 'a', newline = '' ) as file:
                        writer = csv.writer(file)
                        if not add_booking:
                            writer.writerow(['Name', 'Email', 'Date of Booking', 'Date of Return', 'Equipment' ])
                            writer.writerow([ Name, Email, Date_of_booking, Date_of_return, Equipment ])
                            return render_template('Staff_conformation.html')
                        writer.writerow([ Name, Email, Date_of_booking, Date_of_return, Equipment ])
                        return render_template('Staff_conformation.html')
                elif pass_check == False:
                    return render_template('Staff_error.html')
    return render_template('Staff_booking.html')


@app.route('/Staff_conformation')
def staff_confirmation():
    return render_template('Staff_conformation.html')

@app.route('/Contact_information')
def Contact_information():
    return render_template('Contact_information.html')

@app.route('/Equipment_table')
def equipment_table():
    return render_template('Equipment_log.html')

@app.route('/Booking_table')
def booking_table():
    return render_template('Booking_log.html')

@app.route('/Student_table')
def student_table():
    return render_template('Student_log.html')

@app.route('/Error_page')
def error():
    return render_template('Error_page.html')
@app.route('/Staff_return', methods = ['GET', 'POST'])

def Staff_return():
    if request.method == 'POST':
        Equipment = request.form.get('equipment')
        Amount_returned = request.form.get('amount returned')
        pass_check = return_check(Equipment,Amount_returned)

        if pass_check == True:
            return render_template('Staff_conformation_for_returns.html')
        elif pass_check == False:
            return render_template('Staff_error_for_returns.html')
    return render_template('Staff_return.html')

def Equipment_check(Equipment):
    count= int()
    for row in open('Student.csv'):
        count+= 1
    test = []
    with open('Equipment.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            test.append(row)
        tries = 0
        row_search = 0
        name_check = test[row_search].get('Name', '').strip() 
        while name_check != Equipment and tries <=3 and row_search < len(test):              
            row_search +=1
            name_check = test[row_search].get('Name').strip()
        else:
            number_check = test[row_search].get('Amount').strip()
            print(number_check)
            if int(number_check) == 0:
                return False
            if name_check == Equipment:
                for row in test:
                    fix_amount = int(number_check) -1
                    print(fix_amount)
                    df = pd.read_csv('Equipment.csv')
                    df.Amount[row_search] = fix_amount
                    df.to_csv('Equipment.csv', index=False)
                    return True
            else:
                return False
    tries += 1

def return_check(Equipment, Amount_returned):
    count= int()
    for row in open('Student.csv'):
        count+= 1
    test = []
    with open('Equipment.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            test.append(row)
        tries = 0
        row_search = 0
        name_check = test[row_search].get('Name', '').strip() 
        while name_check != Equipment and tries <=3 and row_search < len(test):              
            row_search +=1
            name_check = test[row_search].get('Name').strip()
        else:
            number_check = test[row_search].get('Amount').strip()
            print(number_check)
            if name_check == Equipment:
                for row in test:
                    fix_amount = int(number_check) + Amount_returned
                    print(fix_amount)
                    df = pd.read_csv('Equipment.csv')
                    df.Amount[row_search] = fix_amount
                    df.to_csv('Equipment.csv', index=False)
                    return True
            else:
                return False
    tries += 1

if __name__ == '__main__':
    app.run(debug=True)
    