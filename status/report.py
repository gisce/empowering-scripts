# -*- coding: utf-8 -*-

import os
import erppeek
from uempowering import Empowering

from datetime import datetime, timedelta
from dateutil import relativedelta

config = {
    'erp':
        {
            'uri': os.getenv('PEEK_SERVER', None),
            'db': os.getenv('PEEK_DB', None),
            'user': os.getenv('PEEK_USER', None),
            'password': os.getenv('PEEK_PASSWORD', None)
        },
    'docs': {
        'uri': 'https://docsapi.helpscout.net/v1',
        'key': ''
        },
    'api': {
        'uri': 'https://api.helpscout.net/v1',
        'key': 'your_key'
        },
    'mandrill': {
        'key': 'your_key',
        'senders': ['info@somenergia.coop'],
        'query': 'subject:\"Benvinguda\" OR subject:\"Bienvenida\"' 
        }
    }

mailbox_id = 55857

class HelpScout(object):

    def __init__(self, config):
        self.config = config 
   
    def get(self, type_id, req, mtype=True):
        if not mtype:
            return self.get_page(type_id, req, None)

        content = self.get_page(type_id, req, 1)
        pages = int(content.get('pages'))
        items = content.get('items')
        for page in range(2, pages+1):
            items += self.get_page(type_id, req, page).get('items')
        return items

    def get_page(self, type_id, req, page_id):
        import base64
        import urllib2
        import json
        import socket

        uri = self.config[type_id]['uri']
        key = self.config[type_id]['key']

        #url = uri + '/' + req + '?page=' + str(page_id)
        url = uri + '/' + req
        if page_id:
            url += '?page=' + str(page_id)

        _req = urllib2.Request(url)
        authheader =  "Basic %s" % base64.encodestring('%s:%s' % (key, "DUMMY_PASSWORD"))
        authheader = authheader.split('=')[0] #Problema HelpScout amb el padding ==
        _req.add_header("Authorization", authheader)
    
        content = ''
        try:
            print str(_req)
            print url
            rply = urllib2.urlopen(_req)
            content = rply.read()
        except urllib2.URLError as e:
            return None 
        except socket.timeout, e:
            return None
        return json.loads(content)

    def get_items(self, type_id, uri, obj_id, fields, mtype=True):
        result = self.get(type_id, uri, mtype)
        if not isinstance(result, list):
            result = [result]
        return [{field: item.get(field) for field in fields} 
                for item in result]

    def get_mailboxes(self, fields):
        uri = 'mailboxes.json'
        obj_id = 'mailboxes'
        return self.get_items('api', uri, obj_id, fields)

    def get_conversations(self, mailbox, fields):
        uri = 'mailboxes/{}/conversations.json'.format(mailbox)
        obj_id = 'conversations'
        return self.get_items('api', uri, obj_id, fields)

    def get_reports(self, mailboxes, start, end, fields):
        start_str = start.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_str = end.strftime('%Y-%m-%dT%H:%M:%SZ')
        mailboxes_str = ','.join(mailboxes)
        uri = 'reports/conversations.json?start={start_str}&end={end_str}&mailboxes={mailboxes_str}'.format(**locals())
        obj_id = None
        return self.get_items('api', uri, obj_id, fields, False)


import mandrill
class Mandrill(object):
    def __init__(self, key):
        self.key = key 
        self.client = mandrill.Mandrill(self.key)

    def get_summary(self, senders, start, end, query):
        result = self.client.messages.search_time_series(
            query=query,
            date_from=start, date_to=end, senders=senders)
        aggregated = {u'soft_bounces': 0, 
                      u'rejects': 0, 
                      u'hard_bounces': 0, 
                      u'unsubs': 0,
                      u'unique_clicks': 0,
                      u'sent': 0,
                      u'complaints': 0,
                      u'clicks': 0,
                      u'opens': 0,
                      u'unique_opens': 0}
        for hour in result:
            for k in aggregated:
                if k in hour:
                    aggregated[k] += hour[k]
        return aggregated
          


# Number of contracts pushing data
def get_enabled(O):
    cups_obj = O.model('giscedata.cups.ps')
    return len(cups_obj.search([('empowering', '=', True)])) 

# Number of active contracts 
def get_active(O):
    partner_obj = O.model('res.partner')
    return len(partner_obj.search([('empowering_token', '!=', None)])) 

# Deliver status
def get_deliver_status(O):
    log_obj = O.model('empowering.customize.profile.channel.log')
    now = datetime.now().strftime('%Y-%m-%d')
    prev = (datetime.now() + timedelta(days=-7)).strftime('%Y-%m-%d')
    return (prev, now, len(log_obj.search([('last_generated', '>=', prev),
                               ('last_generated', '<=', now),
                               ('channel_id', '=', 1),
                               ('sent', '=', True)]))) 

# Services
O = erppeek.Client(config['erp']['uri'],
               config['erp']['db'],
               config['erp']['user'],
               config['erp']['password'])


HS = HelpScout(config)
mconfig = config['mandrill']
M = Mandrill(mconfig['key'])

# Non-formatted output
end = datetime.now() 
start = end - timedelta(days=7)
end_str = end.strftime('%Y-%m-%d')
start_str = start.strftime('%Y-%m-%d')

# Statistics 
# OpenERP
result_o = get_deliver_status(O) 
# HelpScout
result_hs = HS.get_reports([str(mailbox_id)], start, end, ['current'])[0]['current']
# Mandrill
result_m = M.get_summary(mconfig['senders'], start_str, end_str, mconfig['query'])
result_m['sent'] = result_m['sent']/2 ## FIX DUE notification forwarding 

print '#INFOENERGIA WEEKLY REPORT (from {start_str} to {end_str})'.format(**locals()) 

print "## Summary"
# NOTE: Temporary disable till reviewed
#print "Contracts enabled: %d\n" % get_enabled(O)
#print "Contracts active: %d\n" % get_active(O)
print "Delivered reports from (%s) to (%s): %d" % (result_o[0], result_o[1], result_o[2])
#print "### Helpscout\n"
print "totalConversations: %d\n" % result_hs['totalConversations'] 
print "conversationsCreated: %d\n" % result_hs['conversationsCreated'] 
print "conversationsPerDay: %d\n" % result_hs['conversationsPerDay']
print "### Mandrill\n"
print "Sent: %d\n" % result_m['sent']
print "Open: %d\n" % result_m['unique_opens']
print "Average open: %0.2f %%\n" % 0
#print "Average open: %0.2f %%\n" % ((result_m['unique_opens']*1.0/result_m['sent'])*100.00)
#print "Clicks: %d\n" % result_m['unique_clicks']
#print "Average Clicks: %0.2f %%\n" % ((result_m['unique_clicks']*1.0/result_m['sent'])*100.00)
#
print "## Helpscout"
print "totalConversations: %d\n" % result_hs['totalConversations'] 
print "conversationsCreated: %d\n" % result_hs['conversationsCreated'] 
print "newConversations: %d\n" % result_hs['newConversations'] 
print "conversationsPerDay: %d\n" % result_hs['conversationsPerDay'] 

print "## Mandrill"
print "Sent: %d\n" % result_m['sent']
print "Rejects: %d\n" % result_m['rejects']
print "Soft_bounces: %d\n" % result_m['soft_bounces']
print "Hard_bounces: %d\n" % result_m['hard_bounces']
print "Open: %d\n" % result_m['unique_opens']
print "Average open: %0.2f %%\n" % 0
#print "Average open: %0.2f %%\n" % ((result_m['unique_opens']*1.0/result_m['sent'])*100.00)
#print "Clicks: %d\n" % result_m['unique_clicks']
#print "Average Clicks: %0.2f %%\n" % ((result_m['unique_clicks']*1.0/result_m['sent'])*100.00)
