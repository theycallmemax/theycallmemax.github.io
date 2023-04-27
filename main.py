from flask import Flask,render_template, request, g, flash,redirect,jsonify,session
import sqlite3
from sqlite3 import Error
#from flask_uploads import UploadSet, configure_uploads, IMAGES
from send_message import telegram_bot_sendtext
from flask import url_for
from flask_frozen import Freezer
import os


app = Flask(__name__)

# photos = UploadSet('photos', IMAGES)
# app.config["UPLOADED_PHOTOS_DEST"] = "static/img/photos"
# app.config["SECRET_KEY"] = os.urandom(24)
# configure_uploads(app, photos)



@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "ling_db"):
        g.link_db.close()


#@app.route('/')
#@app.route('/main')
#@app.route('/card/main') #???
#def main():
 #   return render_template("main.html")



@app.route('/card/<int:id>')
def mentor_profile(id):

    conn = sqlite3.connect('lib1.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM anketa """)
    mentor = cursor.fetchall()

    lst_mentor = []
    for ment in mentor:
        d = {}
        d["id"] = ment[0]
        d["photo"] = ment[1]
        d["company_title"] = ment[2]
        d["telegram"] = ment[3]
        d["specialization"] = ment[4]
        d["projects"] = ment[5]
        d["name"] = ment[6]
        d["experience"] = ment[8]
        d["price"] = ment[9]
        lst_mentor.append(d)
    lst_mentor_in_katalog = ""
    conn.close()
    for i in range(len(lst_mentor)):
        if lst_mentor[i]["id"] == id:
            lst_mentor_in_katalog = lst_mentor[i]

    return render_template('card_1.html', mentor=lst_mentor_in_katalog)


@app.route('/',methods = ["GET","POST"])
def katalog():
    query = "not looking"
    block1 = ["Analytics", "BI analytics", "System analytics", "Data analytics", "Data Science/ML"]
    block2 = ["Development","Backend","Frontend","IOS","Android","Code review","System design"]
    block3 = ["DevOps","Сети","Cloud","Databases","DevOps/SRE"]
    block4 = ["Management","Team lead","Agile","Product","Project"]
    block5 = ["Другое","HR","UX/UI","Marketing","QA","Business"]

    if request.method == "POST":
        try:
            for el in block1:
                try:
                    query = request.form[el]
                    print(query)
                except:
                    pass
            for el in block2:
                try:
                    query = request.form[el]
                    print(query)
                except:
                    pass
            for el in block3:
                try:
                    query = request.form[el]
                    print(query)
                except:
                    pass
            for el in block4:
                try:
                    query = request.form[el]
                    print(query)
                except:
                    pass

            for el in block5:
                try:
                    query = request.form[el]
                    print(query)
                except:
                    pass
        except:
            query = request.form["query"]



    conn = sqlite3.connect('lib1.db')
    cursor = conn.cursor()
    if query == "not looking":

        cursor.execute( """SELECT * FROM anketa 
                            WHERE added=1""")
    else:
        cursor.execute("""SELECT * 
                        FROM anketa 
                        WHERE LOWER(specialization) LIKE LOWER(:query) and added=1""", {"query":  f"%{query}%"})
    mentor = cursor.fetchall()

    lst_mentor = []

    for ment in mentor:
        d = {}
        d["id"] = ment[0]
        d["photo"] = ment[1]
        d["company_title"] = ment[2]
        d["telegram"] = ment[3]
        d["specialization"] = ment[4]
        d["projects"] = ment[5]
        d["name"] = ment[6]
        lst_mentor.append(d)
        conn.close()

    return render_template("main.html", mentor=lst_mentor,block1=block1, block2=block2,block3=block3,block4=block4,block5=block5)


@app.route('/mentor_anketa',methods = ["GET","POST"])
def mentor_anketa():
    if request.method == "POST":
        conn = sqlite3.connect('lib1.db')
        cursor = conn.cursor()
        try:
            photo = "" #photos.save(request.files['photo'])
        except:
            photo = "Тут должно быть фото"

        company_title = request.form['company']
        telegram = request.form['tg']
        specialization = ""
        experience = ""
        price = ""
        try:
            experience = request.form["experience"]
        except:
            pass
        try:
            price = request.form["price"]
        except:
            price = request.form["price_text"]
        rang = [x for x in range(1, 11)]
        for rang in rang:
            try:
                rq = request.form[f'help{rang}']
                if len(specialization.split())>=1:
                    specialization += f",{rq}"
                else:
                    specialization += f"{rq}"
            except:
                a = []

        specialization +=f',{request.form["additional_information"]}'
        projects = request.form['project']
        name = request.form['name']
        cursor.execute("""INSERT INTO anketa(photo,company_title,telegram,specialization,projects,name, price, experience)
                                                    VALUES (:photo,:company_title,:telegram,:specialization,:projects,:name, :price, :experience)
                                                                   """,
                           {"photo":photo,"company_title": company_title, "telegram": telegram, "specialization": specialization, "projects": projects, "name":name,"price":price,"experience":experience })

        photo_url = url_for('static', filename='/img/photos/' + photo)
        text = f'Фото:{photo_url} \nФИО: {name}\nКомпания и должность:  {company_title}\nТелеграм:  {telegram}\nСпециализация:  {specialization}\nТоп проектов:  {projects}, Цена:  {price}\n Опыт:  {experience}'
        telegram_bot_sendtext(text)
        conn.commit()
        flash("Анкета отправлена")
        conn.close()
    return render_template("mentor_anketa.html")

@app.route('/menti_request',methods = ["GET","POST"])
def menti_request():
    if request.method == "POST":
        try:
            name = request.form["name"]
            telegram_menti = request.form["telegram"]
            message = request.form["message"]
            conn = sqlite3.connect('lib1.db')
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO menti(name,tg,message)
            VALUES (:name, :tg, :message)
            """, {"name":name,"tg":telegram_menti,"message":message})
            conn.commit()
            name_user = session.get('item')

            cursor.execute(
                """
                SELECT chat_id
                FROM user_tg
                WHERE name_user = :name_user
                """, {"name_user":name_user}
            )
            chat_id = str(cursor.fetchall()[0][0])
            print(chat_id)
            text = f'У вас новая заявка!\n\nФИО: {name}\n Телеграм: {telegram_menti}\n Пожелания менти:  {message}'

            telegram_bot_sendtext(text,chat_id)
            flash("Спасибо, ваша заявка отпралена")
            conn.close()
        except:
            tg_mentor = request.form["telegram"]
            session['item'] = tg_mentor

    return render_template("menti_request.html")


@app.route('/advantages')
def advantages():
    return render_template("advantages.html")

@app.route('/o_nas')
def o_nas():
    return render_template("o_nas.html")

@app.route('/team')
def team():
    return render_template("team.html")

@app.route('/faq')
def faq():
    return render_template("FAQ.html")

@app.route('/rules')
def rules():
    return render_template("terms.html")





if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')