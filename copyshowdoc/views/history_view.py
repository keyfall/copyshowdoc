from flask import jsonify
from flask_restful import Resource

from copyshowdoc.model.models import db, History



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
