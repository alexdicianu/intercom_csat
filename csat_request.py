import sys
import urllib, urllib2, json, base64, time

import sendgrid
import os

from sendgrid.helpers.mail import *

from HTMLParser import HTMLParser
from collections import Counter

import pprint

intercom_user = 'xxxxxxxx';
intercom_pass = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx';

class IntercomAPI:

    users  = {}
    
    intercom_api  = 'https://api.intercom.io'

    def __init__(self): pass
        
    def call(self, path, data=''):
        url = self.intercom_api + path
        request = urllib2.Request(url)
        request.add_header('Accept', 'application/json')
        base64string = base64.b64encode('%s:%s' % (intercom_user, intercom_pass))
        request.add_header("Authorization", "Basic %s" % base64string)

        if data:
            result = urllib2.urlopen(request, json.dumps(data))
        else:
            result = urllib2.urlopen(request)
        return json.loads(result.read())

    def get_users_by_segment(self, segment_id):
        path = "/users?segment_id={}".format(segment_id)
        users = self.call(path)

        user_list = []
        if users['users']:
            for user in users['users']:
                 user_list.append({
                    "name": user['name'], 
                    "email": user['email'],
                    "uuid": user['user_id']
                })

        return user_list

    def get_user_conversation(self, user_id):
        #https://api.intercom.io/conversations?type=user&user_id=ec03c927-0872-4f62-ae09-d86b0c0d4613
        path = "/conversations?type=user&user_id={}".format(user_id)
        conversations = self.call(path)
        return conversations

    def get_user(self, user_id, type):
        if user_id not in self.users:
            if type == 'user':
                self.users[user_id] = self.call("/users/" + user_id)
            else:
                self.users[user_id] = self.call("/admins/" + user_id)
        return self.users[user_id]['name'], self.users[user_id]['email']
    

if __name__ == '__main__':
    
    # Sendgrid key as an environment variable
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("alex@pantheon.io")
    subject = "CSAT request"

    # User segment defined in Intercom.
    segment_id = '58738b8085932bd3b6a1ef43'

    intercom = IntercomAPI()
    users = intercom.get_users_by_segment(segment_id)

    for user in users:
        conversations = intercom.get_user_conversation(user['uuid'])
        
        #a_day = 60 * 60 * 24 # 60 seconds * 60 minutes * 24 hours
        if conversations['conversations']:
            # Getting the CSE with the most interactions.
            admins = []
            for conversation in conversations['conversations']:

                #if time.time() - conversation['created_at'] > a_day: continue
                #pprint.pprint(conversation)

                if conversation['assignee']['type'] == 'admin':
                    admins.append(conversation['assignee']['id'])

        if admins:
            cse_id = Counter(admins).most_common(1)[0][0]
            cse_name, cse_email = intercom.get_user(cse_id, 'admin')
            print "User {} ({}) was talking with CSE {} ({})".format(user['name'], user['email'], cse_name, cse_email)

        if user['email'] and cse_email:
            to_email = Email(user['email'])
            message = "You just had a conversation with {}. How did he do? Please rate his response - https://www.nicereply.com/pantheon/{}".format(cse_name, cse_email)
            content = Content("text/plain", message)
            mail = Mail(from_email, subject, to_email, content)
            response = sg.client.mail.send.post(request_body=mail.get())
            print(response.status_code)
            print(response.body)
            print(response.headers)