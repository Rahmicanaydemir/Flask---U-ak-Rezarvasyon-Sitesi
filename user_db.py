

#Gerekli olan kütüphanelerin atama işlemi yapılmmıştır.
import datetime
import time
from flask import Flask, request, render_template_string, render_template,redirect,url_for
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin, user_logged_in, user_logged_out
from sqlalchemy.sql import table, column, select 
from sqlalchemy import MetaData
from sqlalchemy import desc,asc,func
import sqlite3 as sql

class ConfigClass(object):
    """ Flask application config """
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'
    
    #Flask SQLAlchemy ayarları yapılmıştır.
    SQLALCHEMY_DATABASE_URI = 'sqlite:///basic_app2.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'xyz@gmail.com' 
    MAIL_PASSWORD = 'sifre' 
    MAIL_DEFAULT_SENDER = '"MyApp" <xyz@gmail.com>'
    
    #Flask User Ayarları
    USER_APP_NAME = "FLİGHT WEB"      
    USER_ENABLE_EMAIL = True       
    USER_ENABLE_USERNAME = False   
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_EMAIL_SENDER_EMAIL = "noreply@example.com"
 
def create_app():
    """ Flask application factory """
    
    # Flask yaratılmıştır ve uygulama ismi verilmiştir.
    app = Flask(__name__)
    app.config.from_object(__name__+'.ConfigClass')

    #Tarih saat ve metin oluşturma işlemleri için Babel Kütüphanesi kullanılmıştır.
    babel = Babel(app)
   
    @babel.localeselector
    def get_locale():
       translations = [str(translation) for translation in babel.list_translations()]
    

    db = SQLAlchemy(app)
 

   # User Class oluşturulmuştur.
    class User(db.Model, UserMixin):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')
        email = db.Column(db.String(255, collation='NOCASE'), nullable=False, unique=True)
        email_confirmed_at = db.Column(db.DateTime())
        password = db.Column(db.String(255), nullable=False, server_default='')
        first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        roles = db.relationship('Role', secondary='user_roles')

   
    # Rezervasyon Tablosu tanımlanmıştır.
    class Rezervation(db.Model):
        __tablename__='rezervation'
        id = db.Column(db.Integer(), primary_key=True)
        user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
        flight_id=db.Column(db.Integer())
        tarih = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow())
        name=db.Column(db.String(50))
        last_name=db.Column(db.String(50))
        phone=db.Column(db.Integer())
        number=db.Column(db.Integer())
        ticket=db.Column(db.Integer())
        toplam=db.Column(db.Float())
        asiltutar=db.Column(db.Float())
        bonus=db.Column(db.Float())
    #Flight Tablosu tanımlanmıştır.
    class Flight(db.Model):
        __tablename__='flight'
        id = db.Column(db.Integer(), primary_key=True)
        ucus_id=db.Column(db.Integer())
        departure=db.Column(db.String(25))
        landing=db.Column(db.String(25))
        tarih = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow())
        users_id=db.Column(db.Integer())
        empty_seat=db.Column(db.Float())
        full_seat=db.Column(db.Float())
        ticket=db.Column(db.Integer())
        bonus=db.Column(db.Float())
        oran=db.Column(db.Float())
        capacity=db.Column(db.Integer())
        pilot_name=db.Column(db.String(25))
    #Sepet Tablosu tanımlanmıştır.
    class Basket(db.Model):
        __tablename__='basket'
        id = db.Column(db.Integer(), primary_key=True)
        timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow())
        ucus_id=db.Column(db.Integer())
        users_id=db.Column(db.Integer())
        name=db.Column(db.String(50))
        last_name=db.Column(db.String(50))
        phone=db.Column(db.Integer())
        number=db.Column(db.Integer()) 
        bonus=db.Column(db.Integer())
        ticket=db.Column(db.Integer())
        toplam=db.Column(db.Float())
        asiltutar=db.Column(db.Float())
    #Role Tablosu tanımlanmıştır.
    class Role(db.Model):
        __tablename__ = 'roles'
        id = db.Column(db.Integer(), primary_key=True)
        name = db.Column(db.String(50), unique=True)

    # User Roles Tablosu tanımlanmıştır.
    class UserRoles(db.Model):
        __tablename__ = 'user_roles'
        id = db.Column(db.Integer(), primary_key=True)
        user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
        role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))
     

    # Uygulama veritabanları user manager modülünün içerisine eklenmiştir.
    user_manager = UserManager(app, db, User)

    # Tüm veritabanları oluşturulmuştur.
    db.create_all()
    engine = create_engine('sqlite:///basic_app2.sqlite')
    meta = MetaData(engine,reflect=True)
    
    #Metadata tablolar değişkenlere aktarılmıştır.
    
    table_isim2 = meta.tables['rezervation']
    table_isim3 = meta.tables['basket']
    table_isim4 = meta.tables['flight']

    #Kullanıcı Giriş Çıkış İşlemi Yapılmıştır.
    @user_logged_in.connect_via(app)
    def _after_login_hook(sender, user, **extra):
        sender.logger.info('user logged in')
        
       
    
    @user_logged_out.connect_via(app)
    def _after_logout_hook(sender, user, **extra):
        sender.logger.info('user logged out')
      
        
        
    
    #Memberlar yaratılıp gerekli olan bilgileri verilmiştir.
    if not User.query.filter(User.email == 'member@example.com').first():
        user = User(
            email='member@example.com',
            email_confirmed_at=datetime.datetime.utcnow(),
            password=user_manager.hash_password('Password1'),
        )
        db.session.add(user)
        db.session.commit()
    #Memberlar yaratılıp gerekli olan bilgileri verilmiştir.
    if not User.query.filter(User.email == 'member1@example.com').first():
        user = User(
            email='member1@example.com',
            email_confirmed_at=datetime.datetime.utcnow(),
            password=user_manager.hash_password('Password1'),
        )
        db.session.add(user)
        db.session.commit()
    #Memberlar yaratılıp gerekli olan bilgileri verilmiştir.
    if not User.query.filter(User.email == 'member2@example.com').first():
        user = User(
            email='member2@example.com',
            email_confirmed_at=datetime.datetime.utcnow(),
            password=user_manager.hash_password('Password2'),
        )
        db.session.add(user)
        db.session.commit()
    #Memberlar yaratılıp gerekli olan bilgileri verilmiştir.
    if not User.query.filter(User.email == 'member3@example.com').first():
        user = User(
            email='member3@example.com',
            email_confirmed_at=datetime.datetime.utcnow(),
            password=user_manager.hash_password('Password3'),
        )
        db.session.add(user)
        db.session.commit()
    #Memberlar yaratılıp gerekli olan bilgileri verilmiştir.
    if not User.query.filter(User.email == 'member4@example.com').first():
        user = User(
            email='member4@example.com',
            email_confirmed_at=datetime.datetime.utcnow(),
            password=user_manager.hash_password('Password4'),
        )
        db.session.add(user)
        db.session.commit()
    
    #Admin ve Rol ataması yapılmıştır.
    if not User.query.filter(User.email == 'admin@example.com').first():
        user = User(
            email='admin@example.com',
            email_confirmed_at=datetime.datetime.utcnow(),
            password=user_manager.hash_password('Password1'),
        )
        user.roles.append(Role(name='Admin'))
        user.roles.append(Role(name='Agent'))
        db.session.add(user)
        db.session.commit()

    #Anasayfa HTML
    @app.route('/')
    def home_page():
        return render_template('home.html')
    #Admin  HTML   
    @app.route('/admin')
    @roles_required('Admin')
    def admin_page():
        return render_template('admin.html')
    ##Member HTML
    @app.route('/member')
    @login_required
    def member_page():
        return render_template('uye_sayfasi.html')
    #Admin Uçuş Rezerve Etme Kısmıdır.
    @app.route('/rezervation')
    def rezervation_page():
        return render_template('rezervation.html')
    
    @app.route('/rezervation_sayfasi')
    @roles_required('Admin')
    def rezervation_sayfasi():
        return render_template('rezervation.html')
    #Adminin Uçuş ekleme işlemi burada gerçekleştirilmiştir.
    @app.route('/rezervation_ekle',methods=['POST','GET'])
    @roles_required('Admin')
    def rezervation_ekle():
        if request.method =='POST':
            try:
                
                ucus_id=request.form['ucus_id']
                departure=request.form['departure']
                landing=request.form['landing']
                empty_seat=request.form['empty_seat']
                full_seat=request.form['full_seat']
                capacity=request.form['capacity']
                pilot_name=request.form['pilot_name']
                ticket=request.form['ticket']
               
               

                rezervasyon=Flight(
                   ucus_id=ucus_id,
                   departure=departure,
                   landing=landing,
                   empty_seat=empty_seat,
                   full_seat=full_seat,
                   capacity=capacity,
                   pilot_name=pilot_name,
                   ticket=ticket,
                   
                   
                )
                db.session.add(rezervasyon)
                db.session.commit()
 
               
                msg="UÇUŞ EKLEME İŞLEMİNİZ BAŞARIYLA GERÇEKLEŞMİŞTİR"
            except:
                msg="UÇUŞ EKLEME SIRASINDA HATA OLUŞTU"
            finally:
                return render_template('rezervasyongoruntule.html',msg=msg)
    #Kullanıcıların Uçuş listeleme işlemi burada gerçekleştirilmiştir.
    
    @app.route('/rezervasyon_listele')
    def rezervasyon_listele():
        user=current_user.id
        db_uri='sqlite:///basic_app2.sqlite'
        engine=create_engine(db_uri)
        conn=engine.connect()
        bonusyap = table_isim4.update().where(table_isim4.c.bonus==None).values(bonus=(table_isim4.c.ticket)*3/100)
        conn.execute(bonusyap)
        select_st=select([table_isim4.c.ucus_id,table_isim4.c.departure,table_isim4.c.landing,table_isim4.c.empty_seat,table_isim4.c.full_seat,table_isim4.c.capacity,table_isim4.c.pilot_name,table_isim4.c.ticket,table_isim4.c.bonus])
        rows=conn.execute(select_st)
        return render_template("rezervasyon_listele.html",rows=rows)


    @app.route('/sepet_sayfasi')
    @login_required
    def sepet_sayfasi():
        return render_template('rezervasyon_listele.html')

    ##Sepete ekleme işlemi burada gerçekleşmiştir.
    @app.route('/sepet_ekle',methods=['POST','GET'])
    @login_required
    def sepet_ekle():
        
        if request.method =='POST':
          
            try:
                
                ucus_id=request.form['ucus_id']
                name=request.form['name']
                last_name=request.form['last_name']
                phone=request.form['phone']
                number=request.form['number']
                ticket=request.form['ticket']
                user = current_user.id
                
                
                with sql.connect('basic_app2.sqlite') as conn:
                    cur=conn.cursor()
                    cur.execute("SELECT count(ucus_id) FROM flight WHERE ucus_id="+request.form['ucus_id'])
                    conn.commit()
                    row = cur.fetchone()
                    msg=''
                    if row[0]==0:
                        msg="Seçtiğiniz Numaraya Ait Uçuş Bulunamadı."
                        alert='alert-danger'
                    else:
              
                        conn.close()
                        alert='alert-success'
                        msg="Sepete ekleme işleminiz başarıyla gerçekleştirildi"
                        sepet=Basket(
                        ucus_id=ucus_id,
                        name=name,
                        last_name=last_name,
                        phone=phone,
                        number=number,
                        users_id=user,
                        ticket=ticket,
                        
                        )
                        
                        
                        db.session.add(sepet)
                        db.session.commit()
                    

                        rez=Rezervation(
                        flight_id=ucus_id,
                        name=name,
                        last_name=last_name,
                        phone=phone,
                        number=number,
                        user_id=user,
                        tarih=datetime.datetime.utcnow(),
                        ticket=ticket
                        )
                        db.session.add(rez)
                        db.session.commit()

                    
            finally:
                return render_template('sepetgoruntule.html', msg=msg, alert=alert)

    #Tarihsiz sepet listeleme işlemi burada yapılmıştır.
    
    @app.route('/sepet_listele')
    @login_required
    def sepet_listele():
        user=current_user.id
        db_uri='sqlite:///basic_app2.sqlite'
        engine=create_engine(db_uri)
        conn=engine.connect()
        bonusya = table_isim3.update().where(table_isim3.c.bonus==None).values(bonus=(table_isim3.c.ticket*table_isim3.c.number)*3/100)
        conn.execute(bonusya)
        ticke=table_isim3.update().where(table_isim3.c.ticket==None).values(ticket=table_isim3.c.number*table_isim3.c.ticket)
        conn.execute(ticke)
        bilethesab = table_isim3.update().where(table_isim3.c.toplam==None).values(toplam=(table_isim3.c.ticket*table_isim3.c.number))
        conn.execute(bilethesab) 
        asiltutarr=table_isim3.update().where(table_isim3.c.asiltutar==None).values(asiltutar=(table_isim3.c.toplam)-(table_isim3.c.bonus))
        conn.execute(asiltutarr)
        sepet=select([table_isim3.c.users_id,table_isim3.c.ucus_id,table_isim3.c.name,table_isim3.c.last_name,table_isim3.c.phone,table_isim3.c.number,table_isim3.c.ticket,table_isim3.c.bonus,table_isim3.c.toplam,table_isim3.c.asiltutar]).where(table_isim3.c.users_id==user)
        rows=conn.execute(sepet)
        return render_template('sepet_listele.html',rows=rows)
    
    

    #Uçuş listeleme işlemi (Kullanıcı tüm detaylarıyla uçuşları görüntülüyor.)
    @app.route('/rez_listele')
    @login_required
    def rez_listele():
        user=current_user.id
        db_uri='sqlite:///basic_app2.sqlite'
        engine=create_engine(db_uri)
        conn=engine.connect()
        alert='alert-success'
        msg="Bilet alma işleminiz başarıyla gerçekleştirildi."
        bonus = table_isim2.update().where(table_isim2.c.bonus==None).values(bonus=(table_isim2.c.ticket*table_isim2.c.number)*3/100)
        conn.execute(bonus)
        bilethesabı = table_isim2.update().where(table_isim2.c.toplam==None).values(toplam=(table_isim2.c.ticket*table_isim2.c.number))
        conn.execute(bilethesabı) 
        asiltut=table_isim2.update().where(table_isim2.c.asiltutar==None).values(asiltutar=(table_isim2.c.toplam)-(table_isim2.c.bonus))
        conn.execute(asiltut)
        rezliste=select([table_isim2.c.user_id,table_isim2.c.tarih,table_isim2.c.name,table_isim2.c.last_name,table_isim2.c.phone,table_isim2.c.number,table_isim2.c.ticket,table_isim2.c.bonus,table_isim2.c.toplam,table_isim2.c.asiltutar]).where(table_isim2.c.user_id==user)
        rows=conn.execute(rezliste)
            
        return render_template('rezlist.html',rows=rows,msg=msg,alert=alert)
  

            
    #Kullanıcı girişi olmadan anasayfada tüm uçuşlar listeleniyor.
    @app.route('/rez2_listele')
    def rez2_listele():
        
        db_uri='sqlite:///basic_app2.sqlite'
        engine=create_engine(db_uri)
        conn=engine.connect()
        tumucus=select([table_isim4.c.ucus_id,table_isim4.c.departure,table_isim4.c.landing,table_isim4.c.capacity,table_isim4.c.empty_seat,table_isim4.c.full_seat,table_isim4.c.pilot_name])
        rows=conn.execute(tumucus)
        
        return render_template('rezlist1.html',rows=rows)
    #Kulalnıcı bazında bonus listeleme işlemi yapılıyor.
    @app.route('/bonuslistele')
    def bonuslistele():
        user=current_user.id
        db_uri='sqlite:///basic_app2.sqlite'
        engine=create_engine(db_uri)
        conn=engine.connect()
        bonusliste=select([table_isim3.c.users_id,table_isim3.c.name,table_isim3.c.last_name,table_isim3.c.bonus]).where(table_isim3.c.users_id==user)
        rows=conn.execute(bonusliste)
        return render_template('bonuslistele.html',rows=rows)
    #Admin sepet listeleme işlemi Burada yapılmıştır.
    @app.route('/adminsepetlistele')
    @roles_required('Admin')
    def adminsepetlistele():
        user=current_user.id
        db_uri='sqlite:///basic_app2.sqlite'
        engine=create_engine(db_uri)
        conn=engine.connect()
        sepetlistele=select([table_isim3.c.users_id,table_isim3.c.timestamp,table_isim3.c.ucus_id,table_isim3.c.name,table_isim3.c.last_name,table_isim3.c.phone,table_isim3.c.number]).where(user==6)
        rows=conn.execute(sepetlistele)
        return render_template('adminsepetlistele.html',rows=rows)
    #Doluluk oranı hesabını yapılması burada gerçekleştirilmiştir.
    @app.route('/doluluk_orani')
    @login_required
    def doluluk_orani():
        user=current_user.id
        db_uri='sqlite:///basic_app2.sqlite'
        engine=create_engine(db_uri)
        conn=engine.connect()
        oranhesabı = table_isim4.update().where(table_isim4.c.oran==None).values(oran=(table_isim4.c.full_seat/table_isim4.c.capacity)*100)
        conn.execute(oranhesabı) 
        dolulukhesabi=select([table_isim4.c.ucus_id,table_isim4.c.capacity,table_isim4.c.empty_seat,table_isim4.c.full_seat,table_isim4.c.oran]).order_by(desc(table_isim4.c.capacity))
        rows=conn.execute(dolulukhesabi)
        return render_template('dolulukorani.html',rows=rows)
    #Adminin Sepetten Silme İşlemi Gerçekleştirilmiştir.   
    @app.route('/adminsepettensil/<ucus_id>')
    def adminsepettensil(ucus_id):
        adminsil = Basket.query.filter_by(ucus_id=ucus_id).first()
        db.session.delete(adminsil)
        db.session.commit()
        return redirect(url_for('sepet_listele'))
    #Kullanıcı tarafından Sepetten silme işlemi gerçekleştirilmiştir.
    @app.route('/sepettensil/<ucus_id>')
    def sepettensil(ucus_id):
        sepetsil = Basket.query.filter_by(ucus_id=ucus_id).first()
        db.session.delete(sepetsil)
        db.session.commit()
        return redirect(url_for('sepet_listele'))
    #Admin Uçuş Silme İşlemi Yapılmıştır.
    @app.route('/rezsill/<ucus_id>')
    @roles_required('Admin')
    def rezsill(ucus_id):
        ucussil = Flight.query.filter_by(ucus_id=ucus_id).first()
        db.session.delete(ucussil)
        db.session.commit()
        
        return redirect(url_for('rezervasyon_listele'))
    #Admin Rezervasyon Id'si Güncelleme İşlemi Yapabiliyor.
    @app.route('/rezguncelle/<ucus_id>')
    @roles_required('Admin')
    def rezguncelle(ucus_id):   
        db_uri='sqlite:///basic_app2.sqlite'
        engine=create_engine(db_uri)
        conn=engine.connect()
        ucusguncelle= table_isim4.update().where(table_isim4.c.id==table_isim4.c.ucus_id).values(ucus_id=table_isim4.c.ucus_id+str(1))
        conn.execute(ucusguncelle)
        db.session.commit()
        return redirect(url_for('rezervasyon_listele'))
    #Doluluk Silme İşlemi Admin Tarafından Gerçekleştirlmiştir.
    @app.route('/doluluksil/<capacity>')
    @roles_required('Admin')
    def doluluksil(capacity):
        doluluksilme = Flight.query.filter_by(capacity=capacity).first()
        db.session.delete(doluluksilme)
        db.session.commit()
        
        return redirect(url_for('doluluk_orani'))

    return app

#Server başlatmak üzere gerekli olan kod satırları
if __name__ == '__main__':
    app = create_app()
   # App run,host,port ve debug ayarlamaları yapılmışltır.
    app.run(host='127.0.0.1', port=5000, debug=True)
