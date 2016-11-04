# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    try:
        name=auth.user.username
    except:
        name="user"
    x="Hi "+name
    response.flash = T(x)
    form=SQLFORM.factory(Field('Select_City',requires=IS_IN_DB(db,'Cities.id','%(Name)s')))
    if form.process().accepted:
        city=form.vars.Select_City
        redirect(URL('first',vars=dict(city=city)))
    return dict(message=T('Welcome To Food2py'),form=form)

def first():
    session.y={}
    session.city=request.vars.city
    name=request.vars.city
    city=db(db.Cities.id==name).select(db.Cities.Name)
    city=str(city[0])
    city=city[city.find(':')+3::]
    city=city[:city.find('\''):]
    rows=db(db.Main.City==name).select()
    return dict(rows=rows,city=city)

def second():
    name="EMPTY :P"
    if len(request.args)>0:
        name=request.args(0)
    session.Rest=name
    q1=(db.Menu.Rest==name)
#    q2=(db.Menu.Menu_id==db.Main.id)
    rows=db( q1 ).select()
    return dict(rows=rows)


@auth.requires_membership('Manager')
def restdisplay():
    name=auth.user.username
    rows=db( db.Main.User == name ).select()
    return dict(rows=rows)

@auth.requires_membership('Manager')
def menudisplay():
    name=auth.user.username
    crows=db(db.Main.User==name).select(db.Main.Rest)
    h=""
    for crow in crows:
        h=crow.Rest
    rows=db( db.Menu.Rest == h ).select()
    return dict(rows=rows)

@auth.requires_login()
def change():
    x=int(request.args(0))
    rest=str(request.args(1))
    rat=int(request.args(2))
    if x!=0:
        name=auth.user.username
        t=db( db.Rat.Rest==rest ).select()
        p=db( (db.Rat.Rest==rest) & (db.Rat.User==name) ).select()
        if len(t) > 0:
            if len(p) == 0:
                session.y[rest]=x
                db(db.Main.Rest == rest).update(Rating = rat+x)
                db.Rat.insert(Rest=rest,User=name)
                rat=rat+x
        else:
            db.Rat.insert(Rest=rest,User=name)
            db(db.Main.Rest==rest).update( Rating = rat+x)
            session.y[rest]=x
            rat=rat+x
        if len(t) > 0 and len(p)>0:
            if rest in session.y:
                rat=rat+session.y[rest]

    if x==0:
        if rest in session.y:
            rat=rat+session.y[rest]
    return rat

@auth.requires_login()
def delete4():
    x=str(request.args(0))
    db(db.Menu.Rest==x).delete()
    db(db.Main.Rest==x).delete()
    db(db.Rat.Rest==x).delete()
    db(db.Pending.Rest==x).delete()
    return 'Menu_item deleted'

@auth.requires_login()
def delete3():
    x=int(request.args(0))
    db(db.Menu.id==x).delete()
    return 'Menu_item deleted'

@auth.requires_login()
def delete2():
    db((db.Pending.User==request.args(0)) and (db.Pending.Item==request.args(1))).delete()
    return 'Pending List altered'


@auth.requires_login()
def delete():
    x=session.cartItem[int(request.args(0))]+' removed'
    response.flash = x
    del session.cartRest[session.cartItem[int(request.args(0))]]
    del session.cartNum[session.cartItem[int(request.args(0))]]
    session.cartItem.pop(int(request.args(0)))
    session.cartNVeg.pop(int(request.args(0)))
    session.cartPrice.pop(int(request.args(0)))
    y="Product Deleted"
    return y

@auth.requires_login()
def cart():
    try :
        a=session.cartItem[0]
    except:
        session.cartRest={}
        session.cartNum={}
        session.cartItem=[]
        session.cartNVeg=[]
        session.cartPrice=[]
    name=auth.user.username
    if request.vars.Item != None:
        try :
            session.cartNum[request.vars.Item]+=1
        except:
            session.cartItem.append(request.vars.Item)
            session.cartRest[request.vars.Item]=session.Rest
            session.cartNum[request.vars.Item]=1
            session.cartNVeg.append(request.vars.NVeg)
            session.cartPrice.append(request.vars.Price)
    return dict(name=name)

@auth.requires_login()
def paycontrol():
    form=SQLFORM.factory(Field('Address','string',requires=IS_NOT_EMPTY()))
    if form.process().accepted:
        session.address=form.vars.Address
        redirect(URL('success'))
    return dict(form=form)

@auth.requires_login()
def success():
    if len(session.address)==0:
        redirect(URL('paycontrol'))
    return dict()

@auth.requires_membership('Manager')
def pend():
    name=auth.user.username
    crows=db(db.Main.User==name).select(db.Main.Rest)
    h=""
    for crow in crows:
        h=crow.Rest
    rows=db(db.Pending.Rest==h).select()
    return dict(rows=rows)

@auth.requires_membership('Manager')
def addrest():
    name=auth.user.username
    rows=db(db.Main.User==name).select()
    if len(rows) > 0:
        flag=1
        form="You already have a restaurant"
    else:
        flag=0
    if flag == 0:
        form=SQLFORM(db.Main)
        form.vars.User=name
        form.vars.Rating=0
        form.process()
    return dict(form=form)

@auth.requires_membership('Manager')
def addmenu():
    name=auth.user.username
    crows=db(db.Main.User==name).select(db.Main.Rest)
    try:
        for crow in crows:
            h=crow.Rest
            form=SQLFORM(db.Menu)
            form.vars.Rest=h
            form.process()
    except:
        form="You don't have a Restaurant"
    return dict(form=form)

def download():
    return response.download(request,db)
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

"""@auth.requires_login()
def usad():"""
    


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
