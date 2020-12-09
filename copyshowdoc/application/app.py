from flask import Flask

app = Flask(__name__)

# 连接数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost/showdoc2?charset=utf8'

# 设置是否跟踪数据库的修改情况，一般不跟踪
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 数据库操作是否显示原始SQL语句，一般打开
app.config['SQLALCHEMY_ECHO'] = True
