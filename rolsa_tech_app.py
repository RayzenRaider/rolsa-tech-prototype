from flask import Flask, request, render_template, redirect, flash, url_for, make_response
import pandas as pd
import requests
import csv
import os
from datetime import datetime
import uuid
# ^^^ VITAL DEPENDENCIES, DO NOT MESS WITH UNLESS MAKING CHANGES TO CODE AND IMPLEMENTING/REMOVING DEPENDENCIES
app = Flask(__name__)
app.secret_key = os.urandom(24)
# to senior dev / rolsa technologies employees, the 'app.secret_key' line above needs to be set to your very own secret flask session key for sessions (cookies) to work. For testing and prototype purposes
# it is set to 'app.secret_key = os.urandom(24)' (creates a random 24 digit long secret key), but if you want to produce your very own key you need to use 'app.secret_key = 'rolsa-tech-secret-key''

# USER DETAIL VERIFICATION SYSTEM, USED FOR 'Sign In' SYSTEM TO DIFFRENTIATE BETWEEN EXISTING USERS AND NON-EXISTING USERS
def detail_verification_user(name, password, email):
    try:
        with open('users.csv', 'r') as file:
            csv_reader = csv.DictReader(file)
            users = list(csv_reader)
            
            matching_users = [user for user in users 
                if user.get('name', '').strip() == name 
                and user.get('Email', '').strip() == email]
            
            if matching_users:
                return matching_users[0].get('password', '').strip() == password
            return False
        
    except FileNotFoundError:
        return False

# STAFF DETAIL VERIFICATION SYSTEM, USED FOR 'Sign In' SYSTEM TO DIFFRENTIATE BETWEEN USER AND STAFF ACCOUNTS
def details_verification_staff(name, password, email):
    try:
        with open('staff.csv', 'r') as file:
            csv_reader = csv.DictReader(file)
            staff = list(csv_reader)
            
            matching_staff = [user for user in staff 
                if user.get('name', '').strip() == name 
                and user.get('Email', '').strip() == email]
            
            if matching_staff:
                return matching_staff[0].get('password', '').strip() == password
            return False
        
    except FileNotFoundError:
        return False
    
# HOMEPAGE, LINKS TO ALL OF THE OTHER SYSTEMS
# HAS A VERIFICATION SYSTEM TO REDIRECT LOGGED IN USERS / STAFF AFTER SCHEDULE COMPLETION OR MODIFICATION
@app.route('/')
def home_page():
    session_id = request.cookies.get('api-session-id')
    if session_id:
        is_staff = request.cookies.get('is-staff') == 'true'
        
        if is_staff:
            return redirect(url_for('staff_home_page'))
        else:
            return redirect(url_for('user_home_page'))
        
    return render_template('home_page.html')

@app.route('/user_home')
def user_home_page():
    if not request.cookies.get('api-session-id'):
        flash('Please sign in first')
        return redirect(url_for('sign_in'))
    return render_template('user_home_page.html')

@app.route('/staff_home')
def staff_home_page():
    if not request.cookies.get('api-session-id'):
        flash('Please sign in first')
        return redirect(url_for('sign_in'))
    
    is_staff = request.cookies.get('is-staff') == 'true'
    if not is_staff:
        flash('Invalid Access')
        return redirect(url_for('home_page'))
    
    return render_template('staff_home_page.html')

# SIGN IN SYSTEM, REQUIRES THE USERS ACCOUNT PASSWORD AND EMAIL
# HAS A STAFF CHECK BOX, IF TICKED INTEAD LOGS INTO STAFF ACCOUNT
# USES TWO DIFFERENT SERVERS, USER AND STAFF
# IF ACCOUNT NOT PRESENT IN STAFF WHEN STAFF BOX IS CHECKED, FLASHES A MESSAGE
# IF ACCOUNT NOT PRESENT IN USER WHEN STAFF BOX IS UNCHECKED, FLASHES A MESSAGE AND REQUESTS USER GOES TO SIGN UP PAGE IF THEY HAVE NO ACCOUNT
@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        name = request.form.get('name', '')
        password = request.form.get('password', '')
        email = request.form.get('email', '')
        is_staff = request.form.get('is_staff') == 'on'
        verification = details_verification_staff if is_staff else detail_verification_user
        
        if verification(name, password, email):
            client = RestClient(name, email, is_staff)
            session = client.session
            
            if session:
                response = make_response(render_template('staff_home_page.html' if is_staff else 'user_home_page.html'))
                response.set_cookie('api-session-id', session.headers['api-session-id'])
                response.set_cookie('user-name', name)
                response.set_cookie('user-email', email)
                response.set_cookie('is-staff', str(is_staff).lower())
                return response
            
        flash('One of your inputs was incorrect. Please try again.')
        return redirect(url_for('sign_in'))
        
    return render_template('sign_in.html')

# SIGN UP SYSTEM, REQUIRES THE USER TO ENTER THEIR USERNAME, A PASSWORD, THEIR EMAIL AND TO ACCEPT THE TOS ROLSA TECHNOLOGIES APPLIES
# OPTIONAL FIELDS INCLUDE PHONE NUMBER AND DASHBOARD UPDATES NEWSLETTER
# WILL CHECK FOR ALREADY EXISTING USERS VIA EMAIL ENTERED, IF DETECTED FLASHES A MESSAGE
# CREATES THE ACCOUNT IF ALL DATA MATCHES UP AND REDIRECTS TO HOMEPAGE WITH SESSION ID
# IF ALL ELSE FAILS AND SYSTEM SOMEHOW FUMBLES, FLASHES AN ERROR MESSAGE AND REQUESTS USER TO TRY AGAIN
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            password = request.form.get('password', '').strip()
            email = request.form.get('email', '').strip()
            accept_tos = request.form.get('accept_tos') == 'on'
            subscribe_email = request.form.get('subscribe_email') == 'on'
        
            if not all([name, password, email]):
                flash('Please fill in all required fields')
                return redirect(url_for('sign_up'))
        
            if not accept_tos:
                flash('Please accept the Terms of Service to create an account')
                return redirect(url_for('sign_up'))
            
            if detail_verification_user(name, password, email) or details_verification_staff(name, password, email):
                flash("This email is already registered. Please use a different email or recover your account by using our recovery system.\n\
                    If you cannot recover your account as it had been compromised, please contact Rolsa Technologies user support via Email or Phone.")
                return redirect(url_for('sign_up'))
            
            try:
                with open('users.csv', 'r', newline='') as file:
                    existing_content = file.read()
                
                if existing_content and not existing_content.endswith('\n'):
                    existing_content += '\n'
                
                with open('users.csv', 'w', newline='') as file:
                    file.write(existing_content)
                    writer = csv.DictWriter(file, fieldnames=['name', 'password', 'Email', 'subscribed'])
                    if not existing_content:
                        writer.writeheader()
                        
                    writer.writerow({
                        'name': name,
                        'password': password,
                        'Email': email,
                        'subscribed': subscribe_email
                    })

                for log_type in ['consultations', 'installations']:
                    source = f'{log_type}_log.html'
                    dest = f'templates/{log_type}_log.html'

                    if os.path.exists(source):
                        os.replace(source, dest)
                    
                flash('Your account has been registered. Please head to the Sign In page to login.')
                return render_template('home_page_user_side.html')
            
            except Exception as e:
                flash("An error occurred while creating your account. Please try again and verify that you've entered the correct details.")
                return redirect(url_for('sign_up'))
            
        except Exception as e:
            flash("An error occurred while creating your account. Please try again and verify that you've entered the correct details.")
            return redirect(url_for('sign_up'))
            
    return render_template('sign_up.html')

# SIGN OUT SYSTEM
# theres not much to say about this to be honest it just signs you out and clears session cookies
@app.route('/sign_out')
def sign_out():
    response = make_response(redirect(url_for('home_page')))
    
    response.delete_cookie('api-session-id')
    response.delete_cookie('user-name')
    response.delete_cookie('user-email')
    response.delete_cookie('is-staff')
    
    flash('Signed Out Successfully')
    return response


# ACCOUNT RECOVERY SYSTEM, SENDS AN EMAIL WITH A ONE-TIME USE CODE TO THE ENTERED EMAIL IF ASSOCIATED ACCOUNT NAME MATCHES WITHIN SERVER DATABASE
# MUST THEN ENTER THE ONE-TIME USE CODE TO RESET PASSWORD, ONCE RESET REDIRECTS TO 'Sign_In' SYSTEM
# THIS IS UNUSED WITHIN THE PROTOTYPE DUE TO HARDWARE / SYSTEM LIMITATIONS
#@app.route('/account_recovery')
#def account_recovery():
#    return render_template('account_recovery.html')

# MAINTAINS THE CURRENT SESSION CONNECTION TO AVOID UNESSECARY REQUESTS OF DATA
class RestClient:
    _session = None
# Note to employer / Senior Dev, the line below should be changed to the actual domain host used by rolsa technologies if this going is going to be used
    HOST = "rolsatech.com"

    def __init__(self, name, email, is_staff=False):
        self._name = name
        self._email = email
        self._is_staff = is_staff

    @property
    def session(self):
        if self._session:
            return self._session

        try:
            session = requests.Session()
            session.headers.update({
                "api-session-id": str(uuid.uuid4()),
                "user-name": self._name,
                "user-email": self._email,
                "is-staff": str(self._is_staff).lower()
            })
            self._session = session
            return session
        
        except Exception as e:
            print(f"Session creation failed: {str(e)}")
            return None

# SHECULDING SYSTEM DATE VERIFIER
def schedule_date_check(date_str):
    try:
        scheduled_date = datetime.strptime(date_str, '%Y-%m-%d')
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return scheduled_date > today
    
    except ValueError:
        return False

# SCHEDULING SYSTEM SCHEDULING ID MAKER
# i don't know how else to describe this it just makes the associated id for a new schedule.
def next_id(csv_file):
    try:
        df = pd.read_csv(csv_file)
        if df.empty:
            return 1
        return df['associated_ID'].max() + 1
    
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return 1
    
# SCHEDULING SYSTEM SCHEDULE TYPE VERIFIER
def scheduling_check(schedule_type, sub_type):
    try:
        df = pd.read_csv('valid_schedulings.csv')
        valid_schedule = df[
            (df['main_schedule_type'] == schedule_type) & 
            (df['schedule_sub_type_name'] == sub_type) 
        ]
        return not valid_schedule.empty
    
    except FileNotFoundError:
        return False
    
# HTML-BACKUP LOG FOR CSV DATABASE VERIFICATION SYSTEM
# ALSO LETS USERS VIEW HTML VARIANTS OF THEIR SCHEDULES
consultations_log = pd.read_csv('consultations.csv')
installations_log = pd.read_csv('installations.csv')

# CSV DATABASE TO HTML DATABASE SYSTEM
# since this updates as soon as a new schedule is placed, it needs to have its own html_template to use during conversion.
# (if it doesn't have a html_template it will be a pain-point for staff to view (becomes viewer friendly))
# why am I putting so much details into this functions notes? It's a key outstander as its html IN the python program. So people viewing this might go "why is he using html in the python script???"
# + it clears up why im doing it so :smile:
# holy shit i hate this so much why must it break on me, thank god for the grand wizards over at stackoverflow and their problem solving
# ALSO slight warning for senior devs / onviewers trying to view the log files; since the actual host isn't set up yet the return button to the homepage doesn't work correctly (if I am assuming correctly as I've tested it and it pops up with a 404 error)
# I'm unable to fix this issue myself as I'm not that well versed in html (my main focus is python after all) so it'll have to be left up to the senior dev to fix
def CSV_to_HTML():
    html_template = '''<!DOCTYPE html>
<html>
<head>
    <title>Rolsa Technologies: {title}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="log-container">
            {table_html}
        </div>
        <div class="nav-links">
            <a href="{{ url_for('home_page') }}">Back to Homepage</a>
        </div>
    </div>
</body>
</html>'''

    try:
        try:
            consultations = pd.read_csv('consultations.csv')
            if not consultations.empty:
                table_html = consultations.to_html(
                    classes='styled-table',
                    index=False,
                    border=0,
                    justify='left'
                )
                
            else:
                table_html = "<p>No consultations scheduled.</p>"
                
        except FileNotFoundError:
            table_html = "<p>No consultations scheduled.</p>"

        filled_template = html_template.format(
            title='Consultation Schedules Log',
            table_html=table_html
        )
        
        with open('templates/consultations_log.html', 'w', encoding='utf-8') as f:
            f.write(filled_template)

        try:
            installations = pd.read_csv('installations.csv')
            if not installations.empty:
                # Convert DataFrame to HTML table with styling
                table_html = installations.to_html(
                    classes='styled-table',
                    index=False,
                    border=0,
                    justify='left'
                )
                
            else:
                table_html = "<p>No installations scheduled.</p>"
                
        except FileNotFoundError:
            table_html = "<p>No installations scheduled.</p>"

        filled_template = html_template.format(
            title='Installation Schedules Log',
            table_html=table_html
        )
        
        with open('templates/installations_log.html', 'w', encoding='utf-8') as f:
            f.write(filled_template)

        return True

    except Exception as e:
        print(f"Error generating HTML logs: {str(e)}")
        return False

# CONSULTATION / INSTALLATION SCHEDULING SYSTEM
# USERS CAN SCHEDULE SERVICES WITH ROLSA TECHNOLOGIES
@app.route('/user_scheduling', methods=['GET', 'POST'])
def user_scheduling():
    if not request.cookies.get('api-session-id'):
        flash('Please sign in first')
        return redirect(url_for('sign_in'))
    
    user_name = request.cookies.get('user-name')
    user_email = request.cookies.get('user-email')
    
    if request.method == 'POST':
        schedule_type = request.form.get('schedule_type')
        sub_type = request.form.get('sub_type')
        scheduled_date = request.form.get('scheduled_date')
        deadline_date = request.form.get('deadline_date')
        
        if not schedule_date_check(scheduled_date):
            flash('Invalid scheduling date, date cannot be in the past or today')
            return redirect(url_for('user_scheduling'))
            
        if not schedule_date_check(deadline_date):
            flash('Invalid deadline date, date cannot be in the past or today')
            return redirect(url_for('user_scheduling'))
            
        if not scheduling_check(schedule_type, sub_type):
            flash('Invalid scheduling, please restart')
            return redirect(url_for('user_scheduling'))
            
        csv_file = 'consultations.csv' if schedule_type == 'Consultation' else 'installations.csv'
        get_next_id = next_id(csv_file)
        
        new_schedule = {
            'associated_ID': get_next_id,
            'user': user_name,
            'email': user_email,
            f'type_of_{schedule_type.lower()}': sub_type,
            'date_of_scheduling': scheduled_date,
            'deadline': deadline_date,
            'postponed': False,
            'new_postponed_date': ''
        }
        
        try:
            df = pd.read_csv(csv_file)
        except FileNotFoundError:
            df = pd.DataFrame(columns=[
                'associated_ID', 'user', 'email', 
                f'type_of_{schedule_type.lower()}',
                'date_of_scheduling', 'deadline',
                'postponed', 'new_postponed_date'
            ])
            
        df = df._append(new_schedule, ignore_index=True)
        df.to_csv(csv_file, index=False)
        
        if CSV_to_HTML():
            flash('Successfully Created Schedule')
        else:
            flash('Schedule created but log view may be outdated')
        return redirect(url_for('user_home_page'))
        
    try:
        valid_schedules = pd.read_csv('valid_schedulings.csv')
        schedule_types = valid_schedules['main_schedule_type'].unique()
        sub_types_by_main = {
            main_type: valid_schedules[
                valid_schedules['main_schedule_type'] == main_type
            ]['schedule_sub_type_name'].tolist()
            for main_type in schedule_types
        }
    except FileNotFoundError:
        schedule_types = []
        sub_types_by_main = {}
        
    return render_template(
        'user_scheduling_page.html',
        schedule_types=schedule_types,
        sub_types_by_main=sub_types_by_main
    )

# CSV_to_HTML's LITTLE BROTHER
# HANDLES THE LOG.HTML VIEW
@app.route('/consultations_log')
def consultations_log():
    if not request.cookies.get('api-session-id') or request.cookies.get('is-staff') != 'true':
        flash('Staff access required')
        return redirect(url_for('sign_in'))
    
    CSV_to_HTML()
    return render_template('consultations_log.html')

# CSV_to_HTML's LITTLE BROTHER 2
# HANDLES THE LOG.HTML VIEW
@app.route('/installations_log')
def installations_log():
    if not request.cookies.get('api-session-id') or request.cookies.get('is-staff') != 'true':
        flash('Staff access required')
        return redirect(url_for('sign_in'))
    
    CSV_to_HTML()
    return render_template('installations_log.html')

# CONSULTATION / INSTALLATION ASSIGNMENT SYSTEM
# STAFF ARE ABLE TO VIEW ANY CURRENTLY SCHEDULED SERVICE REQUESTS OF ROLSA TECHNOLOGIES
@app.route('/staff_scheduling', methods=['GET', 'POST'])
def staff_scheduling():
    if not request.cookies.get('api-session-id'):
        flash('Please sign in first')
        return redirect(url_for('sign_in'))
        
    is_staff = request.cookies.get('is-staff') == 'true'
    
    if not is_staff:
        flash('Invalid Access')
        return redirect(url_for('home_page'))
    
    try:
        CSV_to_HTML()
        
        consultations = pd.read_csv('consultations.csv')
        installations = pd.read_csv('installations.csv')
        
        stats = {
            'total_consultations': len(consultations) if not consultations.empty else 0,
            'total_installations': len(installations) if not installations.empty else 0,
            'pending_consultations': len(consultations[~consultations['postponed']]) if not consultations.empty else 0,
            'pending_installations': len(installations[~installations['postponed']]) if not installations.empty else 0
        }
        
        return render_template('staff_scheduling_page.html', stats=stats)
        
    except Exception as e:
        flash('Error loading schedule data')
        return redirect(url_for('staff_home_page'))

# CARBON FOOTPRINT CALCULATOR
# LETS USERS AND STAFF ALIKE CALCULATE THEIR ANNUAL CARBON EMISSIONS TO SEE HOW THEY CAN CUT DOWN ON THEIR AMOUNT.
# after testing this myself i can proudly say that oh my god we make so much even when using so little why and how.
# source for values comes from https://justenergy.com/blog/how-to-calculate-your-carbon-footprint/#:~:text=Multiply%20your%20monthly,aluminum%20and%20tin
@app.route('/footprint_calculator', methods=['GET', 'POST'])
def footprint_calculator():
    if not request.cookies.get('api-session-id'):
        flash('Please sign in first')
        return redirect(url_for('sign_in'))
    
    try:
        df = pd.read_csv('carbon_footprint_calculator_values.csv')
        emission_types = df['type_of_emission'].tolist()
        
        if request.method == 'POST':
            try:
                total_footprint = 0
                
                for emission_type in emission_types:
                    value = float(request.form.get(emission_type, 0))
                    multiplier = float(df[df['type_of_emission'] == emission_type]['multiplication_value'].iloc[0])
                    addition = float(df[df['type_of_emission'] == emission_type]['addition_value'].iloc[0])
                    
                    footprint = (value * multiplier) + addition
                    total_footprint += footprint
                
                if total_footprint < 6000:
                    category = "Excellent"
                    message = "You are one of many to produce the least amount of carbon emissions per year, we don't have any advice for you."
                    color = "green"
                    
                elif total_footprint <= 15999:
                    category = "Normal"
                    message = "You produce the average household's worth of carbon emissions per year, we would advise you try and go lower."
                    color = "orange"
                    
                elif total_footprint <= 22000:
                    category = "Bad"
                    message = "You produce a high amount of carbon emissions per year, seek a way to reduce the amount you produce."
                    color = "darkorange"
                    
                else:
                    category = "VERY Bad"
                    message = "You produce one of the largest amounts of carbon emissions per year, PLEASE seek ways to reduce the amount you produce."
                    color = "red"
                
                return render_template(
                    'carbon_footprint_calculator.html',
                    emission_types=emission_types,
                    result=True,
                    total_footprint=round(total_footprint, 2),
                    category=category,
                    message=message,
                    color=color
                )
            except ValueError:
                flash('Please enter valid numbers for all fields')
                return render_template('carbon_footprint_calculator.html', emission_types=emission_types, result=False)
                
        return render_template('carbon_footprint_calculator.html', emission_types=emission_types, result=False)
        
    except Exception as e:
        print(f"Calculator error: {str(e)}")  # Log the error
        flash('Error loading calculator. Please try again.')
        return render_template('carbon_footprint_calculator.html', emission_types=[], result=False)

# DASHBOARD SYSTEM, LINKED TO FOLDER SERVER THAT HOUSES SEVERAL '.txt' FILES RELATING TO THE MOST RECENT GREEN ENERGY TECHNOLOGIES
# PROVIDES A RANDOM '.txt' FILE IF ONE IS NOT CHOSEN WHEN BROWSING THROUGH DASHBOARD, OTHERWISE WILL PROVIDE THE SELECTED ONE
# i have zero clue how to make an info board so this might remain empty by the time my hours are up (if it is empty then please forgive me as i was focusing on making the program function properly before moving on)
# sucks that this is one of the main key points too
#@app.route('/info_board')
#def info_board():
#    if not request.cookies.get('api-session-id'):
#        flash('Please sign in first')
#        return redirect(url_for('sign_in'))
#    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)