from flask import Blueprint, render_template, session
from app.models import Registration

main_bp = Blueprint('main',__name__, 
                template_folder='../templates',
                static_folder='../static')


# venue_images = [
#     'https://res.cloudinary.com/dtr7ausk3/image/upload/w_1000/q_auto/f_auto/FIRST-LOVE-SINGBOARD_jrwxcr.jpg',
#     'https://res.cloudinary.com/dtr7ausk3/image/upload/w_1000/q_auto/f_auto/FIRST_LOVE_CENTER_3_esquyr.jpg',
#     'https://res.cloudinary.com/dtr7ausk3/image/upload/w_1000/q_auto/f_auto/MAIN-CAR-PARK2_ccttek.jpg',
#     # 'https://res.cloudinary.com/dtr7ausk3/image/upload/w_1000/q_auto/f_auto/FIRST_LOVE_CENTER_9_fzadjw.jpg',
#     'https://res.cloudinary.com/dtr7ausk3/image/upload/w_1000/q_auto/f_auto/FIRST_LOVE_CENTER_1_ypbmcx.jpg',
#     'https://res.cloudinary.com/dtr7ausk3/image/upload/w_1000/q_auto/f_auto/THE_CENTER-DAG-HEWARD-MILLSFIRST-LOVE-CENTER_11_xsd8b8.jpg',
#     'https://res.cloudinary.com/dtr7ausk3/image/upload/w_1000/q_auto/f_auto/JSOTW-SING4_loumkh.jpg'
# ]   
venue_images = [
    'https://res.cloudinary.com/dtr7ausk3/image/upload/w_1000/q_auto/f_auto/FIRST-LOVE-SINGBOARD_jrwxcr.jpg',
    'https://res.cloudinary.com/dtr7ausk3/image/upload/w_1000/q_auto/f_auto/FIRST_LOVE_CENTER_3_esquyr.jpg',
    'https://res.cloudinary.com/dtr7ausk3/image/upload/w_1000/q_auto/f_auto/MAIN-CAR-PARK2_ccttek.jpg',
    # 'https://res.cloudinary.com/dtr7ausk3/image/upload/w_1000/q_auto/f_auto/FIRST_LOVE_CENTER_9_fzadjw.jpg',
    'https://res.cloudinary.com/dtr7ausk3/image/upload/w_1000/q_auto/f_auto/worship-cropped_mzwgsu.jpg',
    'https://res.cloudinary.com/dtr7ausk3/image/upload/w_1000/q_auto/f_auto/dancers-hge-edit_lud1na.jpg',
    'https://res.cloudinary.com/dtr7ausk3/image/upload/w_1000/q_auto/f_auto/glgc_singing-cropped_ezh189.jpg'
]

@main_bp.route('/')
def index():
    return render_template('index.html', venue_images=venue_images)

@main_bp.route('/pre-registration')
def pre_registration():
    """Page to choose type of registration"""
    return render_template('pre-registration.html')
@main_bp.route('/accommodation')
def accommodation():
    """Page to choose type of registration"""
    return render_template('accommodation.html')

@main_bp.route('/success')
def success():
    registration_id = session.get('registration_id')
    registration = None
    
    if registration_id:
        registration = Registration.query.filter_by(registration_id=registration_id).first()
    
    return render_template('success.html', registration=registration)

@main_bp.route('/error')
def error():
    return render_template('error.html')