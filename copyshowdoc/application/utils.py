from flask_restful import reqparse

from copyshowdoc.model.models import db, Menu

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


def get_doc_args():
    doc_parse = reqparse.RequestParser()
    doc_parse.add_argument('doctitle', type=str, help="用户名验证错误", required=True)
    doc_parse.add_argument('docdescribe', type=str, help="请填写描述", required=True)
    doc_parse.add_argument('uid', type=int, required=True)
    return doc_parse


def get_menu_args():
    menu_parse = reqparse.RequestParser()
    menu_parse.add_argument('mtitle',type=str,help="用户名验证错误",required=True)
    menu_parse.add_argument('msort',type=int,default=99)
    menu_parse.add_argument('docid',type=int,help="文档号验证错误")
    menu_parse.add_argument('uid',type=int,required=True)
    #0是1级展示
    menu_parse.add_argument('mfather',type=int,help="上级验证错误",required=True)
    return menu_parse

def get_page_args():
    page_parse = reqparse.RequestParser()
    page_parse.add_argument('ptitle',type=str,help="用户名验证错误",required=True)
    page_parse.add_argument('psort',type=int,default=99)
    page_parse.add_argument('menuid',type=int,help="目录验证错误",required=True)
    page_parse.add_argument('uid',type=int,required=True)
    page_parse.add_argument('docid',type=int,help="文档号验证错误")
    page_parse.add_argument('pcontent',type=str,help="加一些内容",required=True)
    page_parse.add_argument('pcreatetime',type=str,help="日期验证错误",required=True)
    return page_parse
