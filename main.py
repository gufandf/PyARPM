from flask import Flask,render_template,request,jsonify,redirect,url_for
import hashlib
import sqlite3

#检验用户名和密码是否对应
def usercheck(username,pw):
    print("验证用户: {}".format(username))
    info = getUserInfo(username)
    if info == None:
        print("[info]未知用户")
        return False
    elif pw == info["passwordMD5"]:
        print("[info]用户 {} 验证通过".format(str(info["username"])))
        return True
    else:
        print("[info]用户 {} 验证失败".format(str(info["username"])))
        return False

#方便修改数据库表中数据
def revisuserinfo(username,table,value):
    print('修改用户: {} 的数据'.format(username))
    # 连接数据库
    database = sqlite3.connect('data.db')
    cursor = database.cursor()
    # 修改
    cursor.execute("update users set {} = {} where username = '{}'".format(table,value,username))
    database.commit()
    database.close()

#方便查找用户的所有数据
def getUserInfo(username):
    print('查找用户: {} 的数据'.format(username))
    # 连接数据库
    database = sqlite3.connect('data.db')
    cursor = database.cursor()
    # 查找
    cursordata = cursor.execute("SELECT * from users where username=?", (username,)).fetchone()
    # 格式化信息
    if cursordata == None:
        print("[info]未找到用户：{} 的数据".format(username))
        return None
    info={
        "username":cursordata[0],
        "passwordMD5":cursordata[1],
        "group":cursordata[2],
        "scores":cursordata[3]
    }
    # for i in info:
    #     print("--{}:{}".format(i,info[i]))
    return info

app = Flask(__name__)

#根目录
@app.route('/',methods=["GET", "POST"])
def index():
    return render_template('index.html')

#注册页面
@app.route('/signup',methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template('signup.html')
    if request.method == "POST":
        print("/signup")
        # 连接数据库
        database = sqlite3.connect('data.db')
        cursor = database.cursor()
        # 输入信息检验
        if request.form.get('username') == "":
            return "未填写用户名"
        elif request.form.get('password') == "":
            return "未填写密码"
        elif request.form.get('group') == "unselect":
            return "组织未选择"
        # 格式化
        users={
            'username':request.form.get('username'),
            'passwordMD5':hashlib.md5(request.form.get('password').encode(encoding='UTF-8')).hexdigest(),
            'group':request.form.get('group')
        }
        print("请求注册信息:\n",str(users))
        if len(request.form.get('username')) < 6:
            print("[info]失败-用户名不足6字符\n")
            return "用户名不足6字符"
        elif len(request.form.get('username')) > 20:
            print("[info]失败-用户名超过20字符\n")
            return "用户名超过20字符"
        elif len(request.form.get('password')) < 8:
            print("[info]失败-密码不足8字符\n")
            return "密码不足8字符"
        elif len(request.form.get('password')) > 20:
            print("[info]失败-密码超过20字符\n")
            return "密码超过20字符"
        # 查重
        userinfo = getUserInfo(users['username'])
        if userinfo == None:
            cursor.execute("INSERT INTO users VALUES('{}', '{}', '{}', 0)".format(users['username'],users['passwordMD5'],users['group']))
            database.commit()
            database.close()
            print("[info]注册成功\n")
            return getUserInfo(users['username'])
        else:
            print("[info]失败-用户重名\n",userinfo)
            return "用户重名"

#交易页面
@app.route('/trading',methods=["GET", "POST"])
def trading():
    if request.method == "GET":
        return render_template('trading.html')
    if request.method == "POST":
        print("/trading")
        tradinginfo={
            'payer':request.form.get('payer'),
            'passwordMD5':hashlib.md5(request.form.get('password').encode(encoding='UTF-8')).hexdigest(),
            'payeed':request.form.get('payeed'),
            'count':request.form.get('count')
        }
        if usercheck(tradinginfo["payer"],tradinginfo["passwordMD5"]) and (not getUserInfo(tradinginfo["payeed"]) == None):
            print("[info]收付款方信息验证通过")
            print("[info]交易申请:\n-付款方: {}\n-收款方: {}\n-金额: {}".format(tradinginfo["payer"],tradinginfo["payeed"],tradinginfo["count"]))
            payerinfo = getUserInfo(tradinginfo["payer"])
            payeedinfo = getUserInfo(tradinginfo["payeed"])
            if payerinfo["scores"] >= int(tradinginfo["count"]):
                revisuserinfo(tradinginfo["payer"],"scores",payerinfo["scores"]-int(tradinginfo["count"]))
                revisuserinfo(tradinginfo["payeed"],"scores",payeedinfo["scores"]+int(tradinginfo["count"]))
                print("[info]交易成功")
                return "交易成功"
            else:
                print("[info]用户余额不足")
                return "余额不足"
        else:
            print("[info]交易失败-收付款方信息验证失败")
            return "收付款方信息验证失败"

#运行服务器
if __name__ == '__main__':
    app.run(debug=True)

