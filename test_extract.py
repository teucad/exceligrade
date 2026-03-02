import app

# `app` module defines a Flask instance also named `app`
client = app.app.test_client()
with open('sample.txt','rb') as f:
    data = {'file': (f, 'sample.txt')}
    res = client.post('/extract', data=data, content_type='multipart/form-data')
    print(res.status_code, res.json)
