from flask import Flask,jsonify,request
from flask_cors import CORS
from flask_pymongo import PyMongo
import pandas as pd
app1=Flask(__name__)
CORS(app1)
app1.secret_key="secretkey"
app1.config['MONGO_URI']="mongodb://localhost:27017/portfolio"
mongo=PyMongo(app1)

@app1.route('/signup',methods=['POST']) 
def add_user():

    _json=request.json
    __file=_json['file']
    _per=_json['Perodic'] 
    _nu=_json['Num']
    print(_nu)
    if _nu and __file and _per and request.method=='POST':
        n=0
        id=mongo.db.user.insert_one({'file':__file,'Perodic':_per,'Num':_nu ,'new':n} )
        resp= jsonify("user add sucess")
        resp.status_code=200
        return resp
    else:
        return not_found()

@app1.route('/file_upload',methods=['POST'])
def file_upload():
        
        resp = {}

        try:
            if(request.method=='POST'):
                req = request.form
                file = request.files.get('file')
                df = pd.read_csv(file)
                data=df.to_dict('records')
                mongo.db.projects.delete_many({'new':True}) 
                mongo.db.final.delete_one({'new':0})
                mongo.db.projects.insert_many(data,ordered=False)
                # print(file)
                # print(df)
                # print(df.head)
                from scipy import stats 
                x = df['X']
                y = df['Y'] 
                slope, intercept, r, p, std_err = stats.linregress(x, y)
                def myfunc(x): 
                 return slope * x + intercept
                m=mongo.db.user.find_one({'new':0})
                s=m['Perodic']
                n=m['Num']
                if(s==1): d=n+23
                elif(s==4): d=n/365+23
                elif(s==3): d=((n*7)/365)+23
                else: d=((n*30)/365)+23
                speed=myfunc(d)
                print(speed)
                mongo.db.final.insert_one({'new':0,'answer':speed,'s':s,'n':n})
                mongo.db.user.delete_one({'new':0}) 
                
                status = {
                "statusCode":"200",
                "statusMessage":"File uploaded Successfully."
            }
            
         
           
        except Exception as e:
            print(e)
            status = {
                "statusCode":"400",
                "statusMessage":str(e)
            }
        resp["status"] =status
        return resp
@app1.route('/final',methods=['GET'])
def final():
        resp = {}
        
        a=mongo.db.final.find_one({'new':0})
        
        resp['data']=a['answer']
        resp['s']=a['s']
        resp['n']=a['n']
        print(a['answer'])
        
        return resp
@app1.route('/display',methods=['GET'])
def dis1():
    resp={
    }
    a=mongo.db.projects.find_one({'id':1})
    resp['y']=a['Y']
    a=mongo.db.projects.find_one({'id':2})
    resp['y1']=a['Y']
    a=mongo.db.projects.find_one({'id':3})
    resp['y2']=a['Y']
    a=mongo.db.projects.find_one({'id':4})
    resp['y3']=a['Y']
    a=mongo.db.projects.find_one({'id':5})
    resp['y4']=a['Y']
    return resp

@app1.errorhandler(404)
def not_found(error=None):
    message={
        'status':404,
        'message':'Not found '+request.url
    }
    resp= jsonify(message)
    resp.status_code=404
    return resp

if __name__=="__main__":
    app1.run(debug=True) 
