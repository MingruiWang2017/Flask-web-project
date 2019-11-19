# encoding: utf-8

"""
@ author: wangmingrui
@ time: 2019/11/18 14:21
@ desc: 最小Flask程序
"""

from flask import Flask
import click

app = Flask(__name__)  # 实例化Flask类


@app.route('/')
def index():
    return '<h1> Hello World </h1>'


# 一个视图函数可以绑定多个URL
@app.route('/hi')
@app.route('/hello')
def say_hello():
    return '<h1> Hello Flask </h1>'


# 动态URL
@app.route('/greet', defaults={'name': 'Flasker'})  # 设置name 默认值，防止在未传<name>时返回404
@app.route('/greet/<name>')
def greet(name):
    return '<h1> Hello %s </h1>' % name


# 将函数注册为flask命令，函数名称可以设置，否则默认为函数名（不能有下划线） --> flask say-hello
@app.cli.command('say-hello')
def hello():
    click.echo("Hello, Flasker!")
