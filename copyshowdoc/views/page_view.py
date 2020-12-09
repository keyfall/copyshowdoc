import datetime
from flask import jsonify
from flask_restful import Resource

from copyshowdoc.model.models import db, Document, Menu, Page, Userpage, User
from copyshowdoc.application.utils import get_page_args

page_parse = get_page_args()


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
