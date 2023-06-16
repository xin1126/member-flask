#初始化資料庫連線
from pymongo import MongoClient
import certifi
conn = MongoClient("mongodb+srv://root:root123@mycluster.itfxeqp.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=certifi.where())
db=conn.member_system
print("資料庫連線建立成功")

#初始化 Flask 伺服器
from flask import *
import os

app=Flask(
    __name__,
    static_folder="public",
    static_url_path="/"
)
app.secret_key="any string but secret"
#處理路由
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/member")
def member():
    #如果沒有紀錄會員的資訊
    if "nickname" in session:
        return render_template("member.html")
    #導回主頁面
    else:
        return redirect("/")

# /error?msg=錯誤訊息
@app.route("/error")
def error():
    message=request.args.get("msg", "發生錯誤、請聯繫客服")    #從要求字串中取得錯誤訊息 放到變數message
    return render_template("error.html", message=message)  #檔案路徑,資料欄位名稱=資料

@app.route("/signup", methods=["POST"])
def signup():
    nickname=request.form["nickname"] #前後端連線方法
    email=request.form["email"]
    password=request.form["password"]
    #根據接收到的資料，和資料庫互動
    # print(nickname,email,password)
    # return "OK"
    collection=db.user
    # 檢查會員集合中是否有相同 Email 的文件資料
    result=collection.find_one({
        "email":email
    })
    if result != None:  #如果result 不等於None
        return redirect("/error?msg=信箱已被註冊")
    #把資料放進資料庫，完成註冊
    collection.insert_one({
        "nickname":nickname,
        "email":email,
        "password":password
    })
    return redirect("/")   #導回首頁


@app.route("/signin", methods=["POST"])
def signin():
    #從前端取得使用者的輸入
    email=request.form["email"]
    password=request.form["password"]
    #和資料庫互動
    collection=db.user
    #檢查信箱密碼是否正確
    result=collection.find_one({
        "$and":[
            {"email":email},
            {"password":password}
        ]    
    })
    
    #找不到對應的資料，登入失敗，導向到錯誤頁面
    if result==None: #最後 檢查result到底有沒有抓到資料 如果是一個空值 代表使用者輸入的email跟password 在資料庫並沒有抓到對應的資訊
        return redirect("/error?msg=帳號或密碼輸入錯誤")
    #登入成功 在Session紀錄會員資訊，導向到會員頁面
    session["nickname"]=result["nickname"]
    return redirect("/member")  

@app.route("/signout")
def signout():
    #移除Sesion 中的會員資訊
    del session["nickname"]
    return redirect("/")

if __name__ == '__main__':
app.run(debug=True, port=os.getenv("PORT", default=5000), host='0.0.0.0')