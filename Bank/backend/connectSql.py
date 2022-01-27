import sqlite3
import functools
import random
import string


def createDb():
    try:
        bankdb = sqlite3.connect('bank_records.sqlite')
        cursor = bankdb.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS clients (iban VARCHAR(255), name VARCHAR(255), email VARCHAR(250), amount INT);")
        cursor.execute("CREATE TABLE IF NOT EXISTS transactions (iban VARCHAR(250), ibanTo VARCHAR(250), transactionAmount INT, status VARCHAR(25), freshnessToken VARCHAR(250));")
        cursor.execute("CREATE TABLE IF NOT EXISTS freshness (freshnessToken VARCHAR(250), nonce VARCHAR(250));")
        bankdb.commit()

    except sqlite3.Error as e:
        print(e)


def insertInitialValuesDb():
    try:
        bankdb = sqlite3.connect('bank_records.sqlite')
        cursor = bankdb.cursor()
        cursor.execute("INSERT INTO clients (iban, name, email, amount) VALUES ('PT1234', 'afonso', 'sirs.client.tester.08@gmail.com', 1000);")
        cursor.execute("INSERT INTO clients (iban, name, email, amount) VALUES ('PT12345', 'joao', 'sirs.client.tester2.08@gmail.com', 1000);")
        cursor.execute("INSERT INTO clients (iban, name, email, amount) VALUES ('PT98765', 'bruno', 'merchant@gmail.com', 400);")
        bankdb.commit()
        print("-----------Database Created--------------")

    except sqlite3.Error as e:
        print(e)


def cleanDb():
    try:
        bankdb = sqlite3.connect('bank_records.sqlite')
        cursor = bankdb.cursor()
        cursor.execute("DROP TABLE IF EXISTS clients;")
        cursor.execute("DROP TABLE IF EXISTS transactions;")
        cursor.execute("DROP TABLE IF EXISTS freshness;")
        bankdb.commit()

    except sqlite3.Error as e:
        print(e)



def createTransaction(iban, ibanTo, transactionAmount, freshnessToken):
    try:
        bankdb = sqlite3.connect('bank_records.sqlite')

        status= "pending"
    
        sql = "INSERT INTO transactions (iban, ibanTo, transactionAmount, status, freshnessToken) VALUES (?, ?, ?, ?, ?);"
        val = (iban, ibanTo, transactionAmount, status, freshnessToken)
        bankdb.execute(sql, val)
        bankdb.commit()

    except sqlite3.Error as e:
        print(e)



def createClient(iban, name, email, amount):
    try:
        bankdb = sqlite3.connect('bank_records.sqlite')
        cursor = bankdb.cursor()
        sql = "INSERT INTO clients (iban, name, email, amount) VALUES (?, ?, ?, ?);"
        val = (iban, name, email, amount)
        cursor.execute(sql, val)
        bankdb.commit()

    except sqlite3.Error as e:
        print(e)


def createFreshness(freshnessToken, nonce):
    try:
        bankdb = sqlite3.connect('bank_records.sqlite')
        cursor = bankdb.cursor()
        sql = "INSERT INTO freshness (freshnessToken, nonce) VALUES (?, ?);"

        val = (freshnessToken, nonce)
        cursor.execute(sql, val)
        bankdb.commit()

    except sqlite3.Error as e:
        print(e)



def verifyFreshness(nonceToTest, token):
    try:
        bankdb = sqlite3.connect('bank_records.sqlite')
        cursor = bankdb.cursor()
        sql = "SELECT nonce FROM freshness WHERE freshnessToken = ?;"
        val = (token,)
        cursor.execute(sql, val)

        nonce = cursor.fetchone()[0]

        if nonceToTest == nonce:
            return True
        else:
            return False

    except sqlite3.Error as e:
        print(e)



def doTransaction(token):
    try:

        bankdb = sqlite3.connect('bank_records.sqlite')
        cursor = bankdb.cursor()
        sql = "SELECT iban FROM transactions WHERE freshnessToken = ?;"
        val = (token,)
        cursor.execute(sql, val)
        ibanClient = cursor.fetchone()[0]

        sql = "SELECT transactionAmount FROM transactions WHERE freshnessToken = ?;"
        val = (token,)
        cursor.execute(sql, val)
        transactionAmount = cursor.fetchone()[0]

        sql = "SELECT amount FROM clients WHERE iban = ?;"
        val = (ibanClient,)
        cursor.execute(sql, val)
        amountClient = cursor.fetchone()[0]

        sql = "SELECT ibanTo FROM transactions WHERE freshnessToken = ?;"
        val = (token,)
        cursor.execute(sql, val)
        ibanTo = cursor.fetchone()[0]

        sql = "SELECT amount FROM clients WHERE iban = ?;"
        val = (ibanTo,)
        cursor.execute(sql, val)
        amountTo = cursor.fetchone()[0]


        if transactionAmount > amountClient:
            return False

        else:
            finalClientAmount = amountClient - transactionAmount
            finalToAmount = amountTo + transactionAmount
            
            sql = "UPDATE clients SET amount = ? WHERE iban = ?;"
            val = (finalClientAmount,ibanClient)
            cursor.execute(sql, val)
            bankdb.commit()

            sql = "UPDATE clients SET amount = ? WHERE iban = ?;"
            val = (finalToAmount,ibanTo)
            cursor.execute(sql, val)
            bankdb.commit()
            return True

    except sqlite3.Error as e:
        print(e)


def updateStatusToSuccess(token):
    bankdb = sqlite3.connect('bank_records.sqlite')
    cursor = bankdb.cursor()

    try:
        sql = "UPDATE transactions SET status = 'success' WHERE freshnessToken = ?;"
        val = (token,)
        cursor.execute(sql, val)
        bankdb.commit()

    except sqlite3.Error as e:
        print(e)

def updateStatusToCancelled(token):
    bankdb = sqlite3.connect('bank_records.sqlite')
    cursor = bankdb.cursor()
    try:
        sql = "UPDATE transactions SET status = 'cancelled' WHERE freshnessToken = ?;"
        val = (token,)
        cursor.execute(sql, val)
        bankdb.commit()

    except sqlite3.Error as e:
        print(e)


def checkStatus(token):
    bankdb = sqlite3.connect('bank_records.sqlite')
    cursor = bankdb.cursor()

    try:
        sql = "SELECT status FROM transactions WHERE freshnessToken = ?;"
        val = (token,)
        cursor.execute(sql, val)

    except sqlite3.Error as e:
        print(e)

    return cursor.fetchone()[0]



def getEmail(iban):
    bankdb = sqlite3.connect('bank_records.sqlite')
    cursor = bankdb.cursor()

    try:
        sql = "SELECT email FROM clients WHERE iban = ?;"
        val = (iban,)
        cursor.execute(sql, val)

    except sqlite3.Error as e:
        print(e)

    return cursor.fetchone()[0]


def verifyClient(iban):
    try:
        bankdb = sqlite3.connect('bank_records.sqlite')
        cursor = bankdb.cursor()
        sql = "SELECT email FROM clients WHERE iban = ?;"
        val = (iban,)
        cursor.execute(sql, val)

    except sqlite3.Error as e:
        print(e)

    if len(cursor.fetchone()) == 0:
        return False
    else:
        return True
    

def getUsers():
    bankdb = sqlite3.connect('bank_records.sqlite')
    cursor = bankdb.cursor()
    
    try:
        sql = "SELECT iban, name, email, amount FROM clients;"
        cursor.execute(sql)
    except sqlite3.Error as e:
        print(e)
    
    return cursor.fetchall()


def deleteNonce(token):
    bankdb = sqlite3.connect('bank_records.sqlite')
    cursor = bankdb.cursor()
    
    try:
        sql = "DELETE FROM freshness WHERE token=?"
        cursor.execute(sql, (token,))
        bankdb.commit()
    except sqlite3.Error as e:
        print(e)