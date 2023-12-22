# app.py
from flask import Flask, render_template, request, redirect, url_for
import pyodbc
import config

app = Flask(__name__)

@app.route('/env')
def env():
    return '<pre>' + '\n'.join(f'{key}: {value}' for key, value in os.environ.items()) + '</pre>'


@app.route('/')
def index():
    conn_string = config.DB_CONNECTION_STRING
    try:
        conn = pyodbc.connect(conn_string)
        cursor = conn.cursor()
        conn.close()
        return redirect(url_for('login'))
    except Exception as e:
        return f"An error occurred: {e}"


#register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # Hash passwords in production
        is_admin = False  # By default, users are not admins

        conn_string = config.DB_CONNECTION_STRING
        try:
            conn = pyodbc.connect(conn_string)
            cursor = conn.cursor()
            # Insert new user record into the database
            cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", (username, password, is_admin))
            conn.commit()
            conn.close()
            return "Registration successful!"
        except Exception as e:
            return f"An error occurred: {e}"
    else:
        return render_template('register.html')


#login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn_string = config.DB_CONNECTION_STRING
        try:
            conn = pyodbc.connect(conn_string)
            cursor = conn.cursor()
            # Assuming you are storing 'is_admin' as a bit (0 or 1) in the database
            cursor.execute("SELECT id, username, is_admin FROM users WHERE username = ? AND password = ?", (username, password))
            user_record = cursor.fetchone()

            conn.close()
            if user_record:
                if user_record.is_admin:
                    return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
                else:
                    return redirect(url_for('user_dashboard'))  # Redirect to user dashboard
            else:
                return "Login failed. Please check your username and password."
        except Exception as e:
            return f"An error occurred: {e}"
    else:
        return render_template('login.html')



#admin dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    # Admin dashboard logic
    return render_template('admin_dashboard.html')

#customer dashboard
@app.route('/user_dashboard')
def user_dashboard():
    # User dashboard logic
    return render_template('user_dashboard.html')



#health information page
from datetime import datetime

@app.route('/insurance_form', methods=['GET', 'POST'])
def insurance_form():
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        height = float(request.form['height'])
        weight = float(request.form['weight'])
        smoking = 'smoking' in request.form
        chronic_disease = request.form['chronic_disease']
        state = request.form['state']
        country = request.form['country']
        # Assume chronic_diseases is a comma-separated string
        chronic_diseases_input = request.form['chronic_disease']
        chronic_diseases = chronic_diseases_input.split(',')
        # List of recognized chronic diseases
        recognized_diseases = ['Alcohol', 'Arthritis', 'Cancer', 'Chronic Kidney Disease', 
                               'Chronic Obstructive Pulmonary', 'Diabetes', 'Epilepsy', 'Healthy Aging', 
                               'Healthy School', 'Inflammatory Bowel Disease', 'Nutrition Physical Activity Obesity', 
                               'Reproductive Health', 'Sleep Disorders', 'Smoking and Tobacco Use', 
                               'Water Fluoridation', 'Workplace Health']
        # Calculate age
        birth_date = datetime.strptime(dob, '%Y-%m-%d')
        age = int((datetime.now() - birth_date).days / 365.25)

        # Initialize risk score
        risk_score = 0

        # Add points based on age
        if age > 50:
            risk_score += 2
        elif age > 30:
            risk_score += 1

        # Add points for smoking
        if smoking:
            risk_score += 2

        # Add points for chronic disease
        if chronic_disease:
            risk_score += 3

        # Add points based on BMI (Body Mass Index)
        bmi = weight / (height / 100) ** 2  # Height in cm to meters
        if bmi > 30:
            risk_score += 2
        elif bmi > 25:
            risk_score += 1

        # Add points for each recognized chronic disease
        for disease in chronic_diseases:
            if disease.strip() in recognized_diseases:
                risk_score += 1  # Add 1 point per disease, adjust as needed

        # Determine risk level based on score
        if risk_score > 5:
            risk_level = 'High'
        elif risk_score > 3:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'

        # Redirect to risk assessment page with the risk level
        return redirect(url_for('risk_assessment', risk_level=risk_level))
    else:
        return render_template('insurance_form.html')

@app.route('/risk_assessment')
def risk_assessment():
    risk_level = request.args.get('risk_level', 'Unknown')
    return render_template('risk_assessment.html', risk_level=risk_level)


#quote agree
@app.route('/quote_response', methods=['POST'])
def quote_response():
    response = request.form.get('quote_response')
    if response == 'agree':
        # User agreed with the quote, proceed to payment
        return redirect(url_for('payment'))
    else:
        # User disagreed with the quote, redirect to another page or show a message
        return "Thank you for considering our services. If you have any questions, please contact us."


#payment
@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        # Simulate processing payment details
        account_number = request.form['account_number']
        # You would typically process payment details here
        # For our fake payment page, we'll just display a confirmation message
        return "Payment successful for account number: " + account_number
    else:
        return render_template('payment.html')



if __name__ == '__main__':
    app.run(debug=True)