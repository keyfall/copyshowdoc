from flask_restful import Api

from copyshowdoc.application.app import app
from copyshowdoc.views.document_view import fordocument, foronedocument
from copyshowdoc.views.menu_view import formenu, foronemenu
from copyshowdoc.views.page_view import forpage, foronepage, fortwoshow
from copyshowdoc.views.history_view import forhistory, foronehistory
from copyshowdoc.views.search_view import searchdocument

api = Api(app)

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
