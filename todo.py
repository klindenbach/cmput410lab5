from flask import *
import sqlite3

app = Flask(__name__)
app.debug = True
app.config['SERVER_NAME'] = '127.0.0.1:8888'

DATABASE = 'tasks.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def list():
    tasks = query_db("select id, category, priority, description from tasks")
    print tasks
    for task in tasks:
        for field in task:
                print field
    return render_template('list.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add():
    try:
        int(request.form['priority'])
    except:
        return "Priority not an integer"

    category = request.form['category']
    description = request.form['description']
    priority = request.form['priority']
    query_db(
            "insert into tasks (category, description, priority) values(?,?,?)",
            [category, description, priority]
    )
    get_db().commit()
    return redirect(url_for('list'))

@app.route('/delete/<id>', methods=['POST'])
def delete(id):
    query_db("delete from tasks where id=?", id)
    get_db().commit()
    return redirect(url_for('list'))

if __name__ == "__main__":
    app.run()
