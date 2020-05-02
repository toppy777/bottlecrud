from bottle import Bottle, run, route, get, post, request, static_file
from bottle import TEMPLATE_PATH, jinja2_template as template
import sqlite3
import datetime
from const import DB_NAME
import markdown
import os

app = Bottle()
markdown = markdown.Markdown()

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
        content = markdown.convert(blog[2])
        return template('views/show.html', blog = blog, content = content)

#カテゴリ一覧
@app.get('/show_categorylist')
def show_categorylist():
    categories = ExecuteGetContents("SELECT * FROM categories")
    return template('show_categorylist', categories=categories)

# 指定されたカテゴリの記事一覧
@app.get('/show_category<id:re:[0-9]+>')
def show_category(id):
    blogs = ExecuteGetContents('SELECT * FROM blogs WHERE category_id = %s' % id)
    print(blogs)
    if not blogs:
        return 'このアイテムはみつかりませんでした。'
    else:
        return template('views/show_category.html', blogs = blogs)

# 記事一覧ページ
@app.get('/admin/showlist')
def show_list():
    blogs = ExecuteGetContents(\
        'SELECT * FROM blogs INNER JOIN categories ON blogs.category_id = categories.category_id')
    if not blogs:
        return '記事はまだありません。'
    else:
        return template('admin/showlist.html', blogs = blogs)

# 指定された記事の閲覧
@app.get('/admin/showblog<id:re:[0-9]+>')
def show(id):
    blog = ExecuteGetContent('SELECT * FROM blogs WHERE id = %s' % id)
    if not blog:
        return 'このアイテムはみつかりませんでした。'
    else:
        content = markdown.convert(blog[2])
        return template('admin/show.html', blog = blog, content = content)


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


####admin#####
@app.get('/admin')
def admin():
    return template('admin/top.html')

# 記事作成ページ
@app.get('/admin/create')
def create():
    categories = ExecuteGetContents('SELECT * FROM categories')
    return template('admin/create.html', categories=categories)
# 記事を作成
@app.post('/admin/create')
def do_create():
    title = request.POST.getunicode('title')
    content = request.POST.getunicode('content')
    category_id = request.POST.getunicode('category')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO blogs (title, content, created_at, category_id) VALUES(?, ?, ?, ?)", (title, content, str(datetime.datetime.now()), category_id))
    conn.commit()
    cursor.close()

    return template('admin/top.html')

# カテゴリ作成ページ
@app.get('/admin/create_category')
def create_category():
    return template('admin/create_category.html')
# カテゴリを作成
@app.post('/admin/create_category')
def create_category():
    category_name = request.POST.getunicode('category')
    ExecuteQuery('INSERT INTO categories (category_name) values ("%s")' % category_name)
    return template('admin/top.html')

#カテゴリ一覧
@app.get('/admin/show_categorylist')
def show_categorylist():
    categories = ExecuteGetContents("SELECT * FROM categories")
    return template('admin/show_categorylist', categories=categories)
# 指定されたカテゴリの記事一覧
@app.get('/admin/show_category<id:re:[0-9]+>')
def show_category(id):
    blogs = ExecuteGetContents('SELECT * FROM blogs WHERE category_id = %s' % id)
    print(blogs)
    if not blogs:
        return 'このアイテムはみつかりませんでした。'
    else:
        return template('admin/show_category.html', blogs = blogs)


# 編集ページ
@app.get('/admin/updateblog<id:re:[0-9]+>')
def update(id):
    blog = ExecuteGetContent('SELECT * FROM blogs WHERE id = %s' % id)
    return template('admin/update.html', blog = blog)
# 編集を実行
@app.post('/admin/updateblog<id:re:[0-9]+>')
def do_update(id):
    title = request.POST.getunicode('title')
    content = request.POST.getunicode('content')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE blogs SET title = ?, content = ? where id = ?', (title, content, id))
    conn.commit()
    cursor.close()
    blog = ExecuteGetContent('SELECT * FROM blogs WHERE id = %s' % id)
    return template('admin/show.html', blog = blog, content=content)

# 記事作成
@app.post('/admin/deleteblog<id:re:[0-9]+>')
def delete(id):
    ExecuteQuery('DELETE FROM blogs where id = %s' % id)
    blogs = ExecuteGetContents('SELECT * FROM blogs')
    return template('admin/showlist.html', blogs = blogs)

# 画像のアップロード画面を表示
@app.get('/admin/upload_img')
def update_img():
    return template('admin/upload_img.html')
# 画像をアップロード
@app.post('/admin/upload_img')
def do_update_img():
    upload = request.files.get('upload_img', '')
    if not upload.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        return 'File extension not allowed!'
    save_path = get_save_path()
    upload.save(save_path)
    return 'Upload OK. FilePath: %s%s' % (save_path, upload.filename)
def get_save_path():
    dt_now = datetime.datetime.now()
    path_dir = "./static/img/" + str(dt_now.year) + "/" + str(dt_now.month) + "/" + str(dt_now.day)
    os.makedirs(path_dir, exist_ok=True)
    return path_dir


run(app=app, host='localhost', port=8080, reloader=True, debug=True)

# 参考サイト
# http://note.kurodigi.com/python-bottle-01/
# https://www.takasay.com/entry/2015/07/04/010000
# https://qiita.com/Gen6/items/f1636be0fe479f42b3ee
# https://qiita.com/masakuni-ito/items/593b9d753c44da61937b

# todo
# ・削除あとの全記事閲覧ページでのカテゴリ表示がされてない
# ・カテゴリ一覧
# ・カテゴリ別一覧