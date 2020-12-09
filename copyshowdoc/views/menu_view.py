from flask import jsonify
from flask_restful import Resource

from copyshowdoc.model.models import db, Document, Menu
from copyshowdoc.application.utils import get_menu_args, delmenufamily, getmenufamily

menu_parse = get_menu_args()


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
