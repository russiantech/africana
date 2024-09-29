from os import environ, path
import secrets
from PIL import Image
from flask import current_app
from flask_login import current_user

from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError
from flask import current_app, flash

regex = "([^\\s]+(\\.(?i)(jpe?g|png|gif|bmp))$)"

cate_choice=[
    (0.0,'...Course category...'),
    (0,'All Courses'), (1,'Trending Courses'), (2,'New Courses'), (3,'Free Courses'), (4,'Analytics'),
    (5,'Moile Development'), (6,'Hacking'), (7,'Cyber Security'), (8,'Programming'),  (9,'Computer Appreciation'),
    (10,'Web Development'),(11, 'Machine Learning'), (12,'Software Testing'), (13,'Javascript'), (14,'Beginner'), 
    (15,'Advanced'), (16,'Internet Of Things'), (17,'Full Stack Development'), (18,'Software Testing'), (19,'Artificial Intelligence '), 
    (20,'Python'),  (21,'Game Development'), (22,'Digital Marketing')
    ]

level_choice = [(0,'...Course Level....'), (1,'Novice'), (2,'Beginner'), (3,'Expert'),  (4,'Pro'), (5,'Advanced') ]

lang_choice = [(0,'...Course Language...'), (1,'English'), (2,'French'), (3,'Spanish'), (4,'Latin'), (5,'Pidgin'), (6,'Other')]

#as alternative to FileAllowed() I can also use this allowed_file()
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in environ.get('ALLOWED_EXTENSIONS')


def validate_(form, model, row):
    if model.query.filter_by(row=form).first():
        raise ValidationError(f'This very {form} has already been saved with another course.')

def saveV(form_file):
    try:
        if form_file:
            random_hex = secrets.token_hex(2)
            _, f_ext = path.splitext(form_file.filename)
            fname = secure_filename(_ + random_hex + f_ext).lower()
            vpath = path.join(current_app.root_path, 'static/img/uploads/videos', fname)
            form_file.save(vpath)
            return fname
        pass
    except UnidentifiedImageError:
        return flash(f'Invalid File Type {form_file} ')

def saveM(form_file):
    try:
        if form_file:
            random_hex = secrets.token_hex(2)
            _, f_ext = path.splitext(form_file.filename)
            fname = secure_filename(_ + random_hex + f_ext).lower()
            mpath = path.join(current_app.root_path, 'static/img/uploads/materials', fname)
            output_size = (600, 430)
            i = Image.open(form_file)
            i.thumbnail(output_size)
            i.save(mpath)
            return fname
        pass
    except UnidentifiedImageError:
        return flash(f'Invalid File Type {form_file} ')



def saveP(form_file):
    try:
        if form_file:
            random_hex = secrets.token_hex(2)
            _, f_ext = path.splitext(form_file.filename)
            fname = secure_filename(_ + random_hex + f_ext).lower()
            ppath = path.join(current_app.root_path, 'static/img/course/', fname)
            output_size = (600, 430)
            i = Image.open(form_file)
            i.thumbnail(output_size)
            i.save(ppath)
            return fname
        pass
    except UnidentifiedImageError:
        return flash(f'Invalid File Type {form_file} ')
    
def save_photo(form_file):
    try:
        if form_file:
            random_hex = secrets.token_hex(2)
            _, f_ext = path.splitext(form_file.filename) if form_file.filename else current_user.photo
            #fname = secure_filename(_ + random_hex + f_ext).lower()
            fname = secure_filename(current_user.username + '_'+ _ + random_hex + f_ext).lower() #->username+'underscore(_)+origial-file-name+file-extension
            photo_path = path.join(current_app.root_path, 'static/img/profile', fname)
            size = (320, 320)
            i = Image.open(form_file)
            i.thumbnail(size)
            i.save(photo_path)
            return fname
        pass
    except UnidentifiedImageError:
        return flash(f'Invalid File Type {form_file} ')


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = path.splitext(form_picture.filename)
    photo_name = (random_hex + f_ext).lower()
    picture_path = path.join(current_app.root_path, 'static/img/profile', photo_name)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return photo_name

