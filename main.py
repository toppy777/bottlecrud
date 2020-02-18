from bottle import Bottle, run, route, get, post, request
from bottle import TEMPLATE_PATH, jinja2_template as template
import sqlite3
import datetime
from const import DB_NAME

app = Bottle()

# トップページ
@app.get('/')
def top():
    return template('views/top.html')

# 記事作成ページ
@app.get('/create')
def create():
    return template('views/create.html')

# 記事のタイトル・本文が、POST送信されるとDBに挿入する
@app.post('/create')
def do_create():
    title = request.POST.getunicode('title')
    content = request.POST.getunicode('content')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO blogs (title, content, date) \
        VALUES('"+ title +"','"+ content +"','"+ str(datetime.datetime.now()) +"')")
    conn.commit()
    c.close()
    return template('views/top.html')

# 記事一覧の閲覧
@app.get('/showlist')
def show_list():
    c = ConnectDB()
    c.execute("SELECT * FROM blogs")
    blogs = c.fetchall()
    c.close()
    if not blogs:
        return '記事はまだありません。'
    else:
        return template('showlist.html', blogs = blogs)

# 指定された記事の閲覧
@app.get('/showblog<id:re:[0-9]+>')
def show(id):
    c = ConnectDB()
    c.execute("SELECT * FROM blogs WHERE id = ?",(id, ))
    blog = c.fetchone()
    c.close()
    if not blog:
        return 'このアイテムはみつかりませんでした。'
    else:
        return template('show.html', blog = blog)

@app.post('/deleteblog<id:re:[0-9]+>')
def delete(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM blogs where id = ?", (id, ))
    conn.commit()
    c.execute("SELECT * FROM blogs")
    blogs = c.fetchall()
    c.close()
    return template('showlist.html', blogs = blogs)

# 編集画面に遷移
@app.get('/updateblog<id:re:[0-9]+>')
def update(id):
    c = ConnectDB()
    c.execute('SELECT * FROM blogs where id = ?', (id, ))
    blog = c.fetchone()
    c.close()
    return template('update.html', blog = blog)

# 編集を実行
@app.post('/updateblog<id:re:[0-9]+>')
def do_update(id):
    title = request.POST.getunicode('title')
    content = request.POST.getunicode('content')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE blogs SET title = ?, content = ? where id = ?", (title, content, id))
    conn.commit()
    c.execute('SELECT * FROM blogs where id = ?', (id, ))
    blog = c.fetchone()
    c.close()
    return template('show.html', blog = blog)

def ConnectDB():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    return c

# flag = False
# start = 0
# while flag :
#     if "str".find('\n', start) != -1:
#         flag = True
#         start = "str".find('\n', start)
#     else:
#         flag = False

run(app=app, host='localhost', port=8080, reloader=True, debug=True)
# c.execute('CREATE TABLE BLOGS(id integer primary key autoincrement, title text, content text, date date)')

# 参考サイト
# http://note.kurodigi.com/python-bottle-01/
# https://www.takasay.com/entry/2015/07/04/010000
# https://qiita.com/Gen6/items/f1636be0fe479f42b3ee