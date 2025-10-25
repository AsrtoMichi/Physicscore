from flask import Flask, current_app, request, session, redirect, url_for, render_template_string, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from datetime import datetime, timedelta
from typing import Tuple, Optional
import secrets
from auth_helpers import populate_session_for_user
import socket

from db import init_db, db, User, Role, OneTimeToken, seed_roles, seed_statuses

def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping({
        'SECRET_KEY': 'super-secret',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///db.sqlite3',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECURITY_REGISTERABLE': True,
        'SECURITY_PASSWORD_SALT': 'salty',
        'SECURITY_SEND_REGISTER_EMAIL': False,
        'RATELIMIT_DEFAULT': "200 per day;50 per hour",
    })
    if config:
        app.config.update(config)

    init_db(app)
    Limiter(key_func=get_remote_address, app=app, default_limits=[app.config['RATELIMIT_DEFAULT']])

    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.login_view = 'request_magic'
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()
        seed_roles()
        seed_statuses()


    # user loader
    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            return db.session.query(User).filter_by(id=user_id).first()
        except Exception:
            return None



    return app

app = create_app()

# ---------------------------
# Token magic: generator e verifier (uguale alla tua logica)
# ---------------------------

class MagicToken:
    
    @staticmethod
    def _get_serializer() -> URLSafeTimedSerializer:
        return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    
    @staticmethod
    def generate_magic_token(email: str, expires_seconds: int = 1800) -> str:
        token_id = secrets.token_urlsafe(16)
        payload = {'tid': token_id, 'e': email}
        signed = _get_serializer().dumps(payload)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_seconds)
        rec = OneTimeToken(token_id=token_id, signed_token=signed, email=email, expires_at=expires_at, used=False)
        db.session.add(rec)
        db.session.commit()
        return signed
        
        
    @staticmethod
    def verify_and_consume_magic_token(signed_token: str, max_age: int = 1800) -> Tuple[Optional[User], str]:
        try:
            payload = _get_serializer().loads(signed_token, max_age=max_age)
        except SignatureExpired:
            return None, 'expired'
        except BadSignature:
            return None, 'invalid'

        token_id = payload.get('tid')
        email = payload.get('e')
        if not token_id or not email:
            return None, 'invalid'

        now = datetime.utcnow()
        try:
            with db.session.begin():
                rec = db.session.query(OneTimeToken).filter_by(token_id=token_id).with_for_update().first()
                if not rec:
                    return None, 'not_found'
                if rec.used:
                    return None, 'used'
                if rec.expires_at and rec.expires_at < now:
                    return None, 'expired'
                rec.used = True
                rec.consumed_at = now

                user = db.session.query(User).filter_by(email=email).first()
                if not user:
                    user = User(email=email, status='active')
                    db.session.add(user)

            return user, 'ok'
        except Exception:
            db.session.rollback()
            return None, 'error'

    @staticmethod
    def request_magic():
        if request.method == 'POST':
            email = request.form.get('email', '').strip().lower()
            if not email:
                flash('Email required', 'error')
                return redirect(url_for('request_magic'))
            token = generate_magic_token(email)
            # Qui dovresti inviare il link via email: url_for('magic_login', token=token, _external=True)
            # Per sviluppo mostriamo il link:
            link = url_for('magic_login', token=token, _external=True)
            return render_template_string('<p>Magic link (dev): <a href="{{link}}">{{link}}</a></p>', link=link)

# ---------------------------
# Login: generator e verifier (uguale alla tua logica)
# ---------------------------
def request_from_host():
    addr = request.remote_addr or ''
    # considera localhost e indirizzi legati all'host
    return addr in  {'127.0.0.1', '::1'} + { res[4][0] for res in socket.getaddrinfo(socket.gethostname(), None)}'

@app.route('/login/<token>')
def magic_login(token):
    user, status = MagicToken.verify_and_consume_magic_token(token)
    if user is None:
        if status == 'expired':
            flash('Token expired', 'error')
        elif status == 'used':
            flash('Token already used', 'error')
        elif status == 'not_found':
            flash('Token not found', 'error')
        else:
            flash('Invalid token', 'error')
        return redirect(url_for('request_magic'))

    # login via Flask-Login
    login_user(user, remember=True)
    populate_session_for_user(user, session)
    flash('Logged in successfully', 'success')
    return redirect(url_for('index'))

@app.route('/login/admin')
def admin_login():
    
    if not request_from_host():
        return abort(401)
        
    admin_email = current_app.config.get('ADMIN_EMAIL')
    admin_user = db.session.query(User).filter_by(email=admin_email).first()
    login_user(admin_user, remember=True, fresh=True)
    return redirect(url_for('admin'))
    
    

@app.route('/account')
@login_required
def protected():
    return render_template_string('<p>Protected area. Hello {{email}}.</p>', email=current_user.email, 
    )

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('/'))







# Route: lista utenti (admin)
@app.route('/admin/users', methods=['GET'])
@roles_required('admin', 'mmoderator')
def admin_list_users():
    users = db.session.query(User).order_by(User.role.desc()).all()
    return render_template('modarations/users.html', users=users)


# Route: resend token per user (admin)
@app.route('/admin/users/<user_id>/resend-token', methods=['POST'])
@admin_required
def admin_resend_token(user_id):
    user = db.session.query(User).filter_by(id=user_id).first()
    if not user:
        flash("Utente non trovato")
        return redirect(url_for('admin_list_users'))
    if user.status == 'suspended':
        flash("Utente sospeso, non è possibile reinviare token finché è sospeso")
        return redirect(url_for('admin_list_users'))

    # Genera token e invia email
    create_and_send_token_for_email(user.email)

    # Audit log
    log = AuditLog(user_id=None, action='admin_resend_token', resource=user.email,
                   ip=request.remote_addr, user_agent=request.headers.get('User-Agent'),
                   meta={'admin': session.get('admin_email')})
    db.session.add(log)
    db.session.commit()

    flash(f"Token reinviato a {user.email}")
    return redirect(url_for('admin_list_users'))

# Route: sospendi utente (temporaneo)
@app.route('/admin/users/<user_id>/suspend', methods=['POST'])
@admin_required
def admin_suspend_user(user_id):
    user = db.session.query(User).filter_by(id=user_id).first()
    if not user:
        flash("Utente non trovato")
        return redirect(url_for('admin_list_users'))

    user.status = 'suspended'
    # revoca sessioni attive
    db.session.query(SessionModel).filter_by(user_id=user.id, revoked=False).update({'revoked': True})
    # opzionale: invalidare token non ancora usati
    db.session.query(OneTimeToken).filter_by(email=user.email, used=False).update({'used': True, 'consumed_at': datetime.utcnow()})
    # audit
    log = AuditLog(user_id=None, action='admin_suspend_user', resource=user.email,
                   ip=request.remote_addr, user_agent=request.headers.get('User-Agent'),
                   meta={'admin': session.get('admin_email')})
    db.session.add(log)
    db.session.commit()

    flash(f"Utente {user.email} sospeso")
    return redirect(url_for('admin_list_users'))

# Route: riammetti utente
@app.route('/admin/users/<user_id>/reinstate', methods=['POST'])
@admin_required
def admin_reinstate_user(user_id):
    user = db.session.query(User).filter_by(id=user_id).first()
    if not user:
        flash("Utente non trovato")
        return redirect(url_for('admin_list_users'))

    user.status = 'active'
    # audit
    log = AuditLog(user_id=None, action='admin_reinstate_user', resource=user.email,
                   ip=request.remote_addr, user_agent=request.headers.get('User-Agent'),
                   meta={'admin': session.get('admin_email')})
    db.session.add(log)
    db.session.commit()

    flash(f"Utente {user.email} riamesso")
    return redirect(url_for('admin_list_users'))


# Simple endpoint to show public pages
@app.route('/')
def home():
    return '<h1>Home pubblica</h1>'

# --- Startup ---
if __name__ == '__main__':


    app.run(debug=True, host='127.0.0.1', port=int(os.environ.get('PORT', 5000)))






