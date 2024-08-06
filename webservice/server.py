# IMPORTS OF OWN LIBRARIES
from database.db_connect import drop_db, create_db, add_user_and_passw, check_user_and_passw, get_user_id
from knn_sdk.KNNClassifier import Classifier
import datetime

import csv
from flask import Flask, render_template, request, jsonify, url_for

# Paths and Constants
TYPING_DATA_PATH = './database/keystroke.csv'
LOG_NAME = 'results.log'
K = 1
SPLIT = 0.8
app = Flask(__name__, static_folder='./static')

@app.route('/')
def home():
    return render_template('./home/home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('./register/register.html')
    elif request.method == 'POST':
        response = dict(request.get_json())
        username = response['username']
        password = response['password']
        id, result = add_user_and_passw(username, password)

        if result:
            return jsonify({'register_code': 'UserRegistrySuccess', 'user_id': id})
        else:
            return jsonify({'register_code': 'UsernameAlreadyExist'})

@app.route('/register/biometrics', methods=['POST'])
def biometrics():
    if request.method == 'POST':
        response = dict(request.get_json())
        user_id = response['user_id']
        data = response['data']
        data.append(user_id)  # append user id to the end of the list
        try:
            with open(TYPING_DATA_PATH, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(data)

            return jsonify({'biometric_code': 'Success'})
        except:
            return jsonify({'biometric_code': 'Unable to register biometric data'})

@app.route('/train/biometrics', methods=['POST'])
def train_biometrics():
    if request.method == 'POST':
        response = dict(request.get_json())
        username = response['username']
        data = response['data']
        user_id = get_user_id(username)
        if user_id is None:
            user_id = 999  # If user not registered for training, data can still be used.
        data.append(user_id)  # add user id to the end of the list
        try:
            with open(TYPING_DATA_PATH, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(data)

            return jsonify({'biometric_code': 'Success'})
        except:
            return jsonify({'biometric_code': 'Unable to register biometric data'})

@app.route('/login', methods=['GET'])
def login():
    return render_template('./login/login.html')

@app.route('/login/auth1', methods=['POST'])  # Route for first authentication
def auth1():
    response = dict(request.get_json())
    username = response['username']
    password = response['password']

    id, result, user_id = check_user_and_passw(username, password)

    if result:
        return jsonify({'auth1_code': 'success', 'user_id': user_id})
    else:
        if id == 3:
            return jsonify({'auth1_code': 'UsernameNotExist'})
        elif id == 1:
            return jsonify({'auth1_code': 'PasswordIsWrong'})

@app.route('/login/auth2', methods=['POST'])  # Route for second authentication
def auth2():
    response = dict(request.get_json())
    typing_data = response['typing_data']
    user_id = response['user_id']
    
    ##### Classification
    classifier = Classifier(TYPING_DATA_PATH, typing_data, SPLIT, K)
    result, cross_val_score = classifier.knn_manhattan_without_training()

    if str(user_id) in result[0]:
        match = True
    else:
        match = False
    
    current_datetime = datetime.datetime.now()
    current_date = current_datetime.strftime("%d/%m/%Y %H:%M:%S ")
    
    with open(LOG_NAME, 'a') as file:  # Create the log file
        file.write('[+]  Real User: ')
        file.write(str(user_id))
        file.write(' | Predicted User: ')
        file.write(str(result[0]))
        file.write(' | Algorithm: ')
        file.write(str(result[2]))
        file.write(' | Value of K: ')
        file.write(str(K))
        file.write(' | Match: ')
        file.write(str(match))
        file.write(' | Accuracy: ')
        file.write(str(cross_val_score))
        file.write(' | Date: ')
        file.write(current_date)
        file.write('\n')

    return jsonify({'user_id': str(user_id), 'predict': result[0], 'accuracy': cross_val_score, 'result': str(match), 'algorithm': result[2]})

@app.route('/train', methods=['GET', 'POST'])
def train_biometrics_page():
    if request.method == 'GET':
        return render_template('./training/training.html')

@app.route('/best_params', methods=['GET'])
def best_params():
    return render_template('./best_params/best_params.html')

@app.route('/best_params/result', methods=['GET'])
def best_params_result():
    typing_data = ''
    classifier = Classifier(TYPING_DATA_PATH, typing_data, 0.7, 3)
    best_score, best_params, best_estimator = classifier.hyper_parameters_tuning()

    current_datetime = datetime.datetime.now()
    current_date = current_datetime.strftime("%d/%m/%Y %H:%M:%S ")

    with open(LOG_NAME, 'a') as file:  # Create the log file
        file.write('[+]  Best Score: ')
        file.write(str(best_score))
        file.write(' |  Best Params: ')
        file.write(str(best_params))
        file.write(' |  Best Estimator: ')
        file.write(str(best_estimator))
        file.write(' | Date: ')
        file.write(current_date)
        file.write('\n')

    return jsonify({'best_score': str(best_score), 'best_params': str(best_params), 'best_estimator': str(best_estimator) })

# Server Start
if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True, port=3000)
