from flask import jsonify
from flask_restful import Resource

from copyshowdoc.model.models import db, Document
from copyshowdoc.application.utils import get_doc_args

doc_parse = get_doc_args()


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
