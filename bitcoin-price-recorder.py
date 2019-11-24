import time
import requests
import sqlite3
import datetime
import poplib
import re

clock = time.time()

pop3inbound_server = input('pop3 inbound server: ')
pop_user = input('pop3 username: ')
pop_pass = input('pop3 password: ')
rh_user = input('Robinhood username: ')
rh_pass = input('Robinhood password: ')
sqlite_location = input('sqlite3 database filepath: ')

def getnewtoken():
    pop = poplib.POP3_SSL(pop3inbound_server)
    pop.user(pop_user)
    pop.pass_(pop_pass)
    messagecount = len(pop.list()[1])
    lasttoken = ''
    for i in pop.retr(messagecount)[1]:
        m = re.search('<h3>(\\d{6})', str(i), re.M)
        if m:
            print(m.group(1))
            lasttoken = m.group(1)
    pop.quit()
    print(lasttoken)
    session = requests.Session()
    print(session.cookies.get_dict())
    response = session.get('https://robinhood.com/login')
    print(session.cookies.get_dict())
    deviceid = str(session.cookies.get_dict())[15:-2]
    print(deviceid)
    firstpostresponse = session.post('https://api.robinhood.com/oauth2/token/',
                                     data={
                                           'client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS',
                                           'device_token': deviceid,
                                           'expires_in': '86400',
                                           'grant_type': 'password',
                                           'password': rh_pass,
                                           'scope': 'internal',
                                           'username': rh_user,
                                           'challenge_type': 'email'
                                     }).text
    print(firstpostresponse)
    print(firstpostresponse.split(':')[3][1:-8])
    currenttoken = lasttoken
    while lasttoken == currenttoken:
        pop = poplib.POP3_SSL(pop3inbound_server)
        pop.user(pop_user)
        pop.pass_(pop_pass)
        messagecount = len(pop.list()[1])
        for i in pop.retr(messagecount)[1]:
            m = re.search('<h3>(\\d{6})', str(i), re.M)
            if m:
                print(m.group(1))
                currenttoken = m.group(1)
        pop.quit()
        time.sleep(1)
    print(currenttoken)
    response = session.post('https://api.robinhood.com/challenge/' + firstpostresponse.split(':')[3][1:-8] + '/respond/',
                            data={
                                  'response': currenttoken
                            })
    print(response.text)
    response = session.post('https://api.robinhood.com/oauth2/token/',
                            headers={
                                     'x-robinhood-challenge-response-id': firstpostresponse.split(':')[3][1:-8]
                            },
                            data={
                                  'grant_type': 'password',
                                  'client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS',
                                  'device_token': deviceid,
                                  'expires_in': '86400',
                                  'scope': 'internal',
                                  'username': rh_user,
                                  'password': rh_pass
                            })
    print(response.text)
    return response.text.split('"')[3]


bearer = getnewtoken()

while True:
    time.sleep(1)
    try:
        if time.time() - clock > 60:

            timestamp = str(datetime.datetime.today()).replace('-', '').replace(' ', '').replace(':', '').replace('.', '')[
                        :19]
            headers = {'Authorization':
                       'Bearer ' + bearer}
            request = (requests.get(
                       'https://api.robinhood.com/marketdata/forex/quotes/3d961844-d360-45fc-989b-f6fca761d511/',
                       headers=headers).text[:-1] + ',"timestamp":"' + timestamp + '"').replace('{', '').split(',')
            request = request[9], request[0], request[1], request[2], request[3], request[4], request[5], request[8]
            request = tuple([i.split(':')[1] for i in request])
            request = tuple([int(request[0].replace('"', ''))] + [float(i.replace('"', '')) for i in request[1:]])

            conn = sqlite3.connect(sqlite_location)
            curs = conn.cursor()
            curs.execute('INSERT INTO tbl1 VALUES (?, ?, ?, ?, ?, ?, ?, ?)', request)
            conn.commit()
            conn.close()
            clock = time.time()
    except IndexError:
        bearer = getnewtoken()
