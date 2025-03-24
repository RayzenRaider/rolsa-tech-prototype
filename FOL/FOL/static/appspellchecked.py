# This is the code allows the booking system to work as it should, above each set I have put comments describing the code of it incase any code that may be hard to understand. 
# Furthermore, this project has been given help by a Steve Stroud who helped with the code. 
import csv
import os
from flask import Flask, render_template, request
from datetime import *
import pandas as pd
app = Flask(__name__) 
# The testing of all code was undertaken by Cia Roxburgh and Callum Rynhart-Albert

# Now this set of code checks the users inputted data to see if they are a student on system. 
# Code help given by Cia Roxburgh
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
        # Now the line above goes into the CSV file and gets the first value it finds and checks it against the users input (which is below), if the data doesn't match it run back through the CSV - (next line)
        # with a plus one to the row it checks, so if it finds it on row two, it keeps the two value and checks to see if the password on the row matches as well, if it does then it loads the page back for - (next line)
        # them to try again. 
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

# Now this set of code checks the users inputted data to see if they are a staff member on system. 
# Code help given by Cia Roxburgh
def details_check_staff(Name, Password):
    test = []
    with open('Staff.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            test.append(row)
        tries = 0
        row_search = 0
        name_check = test[row_search].get('Name', '').strip()
        # Now the line above goes into the CSV file and gets the first value it finds and checks it against the users input (which is below), if the data doesn't match it run back through the CSV - (next line)
        # with a plus one to the row it checks, so if it finds it on row two, it keeps the two value and checks to see if the password on the row matches as well, if it does then it loads the page back for - (next line)
        # them to try again. 
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

# These functions allow for the needed files to be readable on the webpage. 
def CSV_check():
    equipment_log.to_html('Equipment_log.html')

# The reason for the two of them is that, some files don't need to be seen by the students so this function has been made to avoid some files being made for less than optimal reasons. 
def CSV_check_staff():
    equipment_log.to_html('Equipment_log.html')
    booking_log.to_html('Booking_log.html')
    student_log.to_html('Student_log.html')

# This loads the first page to appear, this has been done so the system is more secure than just letting them into a homepage. 
@app.route('/')
def first_page():
   return render_template('index.html')

# The code below collects the users entered data and stores it in a variable which is then checked against the CSV file, then if they have entered the correct data it lets them in, 
# if not the code will reload the page letting them try again. 
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

# The code below collects the users entered data and stores it in a variable which is then checked against the CSV file, then if they have entered the correct data it lets them in, 
# if not the code will reload the page letting them try again. 
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

# This code renders the homepage for students which allows them to make a booking for equipment, plan to put a CSV file which can be viewed to see what is in stock. 
@app.route('/Homepage')
def Homepage():
    return render_template('Homepage.html')
# This define lets the user sign up to the site which requires them to  input their student number, password and email. 
# Which is then stored in the CSV file.
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

# checks for the current date and if the date for the booking is today or later
def past_date(Date_of_booking):
    Date_hold = datetime.fromisoformat(Date_of_booking)
    Todays_date = datetime.now()
    if Date_hold <= Todays_date:
        return False
    else:
        return True

# check to see if the date of return is after the date of booking
def selected_date(Date_of_booking, Date_of_return):
    Date_hold_for_booking = datetime.fromisoformat(Date_of_booking)
    Todays_date = datetime.now()
    Date_hold_for_return = datetime.fromisoformat(Date_of_return)
    if Date_hold_for_booking <= Todays_date or Date_hold_for_return <= Date_hold_for_booking:
        return False
    else:
        return True
    
# This code makes the bookings for the students to make booking for equipment, they need to enter their data just so we are sure about who is making the booking. 
# Once the data has been entered into the HTML it is then append to the CSV and then displays a confirmation message allowing them back to the homepage. 
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

# This is the code that leads to the HTML file for conformation so the user knows their booking has been made. 
@app.route('/Confirmation')
def Confirmation():
    return render_template('Confirmation.html')

# This takes staff to their homepage where they also can make bookings. (plan to allow them to see the CSV file containing all bookings so they can check to see if any equipment is missing)
@app.route('/Staff')
def Staff():
    return render_template('Staff_homepage.html')

# This displays a error for the user, this is triggered if the equipment they booked is out of stock
@app.route('/Staff_error')
def Staff_error():
    return render_template('Staff_error.html')

# This code makes the bookings for the Staff to make booking for equipment, they need to enter their data just so we are sure about who is making the booking. 
# Once the data has been entered into the HTML it is then append to the CSV and then displays a confirmation message allowing them back to the homepage. 
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


# next few lines are how the code renders the html files to what is required of it 
# This shows the Staff member that their booking has been logged in the file. 
@app.route('/Staff_conformation')
def staff_confirmation():
    return render_template('Staff_conformation.html')

# This is meant for students so they know who to contact if they any questions about the system. 
# I do plan on asking people to test it get feedback on it. 
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

# allows for the staff to return to the main page after booking
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

# checks to see if the equipment is available to use
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
        # Now the line above goes into the CSV file and gets the first value it finds and checks it against the users input (which is below), if the data doesn't match it run back through the CSV - (next line)
        # with a plus one to the row it checks, so if it finds it on row two, it keeps the two value and checks to see if the password on the row matches as well, if it does then it loads the page back for - (next line)
        # them to try again. 
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
                    # The code below allows the CSV to have a single cell edited so if a item is booked the amount is decreased on the CSV so it stays accurate. 
                    df = pd.read_csv('Equipment.csv')
                    df.Amount[row_search] = fix_amount
                    df.to_csv('Equipment.csv', index=False)
                    return True
            else:
                return False
    tries += 1

# allows for the students to return the booked items
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
        # Now the line above goes into the CSV file and gets the first value it finds and checks it against the users input (which is below), if the data doesn't match it run back through the CSV - (next line)
        # with a plus one to the row it checks, so if it finds it on row two, it keeps the two value and checks to see if the password on the row matches as well, if it does then it loads the page back for - (next line)
        # them to try again. 
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
                    # The code below allows the CSV to have a single cell edited so if a item is booked the amount is decreased on the CSV so it stays accurate. 
                    df = pd.read_csv('Equipment.csv')
                    df.Amount[row_search] = fix_amount
                    df.to_csv('Equipment.csv', index=False)
                    return True
            else:
                return False
    tries += 1

# This code here runs the files so that the site works. 
if __name__ == '__main__':
    app.run(debug=True)
    