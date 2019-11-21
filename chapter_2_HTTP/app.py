# encoding: utf-8

"""
@ author: wangmingrui
@ time: 2019/11/20 10:42
@ desc: Http 请求
"""

from flask import Flask, request, escape, redirect, url_for, abort, make_response, jsonify, session, g
from urllib.parse import urlparse, urljoin
from jinja2.utils import generate_lorem_ipsum
import datetime
import os
import time

app = Flask(__name__)
app.count = None


# HTTP request
@app.before_first_request
def do_first():
    app.count = 0
    print('init count: %d' % app.count)


@app.before_request
def before_request_doing():
    g.name = request.args.get('name', 'Flasker')
    app.count += 1
    print('count: %d' % app.count)


@app.route('/hello')  # /hello?name=John
def hello():
    name = request.args.get('name', 'Flask')  # 获取查询参数name的值，如果没有使用默认值Flask
    return '<h1> Hello %s </h1>' % escape(name)


@app.route('/hello2', methods=['GET', 'POST'])
def hello2():
    return '<h1> Hello World! </h1>'


@app.route('/goback/<int:year>')  # url变量转换器，默认为字符串
def go_back(year):
    now_year = datetime.datetime.now().year - year
    return 'Welcome to %d !' % now_year


# use any URL converter
@app.route('/colors/<any(blue, white, red):color>')
def three_colors(color):
    return '<p>Love is patient and kind. Love is not jealous or boastful or proud or rude. %s </p>' % color


# HTTP response
@app.route('/hello3')
def hello3():
    return '<h1> Hello World </h1>', 201  # 自定义返回状态码


@app.route('/hello4')
def hello4():
    return "", 302, {'Location': '/hello'}  # 302重定向，添加Location Header指明跳转地址


@app.route('/hello5')
def hello5():
    return redirect('/hello')


@app.route('/hello6')
def hello6():
    return redirect(url_for(hello))


# 错误响应
@app.route('/404')
def not_found():
    abort(404)


@app.route('/brew/<drink>')
def brew_drink(drink):
    if drink == 'coffee':
        abort(418)  # 抛出自定义错误
    else:
        return 'a drop of tea'


# 返回其他文件类型
@app.route('/text')
def text():
    response = make_response('Hello World!!!')
    response.mimetype = 'text/plain'
    return response


@app.route('/foo2')
def foo2():
    response = make_response('Hello World!!!')
    response.headers['Content-Type'] = 'text/plain;charset=utf-8'
    return response


# 使用不同类型表式数据
@app.route('/note', defaults={'content_type': 'text'})
@app.route('/note/<content_type>')
def note(content_type):
    content_type = content_type.lower()

    # text/plain
    if content_type == 'text':
        body = '''Note
to: Peter
from: Jane
heading: Reminder
body: Don't forget the party!
'''
        response = make_response(body)
        response.mimetype = 'text/plain'

    # text/html
    elif content_type == 'html':
        body = """<!DOCTYPE html>
<html>
<head></head>
<body>
    <h1>Note</h1>
    <p>to: Peter</p>
    <p>from: Jane</p>
    <p>heading: Reminder</p>
    <p>body: <strong>Don't forget the party!</strong></p>
</body>
</html>
        """
        response = make_response(body)
        response.mimetype = 'text/html'

    # text/xml
    elif content_type == 'xml':
        body = """<?xml version="1.0" encoding="UTF-8"?>
<note>
    <to>Peter</to>
    <from>Jane</from>
    <heading>Reminder</heading>
    <body>Don't forget the party!</body>
</note>
        """
        response = make_response(body)
        response.mimetype = 'text/xml'

    # application/json
    elif content_type == 'json':
        body = {
            "note": {
                "to": "Peter",
                "from": "Jane",
                "heading": "Reminder",
                "body": "Don't forget the party!"
            }
        }
        body = jsonify(body)  # 将dict转为json，并自动设置mime为application/json
        response = make_response(body)
        response.mimetype = 'application/json'
    else:
        abort(400)
    return response


@app.route('/foo')
def foo():
    return jsonify(message="Error"), 500


# Cookie: 在请求和响应报文中添加Cookie数据可以保存客户端的状态信息
@app.route('/set/<name>')
def set_cookie(name):
    response = make_response(redirect(url_for('hello_with_cookie')))
    response.set_cookie('name', name)
    return response


@app.route('/hello-wc')
def hello_with_cookie():
    name = request.args.get('name')
    if name is None:
        name = request.cookies.get('name', 'Human')  # 从cookie中获取name值
    return '<h1> Hello %s </h1>' % name


# session: 将Cookie数据加密存储
# 设置加密秘钥,可以使设置在Flask的secret_key属性中，或者配置在环境变量或.env文件中
# app.secret_key = "naHkns1djfh_jKKas-8knsyfOPo"
app.secret_key = os.getenv('SECRET_KEY', 'secret_key')
print(app.secret_key)


@app.route('/login')
def login():
    session['logged_in'] = True  # 写入session
    return redirect(url_for('hello_with_session'))


@app.route('/hello_ws')
def hello_with_session():
    name = request.args.get('name')
    if name is None:
        name = request.cookies.get('name', 'Human')
    response = '<h1> Hello, %s </h1>' % name
    # 根据用户认证状态返回不同内容
    if 'logged_in' in session:
        response += '[Authenticated]'
        print(session.get('logged_in'))
    else:
        response += '[Not Authenticated]'
    return response


@app.route('/admin')
def admin():
    if 'logged_in' not in session:
        abort(403)
    return 'Welcome to admin page'


@app.route('/logout')
def logout():
    if 'logged_in' in session:
        session.pop('logged_in')
    return redirect(url_for('hello_with_session'))


# 上下文context
# 全局变量g
@app.route('/g')
def var_g():
    return '<h1> Hello, %s </h1>' % g.name


# 重定向回上一个页面
@app.route('/page1')
def page_1():
    return '<p> Foo page1 </p> <a href="%s">Do something</a>' % url_for('do_something',
                                                                        next=request.full_path)  # 使用next参数，告诉被调用函数之前页面的url


@app.route('/page2')
def page_2():
    return '<p> Bar page2 </p> <a href="%s">Do something </a>' % url_for('do_something', next=request.full_path)


@app.route('/do_something')
def do_something():
    # do something
    time.sleep(1)
    # if request.args.get('next') is None:
    #     return redirect(request.referrer or url_for('hello'))  # 使用referrer重定向回上一页面,当referer为空时则回到hello
    # else:
    #     return redirect(request.args.get('next', url_for('hello'))) # 使用next参数传入的url跳转
    return redirect_back()


def redirect_back(default='hello', **kwargs):
    """重定向回上一页面"""
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):  # 判断跳转url是否安全
            return redirect(target)
    return redirect(url_for(default, **kwargs))


# 对URL进行安全验证, 判断next变量值是否为程序内部URL
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.neturl


# 使用Ajax技术发送异步请求
@app.route('/post')
def show_post():
    post_body = generate_lorem_ipsum(n=2)  # 生成两端随机文本
    return """
<h1> A very long post </h1>
<div class="body">%s</div>
<button id="load">Load More</button>
<script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
<script type="text/javascript">
$(function() {
    $('#load').click(function() {
        $.ajax({
            url: '/more',
            type: 'get',
            success: function(data){
                $('.body').append(data);
            }
        })
    })
})
</script>""" % post_body


@app.route('/more')
def load_post():
    return generate_lorem_ipsum(n=1)
