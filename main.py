from bottle import Bottle, run, route, get, post, request, static_file
from bottle import TEMPLATE_PATH, jinja2_template as template
import sqlite3
import datetime
from const import DB_NAME

app = Bottle()

# Static file
@app.get("/static/<filename:path>")
def css(filename):
    return static_file(filename, root="./static/")

# トップページ
@app.get('/')
def top():
    return template('views/top.html')

# 記事作成ページ
@app.get('/create')
def create():
    c= ConnectDB()
    c[1].execute("SELECT * FROM categories")
    categories = c[1].fetchall()
    c[1].close()
    return template('views/create.html', categories=categories)

# 記事のタイトル・本文が、POST送信されるとDBに挿入する
@app.post('/create')
def do_create():
    title = request.POST.getunicode('title')
    content = request.POST.getunicode('content')
    category_id = request.POST.getunicode('category')
    c = ConnectDB()
    c[1] = conn.cursor()
    c[1].execute("INSERT INTO blogs (title, content, created_at, category_id) \
        VALUES( ?, ?, ?, ?)", (title, content, str(datetime.datetime.now()), category_id))
    c[0].commit()
    c[1].close()
    return template('views/top.html')

# 記事一覧の閲覧
@app.get('/showlist')
def show_list():
    c = ConnectDB()
    c[1].execute("SELECT * FROM blogs INNER JOIN categories ON blogs.category_id = categories.category_id")
    blogs = c[1].fetchall()
    c[1].close()
    if not blogs:
        return '記事はまだありません。'
    else:
        return template('views/showlist.html', blogs = blogs)

# 指定された記事の閲覧
@app.get('/showblog<id:re:[0-9]+>')
def show(id):
    c = ConnectDB()
    c[1].execute("SELECT * FROM blogs WHERE id = ?",(id, ))
    blog = c[1].fetchone()
    c[1].close()
    if not blog:
        return 'このアイテムはみつかりませんでした。'
    else:
        return template('views/show.html', blog = blog)

@app.post('/deleteblog<id:re:[0-9]+>')
def delete(id):
    c = ConnectDB()
    c[1].execute("DELETE FROM blogs where id = ?", (id, ))
    c[0].commit()
    c[1].execute("SELECT * FROM blogs")
    blogs = c[1].fetchall()
    c[1].close()
    return template('views/showlist.html', blogs = blogs)

# 編集画面に遷移
@app.get('/updateblog<id:re:[0-9]+>')
def update(id):
    c = ConnectDB()
    c[1].execute('SELECT * FROM blogs where id = ?', (id, ))
    blog = c[1].fetchone()
    c[1].close()
    return template('views/update.html', blog = blog)

# 編集を実行
@app.post('/updateblog<id:re:[0-9]+>')
def do_update(id):
    title = request.POST.getunicode('title')
    content = request.POST.getunicode('content')
    c = ConnectDB()
    c[1].execute("UPDATE blogs SET title = ?, content = ? where id = ?", (title, content, id))
    c[0].commit()
    c[1].execute('SELECT * FROM blogs where id = ?', (id, ))
    blog = c[1].fetchone()
    c[1].close()
    return template('views/show.html', blog = blog)

@app.get('/create_category')
def create_category():
    return template('views/create_category.html')
@app.post('/create_category')
def create_category():
    category_name = request.POST.getunicode('category')
    c = ConnectDB()
    c[1].execute("INSERT INTO categories (category_name) values (?)", (category_name, ))
    c[0].commit()
    c[1].close()
    return template('views/top.html')

def ConnectDB():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    return conn, c

run(app=app, host='localhost', port=8080, reloader=True, debug=True)
# c.execute('CREATE TABLE BLOGS(id integer primary key autoincrement, title text, content text, date date)')

# 参考サイト
# http://note.kurodigi.com/python-bottle-01/
# https://www.takasay.com/entry/2015/07/04/010000
# https://qiita.com/Gen6/items/f1636be0fe479f42b3ee

