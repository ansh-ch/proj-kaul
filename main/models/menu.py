# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(B('Food',SPAN(2),'py'),XML('&trade;&nbsp;'),
                _class="navbar-brand",_href="http://www.web2py.com/",
                _id="web2py-logo")
response.title = request.application.replace('_',' ').title()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Your Name <you@example.com>'
response.meta.description = 'a cool new app'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    (T('Home'), False, URL('default', 'index'), [])
]

DEVELOPMENT_MENU = True

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():
    # shortcuts
    app = request.application
    ctr = request.controller
    # useful links to internal and external resources
    try:
        xu=auth.user.id
        q1=(db.auth_membership.user_id==xu)
        q2=(db.auth_membership.group_id==db.auth_group.id)
        ys=db(q1 & q2).select(db.auth_group.role)
        flag=0
        for y in ys:
            if y.role=="Manager":
                flag=1
        if flag==1:
            response.menu += [
                (T('Manage'), False, None , [
                (T('Add Restaurant'), False, '/main/default/addrest'),
                (T('Add Menu'), False, '/main/default/addmenu' ),
                (T('Pending Orders'),False,'/main/default/pend')])
                ]
    except:
        pass
    response.menu+=[
        (T('My_Cart'), False , URL('default','cart')),
        (T('Community'), False, None, [
        (T('Groups'), False,
        'http://www.web2py.com/examples/default/usergroups'),
         (T('Twitter'), False, 'http://twitter.com/web2py'),
         (T('Live Chat'), False,
         'http://webchat.freenode.net/?channels=web2py'),
         ])
        ]
if DEVELOPMENT_MENU: _()

if "auth" in locals(): auth.wikimenu()
