import pyrebase

config = {
    "apiKey": "AIzaSyAC2i-lJjssOFI3NG91p387JbbZrMI76ew",
    "authDomain": "areclamborddb.firebaseapp.com",
    "databaseURL": "https://areclamborddb-default-rtdb.firebaseio.com",
    "projectId": "areclamborddb",
    "storageBucket": "areclamborddb.appspot.com",
    "messagingSenderId": "955295904281",
    "appId": "1:955295904281:web:f127fec80963f5b8c67088",
    "measurementId": "G-PYJM79Z3KZ"
}

# initialize app with config
firebase = pyrebase.initialize_app(config)

# authenticate a user
auth = firebase.auth()
# user = auth.sign_in_with_email_and_password("email@usedforauthentication.com", "FstrongPasswordHere")

db = firebase.database()


#data = {"name": "Sampath", "age": 12, "address": ["road","Kandy"]}
#db.push(data)
