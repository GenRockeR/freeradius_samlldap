#!/usr/bin/env python

import ldap
import os
import radiusd
from saml2.server import Server

LDAP_SERVER = 'ldap.id.kent.ac.uk'
LDAP_BASE_DN = 'o=uni'
LDAP_ATTR = 'uid='

def eq_len_parts(str, delta=230):
    res = []
    n = 0
    strlen = len(str)
    while n <= strlen:
        m = n + delta
        res.append(''.join(str[n:m]))
        n = m
    return res

def instantiate(p):
    return radiusd.RLM_MODULE_OK

def ldap_attributes(userName, userPassword):
    try:
        l = ldap.open(LDAP_SERVER)

        ldap_result_id = l.search(
            LDAP_BASE_DN, ldap.SCOPE_SUBTREE, LDAP_ATTR + userName, None
        )

        result_type, result_data = l.result(ldap_result_id, 0)
        if result_type != ldap.RES_SEARCH_ENTRY or result_data == []:
            return

        user = result_data[0][0]
        l.simple_bind_s(user, userPassword)
        
        ldap_result_id = l.search(user, ldap.SCOPE_BASE)
        result_type, result_data = l.result(ldap_result_id, 0)
        if result_type != ldap.RES_SEARCH_ENTRY or result_data == []:
            return

        l.unbind_s()

        return result_data[0][1]

    except ldap.LDAPError, e:
        print e

def post_auth(authData):
    for t in authData:
        if t[0] == 'Stripped-User-Name':
            userName = t[1][1:-1]
        elif t[0] == 'User-Password':
            userPassword = t[1][1:-1]

    identity = ldap_attributes(userName, userPassword)
    #identity = None
    server = Server('idp_conf')
    name_id = server.ident.transient_nameid('urn:mace:kent.ac.uk', 'id')
    assertion = server.create_authn_response(
        identity,
       'id', 'http://localhost',
       'urn:mace:kent.ac.uk'
       '',
       name_id=name_id)

    attr = 'SAML-AAA-Assertion'
    result = (tuple([(attr, x) for x in eq_len_parts("%s" % assertion)]))
    return radiusd.RLM_MODULE_UPDATED, result, None

# Usage with rlm_exec
if __name__ == '__main__':
    instantiate(None)
    status, result, none  = post_auth((
        ('Stripped-User-Name', os.environ['STRIPPED_USER_NAME']),
        ('User-Password', os.environ['USER_PASSWORD']))
    )
    
    for attr in result:
        print attr[0] + ' = "' + attr[1].replace('"','\\"').replace('\n', '') + '"'

