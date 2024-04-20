import MySQLdb.cursors
from flask import *
from flask import Flask, render_template,request,session,url_for,redirect,flash
from flask_mysqldb import MySQL
import datetime
import gunicorn

app = Flask(__name__)
app = Flask(__name__, static_folder='static')

app.secret_key = 'Pobb'

app.config['MYSQL_HOST'] = '82.180.140.1'
app.config['MYSQL_USER'] = 'u146569662_admin1'
app.config['MYSQL_PASSWORD'] = 'Laksh_2024'
app.config['MYSQL_DB'] = 'u146569662_auction1'
mysql = MySQL(app)



@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the 'username' from the session
    flash("You have been logged out successfully.")
    return redirect(url_for('mainlogin'))  # Redirect to the login page or any other desired page


@app.route('/')
def index():
    return render_template('index.html', name='pyCharm')

@app.route('/electronic')
def electronic():
    return render_template('electronic.html')

@app.route('/main-login')
def mainlogin():
    return render_template('main_login.html')


import os
# Assuming 'img_avatar.png' is available in the 'static/upload_img' directory
DEFAULT_IMAGE_PATH = 'img_avatar.png'

@app.route('/user-singup', methods=['GET', 'POST'])
def usersingup():
    error = None
    if request.method == "POST":
        fullname = request.form['txtfullname']
        username = request.form['txtusername']
        email = request.form['txtemail']
        mobile = request.form['txtmobile']
        password1 = request.form['txtpassword1']
        password2 = request.form['txtpassword2']
        
        # Check if user uploaded an image
        if 'file' in request.files:
            userimage = request.files['file']
            if userimage.filename == '':
                userimage = None
        else:
            userimage = None

        if not username or not email or not password1 or not password2:
            flash("Please fill in all required fields.")
        else:
            # Check if the username is already taken
            cur = mysql.connection.cursor()
            cur.execute("SELECT COUNT(*) FROM signup WHERE uname = %s", (username,))
            count = cur.fetchone()[0]
            cur.close()

            if count > 0:
                flash("Username is already taken. Please choose a different one.")
            else:
                if password1 != password2:
                    flash("Your Password and Confirm Password are not the same!!")
                else:
                    cur = mysql.connection.cursor()
                    if userimage:
                        cur.execute("INSERT INTO signup (fname, uname, email, mb, pass, uimg) VALUES (%s, %s, %s, %s, %s, %s)",
                                    (fullname, username, email, mobile, password1, userimage.filename))
                        userimage.save('static/upload_img/' + userimage.filename)
                    else:
                        cur.execute("INSERT INTO signup (fname, uname, email, mb, pass, uimg) VALUES (%s, %s, %s, %s, %s, %s)",
                                    (fullname, username, email, mobile, password1, DEFAULT_IMAGE_PATH))

                    mysql.connection.commit()
                    cur.close()

                    flash("Signup successful!!")  # You can redirect to another page or show a success message.

    return render_template('user_singup.html', error=error)



@app.route('/user-login',methods=['GET','POST'])
def userlogin():
    error = None

    if request.method =="POST":
        username = request.form['username']
        password = request.form['pass']

        # Check if the provided username and password match your database records
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM signup WHERE uname = %s AND pass = %s", (username, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['username'] = username
            flash("You are Login Successfully!!")

            user_dict = {'uname': user[0], 'uimg': user[1]}

            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT uname, uimg FROM signup WHERE uname=%s", (username,))
            # cur.execute("SELECT * FROM signup WHERE uname=%s", (uname,))
            ulist = cur.fetchall()
            cur.close()

            return render_template('user_index.html', uname=username, user=user_dict, ulist=ulist)

        else:
            error = "Invalid username and password"
            # return "Invalid username or password"

    return render_template('user_login.html', error=error)



@app.route('/admin-login', methods=['GET', 'POST'])
def adminlogin():
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pass']

        if username == "admin" and password == 'star':
            flash("You are Login Successfully!!")
            return redirect("/Admin_Dashboard")
            # return render_template('admindashboardindex.html')
        else:
            error = "Invalid username and password"

    return render_template('admin_login.html', error=error)


@app.route('/admin-index')
def adminindex():
    return render_template('admin_index.html')



@app.route('/admin-addpro', methods=['GET', 'POST'])
def addproduct():
    error = None
    uname = session.get('username')
    ulist =''

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM category")
    clist = cur.fetchall()
    cur.close()

    x = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if request.method == "POST":
        username = request.form['txtprouser']
        productname = request.form['txtproname']
        about = request.form['txtabout']
        productc = request.form['txtcname']
        productprice = request.form['txtprice']
        productimage = request.files['file']
        productuse = request.form['txtusemonth']
        proexpire = request.form['txtdate']

        # Connect to the database
        cur = mysql.connection.cursor()

        # Fetch the current maximum proid
        cur.execute("SELECT MAX(proid) FROM product")
        result = cur.fetchone()
        max_proid = result[0] if result[0] else 0

        # Increment proid by 1
        new_proid = max_proid + 1

        try:
            # Insert the new product with the incremented proid
            cur.execute("INSERT INTO product(proid, prouser, proname, proabout, procname, proprice, proimage, proumonth, proedate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)",
                        (new_proid, username, productname, about, productc, productprice, productimage.filename, productuse, proexpire))
            mysql.connection.commit()
            cur.close()

            # Save the product image to the 'static' directory
            productimage.save('static/upload_img/' + productimage.filename)

            flash("You have successfully added the product")
            return render_template('admin_addpro.html')
        except:
            error = "An error occurred while adding the product"

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT uname, uimg FROM signup WHERE uname=%s", (uname,))
        # cur.execute("SELECT * FROM signup WHERE uname=%s", (uname,))
        ulist = cur.fetchall()
        cur.close()

    return render_template('admin_addpro.html', error=error,  uname=uname,ulist=ulist, c_list=clist, date=x)



@app.route('/admin-updatepro/<int:proid>', methods=['GET', 'POST'])
def update_product(proid):
    uname = session.get('username')

    if request.method == 'POST':
        id = request.form['txtproid']
        username = request.form['txtprouser']
        productname = request.form['txtproname']
        about = request.form['txtabout']
        productc = request.form['txtcname']
        productprice = request.form['txtprice']
        productuse = request.form['txtusemonth']
        productstatus = request.form['txtsold']
        proexpire = request.form['txtdate']

        if uname == username:
            if 'update' in request.form:
                try:
                    cur = mysql.connection.cursor()
                    cur.execute(
                        "UPDATE product SET prouser=%s, proname=%s, proabout=%s, procname=%s, proprice=%s, proumonth=%s, prostatus=%s, proedate=%s WHERE proid=%s",
                        (username, productname, about, productc, productprice, productuse, productstatus, proexpire, id))
                    mysql.connection.commit()
                    cur.close()
                    flash("Product updated successfully")
                    # return redirect('/addsuccess')
                except Exception as e:
                    return f"Error: {str(e)}"

            elif 'delete' in request.form:
                # Create a cursor
                cur = mysql.connection.cursor()

                # Execute the DELETE statement to remove the product with the specified proid
                cur.execute("DELETE FROM product WHERE proid = %s", (proid,))

                # Commit the changes to the database
                mysql.connection.commit()

                # Close the cursor
                cur.close()

                flash("Product deleted successfully")
                # return 'Delete User Successfully'
        else:
            flash("Only Product Owner can Update or Delete This Product")
            # return "Only Product Winner can Update or Delete This Product"

    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM product WHERE proid=%s", (proid,))
        productlist = cur.fetchall()
        cur.close()

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT uname, uimg FROM signup WHERE uname=%s", (uname,))
        # cur.execute("SELECT * FROM signup WHERE uname=%s", (uname,))
        ulist = cur.fetchall()
        cur.close()

        return render_template('admin_editpro.html', productlist=productlist, uname=uname, ulist=ulist)

    except Exception as e:
        return f"Error: {str(e)}"



@app.route('/admin-prolist')
def adminprolist():
    uname = session.get('username')

    try:
        if 'username' in session:  # Check if the user is logged in
            username = session['username']  # Get the logged-in user's username

            # Query the database to retrieve products for the logged-in user
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT * FROM product WHERE prouser = %s", (username,))
            productlist = cur.fetchall()
            cur.close()

            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT uname, uimg FROM signup WHERE uname=%s", (uname,))
            # cur.execute("SELECT * FROM signup WHERE uname=%s", (uname,))
            ulist = cur.fetchall()
            cur.close()

            return render_template('admin_prolist.html', productlist=productlist,  uname=uname, ulist=ulist)
        else:
            flash("Please log in to view your products.")

            return redirect('/user-login')  # Redirect to the login page if the user is not logged in
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/user-prolist', methods=['GET', 'POST'])
def userprolist():
    uname = session.get('username')
    msglist = []

    try:
        if request.method == 'POST':
            search_term = request.form.get('search_term')

            if search_term:
                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                # Query the database to retrieve products matching the search term
                cur.execute("SELECT * FROM product WHERE proname LIKE %s AND prostatus NOT IN ('item sold', 'Not Available')", ('%' + search_term + '%',))
                productlist = cur.fetchall()
                cur.close()
            else:
                # If no search term provided, retrieve all products excluding "item sold" and "Not Available"
                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cur.execute("SELECT * FROM product WHERE prouser != %s AND prostatus NOT IN ('item sold', 'Not Available')", (uname,))
                productlist = cur.fetchall()
                cur.close()

        else:
            # If it's a 'GET' request without search, retrieve all products excluding "item sold" and "Not Available"
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT * FROM product WHERE prouser != %s AND prostatus NOT IN ('item sold', 'Not Available')", (uname,))
            productlist = cur.fetchall()
            cur.close()

            # If it's a 'GET' request without search, retrieve all products excluding "item sold" and "Not Available"
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT * FROM msg")
            msglist = cur.fetchall()
            cur.close()

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT uname, uimg FROM signup WHERE uname=%s", (uname,))
        ulist = cur.fetchall()
        cur.close()

        return render_template('user_prolist.html', productlist=productlist, uname=uname, msglist=msglist, ulist=ulist)
    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/report/<int:proid>', methods=['GET', 'POST'])
def adminreport(proid):
    uname = session.get('username')

    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cur.execute("SELECT * FROM rate ORDER BY bid ASC, budjet DESC")
        cur.execute("SELECT * FROM rate WHERE bid = %s ORDER BY bid ASC, budjet DESC", (proid,))
        productlist = cur.fetchall()
        cur.close()

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT mb,uname, uimg FROM signup WHERE uname=%s", (uname,))
        # cur.execute("SELECT * FROM signup WHERE uname=%s", (uname,))
        ulist = cur.fetchall()
        cur.close()

        return render_template('admin_proreport.html', productlist=productlist, uname=uname, ulist=ulist)
    except Exception as e:
        return f"Error: {str(e)}"




@app.route('/msg_send/<int:bid>/<string:buname>', methods=['GET', 'POST'])
def msgsend(bid, buname):
    productlist = []

    uname = session.get('username')
    if request.method == "POST":
        mid = request.form['txtproid']
        mcname = request.form['txtprouser']
        mdate  = request.form['txtproname']
        mprice = request.form['txtabout']
        mproname = request.form['txtcname']
        mname  = request.form['txtprice']
        mbudget = request.form['txtusemonth']
        mmsg  = request.form['txtmsg']

        try:
            cur = mysql.connection.cursor()
            # Check if the record exists
            cur.execute("SELECT * FROM msg WHERE msgid = %s AND msgcname = %s", (mid, mcname))
            existing_record = cur.fetchone()

            if existing_record:
                # If the record exists, update it
                cur.execute(
                    "UPDATE msg SET msgdate=%s, msgprice=%s, msgpname=%s, msgoname=%s, msgbudget=%s, msg=%s WHERE msgid=%s AND msgcname=%s",
                    (mdate, mprice, mproname, mname, mbudget, mmsg, mid, mcname)
                )
            else:
                # If the record doesn't exist, insert it
                cur.execute(
                    "INSERT INTO msg (msgid, msgcname, msgdate, msgprice, msgpname, msgoname, msgbudget, msg) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (mid, mcname, mdate, mprice, mproname, mname, mbudget, mmsg)
                )

            mysql.connection.commit()
            cur.close()
            flash("Message updated/inserted successfully")
            # Redirect to a success page or wherever needed

        except Exception as e:
            return f"Error: {str(e)}"

    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM rate WHERE bid = %s AND buname = %s ORDER BY bid ASC, budjet DESC", (bid, buname))
        productlist = cur.fetchall()
        cur.close()

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT uname, uimg FROM signup WHERE uname=%s", (uname,))
        # cur.execute("SELECT * FROM signup WHERE uname=%s", (uname,))
        ulist = cur.fetchall()
        cur.close()

    except Exception as e:
        return f"Error: {str(e)}"

    return render_template('admin_msgsend.html', productlist=productlist,uname=uname,ulist=ulist)




@app.route('/buyview')
def adminbuyview():
    uname = session.get('username')

    try:
        # Query the database to retrieve all products
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # Use dictionary cursor to get results as dictionaries
        #cur.execute("SELECT * FROM buy ")
        cur.execute("SELECT * FROM buy WHERE owner = %s", (uname,))
        productlist = cur.fetchall()
        cur.close()

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT uname, uimg FROM signup WHERE uname=%s", (uname,))
        # cur.execute("SELECT * FROM signup WHERE uname=%s", (uname,))
        ulist = cur.fetchall()
        cur.close()

        return render_template('admin_buyview.html', productlist=productlist,uname=uname, ulist=ulist)
    except Exception as e:
        return f"Error: {str(e)}"



@app.route('/addsuccess')
def addsuccess():
    return render_template('admin_productaddsucc.html')


@app.route('/user-index')
def userindex():
    uname = session.get('username')

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT uname, uimg FROM signup WHERE uname=%s", (uname,))
    # cur.execute("SELECT * FROM signup WHERE uname=%s", (uname,))
    ulist = cur.fetchall()
    cur.close()

    return render_template('user_index.html',uname=uname, ulist=ulist)


@app.route('/user-buy/<int:proid>', methods=['GET', 'POST'])
def userbuy(proid):
    uname = session.get('username')

    if request.method == 'POST':
        id = request.form['txtproid']
        productname = request.form['txtproname']
        productprice = request.form['txtprice']
        username = request.form['txtprouser']
        address = request.form['txtaddress']
        payment = request.form['txtpayment']
        owner_name = request.form['txtowner']


        try:
            cur = mysql.connection.cursor()
            # cur.execute(
            #     "UPDATE buy SET bname=%s, bprice=%s, buname=%s, baddress=%s, bmethod=%s, bsure=%s WHERE bid=%s",
            #     (productname, productprice, username, address, payment, sure, id))

            cur.execute("INSERT INTO buy(bid, bname, bprice, buname, baddress, bmethod, owner) VALUES (%s, %s, %s, %s, %s, %s, %s)", (id, productname, productprice, username, address, payment, owner_name))

            mysql.connection.commit()
            cur.close()
            flash("Product Buy Request send successfully")
        except Exception as e:
            return f"Error: {str(e)}"


    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM product WHERE proid=%s", (proid,))
    productlist = cur.fetchall()
    cur.close()

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT uname, uimg FROM signup WHERE uname=%s", (uname,))
    # cur.execute("SELECT * FROM signup WHERE uname=%s", (uname,))
    ulist = cur.fetchall()
    cur.close()

    # Get the username from the session (assuming it's stored in the session)
    uname = session.get('username')

    return render_template('user_buy.html',productlist=productlist,uname=uname,ulist=ulist)


@app.route('/rate/<int:proid>', methods=['GET', 'POST'])
def customerrate(proid):
    uname = session.get('username')


    x = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(x)
    if request.method == 'POST':
        id = request.form['txtproid']
        productname = request.form['txtproname']
        productseller = request.form['txtseller']
        productprice = request.form['txtprice']
        username = request.form['txtprouser']
        date = request.form['txtdate']
        budjet = request.form['txtrate']


        try:
            cur = mysql.connection.cursor()
            # cur.execute(
            #     "UPDATE buy SET bname=%s, bprice=%s, buname=%s, baddress=%s, bmethod=%s, bsure=%s WHERE bid=%s",
            #     (productname, productprice, username, address, payment, sure, id))

            cur.execute("INSERT INTO rate(bid, bname, bseller, bprice, buname, bdate, budjet) VALUES (%s, %s, %s, %s, %s,%s, %s)", (id, productname,productseller, productprice, username,date, budjet))

            mysql.connection.commit()
            cur.close()
            flash("Product Buy Request send Successfully")
            # return "Product Buy Request send  successfully"
        except Exception as e:
            return f"Error: {str(e)}"


    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM product WHERE proid=%s", (proid,))
    productlist = cur.fetchall()
    cur.close()

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT uname, uimg FROM signup WHERE uname=%s", (uname,))
    # cur.execute("SELECT * FROM signup WHERE uname=%s", (uname,))
    ulist = cur.fetchall()
    cur.close()

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM rate WHERE bid=%s ORDER BY bid ASC, budjet DESC",(proid,))
    #cur.execute("SELECT * FROM rate")
    rate_list = cur.fetchall()
    cur.close()

    # Get the username from the session (assuming it's stored in the session)
    uname = session.get('username')

    return render_template('customer_rate.html',productlist=productlist,uname=uname, dt=x, ulist=ulist, rate_list=rate_list)


@app.route('/user-mybid')
def userbid():
    try:
        uname = session.get('username')

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Use dictionary cursor to get results as dictionaries
        cur.execute("SELECT * FROM msg WHERE msgcname = %s", (uname,))
        productlist = cur.fetchall()
        cur.close()

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT uname, uimg FROM signup WHERE uname=%s", (uname,))
        # cur.execute("SELECT * FROM signup WHERE uname=%s", (uname,))
        ulist = cur.fetchall()
        cur.close()


        return render_template('user_mybid.html', productlist=productlist,uname=uname,ulist=ulist )
    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/user-profile')
def userprofile():
    uname = session.get('username')
    Check_status = "Item Sold"

    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM signup WHERE uname=%s", (uname,))
        productlist = cur.fetchall()
        cur.close()


        if 'username' in session:  # Check if the user is logged in
            username = session['username']  # Get the logged-in user's username

            # Query the database to retrieve products for the logged-in user
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT * FROM product WHERE prouser = %s", (username,))
            add_product_view = cur.fetchall()
            cur.close()

            total_products = len(add_product_view)

            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT uname, uimg FROM signup WHERE uname=%s", (uname,))
            # cur.execute("SELECT * FROM signup WHERE uname=%s", (uname,))
            ulist = cur.fetchall()
            cur.close()

            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            #cur.execute("SELECT * FROM product WHERE prouser = %s", (username,))
            cur.execute("SELECT COUNT(prostatus) as total_sold FROM product WHERE prostatus=%s AND prouser = %s ", (Check_status,username))
            total_sold  = cur.fetchall()
            cur.close()

            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # cur.execute("SELECT * FROM product WHERE prouser = %s", (username,))
            cur.execute("SELECT COUNT(proid) as total_p FROM product WHERE  prouser = %s ",
                        ( username,))
            total_p = cur.fetchall()
            cur.close()

        return render_template('user_profile.html', productlist=productlist, uname=uname,add_product_view=add_product_view, total_products=total_products, ulist=ulist, total_sold=total_sold, total_p=total_p)

    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/user-profileupdate', methods=['GET', 'POST'])
def userupdate():
    uname = session.get('username')

    if request.method == 'POST':
        fullname = request.form['txtfullname']
        username = request.form['txtusername']
        email = request.form['txtemail']
        mobile = request.form['txtmobile']
        password1 = request.form['txtpassword1']
        userimage = request.files['file']

        if 'update' in request.form:
            try:
                cur = mysql.connection.cursor()

                if userimage:  # Check if an image is provided
                    # Save the image to a subdirectory within 'static'
                    image_filename = secure_filename(userimage.filename)
                    image_path = os.path.join('static', 'upload_img', image_filename)
                    userimage.save(image_path)

                    print("Image saved as:", image_path)  # Debugging statement

                    cur.execute(
                        "UPDATE signup SET fname=%s, uname=%s, email=%s, mb=%s, pass=%s, uimg=%s WHERE uname=%s",
                        (fullname,username, email, mobile, password1, image_filename, uname))

                    print("SQL Query executed")  # Debugging statement
                else:
                    cur.execute(
                        "UPDATE signup SET fname=%s, uname=%s, email=%s, mb=%s, pass=%s WHERE uname=%s",
                        (fullname, username, email, mobile, password1, uname))

                mysql.connection.commit()
                cur.close()
                flash("Customer updated successfully")

            except Exception as e:
                return f"Error: {str(e)}"


        elif 'delete' in request.form:
            try:
                cur = mysql.connection.cursor()
                cur.execute("DELETE FROM signup WHERE uname = %s", (uname,))
                mysql.connection.commit()
                cur.close()
                flash("Deleted successfully")
            except Exception as e:
                return f"Error: {str(e)}"

    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM signup WHERE uname=%s", (uname,))
        productlist = cur.fetchall()
        cur.close()

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT uname, uimg FROM signup WHERE uname=%s", (uname,))
        # cur.execute("SELECT * FROM signup WHERE uname=%s", (uname,))
        ulist = cur.fetchall()
        cur.close()

        return render_template('user_profileupdate.html', productlist=productlist, uname=uname, ulist=ulist)
    except Exception as e:
        return f"Error: {str(e)}"




@app.route('/admin-addcustomer', methods=['GET', 'POST'])
def addcustomer():
    uname = session.get('username')
    error = None
    if request.method == "POST":
        username = request.form['txtusername']
        email = request.form['txtemail']
        password1 = request.form['txtpassword1']
        password2 = request.form['txtpassword2']

        if not username or not email or not password1 or not password2:
            flash("Please fill in all required fields.")
        else:
            # Check if the username is already taken
            cur = mysql.connection.cursor()
            cur.execute("SELECT COUNT(*) FROM signup WHERE uname = %s", (username,))
            count = cur.fetchone()[0]
            cur.close()

            if count > 0:
                flash("Username is already taken. Please choose a different one.")
            else:
                if password1 != password2:
                    flash("Your Password and Confirm Password are not the same!!")
                else:
                    cur = mysql.connection.cursor()
                    cur.execute("INSERT INTO signup (uname, email, pass) VALUES (%s, %s, %s)", (username, email, password1))
                    mysql.connection.commit()
                    cur.close()
                    flash("Signup successful!!")  # You can redirect to another page or show a success message.

    return render_template('admin_addcustomer.html',error=error,uname=uname)





@app.route('/admin-viewcustomer')
def viewcustomer():
    uname = session.get('username')

    try:
        # Query the database to retrieve all products
        cur = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor)  # Use dictionary cursor to get results as dictionaries
        cur.execute("SELECT * FROM signup")
        list = cur.fetchall()
        cur.close()

        return render_template('admin_viewcustomer.html', list=list,uname=uname)
    except Exception as e:
        return f"Error: {str(e)}"


from werkzeug.utils import secure_filename
import os

@app.route('/admin-editcustomer/<uname>', methods=['GET', 'POST'])
def editcustomer(uname):
    if request.method == 'POST':
        username = request.form['txtusername']
        email = request.form['txtemail']
        mobile = request.form['txtmobile']
        password1 = request.form['txtpassword1']
        userimage = request.files['file']

        if 'update' in request.form:
            try:
                cur = mysql.connection.cursor()
                cur.execute(
                        "UPDATE signup SET uname=%s, email=%s, mb=%s, pass=%s, uimg=%s WHERE uname=%s",
                        (username, email, mobile, password1, userimage.filename, uname))
                mysql.connection.commit()
                cur.close()
                userimage.save('static/upload_img' + userimage.filename)

                flash("Customer updated successfully")

            except Exception as e:
                return f"Error: {str(e)}"
        elif 'delete' in request.form:
            # Create a cursor
            cur = mysql.connection.cursor()

            # Execute the DELETE statement to remove the product with the specified proid
            cur.execute("DELETE FROM signup WHERE uname = %s", (username,))

            # Commit the changes to the database
            mysql.connection.commit()

            # Close the cursor
            cur.close()

            flash("Customer Deleted successfully")

    try:
        # Query the database to retrieve all products
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # Use dictionary cursor to get results as dictionaries
        cur.execute("SELECT * FROM signup")
        customer_list = cur.fetchall()
        cur.close()

        return render_template('admin_editcustomer.html', list=customer_list, name=uname)

    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/user-pay')
def userpay():
    uname = session.get('username')

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT uname, uimg FROM signup WHERE uname=%s", (uname,))
    # cur.execute("SELECT * FROM signup WHERE uname=%s", (uname,))
    ulist = cur.fetchall()
    cur.close()

    return render_template('payment.html',uname=uname, ulist=ulist)

@app.route('/user-payment')
def upay():
    uname = session.get('username')

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT uname, uimg FROM signup WHERE uname=%s", (uname,))
    # cur.execute("SELECT * FROM signup WHERE uname=%s", (uname,))
    ulist = cur.fetchall()
    cur.close()

    flash("Your Payment Successfully...!!!")

    return render_template('payment_qrcode.html',uname=uname,ulist=ulist)


@app.route('/Admin_Dashboard')
def Admindashboard():
    Check_status = "Item Sold"

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Calculate the total value in the bprice column
    cur.execute("SELECT COUNT(uname) as total_user FROM signup")
    total_user = cur.fetchone()

    cur.execute("SELECT COUNT(proid) as total_product FROM product")
    total_product = cur.fetchone()

    cur.execute("SELECT COUNT(prostatus) as total_sold FROM product WHERE prostatus=%s", (Check_status,))
    total_sold = cur.fetchone()

    # Calculate the total number of unsold products
    total_unsold = total_product['total_product'] - total_sold['total_sold']

    cur.close()
    return render_template('admindashboardindex.html', total_user=total_user,total_product=total_product,total_sold=total_sold, total_unsold=total_unsold)



@app.route('/Admin_adduser', methods=['GET', 'POST'])
def Adminadduser():

    error = None
    if request.method == "POST":
        username = request.form['txtusername']
        email = request.form['txtemail']
        mobile = request.form['txtmobile']
        password1 = request.form['txtpassword1']
        password2 = request.form['txtpassword2']
        userimage = request.files['file']

        if not username or not email or not password1 or not password2:
            flash("Please fill in all required fields.")
        else:
            # Check if the username is already taken
            cur = mysql.connection.cursor()
            cur.execute("SELECT COUNT(*) FROM signup WHERE uname = %s", (username,))
            count = cur.fetchone()[0]
            cur.close()

            if count > 0:
                flash("Username is already taken. Please choose a different one.")
            else:
                if password1 != password2:
                    flash("Your Password and Confirm Password are not the same!!")
                else:
                    cur = mysql.connection.cursor()
                    cur.execute("INSERT INTO signup (uname, email,mb, pass,uimg) VALUES (%s, %s,%s, %s, %s)",
                                (username, email, mobile, password1, userimage.filename,))
                    mysql.connection.commit()
                    cur.close()

                    userimage.save('static/upload_img/' + userimage.filename)

                    flash("Signup successful!!")  # You can redirect to another page or show a success message.

    return render_template('blank.html', error=error)



@app.route('/Admin_viewuser')
def Adminviewuser():

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM signup")
    ulist = cur.fetchall()
    cur.close()

    return render_template('adm_viewuser.html', user_list=ulist)

@app.route('/Admin_view_allProduct')
def Adminvallproduct():

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM product")
    plist = cur.fetchall()
    cur.close()

    return render_template('adm_allproduct.html', product_list=plist)

@app.route('/Admin_sold_allProduct')
def Adminsallproduct():
    product_status = "Item Sold"

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM product WHERE prostatus=%s", (product_status,))
    plist = cur.fetchall()
    cur.close()

    return render_template('adm_soldproduct.html', product_list=plist)

@app.route('/Admin_add_Product', methods=['GET', 'POST'])
def Adminaddproduct():
    error = None
    ulist = ''

    if request.method == "POST":
        username = request.form['txtprouser']
        productname = request.form['txtproname']
        about = request.form['txtabout']
        productc = request.form['txtcname']
        productprice = request.form['txtprice']
        productimage = request.files['file']
        productuse = request.form['txtusemonth']

        # Connect to the database
        cur = mysql.connection.cursor()

        # Fetch the current maximum proid
        cur.execute("SELECT MAX(proid) FROM product")
        result = cur.fetchone()
        max_proid = result[0] if result[0] else 0

        # Increment proid by 1
        new_proid = max_proid + 1

        try:
            # Insert the new product with the incremented proid
            cur.execute(
                "INSERT INTO product(proid, prouser, proname, proabout, procname, proprice, proimage, proumonth) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (new_proid, username, productname, about, productc, productprice, productimage.filename, productuse))
            mysql.connection.commit()
            cur.close()

            # Save the product image to the 'static' directory
            productimage.save('static/upload_img/' + productimage.filename)

            flash("You have successfully added the product")
            return render_template('admin_addpro.html')
        except:
            error = "An error occurred while adding the product"

    return render_template('adm_addproduct.html', error=error, ulist=ulist)



@app.route('/Admin_buyer_view')
def Adminbuyerview():

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Calculate the total value in the bprice column
    cur.execute("SELECT SUM(bprice) as total_value FROM buy")
    total_value = cur.fetchone()

    cur.execute("SELECT * FROM buy")
    blist = cur.fetchall()
    cur.close()

    return render_template('adm_buyer_view.html', buyer_list=blist, total_value=total_value)

@app.route('/Admin_update_user/<uname>', methods=['GET', 'POST'])
def Adminupdateuser(uname):

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM signup WHERE uname=%s", (uname,))
    ulist = cur.fetchall()
    cur.close()

    if request.method == 'POST':
        fullname = request.form['txtfullname']
        username = request.form['txtusername']
        email = request.form['txtemail']
        mobile = request.form['txtmobile']
        password1 = request.form['txtpassword1']
        userimage = request.files['file']

        if 'update' in request.form:
            try:
                cur = mysql.connection.cursor()

                if userimage:  # Check if an image is provided
                    # Save the image to a subdirectory within 'static'
                    image_filename = secure_filename(userimage.filename)
                    image_path = os.path.join('static', 'upload_img', image_filename)
                    userimage.save(image_path)

                    print("Image saved as:", image_path)  # Debugging statement

                    cur.execute(
                        "UPDATE signup SET fname=%s,uname=%s, email=%s, mb=%s, pass=%s, uimg=%s WHERE uname=%s",
                        (fullname,username, email, mobile, password1, image_filename, uname))

                    print("SQL Query executed")  # Debugging statement
                else:
                    cur.execute(
                        "UPDATE signup SET fname=%s ,uname=%s, email=%s, mb=%s, pass=%s WHERE uname=%s",
                        (fullname,username, email, mobile, password1, uname))

                mysql.connection.commit()
                cur.close()
                flash("Customer updated successfully")

            except Exception as e:
                return f"Error: {str(e)}"


        elif 'delete' in request.form:
            try:
                cur = mysql.connection.cursor()
                cur.execute("DELETE FROM signup WHERE uname = %s", (uname,))
                mysql.connection.commit()
                cur.close()
                flash("Deleted successfully")
            except Exception as e:
                return f"Error: {str(e)}"

    return render_template('adm_update_user.html',ulist=ulist)


@app.route('/Admin_update_product/<int:proid>', methods=['GET', 'POST'])
def Adminupdateproduct(proid):

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM product WHERE proid=%s", (proid,))
    plist = cur.fetchall()
    cur.close()

    if request.method == 'POST':
        id = request.form['txtproid']
        username = request.form['txtprouser']
        productname = request.form['txtproname']
        about = request.form['txtabout']
        productc = request.form['txtcname']
        productprice = request.form['txtprice']
        productuse = request.form['txtusemonth']
        productstatus = request.form['txtsold']
        productimage = request.files['file']

        if 'update' in request.form:
            try:
                cur = mysql.connection.cursor()

                if productimage:  # Check if an image is provided
                    # Save the image to a subdirectory within 'static'
                    image_filename = secure_filename(productimage.filename)
                    image_path = os.path.join('static', 'upload_img', image_filename)
                    productimage.save(image_path)

                    print("Image saved as:", image_path)  # Debugging statement

                    cur.execute(
                        "UPDATE product SET prouser=%s, proname=%s, proabout=%s, procname=%s, proprice=%s, proumonth=%s, prostatus=%s, proimage=%s WHERE proid=%s",
                        (username, productname, about, productc, productprice, productuse, productstatus, productimage,id))
                    print("SQL Query executed")  # Debugging statement
                else:
                    cur.execute(
                        "UPDATE product SET prouser=%s, proname=%s, proabout=%s, procname=%s, proprice=%s, proumonth=%s, prostatus=%s WHERE proid=%s",
                        (username, productname, about, productc, productprice, productuse, productstatus,
                         id))
                mysql.connection.commit()
                cur.close()
                flash("Product updated successfully")

            except Exception as e:
                return f"Error: {str(e)}"

        elif 'delete' in request.form:
            # Create a cursor
            cur = mysql.connection.cursor()

            # Execute the DELETE statement to remove the product with the specified proid
            cur.execute("DELETE FROM product WHERE proid = %s", (proid,))

            # Commit the changes to the database
            mysql.connection.commit()

            # Close the cursor
            cur.close()

            flash("Product deleted successfully")
            # return 'Delete User Successfully'


    return render_template('adm_update_product.html', product_list=plist)


@app.route('/Admin_categories', methods=['GET', 'POST'])
def Admincate():
    # clist = []

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM category")
    clist = cur.fetchall()
    cur.close()

    if request.method == "POST":
        cat_name = request.form['txtcatname']


        # Connect to the database
        cur = mysql.connection.cursor()

        # Fetch the current maximum proid
        cur.execute("SELECT MAX(cat_id) FROM category")
        result = cur.fetchone()
        max_catid = result[0] if result[0] else 0

        # Increment proid by 1
        new_catid = int(max_catid) + 1

        try:
            # Insert the new product with the incremented proid
            cur.execute(
                "INSERT INTO category(cat_id, cat_name) VALUES (%s, %s )",
                (new_catid, cat_name))
            mysql.connection.commit()
            cur.close()

            flash("You have successfully added the product Category")

        except:
            error = "An error occurred while adding the product"

    return render_template('adm_categories.html', c_list=clist)



@app.route('/customer_profile_view/<uname>')
def customerprofileview(uname):

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM signup WHERE uname=%s", (uname,))
    customer = cur.fetchall()
    cur.close()

    return render_template('user_view_cust_profile.html', customer=customer,)



@app.route('/user_buy_product_list')
def userbuyproductlist():
    uname = session.get('username')

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # cur.execute("SELECT * FROM buy WHERE buname=%s", (uname,))
    cur.execute("SELECT buy.bname, product.proimage, buy.baddress,product.procname, product.proabout, buy.bprice, buy.bmethod FROM product JOIN buy ON product.proid = buy.bid WHERE buy.buname = %s",(uname,))
    product = cur.fetchall()
    cur.close()

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT uname, uimg FROM signup WHERE uname=%s", (uname,))
    ulist = cur.fetchall()
    cur.close()
    return render_template('user_buy_product_list.html',uname=uname,ulist=ulist,product=product)


# if __name__ == '__main__':
#     app.run(debug=True)  # Enable debug mode for development


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")  # Enable debug mode for development
