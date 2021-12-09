from flask import Flask, request, render_template
from datetime import datetime
import psycopg2
import psycopg2.extras
import uuid
import calendar
import socket

app = Flask(__name__)

psycopg2.extras.register_uuid()
calendar.setfirstweekday(calendar.SUNDAY)

connection = psycopg2.connect("dbname='postgres' user='postgres' host='database' password='testing'")

cursor = connection.cursor()
cursor.execute("select exists(select * from information_schema.tables where table_name=%s)", ('data',))
if (cursor.fetchone()[0]):
  dropdrop   = "DROP TABLE data";
  # Execute the drop table command
  cursor.execute(dropdrop);
create_table = "CREATE TABLE data(id uuid NOT NULL PRIMARY KEY, n_terms varchar, sequence varchar, time_submitted timestamp)"
cursor.execute(create_table)
connection.commit()

# cur.close()
# con.close()

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/fibonacci/<nValue>', methods=['POST'])
def fibonacci(nValue):
  if request.method == 'POST':
    seq = initiateSequence(int(nValue))
    id = uuid.uuid4()
    insert_query = """INSERT INTO data (id, n_terms, sequence, time_submitted) VALUES (%s, %s, %s, %s)"""
    time_submitted = datetime.now()
    new_data = (id, int(nValue), seq, time_submitted)
    cursor.execute(insert_query, new_data)
    connection.commit()
    return render_template('index.html', sequence=seq)

@app.route('/fibonacci/requests/<monthYear>', methods=['POST'])
def monthYearRequests(monthYear):
  monthYearSplit = monthYear.split('-')
  month = int(monthYearSplit[0])
  year = int(monthYearSplit[1])

  numWeeks = len(calendar.monthcalendar(year,month))
  weeks = calendar.monthcalendar(year,month)

  summaryArray = []

  for weekNum in range(numWeeks):
    lowVal = 0
    highVal = 0
    for date in weeks[weekNum]:
      if (date > 0):
        if (lowVal == 0):
          lowVal = date
        elif (date < lowVal):
          lowVal = date
        elif (date > highVal):
          highVal = date

    date_query = """SELECT COUNT(*) 
                    FROM data 
                    WHERE EXTRACT(YEAR FROM time_submitted) = '%s' 
                    and EXTRACT(MONTH FROM time_submitted) = '%s' 
                    and EXTRACT(DAY FROM time_submitted) >= '%s' 
                    and EXTRACT(DAY FROM time_submitted) <= '%s'"""
    cursor.execute(date_query, (year, month, lowVal, highVal))
    monthResults = cursor.fetchone()

    newWeek = { "week": weekNum + 1, "count": monthResults[0] }
    summaryArray.append(newWeek)

  return render_template('index.html', monthlyRequests={
    "summary": summaryArray
  })  

def initiateSequence(num):
  if (num <= 0):
    return 'Please enter a number greater than 0.'
  elif (num == 1):
    return '0'
  else:
    arrSeq = sequence(num, [0, 1])
    return '-'.join(str(n) for n in arrSeq)

def sequence(num, seq):
  if (len(seq) == num):
    return seq
  else:
    count = 1
    while count < num - 1:
      new_val = seq[-2] + seq[-1]
      seq.append(new_val)
      count += 1
    return seq


if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=5000)
