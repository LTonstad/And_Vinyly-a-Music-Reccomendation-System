from flask import Flask, render_template, request
from src.recommender import *

app = Flask(__name__)

@app.route('/')
#--------------------------------------------------------------
@app.route('/home', methods=['GET'])
def home():
    return render_template("home.html")
#--------------------------------------------------------------

@app.route('/predict')
def predict():
    return render_template('predict.html')    

#--------------------------------------------------------------
@app.route('/results', methods=['POST'])
def results():
    model = pickle.load(open('../rf_model', 'rb'))
    client = MongoClient('localhost', 27017)
    db = client['frauddb']
    dbfraud = db['dbfraud']

    obj_id = request.form['obj_id']
    
    prediction = predict_probabilities(clean_record(query_record(obj_id, dbfraud)), model)[0][1]

    return render_template('results.html', prediction="{:.2%}".format(prediction))

#--------------------------------------------------------------   
    

if __name__=="__main__":
    model = pickle.load(open('../rf_model', 'rb'))
    app.run(host="0.0.0.0", port = 8080, debug=True)
    
    
#--------below are examples from previous case study-------------

@app.route('/about')
def about():
    return render_template("about.html")
