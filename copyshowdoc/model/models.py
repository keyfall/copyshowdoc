from flask_sqlalchemy import SQLAlchemy

from copyshowdoc.application.app import app

db = SQLAlchemy(app)


# 声明模型类
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer,primary_key = True)
    uname = db.Column(db.String(30),nullable = False)
    upicture = db.Column(db.String(100),nullable=False,default="e:\\guifan\\time.jpg")

    #转json
    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict

class Document(db.Model):
    #表名
    __tablename__ = 'documenttable'

    #设置字段
    id = db.Column(db.Integer,primary_key = True)
    doctitle = db.Column(db.String(20),nullable = False)
    docdescribe = db.Column(db.String(300),nullable = True)
    #创建外键
    uid = db.Column(db.Integer,db.ForeignKey("user.id",ondelete="CASCADE"),nullable = False)

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict


class Page(db.Model):
    __tablename__ = 'pagetable'

    id = db.Column(db.Integer,primary_key = True)
    #可以不填，前台显示默认页面
    ptitle = db.Column(db.String(40))
    psort = db.Column(db.Integer,nullable = False)
    menuid = db.Column(db.Integer,db.ForeignKey("menutable.id",ondelete="CASCADE"),nullable = False)
    uid = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    docid = db.Column(db.Integer, db.ForeignKey("documenttable.id", ondelete="CASCADE"), nullable=False)
    pcontent = db.Column(db.Text,nullable = False)
    pcreatetime = db.Column(db.DateTime,nullable = False)

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict

class History(db.Model):
    __tablename__ = 'historytable'

    id = db.Column(db.Integer,primary_key = True)
    pageid = db.Column(db.Integer,db.ForeignKey("pagetable.id",ondelete="CASCADE"),nullable = False)
    hupdatetime = db.Column(db.DateTime,nullable = False)
    hcontent = db.Column(db.Text,nullable = False)
    uid = db.Column(db.Integer,db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    # 版本号后台生成
    versionnum = db.Column(db.String(60),nullable = False)

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict

# page，用户浏览
class Userpage(db.Model):
    __tablename__ = 'userpagetable'

    id = db.Column(db.Integer,primary_key = True)
    uid = db.Column(db.Integer,db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    pageid = db.Column(db.Integer,db.ForeignKey("pagetable.id",ondelete="CASCADE"),nullable=False)

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict

class Menu(db.Model):
    __tablename__ = 'menutable'

    id = db.Column(db.Integer,primary_key = True)
    mtitle = db.Column(db.String(30),nullable = False)
    msort = db.Column(db.Integer,nullable = False)
    docid = db.Column(db.Integer,db.ForeignKey("documenttable.id",ondelete="CASCADE"),nullable = False)
    uid = db.Column(db.Integer,db.ForeignKey("user.id",ondelete="CASCADE"),nullable = False)
    #mfather = db.Column(db.Integer,db.ForeignKey("menutable.id",ondelete="CASCADE"),nullable = False)
    mfather = db.Column(db.Integer,nullable=False)

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict
