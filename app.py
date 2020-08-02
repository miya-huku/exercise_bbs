import os
# ファイル名をチェックする関数
from werkzeug.utils import secure_filename
# 画像のダウンロード
from flask import send_from_directory
# splite3をimportする
import sqlite3
# flaskをimportしてflaskを使えるようにする
from flask import Flask , render_template , request , redirect , url_for, send_from_directory, session

# fromでstatistics.pyというモジュール(ファイル)を読み込む、importでstatistics.py内のmean()という関数を読み込む
import statistics
from statistics import mean
import datetime  # datetimeというモジュール(ファイル)を読み込む



# appにFlaskを定義して使えるようにしています。Flask クラスのインスタンスを作って、 app という変数に代入しています。
app = Flask(__name__)

# Flask では標準で Flask.secret_key を設定すると、sessionを使うことができます。この時、Flask では session の内容を署名付きで Cookie に保存します。
app.secret_key = 'sunabakoza'

UPLOAD_FOLDER = './static/img'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


# GET  /register => 登録画面を表示
# POST /register => 登録処理をする
@app.route('/register',methods=["GET", "POST"])
def register():
    #  登録ページを表示させる
    if request.method == "GET":
        if 'user_id' in session :
            return redirect ('/bbs')
        else:
            return render_template("register.html")
    # ここからPOSTの処理
    else:
        name = request.form.get("name")
        password = request.form.get("password")

        #画像
        img_file = request.files['img_file']
        if img_file and allowed_file(img_file.filename):
            filename = secure_filename(img_file.filename)
            img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            imgdata = '/static/img/' + filename
            conn = sqlite3.connect('service.db')
            c = conn.cursor()
            c.execute("insert into user values(null,?,?,?)", (name,password,imgdata))
            conn.commit()
            conn.close()
            # return redirect('/login')
            return render_template('login.html', img_url=imgdata)
        else:
            return ''' <p>許可されていない拡張子です</p> '''

@app.route('/static/img/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    


# GET  /login => ログイン画面を表示
# POST /login => ログイン処理をする
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if 'user_id' in session :
            return redirect("/bbs")
        else:
            return render_template("login.html")
    else:
        # ブラウザから送られてきたデータを受け取る
        name = request.form.get("name")
        password = request.form.get("password")

        # ブラウザから送られてきた name ,password を userテーブルに一致するレコードが
        # 存在するかを判定する。レコードが存在するとuser_idに整数が代入、存在しなければ nullが入る
        conn = sqlite3.connect('service.db')
        c = conn.cursor()
        c.execute("select id from user where name = ? and password = ?", (name, password) )
        user_id = c.fetchone()
        conn.close()

        # user_id が NULL(PythonではNone)じゃなければログイン成功
        if user_id is None:
            # ログイン失敗すると、ログイン画面に戻す
            return render_template("login.html")
        else:
            session['user_id'] = user_id[0]
            return redirect("/bbs")


@app.route("/logout")
def logout():
    session.pop('user_id',None)
    # ログアウト後はログインページにリダイレクトさせる
    return redirect("/login")


@app.route('/bbs')
def bbs():
    if 'user_id' in session :
        #日時の取得
        todaynow = datetime.datetime.now() 
        postdate = (str(todaynow.year) + "年" + str(todaynow.month) + "月" + str(todaynow.day) +
            "日" + str(todaynow.hour) + "時" + str(todaynow.minute) + "分")


        # クッキーからuser_idを取得
        user_id = session['user_id']
        conn = sqlite3.connect('service.db')
        c = conn.cursor()
        # # DBにアクセスしてログインしているユーザ名と投稿内容を取得する
        # クッキーから取得したuser_idを使用してuserテーブルのnameを取得
        c.execute("select name,imgdata from user where id = ?", (user_id,))
        # fetchoneはタプル型
        user_info = c.fetchone()

        c.execute("select id,comment,postdate from bbs where userid = ? order by id", (user_id,))
        comment_list = []
        for row in c.fetchall():
            comment_list.append({"id": row[0], "comment": row[1], "postdate": row[2]})

        c.close()
        return render_template('bbs.html' , user_info = user_info , comment_list = comment_list)
    else:
        return redirect("/login")


@app.route('/add', methods=["POST"])
def add():
    #日時の取得
    todaynow = datetime.datetime.now() 
    postdate = (str(todaynow.year) + "年" + str(todaynow.month) + "月" + str(todaynow.day) +
        "日" + str(todaynow.hour) + "時" + str(todaynow.minute) + "分")

    user_id = session['user_id']
    # フォームから入力されたアイテム名の取得
    comment = request.form.get("comment")
    conn = sqlite3.connect('service.db')
    c = conn.cursor()
    # DBにデータを追加する
    c.execute("insert into bbs values(null,?,?,?)", (user_id, comment,postdate))
    conn.commit()
    conn.close()
    return redirect('/bbs')


@app.route('/edit/<int:id>')
def edit(id):
    if 'user_id' in session :
        #日時の取得
        todaynow = datetime.datetime.now() 
        postdate = (str(todaynow.year) + "年" + str(todaynow.month) + "月" + str(todaynow.day) +
            "日" + str(todaynow.hour) + "時" + str(todaynow.minute) + "分")
        conn = sqlite3.connect('service.db')
        c = conn.cursor()
        c.execute("select comment,postdate from bbs where id = ?", (id,) )
        comment = c.fetchone()
        conn.close()

        if comment is not None:
            # None に対しては インデクス指定できないので None 判定した後にインデックスを指定
            comment = comment[0]
            # "りんご" ○   ("りんご",) ☓
            # fetchone()で取り出したtupleに 0 を指定することで テキストだけをとりだす
        else:
            return "アイテムがありません" # 指定したIDの name がなければときの対処

        # item = { "id":id, "comment":comment }
        item = { "id":id, "comment":comment, "postdate":postdate }


        return render_template("edit.html", comment=item)
    else:
        return redirect("/login")


# /add ではPOSTを使ったので /edit ではあえてGETを使う
@app.route("/edit")
def update_item():
    if 'user_id' in session :
        # ブラウザから送られてきたデータを取得
        item_id = request.args.get("item_id") # id
        item_id = int(item_id)# ブラウザから送られてきたのは文字列なので整数に変換する
        comment = request.args.get("comment") # 編集されたテキストを取得する
        #日時の取得
        todaynow = datetime.datetime.now() 
        postdate = (str(todaynow.year) + "年" + str(todaynow.month) + "月" + str(todaynow.day) +
            "日" + str(todaynow.hour) + "時" + str(todaynow.minute) + "分")

        # 既にあるデータベースのデータを送られてきたデータに更新
        conn = sqlite3.connect('service.db')
        c = conn.cursor()
        # c.execute("update bbs set comment = ? where id = ?",(comment,item_id))
        c.execute("update bbs set comment = ?, postdate = ? where id = ?",(comment,postdate,item_id))
        conn.commit()
        conn.close()

        # アイテム一覧へリダイレクトさせる
        return redirect("/bbs")
    else:
        return redirect("/login")


@app.route('/del' ,methods=["POST"])
def del_task():
    # クッキーから user_id を取得
    id = request.form.get("comment_id")
    id = int(id)
    conn = sqlite3.connect("service.db")
    c = conn.cursor()
    c.execute("delete from bbs where id = ?", (id,))
    conn.commit()
    c.close()
    return redirect("/bbs")



@app.errorhandler(403)
def mistake403(code):
    return 'There is a mistake in your url!'


@app.errorhandler(404)
def notfound404(code):
    return "404だよ！！見つからないよ！！！"




# __name__ というのは、自動的に定義される変数で、現在のファイル(モジュール)名が入ります。 ファイルをスクリプトとして直接実行した場合、 __name__ は __main__ になります。
if __name__ == "__main__":
    # Flask が持っている開発用サーバーを、実行します。
    app.run()
