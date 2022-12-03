from flask import Blueprint, render_template, request, flash, jsonify, current_app, session
from PIL import Image as ImagePIL
from flask_login import login_required, current_user
from .models import Page, Image, ImageToRemoveBackground
from . import db
import json
import os
import secrets
import imghdr
import io
import base64
from rembg import remove

views = Blueprint('views', __name__)
success = False

def save_photo(photo):
    rand_hex = secrets.token_hex(10)
    _, file_extention = photo.filename.rsplit('.', 1)
    file_name = rand_hex + '.' + file_extention
    file_path = os.path.join(current_app.root_path, 'static\\images\\', file_name)
    while os.path.exists(file_path):
        rand_hex = secrets.token_hex(10)
        _, file_extention = os.path.splitext(photo.filename)
        file_name = rand_hex +'.' + file_extention
        file_path = os.path.join(current_app.root_path, 'static\\images\\', file_name)
    photo.save(file_path)
    return file_name, file_path

def save_photo_removeBackground(photo):
    success = False
    rand_hex = secrets.token_hex(10)
    _, file_extension = photo.filename.rsplit('.', 1)
    file_name = rand_hex + '.' + file_extension
    file_name_output = rand_hex + ".png"
    file_path = os.path.join(current_app.root_path, 'static/remove_background/input', file_name)
    file_path_out = os.path.join(current_app.root_path, 'static/remove_background/output', file_name_output)
    while os.path.exists(file_path):
        rand_hex = secrets.token_hex(10)
        _, file_extension = os.path.splitext(photo.filename)
        file_name = rand_hex + '.' + file_extension
        file_name_output = rand_hex + ".png"
        file_path = os.path.join(current_app.root_path, 'static/remove_background/input', file_name)
        file_path_out = os.path.join(current_app.root_path, 'static/remove_background/output', file_name_output)
    photo.save(file_path)

    try:
        input = ImagePIL.open(file_path)
        output = remove(input)
        output.save(file_path_out)
        success = True
    except Exception as e:
        print("Error: " + e)
        success = False
        flash("Cannot find the object in image, try again!", category='error')

    return file_name, file_name_output, file_path, file_path_out, file_extension, success


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


@views.route('/removebckg', methods=['GET', 'POST'])
@login_required
def removebckg():
    if request.method == "POST":
        if request.files:
            inputpic = request.files["pictureForRemoveBackground"]
            if allowed_image(inputpic):
                try:
                    temp0, temp1, temp2, resultPath, file_extension, success = save_photo_removeBackground(inputpic)
                    flash('Image added!', category='success')
                except Exception as e:
                    print(e)
                    flash("Something wrong and the image cannot be added.", category='error')
                # if success == False:
                #     return render_template("removebckg.html", user=current_user, result=None)
                # else:
                try:
                    im = ImagePIL.open(resultPath)
                    data = io.BytesIO()
                    im.save(data, "PNG")
                    new_processed_image = ImageToRemoveBackground(input_location=temp2, output_location=resultPath,input_img_name=temp0,output_img_name=temp1,mimetype=inputpic.mimetype)
                    db.session.add(new_processed_image)
                    db.session.commit()
                    encoded_img_data = base64.b64encode(data.getvalue())
                    return render_template("removebckg.html", user=current_user, resultPath=resultPath, nameImg=temp1,
                                           img_data=encoded_img_data.decode('utf-8'), current_img=new_processed_image.id)
                except Exception as e:
                    flash("Something wrong, please try again!", category='error')
                    print(e)
                    return render_template("removebckg.html", user=current_user, result=None)
            else:
                flash("Please upload valid image file!", category='error')
                return render_template("removebckg.html", user=current_user, result=None)
        else:
            flash("Please upload valid image file!", category='error')
            return render_template("removebckg.html", user=current_user, result=None)
    else:
        return render_template("removebckg.html", user=current_user, result=None)


@views.route('/gallery', methods=['GET', 'POST'])
@login_required
def gallery():
    if request.method == "POST":
        if request.files:
            pic = request.files["picture"]
            print(type(pic))
            if allowed_image(pic):
                try:
                    temp1, temp2 = save_photo(pic)
                    new_image = Image(name_location=temp1, img_path=temp2, name=pic.filename,mimetype=pic.mimetype, user_id=current_user.id)
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




@views.route('/save-output-img', methods=['POST'])
def save_removed_background_image():
    print(json.loads(request.data))
    idOfImage = json.loads(request.data)['imageRId']
    image = ImageToRemoveBackground.query.get(idOfImage)
    if image:
        try:
            destination = os.path.join(current_app.root_path, 'static\\images\\', image.output_img_name)
            os.popen("copy \""+image.output_location+"\" \""+destination+"\"")
            new_image = Image(name_location=image.output_img_name, img_path=destination, name=image.output_img_name,mimetype=image.mimetype, user_id=current_user.id)
            db.session.add(new_image)
            db.session.commit()
        except Exception as e:
            print(e)
            flash("Something wrong and the image cannot be added.", category='error')
    return jsonify({})


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
    if sortStatus == "UP":
        session['sortStatus'] = "UP"
        sortStatus = "UP"
    else:
        session['sortStatus'] = "DOWN"
        sortStatus = "DOWN"
    return render_template("home.html", user=current_user, sortStatus=sortStatus)


# API:
    # response = requests.post(
    #     'https://www.cutout.pro/api/v1/matting?mattingType=6',
    #     files={'file': open(file_path, 'rb')},
    #     headers={'APIKEY': 'My api key'},
    # )
    # if response.status_code == requests.codes.ok:
    #     print("Found image")
    #     with open(file_path_out, 'wb') as out:
    #         out.write(response.content)
    #     success = True
    # else:
    #     print("Error:", response.status_code, response.text)
    #     flash("Cannot find the object in image, try again!", category='error')


#selfBuilt:
    # code = "python -m website.AITool.demo.image_matting.colab.inference --input-path \"" + str(
    #     file_path) + "\" --output-path \"" + str(
    #     file_path_out) + "\" --ckpt-path \"website/AITool/pretrained/modnet_photographic_portrait_matting.ckpt\""
    # os.system(code)
    # success = True