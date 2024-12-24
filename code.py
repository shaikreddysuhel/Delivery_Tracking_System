from flask import Flask,render_template,request,redirect,flash,session,url_for
import mysql.connector
import pandas as pd
import string
import random
import hashlib
import numpy as np
import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
app=Flask(__name__)
app.config['SECRET_KEY'] = 'the random string'
mydb = mysql.connector.connect(host="localhost", user="root", passwd="",port=3306, database="delivery_system")
cursor = mydb.cursor()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dp")
def dp():
    return render_template("dp.html")

@app.route('/dpback',methods = ["POST"])
def dpback():
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        pwd=request.form['pwd']
        cpwd=request.form['cpwd']
        pno=request.form['pno']
        addr=request.form['addr']

        sql = "select * from dp"
        result = pd.read_sql_query(sql, mydb)
        email1 = result['email'].values
        all_pno = result['pno'].values
        print(email1)
        if email in email1:
            if pno in all_pno:
                flash("email/Mobile Number already existed","warning")
                return render_template('dp.html', msg="email existed")

        if (pwd == cpwd):
            sql = "INSERT INTO dp (name,email,pwd,addr,pno) VALUES (%s,%s,%s,%s,%s)"
            val = (name, email, pwd, addr, pno)
            cursor.execute(sql, val)
            mydb.commit()
            flash("Successfully Registered", "warning")
            return render_template('dp.html')
        else:
            flash("Password and Confirm Password not same")
        return render_template('dp.html')

    return render_template('dp.html')

@app.route("/dplog")
def dplog():
    return render_template("dplog.html")

@app.route('/dplogback',methods=['POST', 'GET'])
def dplogback():
    if request.method == "POST":

        email = request.form['email']
        password1 = request.form['pwd']

        sql = "select * from dp where email='%s' and pwd='%s' " % (email, password1)
        print('q')
        x = cursor.execute(sql)
        print(x)
        results = cursor.fetchall()
        print(results)
        global name

        if len(results) > 0:
            print('r')
            name = results[0][1]
            print(name)
            session['fname'] = results[0][1]
            session['email'] = email
            flash("Welcome to website", "primary")
            return render_template('dphome.html', m="Login Success", msg=results[0][1])

        else:
            flash("Login failed", "warning")
            return render_template('dplog.html', msg="Login Failure!!!")
    return render_template('dp.html')

@app.route("/tf")
def tf():
    return render_template("tf.html")

@app.route('/tfback',methods=['POST','GET'])
def tfback():
    if request.method=='POST':
        name=request.form['name']
        remail=request.form['remail']
        fname=request.form['fname']
        faddr=request.form['faddr']
        taddr=request.form['taddr']
        file=request.form['file']

        dd="text_files/"+file
        print(dd)
        f = open(dd, "r")
        data = f.read()

        now = datetime.now()
        # currentDay = datetime.now().strftime('%d/%m/%Y')
        status = 'Request'
        datalen = int(len(data) / 2)
        print(datalen, len(data))
        g = 0
        a = ''
        b = ''
        c = ''
        for i in range(0, 2):
            if i == 0:
                a = data[g: datalen:1]
                # a=a.decode('utf-8')

        print(g)
        print(len(data))
        c = data[datalen: len(data):1]
        # c = c.decode('utf-8')
        print(c)

        currentDay = datetime.now().strftime('%Y-%m-%d')
        t1 = datetime.now().strftime('%H:%M:%S')

        email = session.get('email')
        if email==remail:
            flash("You can't share file to ur mail","danger")
            return render_template("tf.html")
        sql = "INSERT INTO transfer_files (name,email,fname,remail,faddr,taddr,d1,block1,block2) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        val = (name, email, fname, remail, faddr, taddr, now, a, c)
        cursor.execute(sql, val)
        mydb.commit()
        # flash("file uploaded successfully", "success")

        sql = "select * from transfer_files where email='%s' "%(email)
        x = pd.read_sql_query(sql, mydb)
        print("^^^^^^^^^^^^^")
        print(type(x))
        print(x)
        # x = x.drop(['demail'], axis=1)
        x = x.drop(['name'], axis=1)
        # x = x.drop(['fname'], axis=1)
        x = x.drop(['email'], axis=1)
        x = x.drop(['remail'], axis=1)
        x = x.drop(['hash1'], axis=1)
        x = x.drop(['hash2'], axis=1)
        x = x.drop(['faddr'], axis=1)
        x = x.drop(['taddr'], axis=1)
        x = x.drop(['d1'], axis=1)
        x = x.drop(['status'], axis=1)
        x = x.drop(['delivery_uname'], axis=1)
        return render_template('tfback.html',row_val=x.values.tolist())
    flash("file not puloaded", "danger")
    return render_template('tf.html')
@app.route('/tfback1/<s>/<s1>/<s2>')
def tfback1(s=0,s1='',s2=''):
    result1 = hashlib.sha1(s1.encode())
    hash1 = result1.hexdigest()
    result2 = hashlib.sha1(s2.encode())
    hash2 = result2.hexdigest()
    # val=AES_ENCRYPT
    sql="update transfer_files set block1=AES_ENCRYPT('%s','keys'),block2=AES_ENCRYPT('%s','keys'),hash1='%s',hash2='%s' where id='%s'" %(s1,s2,hash1,hash2,s)
    cursor.execute(sql)
    mydb.commit()
    flash("Data stored","success")
    return redirect(url_for('tf'))

@app.route("/view_tf")
def view_tf():
    sql = "select * from transfer_files where email='"+session['email']+"'"
    x = pd.read_sql_query(sql, mydb)
    x = x.drop(['id'], axis=1)
    x = x.drop(['name'], axis=1)
    x = x.drop(['email'], axis=1)
    x = x.drop(['hash1'], axis=1)
    x = x.drop(['hash2'], axis=1)
    x = x.drop(['faddr'], axis=1)
    x = x.drop(['block1'], axis=1)
    x = x.drop(['block2'], axis=1)
    x = x.drop(['remail'], axis=1)
    x = x.drop(['delivery_uname'], axis=1)

    return render_template("view_tf.html", cal_name=x.columns.values, row_val=x.values.tolist())
@app.route("/rf")
def rf():
    email=session.get('email')
    print(email)
    sql = "select * from transfer_files where remail='%s' and status='Completed' "%(email)
    x = pd.read_sql_query(sql, mydb)
    x = x.drop(['remail'], axis=1)
    x = x.drop(['taddr'], axis=1)
    x = x.drop(['block1'], axis=1)
    x = x.drop(['block2'], axis=1)
    x = x.drop(['hash1'], axis=1)
    x = x.drop(['hash2'], axis=1)
    x = x.drop(['status'], axis=1)
    x = x.drop(['delivery_uname'], axis=1)

    return render_template("rf.html", cal_name=x.columns.values, row_val=x.values.tolist())

# @app.route("/downfile",methods=['POST','GET'])
# def downfile():
#     print("dfhlksokhso")
#     if request.method == 'POST':
#         print("gekjhiuth")
#         gkey = request.form['p1']
#         gkey1 = request.form['p2']
#         fid = request.form['id']
#
#         sql = "select count(*),CONCAT(aes_decrypt(block1,'keys'),aes_decrypt(block2,'keys'),'') from transfer_files where id='"+fid+"' and hash1='"+gkey+"' and hash2='"+gkey1+"'"
#         x = pd.read_sql_query(sql, mydb)
#         count=x.values[0][0]
#         print(count)
#
#         if count==0:
#             flash("Invalid key please try again","danger")
#             return render_template('down.html')
#         if count==1:
#             asss = x.values[0][1]
#             asss = asss.decode('utf-8')
#             return render_template("downfile.html", msg=asss)
#
#     return render_template("down.html")
#


@app.route("/down/<s>")
def down(s=0):
    global g
    g=s
    return render_template("down.html",g=g)

@app.route("/downfile",methods=['POST','GET'])
def downfile():
    print("dfhlksokhso")
    if request.method == 'POST':
        print("gekjhiuth")
        gkey = request.form['p1']
        gkey1 = request.form['p2']
        fid = request.form['id']

        sql = "select count(*),CONCAT(aes_decrypt(block1,'keys'),aes_decrypt(block2,'keys'),'') from transfer_files where id='"+fid+"' and hash1='"+gkey+"' and hash2='"+gkey1+"'"
        x = pd.read_sql_query(sql, mydb)
        count=x.values[0][0]
        print(count)
        asss=x.values[0][1]
        asss=asss.decode('utf-8')
        if count==0:
            flash("Invalid key please try again","danger")
            return render_template('down.html')
        if count==1:
            return render_template("downfile.html", msg=asss)

    return render_template("down.html")




@app.route("/add_boy")
def add_boy():
    return render_template("add_boy.html")


@app.route('/add_boy_back',methods = ["POST"])
def add_boy_back():
    if request.method=='POST':
        name=request.form['name']
        uname=request.form['uname']
        email=request.form['email']
        pwd=request.form['pwd']
        pno=request.form['pno']
        addr=request.form['addr']

        sql = "select * from delivery_users"
        result = pd.read_sql_query(sql, mydb)
        uname1 = result['uname'].values
        print(uname1)
        if uname in uname1:
            flash("email already existed","warning")
            return render_template('dp.html', msg="email existed")
        else:
            sql = "INSERT INTO delivery_users (name,uname,email,pwd,addr,pno) VALUES (%s,%s,%s,%s,%s,%s)"
            val = (name,uname, email, pwd, addr, pno)
            cursor.execute(sql, val)
            mydb.commit()
            msg = 'Your login details are : '
            t = 'Regards,'
            t1 = 'Online Delivery Services.'
            mail_content = 'Dear ' + name + ',' + '\n' + msg +' User Name: '+ uname+'Password: '+ pwd + '\n' + '\n' + t + '\n' + t1
            sender_address = 'shaikreddysuhel@gmail.com'
            sender_pass = 'ttxdfxvnbokfynkq'
            receiver_address = email
            message = MIMEMultipart()
            message['From'] = sender_address
            message['To'] = receiver_address
            message['Subject'] = 'Delivery Tracking System'
            message.attach(MIMEText(mail_content, 'plain'))
            ses = smtplib.SMTP('smtp.gmail.com', 587)
            ses.starttls()
            ses.login(sender_address, sender_pass)
            text = message.as_string()
            ses.sendmail(sender_address, receiver_address, text)
            ses.quit()
            url = "https://www.fast2sms.com/dev/bulkV2"

            message = 'Dear ' + name + ',' + msg +' User Name: '+ uname+'Password: '+ pwd
            no = pno
            data1 = {
                "route": "q",
                "message": message,
                "language": "english",
                "flash": 0,
                "numbers": no,
            }

            headers = {
                "authorization": "IFvNqg7CPaWst62KwMliEcHrB5VjLGQzmRO8bhxYAJSydDe0X4BeUowPgROjazLrM8pt6EAfNiZqC0S2",
                "Content-Type": "application/json"
            }

            response = requests.post(url, headers=headers, json=data1)
            print(response)

            flash("Data added", "warning")
            return render_template('add_boy.html')
    return render_template('add_boy.html')

@app.route("/view_delivery_boys")
def view_delivery_boys():
    sql = "select * from delivery_users"
    x = pd.read_sql_query(sql, mydb)
    return render_template("view_delivery_boys.html", cal_name=x.columns.values, row_val=x.values.tolist())

@app.route("/trans_files")
def trans_files():
    sql = "select * from transfer_files where status='waiting' "
    x = pd.read_sql_query(sql, mydb)
    x=x.drop(['block1','block2','hash1','hash2','status','delivery_uname'],axis=1)
    return render_template("trans_files.html", cal_name=x.columns.values, row_val=x.values.tolist())

@app.route('/transfer/<s>/<s1>/<s2>/<s3>/<s4>/<s5>/<a>')
def transfer(s='',s1='',s2='',s3='',s4='',s5='',a=0):
    sql="select * from delivery_users"
    x=pd.read_sql_query(sql,mydb)
    email=x['uname'].values
    arr=np.array(email)
    email = arr.tolist()
    secure_random = random.SystemRandom()
    email = secure_random.choice(email)
    print(email)
    sq="update transfer_files set delivery_uname='"+email+"', status='Transfered' where id='"+str(a)+"'"
    cursor.execute(sq)
    mydb.commit()
    ss="select * from delivery_users where uname='"+email+"'"
    xx=pd.read_sql_query(ss,mydb)
    name=xx['name'].values
    all_pno=xx['pno'].values
    all_pno=list(all_pno)
    all_pno=all_pno[0]
    msg = 'Kindly share this file with perticular user immediatly . '

    print(all_pno)
    url = "https://www.fast2sms.com/dev/bulkV2"

    message = 'Dear ' +str(name) + ',' + msg
    no = all_pno
    data1 = {
        "route": "q",
        "message": message,
        "language": "english",
        "flash": 0,
        "numbers": no,
    }

    headers = {
        "authorization": "IFvNqg7CPaWst62KwMliEcHrB5VjLGQzmRO8bhxYAJSydDe0X4BeUowPgROjazLrM8pt6EAfNiZqC0S2",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=data1)
    print(response)
    flash("Data transfered to delivery person","success")
    return redirect(url_for('trans_files'))

@app.route('/status_track')
def status_track():
    sql="select * from transfer_files where status='Transfered'"
    x = pd.read_sql_query(sql, mydb)
    x = x.drop(['block1', 'block2', 'hash1', 'hash2','faddr','taddr','d1','delivery_uname'], axis=1)
    return render_template("status_track.html", cal_name=x.columns.values, row_val=x.values.tolist())
@app.route("/cs")
def cs():
    return render_template("cs.html")
@app.route('/csback',methods=['POST', 'GET'])
def csback():
    if request.method == 'POST':
        print("aaaaaaaaaaaaaaa")
        username = request.form['uname']
        password1 = request.form['pwd']
        if username == 'cloud' and password1 == 'cloud' :
            flash("Welcome to website cloud", "primary")
            return render_template('cshome.html')
        else:
            print("&&&&&&&&&&&&")
            flash("Invalid Credentials Please Try Again","warning")
            return render_template('cs.html')

    return render_template('cs.html')

@app.route('/av')
def av():
    return render_template("av.html")

@app.route('/avback',methods=['POST', 'GET'])
def avback():
    if request.method == "POST":

        uname = request.form['uname']
        password1 = request.form['pwd']

        sql = "select * from delivery_users where uname='%s' and pwd='%s' " % (uname, password1)
        print('q')
        x = cursor.execute(sql)
        print(x)
        results = cursor.fetchall()
        print(results)
        global name
        if len(results) > 0:
            name = results[0][1]
            print(name)
            session['name'] = results[0][1]
            session['email'] =  results[0][3]
            session['uname']=uname
            flash("Welcome ", "primary")
            return render_template('avhome.html', msg=results[0][1])
        else:
            flash("Login failed", "warning")
            return render_template('av.html', msg="Login Failure!!!")
    return render_template('av.html')

@app.route("/transfered_files")
def transfered_files():
    print(session['uname'])
    sql = "select * from transfer_files where delivery_uname ='"+session['uname']+"' and status='Transfered' "
    x = pd.read_sql_query(sql, mydb)
    x = x.drop(['block1'], axis=1)
    x = x.drop(['block2'], axis=1)
    x = x.drop(['name'], axis=1)
    x = x.drop(['delivery_uname'], axis=1)
    x = x.drop(['faddr'], axis=1)
    x = x.drop(['status'], axis=1)
    x = x.drop(['email'], axis=1)
    x = x.drop(['d1'], axis=1)
    return render_template("transfered_files.html", cal_name=x.columns.values, row_val=x.values.tolist())

@app.route('/transfer_to_receiver/<s>/<s1>/<s2>/<s3>/<s4>/<s5>')
def transfer_to_receiver(s=0,s1='',s2='',s3='',s4='',s5=''):
    sql="update transfer_files set status='Completed' where id='"+s+"'"
    cursor.execute(sql)
    mydb.commit()

    msg = 'Your login details are : '
    t = 'Regards,'
    t1 = 'Online Delivery Services.'

 
    mail_content = 'Dear hash key1 ' + s4 + ' hash key2 ' +s5
    sender_address = 'shaikreddysuhel@gmail.com'
    sender_pass = 'ttxdfxvnbokfynkq'
    receiver_address = s2
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'Delivery Tracking System'
    message.attach(MIMEText(mail_content, 'plain'))
    ses = smtplib.SMTP('smtp.gmail.com', 587)
    ses.starttls()
    ses.login(sender_address, sender_pass)
    text = message.as_string()
    ses.sendmail(sender_address, receiver_address, text)
    ses.quit()



    # msg = 'Thanks for choosing Online file transfer'
    # otp = "Your file is successfully transfered."
    # m1 = "These are the key's for decrypting the file"

    # url = "https://www.fast2sms.com/dev/bulkV2"

    # message =  msg + ',' + otp + m1 + s4 +','+ s5 +' . '
    # no = s2
    # print(no)
    # data1 = {
    #     "route": "q",
    #     "message": message,
    #     "language": "english",
    #     "flash": 0,
    #     "numbers": no,
    # }

    # headers = {
    #     "authorization": "IFvNqg7CPaWst62KwMliEcHrB5VjLGQzmRO8bhxYAJSydDe0X4BeUowPgROjazLrM8pt6EAfNiZqC0S2",
    #     "Content-Type": "application/json"
    # }

    # response = requests.post(url, headers=headers, json=data1)
    # print(response)
    flash("File transefered","success")
    return redirect(url_for('transfered_files'))

@app.route('/remove_data/<s>')
def remove_data(s=0):
    sql = "delete from delivery_users where id='%s'" %s
    cursor.execute(sql, mydb)
    mydb.commit()
    flash("Data deleted", "info")
    return redirect(url_for('view_delivery_boys'))

if __name__=='__main__':
    app.run(debug=True)