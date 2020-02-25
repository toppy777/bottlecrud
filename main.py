from bottle import Bottle, run, route, get, post, request, static_file
from bottle import TEMPLATE_PATH, jinja2_template as template
import sqlite3
import datetime
from const import DB_NAME

app = Bottle()

# CSSとか
@app.get("/static/<filename:path>")
def css(filename):
    return static_file(filename, root="./static/")

# 画像
@app.get('/static/img/<filename:path>')
def img(filename):
    return static_file(filename, root="./static/img/")

# トップページ
@app.get('/')
def top():
    return template('views/top.html')

# 記事作成ページ
@app.get('/create')
def create():
    categories = ExecuteGetContents('SELECT * FROM categories')
    return template('views/create.html', categories=categories)

# 記事のタイトル・本文が、POST送信されるとDBに挿入する
@app.post('/create')
def do_create():
    title = request.POST.getunicode('title')
    content = request.POST.getunicode('content')
    category_id = request.POST.getunicode('category')

    ExecuteQuery('INSERT INTO blogs (title, content, created_at, category_id) VALUES( "%s", "%s", "%s", %s)' \
                  % (title, content, str(datetime.datetime.now()), category_id))
    return template('views/top.html')

# 記事一覧の閲覧
@app.get('/showlist')
def show_list():
    blogs = ExecuteGetContents(\
        'SELECT * FROM blogs INNER JOIN categories ON blogs.category_id = categories.category_id')
    if not blogs:
        return '記事はまだありません。'
    else:
        return template('views/showlist.html', blogs = blogs)

# 指定された記事の閲覧
@app.get('/showblog<id:re:[0-9]+>')
def show(id):
    blog = ExecuteGetContent('SELECT * FROM blogs WHERE id = %s' % id)
    if not blog:
        return 'このアイテムはみつかりませんでした。'
    else:
        return template('views/show.html', blog = blog)

@app.post('/deleteblog<id:re:[0-9]+>')
def delete(id):
    ExecuteQuery('DELETE FROM blogs where id = %s' % id)
    blogs = ExecuteGetContents('SELECT * FROM blogs')
    return template('views/showlist.html', blogs = blogs)

# 編集画面に遷移
@app.get('/updateblog<id:re:[0-9]+>')
def update(id):
    blog = ExecuteGetContent('SELECT * FROM blogs WHERE id = %s' % id)
    return template('views/update.html', blog = blog)

# 編集を実行
@app.post('/updateblog<id:re:[0-9]+>')
def do_update(id):
    title = request.POST.getunicode('title')
    content = request.POST.getunicode('content')
    ExecuteQuery('UPDATE blogs SET title = "%s", content = "%s" where id = %s' % (title, content, id))
    blog = ExecuteGetContent('SELECT * FROM blogs WHERE id = %s' % id)
    return template('views/show.html', blog = blog)

# カテゴリ作成ページに遷移
@app.get('/create_category')
def create_category():
    return template('views/create_category.html')
# カテゴリを作成
@app.post('/create_category')
def create_category():
    category_name = request.POST.getunicode('category')
    ExecuteQuery('INSERT INTO categories (category_name) values ("%s")' % category_name)
    return template('views/top.html')

# 画像のアップロード画面を表示
@app.get('/upload_img')
def update_img():
    return template('views/upload_img.html')
# 画像をアップロード
@app.post('/upload_img')
def do_update_img():
    upload = request.files.get('upload_img', '')
    if not upload.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        return 'File extension not allowed!'
    save_path = get_save_path()
    upload.save(save_path)
    return 'Upload OK. FilePath: %s%s' % (save_path, upload.filename)

def get_save_path():
    path_dir = "./static/img/"
    return path_dir

# SQLクエリを実行する
def ExecuteQuery(query):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    cursor.close()

# SELECT文を実行して、その内容を得る
def ExecuteGetContents(get_contents_query):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(get_contents_query)
    result = cursor.fetchall()
    return result

#SELECT文を実行して、その最初の内容を得る
def ExecuteGetContent(get_content_query):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(get_content_query)
    result = cursor.fetchone()
    return result

run(app=app, host='localhost', port=8080, reloader=True, debug=True)
# c.execute('CREATE TABLE BLOGS(id integer primary key autoincrement, title text, content text, date date)')

# 参考サイト
# http://note.kurodigi.com/python-bottle-01/
# https://www.takasay.com/entry/2015/07/04/010000
# https://qiita.com/Gen6/items/f1636be0fe479f42b3ee

