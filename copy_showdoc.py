from flask import Flask,request,jsonify
from flask_restful import Api,Resource,reqparse
from flask_sqlalchemy import SQLAlchemy
import pymysql
from datebase import User,Document,Page,Userpage,History,Menu
from sqlalchemy import and_
import datetime
import time

abc=pymysql.install_as_MySQLdb()
app = Flask(__name__)

# 连接数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost/showdoc2?charset=utf8'

# 设置是否跟踪数据库的修改情况，一般不跟踪
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 数据库操作是否显示原始SQL语句，一般打开
app.config['SQLALCHEMY_ECHO'] = True

#实例化orm框架的操作对象，后续数据库操作，都要基于操作对象来完成
db = SQLAlchemy(app)
api = Api(app)

# 获取前台传得值，并做类型验证，是否必须
# document
doc_parse = reqparse.RequestParser()
doc_parse.add_argument('doctitle', type=str, help="用户名验证错误", required=True)
doc_parse.add_argument('docdescribe', type=str, help="请填写描述", required=True)
doc_parse.add_argument('uid', type=int, required=True)

# menu
menu_parse = reqparse.RequestParser()
menu_parse.add_argument('mtitle',type=str,help="用户名验证错误",required=True)
menu_parse.add_argument('msort',type=int,default=99)
menu_parse.add_argument('docid',type=int,help="文档号验证错误")
menu_parse.add_argument('uid',type=int,required=True)
#0是1级展示
menu_parse.add_argument('mfather',type=int,help="上级验证错误",required=True)

#page
page_parse = reqparse.RequestParser()
page_parse.add_argument('ptitle',type=str,help="用户名验证错误",required=True)
page_parse.add_argument('psort',type=int,default=99)
page_parse.add_argument('menuid',type=int,help="目录验证错误",required=True)
page_parse.add_argument('uid',type=int,required=True)
page_parse.add_argument('docid',type=int,help="文档号验证错误")
page_parse.add_argument('pcontent',type=str,help="加一些内容",required=True)
page_parse.add_argument('pcreatetime',type=str,help="日期验证错误",required=True)


#迭代获取menu
def getmenufamily(docid, menuid):
    menus = Menu.query.filter(Menu.docid==docid,Menu.mfather==menuid,Menu.id!=1).all()
    if menus is not None:
        result=[]
        for menu in menus:
            menudict = menu.to_json()
            menudict['children'] = getmenufamily(docid,menu.id)
            result.append(menudict)
        return result
    else:
        return "no menus"

#迭代删除menu
def delmenufamily(docid,menuid):
    menus = db.session.query(Menu).filter(Menu.docid == docid, Menu.mfather == menuid,Menu.id!=1).all()
    if menus is not None:
        for menu in menus:
            menus2=delmenufamily(docid,menu.id)
            db.session.delete(menu)
    else:
        for menu in menus:
            db.session.delete(menu)




#document相关
class fordocument(Resource):
    #获得所有的document
    def get(self):
        #这里做个用户验证,利用cookies中的uname得到值，进行解密，然后跟数据库中进行比较


        #验证完成后，通过uid进行数据库取对应的document,这里没有登录验证，就取所有的document
        documents = Document.query.filter(Document.id!=1).all()
        result = []
        for comment in documents:
            result.append(comment.to_json())

        return jsonify(result)

    #新增document
    def post(self):
        args = doc_parse.parse_args()

        #存数据库
        document = Document(doctitle=args['doctitle'],docdescribe=args['docdescribe'],uid=args['uid'])
        db.session.add(document)
        try:
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            raise e
        return "ok"

#单个document
class foronedocument(Resource):
    #获取对应文档
    def get(self,docmentid):
        document = Document.query.filter(Document.id==docmentid).first()
        if document is not None:
            return jsonify(document.to_json())
        else:
            return "no document"

    #删除文档
    def delete(self,docmentid):
        document = db.session.query(Document).filter(Document.id == docmentid).first()
        if document is not None:
            db.session.delete(document)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e
            return "ok"
        else:
            return "no document"

    #更新文档,uid无需更改，部分修改就使用了patch,完全修改使用put
    def patch(self,docmentid):
        document = db.session.query(Document).filter(Document.id == docmentid).first_or_404()
        if document is not None:
            args = doc_parse.parse_args()
            document.doctitle=args['doctitle']
            document.docdescribe = args['docdescribe']
            try:
                db.session.commit()

            except Exception as e:
                db.session.rollback()
                raise e
            return "ok"
        else:
            return "no document"

#目录
class formenu(Resource):
    #获得当前document的所有menu,这里需要循环，使用迭代
    def get(self,documentid):
        document = Document.query.filter(Document.id == documentid,Document.id!=1).first()
        if document is not None:

            return jsonify(getmenufamily(documentid,0))
        else:
            return "no document"

    #新增menu
    def post(self,documentid):
        args = menu_parse.parse_args()
        document = Document.query.filter(Document.id == documentid).first()
        menu = Menu.query.filter(Menu.id == args['mfather']).first()
        #mfather不能为1，mfather不能为不存在的menuid
        if document is not None and args['mfather']!=1 and menu is not None:
            #存数据库
            menu = Menu(mtitle=args['mtitle'],msort=args['msort'],docid=documentid,
                    uid=args['uid'],mfather=args['mfather'])
            db.session.add(menu)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e
            return "ok"
        else:
            return "no document"

#单个目录
class foronemenu(Resource):
    #获得此目录的内容
    def get(self,documentid,menuid):
        menu = Menu.query.filter(Menu.id == menuid,Menu.docid==documentid,Menu.id !=1).first()
        if menu is not None:
            return jsonify(menu.to_json())
        else:
            return "no menu"
        return "ok"

    #删除此目录
    def delete(self,documentid,menuid):
        menu = db.session.query(Menu).filter(Menu.id == menuid,Menu.docid==documentid,Menu.id !=1).first()
        if menu is not None:
            delmenufamily(documentid,menu.id)
            db.session.delete(menu)
            try:
                db.session.commit()
            except Exception as e:
                db.session.roolback()
                raise e
            return "ok"
        else:
            return "no menu"

    #更新目录，uid无需更改，但是需要传过来
    #原因有2：1.懒得添加一个menu_parser
    #       2.安全，没有uid,后台存数据时会报外键错误
    def patch(self,documentid,menuid):
        menu = db.session.query(Menu).filter(Menu.id==menuid,Menu.docid==documentid,Menu.id!=1).first()
        if menu is not None:
            args = menu_parse.parse_args()
            #mfather不能为没有id的menu
            mfatherappear = db.session.query(Menu).filter(Menu.id==args['mfather']).first()
            #mfather不能为1,不能为自己的id,不能为没有出现过的id
            if args['mfather'] !=1 and args['mfather'] !=menu.id and mfatherappear is not None:
                menu.mtitle = args['mtitle']
                menu.msort = args['msort']
                #这里没有修改docid和uid,节省消耗
                menu.mfather = args['mfather']
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    raise e
                return "ok"
            else:
                return "mfather can not be 1 or mfather equals 1 or mfather not appear in menutable"
        else:
            return "no menu"

#页面
class forpage(Resource):

    #获得menus和pages，点击document时展示
    def get(self,documentid):
        # 由于使用了first_or_404,如果没有搜到，就报404错误
        document = Document.query.filter(Document.id == documentid).first()
        if document is not None:
            # menuid=1就是一级显示
            pages = Page.query.filter(Page.menuid == 1, Page.docid == document.id).order_by(Page.psort).all()
            # mfather=0就是一级显示，为了给page为一级显示，所以id为1的menu不显示
            menus = Menu.query.filter(Menu.docid == document.id, Menu.id != 1, Menu.mfather == 0).order_by(
                Menu.msort).all()
            # 这里为了前台取值，利用字典的key表名pages和menus
            result = []
            dict = {}
            dictvalue = []
            dictvalue2=[]
            for page in pages:
                dictvalue.append(page.to_json())
            dict['pages'] = dictvalue
            for menu in menus:
                dictvalue2.append(menu.to_json())
            dict['menus'] = dictvalue2
            result.append(dict)
            return jsonify(result)
        else:
            return "no document"

    #新增page
    def post(self,documentid):
        args = page_parse.parse_args()
        #先判断menuid是否为1，即是否一级显示
        #是1，就判断document是否存在，存在就存储
        #不是1，就判断menu是否存在，存在就存储
        if args['menuid']==1:
            document = Document.query.filter(Document.id==documentid).first()
            if document is not None:
                createtime = datetime.datetime.strptime(args["pcreatetime"], '%Y-%m-%d %H:%M:%S')
                page = Page(ptitle=args['ptitle'], psort=args['psort'], menuid=args['menuid'], uid=args['uid'],
                            docid=documentid,
                            pcontent=args['pcontent'], pcreatetime=createtime)
                db.session.add(page)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    raise e
                return "ok"
            else:
                return "no document"
        else:
            menu = Menu.query.filter(Menu.docid == documentid, Menu.id == args['menuid']).first()
            if menu is not None:
                createtime = datetime.datetime.strptime(args["pcreatetime"],'%Y-%m-%d %H:%M:%S')
                page = Page(ptitle=args['ptitle'],psort=args['psort'],menuid=args['menuid'],uid=args['uid'],docid=documentid,
                        pcontent=args['pcontent'],pcreatetime=createtime)
                db.session.add(page)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    raise e
                return "ok"
            else:
                return "no menu"

#单个页面
class foronepage(Resource):

    #获得page显示,包含users(为了头像)
    def get(self,documentid,pageid):
        page = Page.query.filter(Page.docid==documentid,Page.id==pageid).first()
        if page is not None:
            #传id为1的user不会浏览的
            userpages = Userpage.query.filter(Userpage.pageid==pageid,Userpage.uid!=1).all()
            userids = []
            for userpage in userpages:
                userids.append(userpage.uid)
            usersresult=[]
            users = User.query.filter(User.id.in_(userids)).all()
            for user in users:
                usersresult.append(user.to_json())
            pagedict = page.to_json()
            pagedict['users']=usersresult
            return jsonify(pagedict)
        return "no page"

    #删除此page
    def delete(self,documentid,pageid):
        page = db.session.query(Page).filter(Page.id==pageid,Page.docid==documentid).first()
        if page is not None:
            db.session.delete(page)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e
            return "ok"
        else:
            return "no page"

    #更新page
    def patch(self,documentid,pageid):
        args = page_parse.parse_args()
        page = db.session.query(Page).filter(Page.id == pageid, Page.docid == documentid).first()
        if page is not None:
            createtime = datetime.datetime.strptime(args["pcreatetime"], '%Y-%m-%d %H:%M:%S')
            getversionnum = str(pageid) + str(int(time.time()))
            if args['menuid']==1:
                document = Document.query.filter(Document.id==documentid).first()
                if document is not None:
                    #需要修改page,把原page放到历史表中,这是2个事务，最后commit，错误就回滚
                    #别做了一个事务，commit一次
                    #存储history

                    history = History(pageid=pageid,hupdatetime=page.pcreatetime,hcontent=page.pcontent,uid=page.uid,
                                      versionnum=getversionnum)
                    db.session.add(history)

                    #修改page
                    page.ptitle = args['ptitle']
                    page.psort = args['psort']
                    page.menuid = args['menuid']
                    page.pcontent = args['pcontent']
                    page.pcreatetime = createtime
                    try:
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        raise e
                    return "ok"
                else:
                    return "no document"

            else:
                #查找menu是否存在，存在就存储
                menu = Menu.query.filter(Menu.id==args['menuid'],Menu.docid==documentid).first()
                if menu is not None:
                    history = History(pageid=pageid,hupdatetime=page.pcreatetime,hcontent=page.pcontent,uid=page.uid,
                                      versionnum=getversionnum)
                    db.session.add(history)

                    #修改page
                    page.ptitle = args['ptitle']
                    page.psort = args['psort']
                    page.menuid = args['menuid']
                    page.pcontent = args['pcontent']
                    page.pcreatetime = createtime
                    try:
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        raise e
                    return "ok"
                else:
                    return "nomenu"
        else:
            return "no page"

#历史记录
class forhistory(Resource):

    #获取所有history,这里面需要显示修改人
    # 我存的是id,所以name都一样，没有改变
    #如果存的是name,用户查看修改文档以后，如果用户改过名字，就会形成不一样的修改人
    def get(self,pageid):
        page = Page.query.filter(Page.id==pageid).first()
        if page is not None:
            historys = History.query.filter(History.pageid==pageid).all()
            user = User.query.filter(User.id==page.uid).first()
            if historys is not None:
                result = []
                for history in historys:
                    historydict = history.to_json()
                    historydict['updatename']=user.uname
                    result.append(historydict)
                return jsonify(result)
            else:
                return "no historys"
        else:
            return "no page"

#单个历史记录
class foronehistory(Resource):

    #获得history
    def get(self,pageid,historyid):
        history = History.query.filter(History.pageid==pageid,History.id==historyid).first()
        if history is not None:
            return jsonify(history.to_json())
        else:
            return "no history"

    #history与page对换
    def patch(self,pageid,historyid):
        page = db.session.query(Page).filter(Page.id==pageid).first()
        history = db.session.query(History).filter(History.id==historyid,History.pageid==pageid).first()
        if history is not None and page is not None:
            history.hupdatetime,page.pcreatetime=page.pcreatetime,history.hupdatetime
            history.hcontent,page.pcontent= page.pcontent,history.hcontent
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e
            return "ok"
        else:
            return "no history or no page"

#搜索
class searchdocument(Resource):

    #搜索
    def get(self):
        searchstr = request.args.get("searchstr")
        if searchstr is not None:
            documents=Document.query.filter(Document.doctitle.contains(searchstr),Document.id!=1).all()
            if documents is not None:
                result=[]
                for document in documents:
                    result.append(document.to_json())
                return jsonify(result)
            else:
                return "no search"
        else:
            return "no searchstr"

#得到二级目录和page
class fortwoshow(Resource):

    def get(self,menuid):
        menus = Menu.query.filter(Menu.mfather==menuid,Menu.mfather!=1,Menu.mfather!=0).order_by(Menu.msort).all()
        pages = Page.query.filter(Page.menuid == menuid,Page.menuid!=1).order_by(Page.psort).all()
        result=[]
        dict = {}
        dictvalue=[]
        dictvalue2=[]

        for page in pages:
            dictvalue2.append(page.to_json())
        dict['pages']=dictvalue2


        for menu in menus:
            dictvalue.append(menu.to_json())
        dict['menus']=dictvalue

        result.append(dict)
        return jsonify(result)



api.add_resource(fordocument,'/document','/')
api.add_resource(foronedocument,'/document/<int:docmentid>','/<int:docmentid>')
api.add_resource(formenu,'/document/<int:documentid>/menu','/<int:documentid>/menu')
api.add_resource(foronemenu,'/document/<int:documentid>/menu/<int:menuid>','/<int:documentid>/menu/<int:menuid>')
api.add_resource(forpage,'/document/<int:documentid>/page','/<int:documentid>/page')
api.add_resource(foronepage,'/document/<int:documentid>/page/<int:pageid>','/<int:documentid>/page/<int:pageid>')
api.add_resource(forhistory,'/document/page/<int:pageid>/history','/page/<int:pageid>/history')
api.add_resource(foronehistory,'/document/page/<int:pageid>/history/<int:historyid>','/page/<int:pageid>/history/<int:historyid>')
api.add_resource(searchdocument,'/search')
api.add_resource(fortwoshow,'/menu/<int:menuid>')

if __name__=='__main__':
    app.run(debug=True)
