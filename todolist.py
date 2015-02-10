from flask import *
import sqlite3

app = Flask(__name__)
app.debug = True
app.config['SERVER_NAME'] = '127.0.0.1:8888'
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'aslkfjalsdkfj'

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

def create_db():
    db = get_db()
    get_db().execute("create table if not exists tasks (id integer primary key autoincrement, category vchar(256), priority integer, description vchar(256))")
    db.commit()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        if request.form["username"] == "user" and \
           request.form["password"]== "pass":
            session['user'] = request.form["username"]
            return redirect('/')
        else:
            return render_template('login.html', error="Bad username or password")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/')
def list(errors=None):
    if 'user' not in session:
        return login()

    create_db()
    tasks = query_db("select id, category, priority, description from tasks")
    print tasks
    for task in tasks:
        for field in task:
                print field
    return render_template('list.html', tasks=tasks, error=errors)

@app.route('/add', methods=['POST'])
def add():
    if 'user' not in session:
        return login()

    try:
        int(request.form['priority'])
    except:
        return list("Priority must be an integer")

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
    if 'user' not in session:
        return login()

    query_db("delete from tasks where id=?", id)
    get_db().commit()
    return redirect(url_for('list'))

if __name__ == "__main__":
    app.run()
