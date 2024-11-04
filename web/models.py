import jwt, random, time
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from sqlalchemy.sql import func
from flask import current_app
from datetime import datetime
db = SQLAlchemy()
#s_manager = LoginManager()

user_role_association = db.Table(
    'user_role_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    keep_existing=True
)

apportion_items_association = db.Table(
    'apportion_items_association',
    db.Column('apportion_id', db.Integer, db.ForeignKey('apportion.id')),
    db.Column('items_id', db.Integer, db.ForeignKey('items.id')),
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

    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())
    deleted = db.Column(db.Boolean(), default=False) 
    
    role = db.relationship('Role', secondary=user_role_association, back_populates='user', lazy='dynamic')

    notification = db.relationship("Notification", backref="user", lazy=True) 

    ord = db.relationship("Order", backref="usar", lazy=True) 
    
    def get_id(self):
        return str(self.id)

    def is_admin(self):
        return any(role.type == 'admin' for role in self.role)
    
    def roles(self):
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
    user = db.relationship('User', secondary=user_role_association, back_populates='role', lazy='dynamic')

class Items(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, default='0', nullable=True)
    name = db.Column(db.String(80), nullable=False) 
    dept = db.Column(db.String(80), nullable=False, default='k') 
    in_stock = db.Column(db.Integer, nullable=True, default=0)
    c_price = db.Column(db.Integer, nullable=True) #cost-price
    s_price = db.Column(db.Integer, nullable=False) #selling-price, not-a
    new_stock = db.Column(db.Integer, nullable=True)
    photos = db.Column(db.JSON)
    
    disc = db.Column(db.Integer, default=0) #discount
    desc = db.Column(db.Text)
    
    attributes = db.Column(db.JSON) #[ weight, size, condition, model, type, subtype, processor etc] 
    color = db.Column(db.JSON) #color:- ['red','wine', 'etc'],
    size = db.Column(db.JSON) #size:- ['s','m', 'l', 'xl', 'xxl'],
    sku = db.Column(db.String(1000))  #just refference (stock keeping unit)
    ip = db.Column(db.String(50))
    status = db.Column(db.Boolean(), default= 1) #[sold, active,]
    deleted = db.Column(db.Boolean(), default= 0)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    # apportioned_quantities = db.relationship('Apportion', secondary=apportion_items_association, backref='items')
    apportion_items = db.relationship('Apportion', secondary=apportion_items_association, backref='items')
    
    #tag = db.relationship('Tag', secondary=item_tag, back_populates='item', overlaps="tag")
    sales = db.relationship("Sales", backref="item", lazy=True)
    
    # Define the one-to-many relationship with StockHistory
    # s_history = db.relationship('StockHistory', back_populates='item')
    s_history = db.relationship('StockHistory', back_populates='item', cascade="all, delete")
    
    def item_exists(item):
        return Items.query.filter(Items.id==item).first() is not None

    __table_args__ = (
        db.UniqueConstraint('name', 'category_id', 'dept', 'deleted'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'name': self.name,
            'dept': self.dept,
            'in_stock': self.in_stock,
            'c_price': self.c_price,
            's_price': self.s_price,
            'new_stock': self.new_stock,
            'photos': self.photos,
            'disc': self.disc,
            'desc': self.desc,
            'attributes': self.attributes,
            'color': self.color,
            'size': self.size,
            'ip': self.ip,
            'status': self.status,
            'deleted': self.deleted,
            'created': self.created.isoformat() if self.created else None,
            'updated': self.updated.isoformat() if self.updated else None,
            'sku': self.sku,
            
            # Relationships (avoid recursion)
            'apportion_items': [item.id for item in self.apportion_items] if self.apportion_items else [],
            # 'tags': [tag.id for tag in self.tag.all()] if self.tag else [],
            'stock_history': [history.to_dict() for history in self.s_history] if self.s_history else [],
            
            # 'sales': [sale.to_dict() for sale in self.sales] if self.sales else [],
            # 'sales': [{'id': sale.id, 'title': sale.title} for sale in self.sales] if self.sales else [],
            # NOTE: Below is prefered instead of  to_dict() to avoid infinite loop that result to maximum recursion error due to 
            # multiple use of to_dict on both Items and other models like Sales
            
            'sales': [
                {
                    'id': sale.id,
                    'title': sale.title,
                    'qty': sale.qty,
                    'qty_left': sale.qty_left,
                    'price': sale.price,
                    'created': sale.created.isoformat() if isinstance(sale.created, datetime) else sale.created,
                    # Add other relevant fields for Sales as needed
                }
                for sale in self.sales
            ] if self.sales else [],
        }

class Apportion(db.Model):
    __tablename__ = 'apportion'
    id = db.Column(db.Integer, primary_key=True)
    dept = db.Column(db.String(80), nullable=False, default='k') 
    product_title = db.Column(db.String(255), nullable=False)
    main_qty = db.Column(db.Integer, nullable=False)
    initial_apportioning = db.Column(db.Integer, nullable=False)
    apportioned_qty = db.Column(db.Integer, nullable=False)
    extracted_qty = db.Column(db.Integer, default=0)
    cost_price = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    extractions = db.relationship('Extraction', backref='apportion', lazy=True)
    s_history = db.relationship('StockHistory', backref='apportion')
    
    def to_dict(self):
        """Convert the Apportion instance to a dictionary."""
        return {
            "id": self.id,
            "product_title": self.product_title,
            "dept": self.dept,
            "main_qty": self.main_qty,
            "initial_apportioning": self.initial_apportioning,
            "apportioned_qty": self.apportioned_qty,
            "extracted_qty": self.extracted_qty or self.initial_apportioning - self.apportioned_qty,
            "cost_price": self.cost_price,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            # Additional details if needed
            "extractions": [ extraction.to_dict() for extraction in self.extractions] if self.extractions else [],
            "s_history": [ history.to_dict() for history in self.s_history ] if self.s_history else []
        }

class Extraction(db.Model):
    __tablename__ = 'extracted'
    id = db.Column(db.Integer, primary_key=True)
    extracted_title  = db.Column(db.String(255), nullable=False)
    # Foreign key to Apportion table
    extracted_qty = db.Column(db.Integer, nullable=False)
    remaining_stock = db.Column(db.Integer)
    descr = db.Column(db.String(255))
    # sales_qty = db.Column(db.Integer, default=0)
    
    # One-to-many relationship with Sale
    sales = db.relationship('Sales', backref='extraction', lazy=True)
    apportion_id = db.Column(db.Integer, db.ForeignKey('apportion.id'), nullable=False)  # Fixing the FK reference

    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())

    def to_dict(self):
        """Convert the Apportion instance to a dictionary."""
        return {
            "id": self.id,
            "extracted_title": self.extracted_title,
            "product_title": self.apportion.product_title,
            "apportion_id": self.apportion_id,
            "extracted_qty": self.extracted_qty,
            "remaining_stock": self.remaining_stock,
            "descr": self.descr,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "created_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            
            # "sales": [sale.to_dict() for sale in self.sales] if self.sales else [],
            'sales': [
                {
                    'id': sale.id,
                    'title': sale.title,
                    'qty': sale.qty,
                    'qty_left': sale.qty_left,
                    'price': sale.price,
                    'created': sale.created.isoformat() if isinstance(sale.created, datetime) else sale.created,
                    # Add other relevant fields for Sales as needed
                }
                for sale in self.sales
            ] if self.sales else [],
        }
    
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

    # New Apportion Model
    apportion_id = db.Column(db.Integer, db.ForeignKey('apportion.id')) #can be null bcos, only item can be inserted atimes without apportioning.
    apportion_item = db.relationship('Apportion', back_populates='s_history', viewonly=True)
    
    extracted_id = db.Column(db.Integer, db.ForeignKey('extracted.id')) #can be null bcos, only item can be inserted atimes without apportioning.
    extracted_item = db.relationship('Apportion', back_populates='s_history', viewonly=True)
    
    #item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    item = db.relationship('Items', back_populates='s_history') #define the relationship back to Item

    # Check Constraint to ensure at least one of the columns is not null
    __table_args__ = (
        CheckConstraint("item_id IS NOT NULL OR apportion_id IS NOT NULL"),
    )
    # print(c for c in StockHistory.__table__.columns)
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    

    def to_dict(self):
        """Convert StockHistory instance to dictionary, including related models."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "in_stock": self.in_stock,
            "desc": self.desc,
            "version": self.version,
            "difference": self.difference,
            "deleted": self.deleted,
            "created": self.created.isoformat() if isinstance(self.created, datetime) else self.created,
            "updated": self.updated.isoformat() if isinstance(self.updated, datetime) else self.updated,
            
            "item": {
                "id": self.item.id,
                "name": self.item.name,
                # Include other necessary item fields
            } if self.item else None,
            
            "apportion": {
                "id": self.apportion_item.id,
                "product_title": self.apportion_item.product_title,
                # Include other necessary apportion fields
            } if self.apportion_item else None,
            
            "extracted": {
                "id": self.extracted_item.id,
                "extracted_title": self.extracted_item.extracted_title,
                # Include other necessary extraction fields
            } if self.extracted_item else None,
            
        }

class Sales(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))  # e.g., 'Chicken & Chips'
    qty_left = db.Column(db.Integer, default=0) #pcs-left
    qty = db.Column(db.Integer) #pcs-sold
    price = db.Column(db.Integer) # Combined price
    total = db.Column(db.Integer)
    dept = db.Column(db.String(80), nullable=False, default='k') #[k=kitchen, c=cocktail, b=bar]
    comment = db.Column(db.String(100))
    
    #!relationships
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    extracted_id = db.Column(db.Integer, db.ForeignKey('extracted.id'))

    deleted = db.Column(db.Boolean(), default=False)  # 0-deleted, 1-not-deleted
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())

    # Check Constraint to ensure at least one of the columns is not null
    # __table_args__ = (
    # CheckConstraint(
    #     "(item_id IS NOT NULL OR extracted_id IS NOT NULL) AND "
    #     "(title IS NOT NULL AND price IS NOT NULL) AND "
    #     "(qty_left IS NOT NULL OR qty IS NOT NULL)",
    #     name="sales_item_extracted_qty_check"
    # ),
    # )
    
    __table_args__ = (
        CheckConstraint(
            "(item_id IS NOT NULL AND (qty IS NOT NULL OR qty_left IS NOT NULL)) "
            "OR (item_id IS NULL AND extracted_id IS NULL AND title IS NOT NULL AND price IS NOT NULL)",
            name="item_apportion_extraction_sales_constraints"
        ),
    )
    
    def to_dict(self):
        """Converts the Sales instance to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "qty_left": self.qty_left,
            "qty": self.qty,
            "price": self.price,
            # "c_price": self.item.c_price,
            # "s_price": self.item.s_price,
            "total": self.total,
            "dept": self.dept,
            "comment": self.comment,
            "item_id": self.item_id,
            "extracted_id": self.extracted_id,
            "deleted": self.deleted,
            "created": self.created.isoformat() if isinstance(self.created, datetime) else self.created,
            "updated": self.updated.isoformat() if isinstance(self.updated, datetime) else self.updated,
            # Related item and extraction information
            "items": self.item.to_dict() if self.item else None,
            "extraction": self.extraction.to_dict() if self.extraction else None,
        }
        
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
   
class Category(db.Model):  #levels-> (super1->main2->sub3->mini4)
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    parent = db.Column(db.Integer, db.ForeignKey('category.id')) #or root
    lev = db.Column(db.Integer, default=0)
    name = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.String(100))
    photo = db.Column(db.String(50))
    dept = db.Column(db.String(50), nullable=False, default='k')
    children = db.relationship("Category")
    items = db.relationship('Items', backref='categories', lazy=True)
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())
    deleted = db.Column(db.Boolean(), default=False)  # 0-deleted, 1-not-deleted

#can be comments/likes/dislikes/reviews/views
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)  # ranges from 1(worst) to 5(best)
    comment = db.Column(db.Text)  # reviews/comment/feed-back texts
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())
    deleted = db.Column(db.Boolean(), default=False)  # 0-deleted, 1-not-deleted

    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # user->feedback
    items = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)  # user->course

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
