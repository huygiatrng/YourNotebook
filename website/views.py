from flask import Blueprint, render_template, request, flash, jsonify, current_app, session
from flask_login import login_required, current_user
from .models import Page, Image
from . import db
import json
import os
import secrets
import imghdr

views = Blueprint('views', __name__)


def save_photo(photo):
    rand_hex = secrets.token_hex(10)
    _, file_extention = photo.filename.rsplit('.', 1)
    file_name = rand_hex + '.' + file_extention
    file_path = os.path.join(current_app.root_path, 'static/images/', file_name)
    while os.path.exists(file_path):
        rand_hex = secrets.token_hex(10)
        _, file_extention = os.path.splitext(photo.filename)
        file_name = rand_hex + file_extention
        file_path = os.path.join(current_app.root_path, 'static/images/', file_name)
    photo.save(file_path)
    return file_name, file_path


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if session.get('sortStatus', None) == None:
        session['sortStatus'] = "UP"
        sortStatus = "UP"
    else:
        sortStatus = session.get('sortStatus')

    if request.method == 'POST':
        page = request.form.get('page')
        if len(page) < 1:
            flash('Page is too short!', category='error')
        else:
            new_page = Page(data=page, user_id=current_user.id)
            db.session.add(new_page)
            db.session.commit()
            flash('Page added!', category='success')

    return render_template("home.html", user=current_user, sortStatus=sortStatus)

def allowed_image(photo):
    if (str(imghdr.what(photo))).upper() in {'PNG', 'JPEG', 'JPG', 'GIF', 'TIFF', 'RAW', 'WEBP', 'PSD', 'BMP', 'HEIF',
                                             'INDD'}:
        return True
    else:
        return False


@views.route('/gallery', methods=['GET', 'POST'])
@login_required
def gallery():
    if request.method == "POST":
        if request.files:
            pic = request.files["picture"]
            if allowed_image(pic):
                try:
                    temp1, temp2 = save_photo(pic)
                    new_image = Image(name_location=temp1, img_path=temp2, name=pic.filename, user_id=current_user.id)
                    db.session.add(new_image)
                    db.session.commit()
                    flash('Image added!', category='success')
                except Exception as e:
                    print(e)
                    flash("Something wrong and the image cannot be added.", category='error')
            else:
                flash("Please upload valid image file!", category='error')
        else:
            flash("Cannot upload your file.", category='error')
    return render_template("gallery.html", user=current_user)


@views.route('/delete-image', methods=['POST'])
def delete_image():
    image = json.loads(request.data)
    imageId = image['imageId']
    image = Image.query.get(imageId)
    if image:
        if image.user_id == current_user.id:
            if os.path.exists(image.img_path):
                os.remove(image.img_path)
                db.session.delete(image)
                db.session.commit()
            else:
                flash('Something wrong and the image cannot be deleted.', category='error')
    return jsonify({})


@views.route('/delete-page', methods=['POST'])
def delete_page():
    page = json.loads(request.data)
    pageId = page['pageId']
    page = Page.query.get(pageId)
    if page:
        if page.user_id == current_user.id:
            db.session.delete(page)
            db.session.commit()
    return jsonify({})

@views.route('/sort-page', methods=['POST'])
def sort_page():
    data = json.loads(request.data)
    sortStatus = data['sortStatus']
    if sortStatus=="UP":
        session['sortStatus'] = "UP"
        sortStatus = "UP"
    else:
        session['sortStatus'] = "DOWN"
        sortStatus = "DOWN"
    return render_template("home.html", user=current_user, sortStatus=sortStatus)