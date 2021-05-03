from model import *
from flask import Blueprint, session, render_template, request, flash, redirect, url_for
from werkzeug.security import check_password_hash
from decorators import login_limit

index = Blueprint("index", __name__)

# 首页
@index.route('/')
def hello():
    return render_template('index.html')

# 注册请求
@index.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter(User.username == username).first();
        if user is not None:
            flash("该用户名已存在")
            return render_template('register.html')
        else:
            user = User(username=username, name=name)
            # 调用password_hash对密码加密
            user.password_hash(password)
            db.session.add(user)
            db.session.commit();
            flash("注册成功！")
            return render_template('register.html')

# 登录请求
@index.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter(User.username == username).first();
        # check_password_hash比较两个密码是否相同
        if (user is not None) and (check_password_hash(user.password, password)):
            session['username'] = user.username
            session.permanent = True
            return redirect(url_for('index.hello'))
        else:
            flash("账号或密码错误")
            return render_template('login.html');

# 修改密码
@index.route("/updatePwd", methods=['POST', 'GET'])
@login_limit
def update():
    if request.method == "GET":
        return render_template("updatePwd.html")
    if request.method == 'POST':
        lodPwd = request.form.get("lodPwd")
        newPwd1 = request.form.get("newPwd1")
        newPwd2 = request.form.get("newPwd2")
        username = session.get("username");
        user = User.query.filter(User.username == username).first();
        if check_password_hash(user.password, lodPwd):
            if newPwd1 != newPwd2:
                flash("两次新密码不一致！")
                return render_template("updatePwd.html")
            else:
                user.password_hash(newPwd2)
                db.session.commit();
                flash("修改成功！")
                return render_template("updatePwd.html")
        else:
            flash("原密码错误！")
            return render_template("updatePwd.html")

# 关于页面
@index.route('/about')
def about():
    return render_template('about.html')

# 退出
@index.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index.hello'))

