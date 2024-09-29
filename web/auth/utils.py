from os import path
import secrets
from PIL import Image
from flask import url_for, render_template, current_app
from flask_mail import Message
from threading import Thread

from web import mail

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)




def async_send_mail(app, msg):
    with app.app_context():
        mail.send(msg)

def send_mail(subject, recipient, template, **kwargs):
    msg = Message(subject, sender= 'noreply@russian.com', recipients=[recipient])
    msg.html = render_template(template, **kwargs)
    thr = Thread(target=async_send_mail, args=[current_app, msg])
    thr.start()
    return thr

'''
def send_mail(subject, recipient, template, **kwargs):
    msg = Message(subject, sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[recipient])
    msg.html = render_template(template, **kwargs)
    thr = Thread(target=async_send_mail, args=[app, msg])
    thr.start()
    return thr

'''


def badger(level):
    match level:
        case 1:
            return '1.svg'
        case 2:
            return '2.svg'
        case 3:
            return '3.svg'
        case 4:
            return '4.svg'
        case _:
            return '0.svg'