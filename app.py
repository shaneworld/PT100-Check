from flask import Flask
from flask import render_template, request, flash, redirect
import sqlite3, os

app = Flask(__name__)

app.config['DATABASE'] = 'database.db'
app.config['SECRET_KEY'] = 'ewfwef35sshjkl'

# Create a database for history and metadata
def create_database():
    if not os.path.exists(app.config['DATABASE']):
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        # Create the database if it doesn't exsit
        cursor.execute('CREATE TABLE IF NOT EXISTS resistance_temperature (temperature REAL PRIMARY KEY, resistance REAL)')
        cursor.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, temperature REAL, resistance REAL)')
        metadata = [(-200.0, 18.52), (-190.0, 22.83), (-180.0, 27.10), (-170.0, 31.34), 
                    (-160.0, 35.54), (-150.0, 39.72), (-140.0, 43.88), (-130.0, 48.0), 
                    (-120.0, 52.11), (-110, 56.19),(-100.0, 60.25), (-90.0, 64.3), 
                    (-80.0, 68.33), (-70.0, 72.33), (-60.0, 76.33), (-50.0, 80.31), 
                    (-40.0, 84.27), (-30.0, 88.22), (-20.0, 92.16), (-10.0, 96.09), 
                    (0.0, 100), (10.0, 103.9), (20.0, 107.79), (30.0, 111.67), (40.0, 115.54), 
                    (50.0, 119.4), (60.0, 123.24), (70.0, 127.07), (80.0, 130.89), (90.0, 134.70), 
                    (100.0, 138.50), (110.0, 142.29), (120.0, 146.06), (130.0, 149.82), (140.0, 153.58),
                    (150.0, 157.33), (160.0, 161.05), (170.0, 164.77), (180.0, 168.48), (190.0, 172.17),
                    (200.0, 175.86), (210.0, 179.53), (220.0, 183.19), (230.0, 186.84), (240.0, 190.47),
                    (250.0, 194.10), (260.0, 197.71), (270.0, 201.31), (280.0, 204.90), (290.0, 208.48),
                    (300.0, 212.05), (310.0, 215.61), (320.0, 219.15), (330.0, 222.68), (340.0, 226.21),
                    (350.0, 229.72), (360.0, 233.21), (370.0, 236.70), (380.0, 240.18), (390.0, 243.64),
                    (400.0, 247.09), (410.0, 250.53), (420.0, 253.96), (430.0, 257.38), (440.0, 260.78),
                    (450.0, 264.18), (460.0, 267.56), (470.0, 270.93), (480.0, 274.29), (490.0, 277.64),
                    (500.0, 280.98), (510.0, 284.30), (520.0, 287.62), (530.0, 290.92), (540.0, 294.21),
                    (550.0, 297.49), (560.0, 300.75), (570.0, 304.01), (580.0, 307.25), (590.0, 310.49),
                    (600.0, 313.71), (610.0, 316.92), (620.0, 320.12), (630.0, 323.30), (640.0, 326.48),
                    (650.0, 329.64), (660.0, 332.79)]
        cursor.executemany('INSERT INTO resistance_temperature (temperature, resistance) VALUES (?, ?)', metadata)
        conn.commit()
        conn.close()

@app.route("/", methods = ["GET", "POST"])
def search():
    # Initialize the result
    result_temp = 0
    result_res = 0

    if request.method == "POST":
        # connect to the database
        with sqlite3.connect(app.config['DATABASE']) as conn:
            cursor = conn.cursor()

            # Handle search temp
            if "search_temp" in request.form:
                result_res = request.form.get("resistance")
                # Input is none
                if not result_res or result_res.strip() == "":
                    flash('输入不能为空！', 'error')
                    return render_template("inquire.html")
                # Input is invalid
                try:
                    result_res = float(result_res)
                except ValueError:
                    flash('请输入有效数据！', 'error')
                    return render_template("inquire.html")
                # Input out of range
                if result_res > 326.48 or result_res < 18.52:
                    flash('电阻值超出范围！', 'error')
                    return render_template("inquire.html")

                # Try to get the resistance = res
                cursor.execute('SELECT temperature FROM resistance_temperature WHERE resistance = ?', (result_res,))
                equal = cursor.fetchone()
                if equal:
                    result_temp = equal[0]
                else:
                    # Get the resistance < res
                    cursor.execute('SELECT resistance, temperature FROM resistance_temperature WHERE resistance < ? ORDER BY resistance DESC LIMIT 1', (result_res,))
                    less = cursor.fetchall()
                    # Get the resistance > res
                    cursor.execute('SELECT resistance, temperature FROM resistance_temperature WHERE resistance > ? ORDER BY resistance ASC LIMIT 1', (result_res,))
                    more = cursor.fetchall()
                    # Calculate temperature
                    if less and more:
                        k = (more[0][0] - less[0][0]) / 10
                        b = more[0][0] - k * more[0][1]
                        result_temp = round((result_res - b) / k, 2)

                # Insert into history
                cursor.execute('INSERT INTO history (temperature, resistance) VALUES (?, ?)', (result_temp, result_res))
                conn.commit()

            # Handle search resistance
            if "search_res" in request.form:
                result_temp = request.form.get("temperature")
                if result_temp is None or result_temp.strip() == "":
                     flash('输入不能为空！', 'error')
                     return render_template("inquire.html")
                try:
                    result_temp = float(result_temp)
                except ValueError:
                    flash('请输入有效数据！', 'error')
                    return render_template("inquire.html")
                # Input out of range
                if result_temp > 660.0 or result_temp < -200.0:
                    flash('温度超出范围！', 'error')
                    return render_template("inquire.html")

                # Try to get the temperature = temp
                cursor.execute('SELECT resistance FROM resistance_temperature WHERE temperature = ?', (result_temp,))
                equal = cursor.fetchone()
                if equal:
                    result_res = equal[0]
                else:
                    # Get the temperature < temp
                    cursor.execute('SELECT temperature, resistance FROM resistance_temperature WHERE temperature < ? ORDER BY temperature DESC LIMIT 1', (result_temp,))
                    less = cursor.fetchall()
                    # Get the resistance > res
                    cursor.execute('SELECT temperature, resistance FROM resistance_temperature WHERE temperature > ? ORDER BY temperature ASC LIMIT 1', (result_temp,))
                    more = cursor.fetchall()
                    # Calculate temperature
                    if less and more:
                        k = (more[0][1] - less[0][1]) / 10
                        b = more[0][1] - (k * more[0][0])
                        result_res = round((k * result_temp) + b, 2)

                # Insert into history
                cursor.execute('INSERT INTO history (temperature, resistance) VALUES (?, ?)', (result_temp, result_res))
                conn.commit()

        return render_template("inquire.html", temp = result_temp, res = result_res)
    return render_template("inquire.html")

@app.route("/history", methods=["GET", "POST"])
def history():
    with sqlite3.connect(app.config['DATABASE']) as conn:
        cursor = conn.cursor()
        # Clear all history
        if request.method == "POST":
            cursor.execute('DELETE FROM history')
            conn.commit()
            return render_template("history.html")
        else:
            cursor.execute('SELECT id, temperature, resistance FROM history')
            hist = cursor.fetchall()
            return render_template("history.html", history = hist)

@app.route('/delhistory/<int:id>')
def delhistory(id):
    # Delete history
    with sqlite3.connect(app.config['DATABASE']) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM history WHERE id = ?', (id,))
        conn.commit()
    return redirect('/history')


if __name__ == "__main__":
    create_database()
    app.run(debug=True)
