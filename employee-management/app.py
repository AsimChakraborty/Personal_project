from flask import Flask, render_template, request, redirect, url_for, flash

import os
import MySQLdb  

app = Flask(__name__)
app.secret_key = 'your_secret_key' 


UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


db = MySQLdb.connect(host="localhost", user="root", passwd="", db="employee_mgt")
cursor = db.cursor()


@app.route('/')
def index():
  
    query = "SELECT id, name, email, number, dob, photo FROM employees"
    
    try:
        cursor.execute(query)
        employees = cursor.fetchall()  
    except Exception as e:
        print(f"Error fetching data: {e}")
        employees = []

   
    return render_template('index.html', employeesArr=employees)

@app.route('/all-employee')
def allEmployee():
    
    query = "SELECT id, name, email, number, dob, photo FROM employees"
    
    try:
        cursor.execute(query)
        employees = cursor.fetchall()  
    except Exception as e:
        print(f"Error fetching data: {e}")
        employees = []

   
    return render_template('allEmployee.html', employeesArr=employees)


@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
       
        name = request.form['name']
        email = request.form['email']
        dob = request.form['dob']
        phone = request.form['phone']
        
        
        photo_filename = None
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename != '':
                photo_filename = photo.filename
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
                photo.save(photo_path)  

       
        query = """
        INSERT INTO employees (name, email, number, dob, photo)
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            
            cursor.execute(query, (name, email, phone, dob, photo_filename))
            db.commit() 
        except Exception as e:
            db.rollback()  
            print(f"Error inserting data: {e}")
        
        
        return redirect(url_for('index'))

    return render_template('add.html') 

@app.route('/edit_employee/<int:employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    
    query = "SELECT id, name, email, number, dob, photo FROM employees WHERE id = %s"
    
    cursor.execute(query, (employee_id,))
    employee = cursor.fetchone()

    if request.method == 'POST':
       
        name = request.form['name']
        email = request.form['email']
        number = request.form['number']
        dob = request.form['dob']

        
        update_query = """
            UPDATE employees 
            SET name = %s, email = %s, number = %s, dob = %s 
            WHERE id = %s
        """
        cursor.execute(update_query, (name, email, number, dob, employee_id))
        db.commit()
        
        flash('Employee updated successfully!', 'success')
        return redirect(url_for('index'))

    
    return render_template('edit.html', employee=employee)


@app.route('/delete_employee/<int:id>', methods=['GET', 'POST'])
def delete_employee(id):
    query = "DELETE FROM employees WHERE id = %s"
    
    try:
        cursor.execute(query, (id,))
        db.commit()  
        flash('Employee deleted successfully!', 'success')
    except Exception as e:
        db.rollback()  
        flash(f"Error deleting employee: {e}", 'danger')
    
    return redirect(url_for('index'))  

@app.route('/search', methods=['GET'])
def search_employees():
    name = request.args.get('name', '')
    dob = request.args.get('dob', '')
    email = request.args.get('email', '')
    mobile = request.args.get('mobile', '')

    query = "SELECT * FROM employees WHERE 1=1"
    
    params = []
    if name:
        query += " AND name LIKE %s"
        params.append(f"%{name}%")
    if dob:
        query += " AND dob = %s"
        params.append(dob)
    if email:
        query += " AND email LIKE %s"
        params.append(f"%{email}%")
    if mobile:
        query += " AND number LIKE %s"
        params.append(f"%{mobile}%")

    try:
        cursor.execute(query, tuple(params))
        employees = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching data: {e}")
        employees = []

   
    search_params = {
        'name': name,
        'dob': dob,
        'email': email,
        'mobile': mobile
    }

   
    return render_template('index.html', employeesArr=employees, search_params=search_params)


if __name__ == '__main__':
    app.run(debug=True)
