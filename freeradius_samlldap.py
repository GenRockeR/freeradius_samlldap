 #!/usr/bin/env python

import ldap
import os
import radiusd
from saml2.assertion import Assertion, Policy
from saml2.saml import NameID, Issuer
from saml2.saml import NAMEID_FORMAT_ENTITY
from saml2.saml import NAMEID_FORMAT_TRANSIENT
from saml2.saml import NAME_FORMAT_URI
from saml2.attribute_converter import AttributeConverterNOOP

LDAP_SERVER = 'sec.cs.kent.ac.uk'
LDAP_BASE_DN = 'o=TAAS,c=gb'
LDAP_ATTR = 'cn='

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
    if identity == None:
        return radiusd.RLM_MODULE_FAIL

    policy = Policy({
        'default': {
            'lifetime': {'minutes': 60},
            'attribute_restrictions': None,
            'name_form': NAME_FORMAT_URI
        }
    })

    name_id = NameID(format=NAMEID_FORMAT_TRANSIENT, text='urn:mace:' + LDAP_SERVER)
    issuer = Issuer(text='moonshot.' + LDAP_SERVER, format=NAMEID_FORMAT_ENTITY)
    ast = Assertion(identity)
    assertion = ast.construct('', '', '',
                        name_id, [AttributeConverterNOOP(NAME_FORMAT_URI)],
                        policy, issuer=issuer)

    assertion = str(assertion).replace('\n', '')

    attr = 'SAML-AAA-Assertion'
    result = (tuple([(attr, x) for x in eq_len_parts('%s' % assertion)]))
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

