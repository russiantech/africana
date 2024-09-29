import jwt, json, random, time
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from sqlalchemy.sql import func
from flask import current_app, g, jsonify, request

db = SQLAlchemy()
#s_manager = LoginManager()


#this-will-allow-support-for-multiple-category-for-a-product
item_tag = db.Table(
    'item_tag', db.Model.metadata,
    db.Column('iid', db.Integer, db.ForeignKey('item.id')),
    db.Column('tid', db.Integer, db.ForeignKey('tag.id'))
)

class Brand(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    type = db.Column(db.String(100), unique=True, nullable=False, default='Sales')
    name = db.Column(db.String(100), unique=True, nullable=False, default='ecommerce')
    email = db.Column(db.String(100), unique=True, index=True, nullable=False, default='softwares@russian.com')
    phone = db.Column(db.String(20), unique=True)
    photo = db.Column(db.String(1000))
    title = db.Column(db.String(50))
    logo = db.Column(db.Text())  # ['male','female','other']
    city = db.Column(db.String(50))
    lang = db.Column(db.String(100))
    us = db.Column(db.String(1000))
    owner = db.Column(db.String(500))
    hype = db.Column(db.String(10000))  #slogan
    ratings = db.Column(db.Integer)
    reviews = db.Column(db.Integer)
    bank = db.Column(db.String(100), default='fcmb')
    acct = db.Column(db.Integer, default=5913408010)
    status = db.Column(db.Boolean(), default=True)
    verified = db.Column(db.Boolean(), default=False)

usr_role = db.Table(
    'usr_role',
    db.Column('uid', db.Integer, db.ForeignKey('user.id')),
    db.Column('rid', db.Integer, db.ForeignKey('role.id')),
    keep_existing=True
)

apportioned_items = db.Table(
    'apportioned_items',
    db.Column('apportioned_id', db.Integer, db.ForeignKey('apportioneditems.id')),
    db.Column('item_id', db.Integer, db.ForeignKey('item.id')),
    db.Column('deleted', db.Boolean, default=False)  # Add a 'deleted' column
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, unique=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100), index=True)
    username = db.Column(db.String(100), index=True, nullable=False, unique=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True, index=True)  #str type recommended bcos they're not meant for calculations
    password = db.Column(db.String(500), index=True, nullable=False)
    photo = db.Column(db.String(1000))
    admin = db.Column(db.Boolean(), default=False)  #true/false)
    gender = db.Column(db.String(50))  # ['male','female','other']
    city = db.Column(db.String(50))
    about = db.Column(db.String(5000))
    ratings = db.Column(db.Integer)
    reviews = db.Column(db.Integer)
    acct_no = db.Column(db.String(50))
    bank = db.Column(db.String(50))
    socials = db.Column(db.JSON, default={}) # socials: { 'fb': '@chrisjsm', 'insta': '@chris', 'twit': '@chris','linkedin': '', 'whats':'@techa' }
    src = db.Column(db.String(50))
    cate = db.Column(db.String(50))
    online = db.Column(db.Boolean(), default=False)  # 1-online, 0-offline
    status = db.Column(db.Boolean(), default=False)  # [ active(1), not active(0)]
    verified = db.Column(db.Boolean(), default=False)  # verified or not
    ip = db.Column(db.String(50))
    role = db.relationship('Role', secondary=usr_role, back_populates='user', lazy='dynamic')
    #role = db.relationship('Role', secondary=usr_role, lazy='dynamic')

    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())
    deleted = db.Column(db.Boolean(), default=False)  # 0-deleted, 1-not-deleted
    
    notified = db.relationship("Notification", backref="notified", lazy=True) 

    ord = db.relationship("Order", backref="usar", lazy=True) 
    
    def get_id(self):
        return str(self.id)

    def is_admin(self):
        return any(role.type == 'admin' for role in self.role)
    
    def permit(self):
        return [ r.type for r in self.role ]

    def generate_token(self, exp=600, type='reset'):
        payload = {'uid': self.id, 'exp': time.time() + exp, 'type': type }
        secret_key =  current_app.config['SECRET_KEY']
        return jwt.encode( payload, secret_key, algorithm='HS256')

    @staticmethod
    def verify_token(token):
        try:
            secret_key =  current_app.config['SECRET_KEY']
            uid = jwt.decode(token, secret_key, algorithms=['HS256'])['uid']
            user = User.query.get(uid)
            type = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['type']
        except:
            return
        return user, type

    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.photo}')"
        
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True)
    message = db.Column(db.String(255))
    photo = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_read = db.Column(db.Boolean, default=False)
    
    deleted = db.Column(db.Boolean(), default= 0)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())

#class Role(db.Model, RoleMixin):
class Role(db.Model):
    '''Role Table'''
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.String(100), unique=True)
    user = db.relationship('User', secondary=usr_role, back_populates='role', lazy='dynamic')

class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, default='0', nullable=True)
    cate = db.Column(db.Integer, db.ForeignKey('cate.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False) 
    dept = db.Column(db.String(80), nullable=False, default='k') 
    in_stock = db.Column(db.Integer, nullable=True, default=0)
    c_price = db.Column(db.Integer, nullable=True) #cost-price
    s_price = db.Column(db.Integer, nullable=False) #selling-price, not-a
    new_stock = db.Column(db.Integer, nullable=True)
    photos = db.Column(db.JSON, nullable=False, default='photo.png')
    
    disc = db.Column(db.Integer, default=0) #discount
    desc = db.Column(db.Text)
    
    attributes = db.Column(db.JSON) #[ weight, size, condition, model, type, subtype, processor etc] 
    color = db.Column(db.JSON) #color:- ['red','wine', 'etc'],
    size = db.Column(db.JSON) #size:- ['s','m', 'l', 'xl', 'xxl'],

    ip = db.Column(db.String(50))
    status = db.Column(db.Boolean(), default= 1) #[sold, active,]
    deleted = db.Column(db.Boolean(), default= 0)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())

    apportioned_quantities = db.relationship('ApportionedItems', secondary=apportioned_items, backref='items')
    #tag = db.relationship('Tag', secondary=item_tag, back_populates='item', overlaps="tag")
    tag = db.relationship('Tag', secondary=item_tag, back_populates='item', lazy='dynamic')
    salez = db.relationship("Sales", backref="salez", lazy=True)  # Monie->course
    sku = db.Column(db.String(1000))  #just refference (stock keeping unit)
     # Define the one-to-many relationship with StockHistory
    s_history = db.relationship('StockHistory', back_populates='item')

    def item_exists(item):
        return Item.query.filter(Item.id==item).first() is not None

    __table_args__ = (
        db.UniqueConstraint('name', 'cate', 'dept', 'deleted'),
    )

class ApportionedItems(db.Model):
    __tablename__ = 'apportioneditems'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, default='0', nullable=True)
    #item_series = db.Column(db.JSON) #[11,3,44,5,6] #//list of item ids
    items_dept = db.Column(db.String(80), nullable=False, default='k') 
    #item_type = db.Column(db.String(80), nullable=False, default='k') 
    items_title = db.Column(db.String(80), nullable=False) 
    items_qty = db.Column(db.Integer, nullable=False)

    deleted = db.Column(db.Boolean(), default= 0)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())

    """ Also has many-many relationship with Item model """
    # Define the one-to-many relationship with StockHistory & Sales
    #salez = db.relationship("Sales", back_populates="salez", lazy=True) 
    s_history = db.relationship('StockHistory', back_populates='apportioned_item', viewonly=True, lazy=True)

    # Custom method to mark the apportioned item as deleted
    def mark_deleted(self):
        self.deleted = True
        # Remove the association with items
        for item in self.items:
            self.items.remove(item)  # This disassociates the item

    def item_exists(item_id):
        return ApportionedItems.query.filter(ApportionedItems.id==item_id).first() is not None

    __table_args__ = (
        #db.UniqueConstraint('item_series', 'item_dept', 'item_type', 'item_qty', 'deleted'),
        db.UniqueConstraint('items_title', 'items_qty', 'user_id', 'deleted'),
    )
    

class StockHistory(db.Model):
    __tablename__ = 'stock_history'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, default='0', nullable=True)
    in_stock = db.Column(db.Integer, nullable=False)
    desc = db.Column(db.Text)
    version = db.Column(db.Integer, nullable=False, autoincrement=True)
    difference = db.Column(db.Integer, nullable=False, default=0)
    deleted = db.Column(db.Boolean(), default= False)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())

    apportioned_item_id = db.Column(db.Integer, db.ForeignKey('apportioneditems.id')) #can be null bcos, only item can be inserted atimes without apportioning.
    apportioned_item = db.relationship('ApportionedItems', back_populates='s_history', viewonly=True)
    
    #item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    item = db.relationship('Item', back_populates='s_history') #define the relationship back to Item

    # Check Constraint to ensure at least one of the columns is not null
    __table_args__ = (
        CheckConstraint("item_id IS NOT NULL OR apportioned_item_id IS NOT NULL"),
    )
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Sales(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qty_left = db.Column(db.Integer) #pcs-left
    qty = db.Column(db.Integer) #pcs-sold
    price = db.Column(db.Integer)
    total = db.Column(db.Integer)
    dept = db.Column(db.String(80), nullable=False, default='k') #[k=kitchen, c=cocktail, b=bar]
    comment = db.Column(db.String(100))
    #//relationships
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    #apportioned_item_id = db.Column(db.Integer, db.ForeignKey('apportioneditems.id'), nullable=False)

    deleted = db.Column(db.Boolean(), default=False)  # 0-deleted, 1-not-deleted
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())

    # Check Constraint to ensure at least one of the columns is not null
    __table_args__ = (
        CheckConstraint("item_id IS NOT NULL AND (qty_left IS NOT NULL OR qty IS NOT NULL)"),
    )
   
    def calctot(self, qty, price):
        self.total = qty * price

    def grandtot(self, total):
        return sum(total)

class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    cost = db.Column(db.Integer)
    dept = db.Column(db.String(80), nullable=False, default='k') #[k=kitchen, c=cocktail, b=bar]
    comment = db.Column(db.String(100)) #desc
    
    deleted = db.Column(db.Boolean(), default=False)  # 0-deleted, 1-not-deleted
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())
   
class Cate(db.Model):  #levels-> (super1->main2->sub3->mini4)
    __tablename__ = 'cate'
    id = db.Column(db.Integer, primary_key=True)
    parent = db.Column(db.Integer, db.ForeignKey('cate.id')) #or root
    lev = db.Column(db.Integer, default=0)
    name = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.String(100))
    photo = db.Column(db.String(50))
    dept = db.Column(db.String(50), nullable=False, default='k')
    children = db.relationship("Cate")
    #item = db.relationship('Item', secondary=item_cate, back_populates='cate')
    item = db.relationship('Item', backref='cates', lazy=True)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())
    deleted = db.Column(db.Boolean(), default=False)  # 0-deleted, 1-not-deleted

class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    item = db.relationship('Item', secondary=item_tag, back_populates='tag', lazy='dynamic')
    #item = db.relationship('Item', secondary=item_tag, backref='itag')

    def __repr__(self):
        return f'<Tag "{self.name}">' 

#can be comments/likes/dislikes/reviews/views
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)  # ranges from 1(worst) to 5(best)
    comment = db.Column(db.Text)  # reviews/comment/feed-back texts
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())
    deleted = db.Column(db.Boolean(), default=False)  # 0-deleted, 1-not-deleted

    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # user->feedback
    prod = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)  # user->course

randm = random.randint(0, 999999)

class Payment(db.Model):
    __tablename__ = 'payment'
    id = db.Column(db.Integer, unique=True, primary_key=True, nullable=False)
    usr_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Orderinfo->User->foreign-key
    #order_id = db.relationship("Order", backref="pment", lazy=True)  # Order->Payment->foreign-key
    
    txn_ref = db.Column(db.String(100)) #['dollar, naira etc]
    txn_amt = db.Column(db.Integer())
    txn_desc = db.Column(db.String(100)) 
    txn_status = db.Column(db.String(100), default='pending') #['pending','successful', 'cancelled', 'reversed']
    currency_code = db.Column(db.String(100)) #['dollar, naira, cedis etc]
    provider = db.Column(db.String(100)) #['paypal','stripe', 'visa', 'mastercard', paystack']

    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())
    deleted = db.Column(db.Boolean(), default=False)  # 0-deleted, 1-not-deleted

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usr_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    order_item = db.Column(db.JSON) #['key:alue' / 'itemid:Qty']
    
    order_id = db.Column(db.Integer, unique=True, nullable=False, default=(random.randint(0, 999999)))    

    pment_option = db.Column(db.String(45), nullable=False, default='fw') #[flutterwave, paystack, paypal,cash-on-delivery,cheque, etc]
    order_status = db.Column(db.String(50), nullable=True, default='pending') #[received, pending, delivered, processing, underway]
    in_cart = db.Column(db.Boolean(), default=False)  #[set to true if user-placed the order, set to false if it's a carted order(items in user cart)]

    name = db.Column(db.String(45), nullable=True)
    email = db.Column(db.String(100), nullable=False, index=True)
    phone = db.Column(db.String(45), nullable=True)
    zipcode = db.Column(db.String(45), nullable=False)
    adrs= db.Column(db.String(45), nullable=False)
    state = db.Column(db.String(45), nullable=False)
    country = db.Column(db.String(45), nullable=False)

    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())
    deleted = db.Column(db.Boolean(), default=False)  # 0-deleted, 1-not-deleted
