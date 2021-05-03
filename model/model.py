# 表——实体类

from app import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

# # 实例SQLAlchemy类，use_native_unicode='utf8'设置编码，必须设置
db = SQLAlchemy(app, use_native_unicode='utf8');

class User(db.Model):
    # 设置表名
    __tablename__ = 'tb_user';
    # id，主键并自动递增
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(256), nullable=True)
    name = db.Column(db.String(64))

    # 设置只可写入，对密码进行加密
    def password_hash(self, password):
        self.password = generate_password_hash(password);

class Blog(db.Model):
    __tablename__ = 'blog'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128))
    text = db.Column(db.TEXT)
    create_time = db.Column(db.String(64))
    #关联用户id
    user_id = db.Column(db.Integer, db.ForeignKey('tb_user.id'))
    user = db.relationship('User', backref='user')

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(256))    # 评论内容
    create_time = db.Column(db.String(64))
    # 关联博客id
    blog_id = db.Column(db.Integer, db.ForeignKey("blog.id"))
    # 关联用户id
    user_id = db.Column(db.Integer, db.ForeignKey("tb_user.id"))
    blog = db.relationship("Blog", backref="blog")
    user = db.relationship("User", backref="use")

# 创建
def creat():
    db.create_all()

# 删除
def drop():
    db.drop_all()

# 建表
creat()
