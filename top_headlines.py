from flask import Flask, render_template
import requests
import json
import secrets as s
from datetime import datetime

def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())

    # check for staleness:
    now = datetime.now()
    sse = now.timestamp()
    every1000 = round(sse,-3)

    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    print(baseurl + "_".join(res))
    return baseurl + "_" + "_".join(res)+'_{}'.format(every1000)

def make_request_using_cache(baseurl,params,CACHE_FNAME='cache.json'):
    # Note, that the params passed to this function must be in dictionary form.

    try:
        cache_file = open(CACHE_FNAME,'r')
        cache_contents = cache_file.read()
        CACHE_DICTION = json.loads(cache_contents)
        cache_file.close()
    except:
        CACHE_DICTION =  {}

    # actually make the request:
    unique_ident = params_unique_combination(baseurl, params)

    if unique_ident in CACHE_DICTION:
        print("\nGetting cached data...\n")

        return CACHE_DICTION[unique_ident]

    else:
        # go get more new data:
        print("\nFetching new data from API...\n")
        resp = requests.get(baseurl,params)
        #print(resp.text,'\n\n\n')
        CACHE_DICTION[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_DICTION)
        with open (CACHE_FNAME,'w') as fw: # when the file opens for writing, it clears current data.
            fw.write(dumped_json_cache) # I believe this method clobbers by default.

        return CACHE_DICTION[unique_ident]

def retrieve_top_tech_stories(num):

    burl = "https://api.nytimes.com/svc/topstories/v2/technology.json"
    params = {'api-key':s.NYT_apikey}
    fetched = make_request_using_cache(burl,params)
    result_list = fetched['results']
    headlines = []
    for result in result_list:
        headlines.append(result['title'])

    return headlines[:num]

# Begin Flask app.
app = Flask(__name__)

@app.route('/')
def index():
    # return an html string
    return '''
            <h1>Welcome!</h1>
    '''

@app.route('/user/<nm>')
def hello_name(nm):
    datetime_object = datetime.now()
    myhour = int(datetime.strftime(datetime_object,'%H'))
    headline_list = retrieve_top_tech_stories(5)
    return render_template('user.html', name=nm, newslist=headline_list,hour=myhour)

# Spin up the local server:
if __name__ == '__main__':
    print('starting Flask app', app.name)
    app.run(debug=True)
