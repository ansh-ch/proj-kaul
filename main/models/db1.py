db = DAL('sqlite://storage.db')

from gluon.tools import Auth
auth = Auth(db)
auth.settings.table_user_name = 'auth_user'
auth.settings.extra_fields['auth_user']= [ Field('Address','string',notnull=True),Field('city','string',notnull=True),Field('phone')]

auth.define_tables(username=True)
auth.verify_Email=True

db.define_table('Main',
        Field('User','string',requires = [IS_ALPHANUMERIC()]),
        Field('Rest','string',requires = [IS_ALPHANUMERIC()]),
        Field('Cuisine','string',requires = IS_NOT_EMPTY()),
        Field('Rating','integer',requires = IS_NOT_EMPTY()),
        Field('City','string',requires = IS_NOT_EMPTY()),
        Field('Logo','upload'),
        format='%(Rest)s'
)

db.define_table('TheOrder',
        Field('Rest','string',requires = IS_NOT_EMPTY()),
        Field('Foodit','string',requires = IS_NOT_EMPTY()),
        Field('Price','integer',requires = IS_NOT_EMPTY())
)

db.define_table('Menu',
        Field('Menu_id','reference Main'),
        Field('Rest','string'),
        Field('NVeg','string',requires = IS_NOT_EMPTY()),
        Field('Item','string',requires =  [IS_ALPHANUMERIC()]),
        Field('Price','integer',requires = IS_NOT_EMPTY()),
        Field('Image',type='upload'),
)

db.define_table('Pending',
        Field('Rest','string',requires = IS_NOT_EMPTY()),
        Field('User','string',requires = IS_NOT_EMPTY()),
        Field('Address','string',requires = IS_NOT_EMPTY()),
        Field('Item','string',requires = IS_NOT_EMPTY()),
        Field('Count','integer',requires = IS_NOT_EMPTY()),
        Field('Price','integer',requires = IS_NOT_EMPTY())
)

db.define_table('Rat',
        Field('Rest','string'),
        Field('User','string'),
)

db.define_table('Cities',
        Field('Name','string',requires = IS_NOT_EMPTY()),
        format='%(Name)s'
)

db.define_table('EAT',
        Field('Name','string',requires = IS_NOT_EMPTY()),
        format='%(Name)s'
)

db.define_table('Advertisement',
		Field('Rest','string',requires = IS_NOT_EMPTY()),
		Field('Caption','upload',requires= IS_NOT_EMPTY())
)

#db.Menu.Menu_id.requires = IS_IN_DB(db,db.Main.id,'%(Rest)s')
db.Menu.Menu_id.writable=db.Menu.Menu_id.readable=False

db.Advertisement.Rest.requires=IS_IN_DB(db,db.Main.Rest,'%(Name)s')

db.Main.Rest.requires=IS_NOT_IN_DB(db,db.Main.Rest)
db.Main.Rating.writable=db.Main.Rating.readable=False
db.Main.User.writable=db.Main.User.readable=False
x=db(db.EAT.Name=='Veg').select()
if len(x) == 0:
    db.EAT.insert(Name='Veg')
y=db(db.EAT.Name=='Non-Veg').select()
if len(y) == 0:
    db.EAT.insert(Name='Non-Veg')
db.Menu.NVeg.requires=IS_IN_DB(db,db.EAT.id,'%(Name)s')
db.Menu.Rest.writable=db.Menu.Rest.readable=False
db.Main.City.requires=IS_IN_DB(db,db.Cities.id,'%(Name)s')
