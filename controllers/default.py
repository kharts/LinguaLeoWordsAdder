# -*- coding: utf-8 -*-
# controllets/default.py - default controller
#
# Copyright 2015 kharts (https://github.com/kharts)
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

import urllib, urllib2, json
from cookielib import CookieJar

class Lingualeo:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.cj = CookieJar()

    def auth(self):
        url = "https://api.lingualeo.com/api/login"
        values = {
            "email" : self.email,
            "password" : self.password
        }

        return self.getContent(url, values)
    def getTranslates(self, word):
        url = "http://api.lingualeo.com/gettranslates?word=" + word
        return self.getContent(url, {})

    def addWord(self, word, tword):
        url = "https://api.lingualeo.com/addword"
        values = {
            "word" : word,
            "tword" : tword
        }
        return self.getContent(url, values)
    def getContent(self, url, values):
        data = urllib.urlencode(values)

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        req = opener.open(url, data)

        return json.loads(req.read())

    def check_auth(self):
        """
        Checks auth credentials
        :return: True - if email/password is correct. False - otherwise
        """

        res = self.auth()
        return (u"user" in res)

def index():
    """
    Prepares data for start (index) page
    :return: dictionary with data for start (index) page
    """

    prepare_header()
    #textarea = TEXTAREA(_name='textarea', _ROWS=20)
    textarea = TEXTAREA(_name='textarea')
    okbutton = INPUT(_VALUE='Get translations', _TYPE='submit')
    form = FORM("Insert words:",textarea,okbutton)
    words = []
    translations = []
    translations2 = []
    if form.accepts(request,session, keepvalues=True):
        words=getwords(form.vars.textarea)
        translations = gettranslations2(words)
    return dict(form=form, words=words, translations=translations)


def login():
    """
    Prepares data for login page
    :return: dictionary with data for login page
    """

    prepare_header()
    form_title = B("Enter your email and password")
    email_input = INPUT(_TYPE="text", _name="email", _ID="email")
    br = BR()
    password_input = INPUT(_TYPE="password",
                           _name="password",
                           _ID="password",
                           _VALUE="")
    submit_button = INPUT(_VALUE="Login", _TYPE="submit")
    table = TABLE(TR(TD(form_title)),
                  TR(TD("Email:"), TD(email_input)),
                  TR(TD("Password"), TD(password_input)),
                  TR(TD(""), TD(submit_button)))
    form = FORM(table, _METHOD="POST")
    #form = auth()
    if form.accepts(request, session):
        LL = Lingualeo(form.vars.email,
                       form.vars.password)
        if LL.check_auth():
            session.email = form.vars.email
            session.password = form.vars.password
            redirect(URL("index"))
        else:
            response.flash = "Email/password is incorrect"
    return dict(form=form)


def prepare_header():
    """
    Prepares header of page
    :return: None
    """

    response.title = None
    adminlabel = SPAN('Admin', _CLASS='highlighted')
    adminurl   = URL('admin','default','design', args=['LinguaLeoWordsAdder'])
    adminbutton = (adminlabel,False,adminurl,[])
    lingualeolabel = 'LinguaLeo'
    lingualeourl  = 'http://lingualeo.com'
    lingualeobutton = (lingualeolabel, False, lingualeourl, [])
    #adminlink = A(SPAN('Admin', _CLASS='highlighted'), _HREF=URL('admin','default','design', args=['LinguaLeoWordsAdder']))
    #menu = [{}]
    response.menu = [adminbutton,lingualeobutton]
    response.logo = A('LinguaLeo Words Adder', _HREF=URL('index'), _CLASS='brand')


def gettranslations(words):
    translations = []
    from urllib2 import urlopen
    import json
    for word in words:
        #response.flash = 'Translation word ' + word
        url = "http://lingualeo.com/ru/userdict3/getTranslations?word_value=" + word
        data = urlopen(url)
        fulltranslation = json.load(data)
        word_translations = fulltranslation['userdict3']['translations']
        word_translations.sort(key=translation_key)
        translation = {'word': word, 'translations': word_translations}
        translations.append(translation)
    return translations

def gettranslations2(words):
    translations = []
    email = ""
    password = ""
    LL = Lingualeo(email, password)
    LL.auth()
    for word in words:
        result = LL.getTranslates(word)
        word_translations = result['translate']
        word_translations.sort(key=translation_key2)
        translation = {'word': word, 'translations': word_translations}
        translations.append(translation)
    return translations

def translation_key(translation):
    return -translation['translate_votes']

def translation_key2(translation):
    return -translation['votes']

def add_word_translation():
    email = ""
    password = ""
    LL = Lingualeo(email, password)
    LL.auth()
    word = request.vars.word
    translation = ""
    for charcode in request.vars.translation:
        translation = translation + unichr(int(charcode))
    translation = translation.encode("utf-8")
    result = LL.addWord(word, translation)
    if result['added_translate_count']>0:
        response.flash = "The word " + word + " has been successfully added to the dictionary"
        id = request.vars.id
        response.js = "document.getElementById('" + id + "').className = 'btn btn-info';"
    
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
