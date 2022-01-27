import sys
from flask import Blueprint, render_template, request, session
from backend.connectSql import doTransaction, updateStatusToSuccess, updateStatusToCancelled, getUsers

views = Blueprint('views', __name__)

@views.route('/home', methods=['GET', 'POST'])
def home():
    session["token"] = request.args.get("token")
    return render_template("home.html")


@views.route('/success', methods=['POST'])
def success():
    if doTransaction(session["token"]) == True:
        
        users = getUsers()
        print("IBAN: ", file=sys.stderr, flush=True)
        for user in users:
            print("IBAN: " + user[0] + ", Name: " + user[1] + ", e-mail: " + user[2] + ", balance: €" + str(user[3]), file=sys.stderr, flush=True)
                
        updateStatusToSuccess(session["token"])
    else:
        updateStatusToCancelled(session["token"]) 
        
    return render_template("success.html")

@views.route('/cancel', methods=['POST'])
def cancel():
    updateStatusToCancelled(session["token"]) 
        
    return render_template("cancel.html")

