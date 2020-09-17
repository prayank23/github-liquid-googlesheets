from flask import json
from flask import request
from flask import Flask

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

#check elements.conf file
rpc_port =
rpc_user = 
rpc_password =

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(r'FULLPATH\client_secret.json', scope)
client = gspread.authorize(creds)

sheet = client.open("Github and Liquid").sheet1

all = sheet.get_all_values()
index = len(all) + 1


app = Flask(__name__)

@app.route('/github', methods=['POST'])
def api():

    if request.headers['Content-Type'] == 'application/json' and request.headers['X-GitHub-Event'] == 'pull_request':
        data=request.json
        j = json.loads(json.dumps(data))
        if j['action']== "closed" and j['pull_request']['merged']== True:
            try:
                txid = liquid(j['pull_request']['body'])
                row = [(j['number']),"merged",j['pull_request']['body'],txid]
                sheet.insert_row(row, index)

                result="success"
            except:
                result="faiure"

        return result

def liquid(address):
    try:
        rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:%s"%(rpc_user, rpc_password, rpc_port))

        txid = rpc_connection.sendtoaddress(address, 2 ,'TEST_ASSET')

    except JSONRPCException as json_exception:
        return("A JSON RPC Exception occured: " + str(json_exception))
    except Exception as general_exception:
        return("An Exception occured: " + str(general_exception))
    return txid
    
if  __name__ == '__main__':
    app.run(debug=True)
