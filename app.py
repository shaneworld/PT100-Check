from flask import Flask
from flask import render_template, request, flash, redirect
import sqlite3, os

app = Flask(__name__)

app.config['DATABASE'] = 'database.db'
app.config['SECRET_KEY'] = 'ewfwef35sshjkl'

# Create a database for history and metadata
def create_database():
    if not os.path.exists(app.config['DATABASE']):
        with sqlite3.connect(app.config['DATABASE']) as conn:
            cursor = conn.cursor()
            # Create the database if it doesn't exsit
            cursor.execute('CREATE TABLE IF NOT EXISTS resistance_temperature (temperature REAL PRIMARY KEY, resistance REAL)')
            cursor.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, temperature REAL, resistance REAL)')
            metadata = [(-200.0, 18.4932), (-190.0, 22.8031), (-180.0, 27.0779), (-170.0, 31.3200), 
                        (-160.0, 35.5313), (-150.0, 39.7137), (-140.0, 43.8691), (-130.0, 47.9993), 
                        (-120.0, 52.1058), (-110, 56.1903),(-100.0, 60.2541), (-90.0, 64.2987), 
                        (-80.0, 68.3251), (-70.0, 72.3346), (-60.0, 76.3282), (-50.0, 80.3068), 
                        (-40.0, 84.2713), (-30.0, 88.2222), (-20.0, 92.1603), (-10.0, 96.0861), 
                        (0.0, 100.0), (10.0, 103.9022), (20.0, 107.7928), (30.0, 111.6718), (40.0, 115.5392), 
                        (50.0, 119.3951), (60.0, 123.2392), (70.0, 127.0718), (80.0, 130.8928), (90.0, 134.7022), 
                        (100.0, 138.5000), (110.0, 142.2862), (120.0, 146.0608), (130.0, 149.8237), (140.0, 153.5751),
                        (150.0, 157.3149), (160.0, 161.0430), (170.0, 164.7596), (180.0, 168.4645), (190.0, 172.5266),
                        (200.0, 175.8396), (210.0, 179.5097), (220.0, 183.1683), (230.0, 186.8152), (240.0, 190.4505),
                        (250.0, 194.0743), (260.0, 197.6864), (270.0, 201.2869), (280.0, 204.8758), (290.0, 208.4531),
                        (300.0, 212.0188), (310.0, 215.5729), (320.0, 219.1154), (330.0, 222.6463), (340.0, 226.1656),
                        (350.0, 229.6733), (360.0, 233.1693), (370.0, 236.6538), (380.0, 240.1267), (390.0, 243.5879),
                        (400.0, 247.0376), (410.0, 250.4757), (420.0, 253.9021), (430.0, 257.3170), (440.0, 260.7202),
                        (450.0, 264.1119), (460.0, 267.4919), (470.0, 270.8603), (480.0, 274.2172), (490.0, 277.5624),
                        (500.0, 280.8960), (510.0, 284.2180), (520.0, 287.5284), (530.0, 290.8272), (540.0, 294.1144),
                        (550.0, 297.3901), (560.0, 300.6540), (570.0, 303.9064), (580.0, 307.1472), (590.0, 310.3764),
                        (600.0, 313.5940), (610.0, 316.8000), (620.0, 319.9944), (630.0, 323.1771), (640.0, 326.3483),
                        (650.0, 329.5079), (660.0, 332.6558), (670.0, 335.7922), (680.0, 338.9169), (690.0, 342.0301),
                        (700.0, 345.1316), (710.0, 348.2215), (720.0, 315.2999), (730.0, 354.3666), (740.0, 357.4217),
                        (750.0, 360.4653), (760.0, 363.4972), (770.0, 366.5175), (780.0, 369.5262), (790.0, 372.5233),
                        (800.0, 375.5088), (810.0, 378.4827), (820.0, 381.4450), (830.0, 384.3957), (840.0, 387.3348),
                        (850.0, 390.2623)]
            cursor.executemany('INSERT INTO resistance_temperature (temperature, resistance) VALUES (?, ?)', metadata)
            conn.commit()

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
