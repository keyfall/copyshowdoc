from flask import request, jsonify
from flask_restful import Resource

from copyshowdoc.model.models import db, Document



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
