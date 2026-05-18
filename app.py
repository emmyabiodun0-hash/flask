import os   # env
import traceback
from datetime import datetime, timedelta


from flask import Flask, abort, flash, json, jsonify, redirect, render_template, request, session, url_for
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from form import Logins
from forms import LoginForm
import requests

from post import PostForm
from db import db

from models import ResetPasswordToken, User, OTPToken, db, Post
from werkzeug.security import check_password_hash, generate_password_hash


from flask_mail import Mail, Message
from dotenv import load_dotenv    # env



from utils import generate_random_otp, send_registration_mail
OTP_LIFESPAN_MINUTES = 10



load_dotenv()    # env








app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data.db"
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("DEFAULT_EMAIL")
app.config['MAIL_PASSWORD'] = os.getenv("GMAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("DEFAULT_EMAIL")



mail = Mail(app)


login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = 'warning'
db.init_app(app)
migrate = Migrate(app, db)



@app.route('/send-email', methods=['GET', 'POST'])
def send_email():
    if request.method == 'POST':
        email = request.form.get('email')
        msg = Message(
            subject="Testing mail from  flask",

            body="Hello world. I'm testing my email",
            recipients=[email]
        )
      
        mail.send(message=msg)
        return f"Mail send to {email}"
    return render_template("send-email.html")



@app.post("/resend-otp")
def resend_otp():
    data = json.loads(request.data)
    email = data.get('email')
    if not email:
        return jsonify({'message':'Email not provided'}, status=400)
    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"message": "User not found"})
    if user.is_verified:
        return jsonify({"message": "User already verified"})
    
    # if user exists
    _new_otp = generate_random_otp(5)
    token = OTPToken(
        token=_new_otp,
        expires_at=datetime.now() + timedelta(minutes=OTP_LIFESPAN_MINUTES),
        user=user,
    )
    db.session.add_all({user, token})
    db.session.commit()

    msg = Message(
        subject=f"Verify Account: Your OTP is {_new_otp}",
        body=f"Welcome\nYour OTP is {token.token}",
        recipients={user.email},
    )
    html_text = render_template(
        "email/verify-email.html", username=user.username, otp=token.token
    )
    msg.html = html_text
    mail.send(msg)
    return jsonify({"message": "Resent OTP"})



@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")



@app.route("/users")
def add_user():
    user = User(email='emmyabiodun@gmail.com', password='Emmy1209')
    db.session.add(user)
    db.session.commit()

    users = User.query.all()
    return str(users)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = Logins()

    # print(form.data)
    if form.validate_on_submit():
        email = form.email.data.lower()
        name = form.full_name.data
        password = form.password.data
        

        user = User(email=email, username=name, password=generate_password_hash(password))
        _new_otp = generate_random_otp(5)
        token = OTPToken(
            token = _new_otp,
            expires_at = datetime.now() + timedelta(minutes=OTP_LIFESPAN_MINUTES),
            user = user
        )


        db.session.add_all([user, token])
        db.session.commit()

        msg = Message(
            subject=f"Verifiy Account: Your OTP is {_new_otp}",
            body=f"Welcome\nYour OTP is {token.token} ",
            recipients=[user.email]
        )
        
        html_text = render_template("email/verify-email.html", username=user.username, otp=token.token)

        msg.html = html_text
        # mail.send(msg)

        # payload = {  
        #     "sender":{  
        #         "name":"Flask App",
        #         "email":"gemmy1866@gmail.com"
        #     },
        #     "to":[  
        #     {  
        #         "email":user.email,
        #         "name":user.username
        #     }
        #     ],
        #         "subject":f"Verifiy Account: Your OTP is {_new_otp}",
        #         "htmlContent": html_text
        #     }
        # response = requests.post(
        #     url=BREVO_URL,
        #     headers={
        #         'accept': "application/json",
        #         'content-type':"application/json",
        #         'api-key':os.getenv("BREVO_API_KEY")
        #     },
        #     data=json.dumps(payload)
        # )
        # print(response.json())


        try:
            brevo_response = send_registration_mail(
                to=user.email,
                username=user.username,
                otp=_new_otp,
                html_content=html_text
            )
            print(brevo_response)
            print(brevo_response.status_code)
            print(user.email)

            # if brevo_response.status_code != 201 or brevo_response.status_code !=200:
            #     print("Condition is true")
            #     raise Exception
        except Exception as e:
            flash("Account created but there was an error  sending the email", category="danger")
            print("An error occured while sending")
            traceback.print_exc()
            return redirect(url_for('register'))
        else:
            session['user_being_verified'] = user.id

            flash ("Sign up success. Please verify your email")

            return redirect(url_for('verify_otp'))

    return render_template("register.html", form=form)




@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user is None:
            flash("Invalid email")
        else:
            if check_password_hash(user.password, password):
                login_user(user)
                # flash(f"Welcome {user.username}", category="success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid password")


       

        # return redirect(url_for('login'))
    
    return render_template("login.html", form=form)

@app.get('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout out successful")
    return redirect(url_for('login'))



@app.route("/posts")
@login_required

def post():
    return render_template("posts.html" )


@app.route("/post-detail/<int:id>")
def post_detail(id):
    post = Post.query.get(id)
    if post is None:
        return abort(404)
    if current_user != post.author:
        return abort(403, "Cannot view other user's post")
    return render_template("post-detail.html", post=post)


@app.post('/posts/delete/<id>')
@login_required
def delete_post(id):
    post = Post.query.get(id)
    if post:
        db.session.delete(post)
        db.session.commit()
        flash("Delete post success", category="success")
        return redirect(url_for("post"))
    else:
        flash("Post not found", category="warning")
        return redirect(url_for("post"))
    

@app.route('/posts/edit/<id>/',methods=['GET', 'POST'])
@login_required
def edit_post(id):
    edit_form = PostForm()
    post = Post.query.get_or_404(id)
    if post.author != current_user:
        flash("Cannot edit other user's post", category='danger')
        return redirect(url_for("post"))
    if request.method == 'GET':
 
        edit_form.title.data = post.title
        edit_form.body.data = post.body
    
    elif edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.body = edit_form.body.data
        
        db.session.commit()
        flash("Post updated successfully", category="success")
        return redirect(url_for("post"))
    return render_template("edit-post.html", form=edit_form)







@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        token =request.form.get('token')

        user_id = session.get('user_being_verified')
        if user_id is None:
            flash("Invalid request", category="danger")
            return abort(400)
        user = User.query.get(user_id)
        
        
        
        otp_token = OTPToken.query.filter_by(token=token, user_id=user_id).first()



        # if otp_token and not otp_token.is_expired:
        #     otp_token.is_used = True
        #     otp_token.user.is_verified = True
        #     db.session.add(otp_token)
        #     db.session.commit()

        if otp_token:
            # IF TOKEN HAS NOT EXPIRED
            if not otp_token.is_used and otp_token.expires_at > datetime.now():
                otp_token.user.is_verified = True
                otp_token.is_used = True

                db.session.add(otp_token)
                db.session.commit()
                
                session.pop("user_being_verified")
                flash("OTP is verified", category="session")
                login_user(user)
                return redirect(url_for("dashboard"))
            
            
            flash("Token has been used or expired", category="danger")
            return render_template("verify-otp.html")
        flash("Invalid OTP token", category="danger")

    return render_template("verify-otp.html")



@app.route("/create-post", methods=["GET", "POST"])
@login_required
def create_post():

    form = PostForm()

    if form.validate_on_submit():

        post = Post(
            title=form.title.data,
            body=form.body.data,
            authod_id=current_user.id
        )



        db.session.add(post)
        db.session.commit()

        flash("Post created successfully!", category= 'success')

        return redirect(url_for("post"))

    return render_template("new_posts.html", form=form)


@app.route("/forget-password", methods=['POST', 'GET'])
def forget_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            _new_otp = generate_random_otp(5)
            token = ResetPasswordToken(
                token = _new_otp,
                expires_at = datetime.now() + timedelta(minutes=OTP_LIFESPAN_MINUTES),
                user = user
            )
            db.session.add_all([ token])
            db.session.commit()

            msg = Message(
                subject=f"Verify  reset password : Your OTP is {_new_otp}",
                body=f"Welcome\nYour password reset OTP is {token.token} ",
                recipients=[user.email]
            )
            html_text = render_template("email/reset-password.html", username=user.username, otp=token.token)

            msg.html = html_text
            mail.send(msg)
            session['user_being_verified'] = user.id
            flash ("OTP verified successfully. You can now reset your password.", "success")
            return redirect(url_for('password_reset'))

            

            
            
        else:
            flash("Email not found","danger")

    return render_template("forgot_password.html")


@app.route("/verify-password-reset-otp", methods=['GET', 'POST'])
def password_reset():
    if request.method == 'POST':
        token =request.form.get('token')

        user_id = session.get('user_being_verified')
        if user_id is None:
            flash("Invalid request", category="danger")
            return abort(400)
        user = User.query.get(user_id)
        
        

        
        reset_password_token = ResetPasswordToken.query.filter_by(token=token, user_id=user_id).first()



        # if otp_token and not otp_token.is_expired:
        #     otp_token.is_used = True
        #     otp_token.user.is_verified = True
        #     db.session.add(otp_token)
        #     db.session.commit()

        if reset_password_token:
            # IF TOKEN HAS NOT EXPIRED
            if not reset_password_token.is_used and reset_password_token.expires_at > datetime.now():
                
                reset_password_token.is_used = True

                db.session.add(reset_password_token)
                db.session.commit()
                
                session.pop("user_being_verified")
                session['reset_email'] = reset_password_token.user.email
                flash("Reset Password OTP verify", category="success")
                
                return redirect(url_for("reset_password"))
            
            
            flash("Reset password Token has been used or expired", category="danger")
            return render_template("reset-password-verification.html")
        flash("Invalid OTP token", category="danger")
       

    return render_template("reset-password-verification.html")



@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        new_password = request.form.get("password")

        user = User.query.filter_by(email=session.get("reset_email")).first()

        if user:
            user.password = generate_password_hash(new_password)

            db.session.commit()

            flash("Password changed successfully. You can now login.", "success")
            return redirect(url_for("login"))

    return render_template("new-password-reset.html")

    











    








with app.app_context():
    db.create_all()



@login_manager.user_loader
def get_user(pk):
    return User.query.filter_by(id=int(pk)).first()

if __name__ == '__main__':
    app.run(debug=True)