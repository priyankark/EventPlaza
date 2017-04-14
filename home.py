from flask import Flask,render_template,url_for,redirect,request,session
from flask_sqlalchemy import SQLAlchemy
app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="mysql+pymysql://root@localhost/event_management"
app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)

class user(db.Model):
    __tablename__="user"
    u_id=db.Column("u_id",db.Integer,primary_key=True)
    u_name=db.Column("u_name",db.Unicode)
    password=db.Column("password",db.Unicode)
    address=db.Column("address",db.Unicode)
    email=db.Column("email",db.Unicode)
    city=db.Column("city",db.Unicode)
    country=db.Column("country",db.Unicode)
    dob=db.Column("dob",db.Date)
    def __init__(self,u_name,password,address,email,city,country,dob):
        self.u_name=u_name
        self.password=password
        self.address=address
        self.email=email
        self.city=city
        self.country=country
        self.dob=dob

class event(db.Model):
    __tablename__="event"
    event_id=db.Column("event_id",db.Integer,primary_key=True)
    e_name=db.Column("e_name",db.Unicode)
    description=db.Column("description",db.Unicode)
    attendees=db.Column("attendees", db.Integer)
    venue=db.Column("venue",db.Unicode)
    city=db.Column("city",db.Unicode)
    pin=db.Column("pin",db.Integer)
    time=db.Column("time",db.Unicode)
    date=db.Column("date",db.Date)
    u_id=db.Column("u_id",db.Integer)
    def __init__(self,e_name,description,attendees,venue,city,pin,time,date,u_id):
        self.e_name=e_name
        self.description=description
        self.attendees=attendees
        self.venue=venue
        self.city=city
        self.pin=pin
        self.time=time
        self.date=date
        self.u_id=u_id
class sponsors(db.Model):
    __tablename__="sponsors"
    s_id=db.Column("s_id",db.Integer,primary_key=True)
    s_name=db.Column("s_name",db.Unicode)
    def __init__(self,s_id,s_name):
        self.s_id=s_id
        self.s_name=s_name
class sponsoredby(db.Model):
    __tablename__="sponsored_by"
    id=db.Column("id",db.Integer,primary_key=True)
    event_id=db.Column("event_id",db.Integer,db.ForeignKey(event.event_id))
    s_id=db.Column("s_id",db.Integer,db.ForeignKey(sponsors.s_id))
    def __init__(self,event_id,s_id):
        self.event_id=event_id
        self.s_id=s_id
##for home
@app.route('/home')
def home():
    if 'username' not in session:
        session["username"]=None
    return render_template("home.html",user=session["username"])

##for regsitering the user
@app.route('/register')
def register():
    return render_template('register.html')
@app.route('/registering',methods=["POST"])
def registering():
    uname=request.form['uname']
    password=request.form['password']
    address=request.form['address']
    email=request.form['email']
    city=request.form['city']
    country=request.form['country']
    dob=request.form['dob']
    u=user(uname, password, address, email, city, country, dob)
    db.session.add(u)
    db.session.commit()
    return redirect(url_for('log'))

###for events

@app.route('/events')
def events():
    #if user==None:
        #return render_template("home.html")
    #else:
        us=event.query.all()
        return render_template("events.html",user=session["username"],us=us)
####for logging in
@app.route('/login')
def log():
    return render_template("login.html")

##for logging ouut
@app.route('/logout')
def logout():
    session["username"]=None
    return render_template('home.html')


###to check weither logged in or not
@app.route('/logging',methods=["POST"])
def logging():
    if request.method=="POST":
        us=user.query.all()
        use=request.form['user']
        passw=request.form['pass']
        for i in us:
            if use==i.u_name and passw==i.password:
                session['userid']=i.u_id
                session['username']=i.u_name
                return redirect(url_for('home',user=session["username"]))
        return redirect(url_for("spo"))
##for increasing the attendees
@app.route('/increase/<eid>')
def increase(eid):
    us=event.query.filter_by(event_id=eid).first()
    us.attendees=int(us.attendees+1)
    db.session.commit()
    return redirect(url_for('template',eid=eid))

##for creating event
@app.route('/createevent')
def create():
    us=sponsors.query.all()
    return render_template("create.html",us=us)
@app.route('/creating',methods=["POST"])
def creation():
    e_name=request.form['e_name']
    description=request.form['description']
    venue=request.form['venue']
    city=request.form['city']
    pin=request.form['pin']
    time=request.form['time']
    date=request.form['date']
    sponsor=request.form['sponsor']
    u_id=int(session['userid'])
    attendees=0
    sp=request.form.getlist('sponsor')
    e=event(e_name,description,attendees,venue,city,pin,time,date,session['userid'])
    db.session.add(e)
    db.session.commit()
    max=0
    s=event.query.all()
    for i in s:
        max=i.event_id
    for i in sp:
        m=int(i)
        a=sponsoredby(int(max),m)
        db.session.add(a)
        db.session.commit()
    return redirect(url_for('home', user=session["username"]))
###for seeing your events
@app.route('/seeyourevents')
def see():
    us=event.query.filter_by(u_id=session["userid"])
    return render_template('yours.html',us=us)
##for the template
@app.route('/template/<eid>')
def template(eid):
    us=event.query.all()
    e=user.query.all()
    name=""
    email=""
    for i in us:
        if i.event_id==int(eid):
            for j in e:
                if i.u_id==j.u_id:
                    name=j.u_name
                    email=j.email
            return render_template("template.html", city=i.city,description=i.description,attend=i.attendees, event_name=i.e_name,name=name,email=email,event_id=eid,venue=i.venue,date=i.date,time=i.time)
@app.route('/sponsors')   ###for sponsors
@app.route('/sponsors')   ###for sponsors
def spo():
    us=sponsors.query.all()
    return render_template("sponsors.html",us=us)
if __name__=='__main__':
    db.create_all()
    app.run(debug=True)