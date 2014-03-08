#!/usr/bin/python
"""Set nss-ldapd connection parameters

Option:
    --base=     unless provided, will ask interactively
    --binddn=   unless provided, will ask interactively
    --pass=     unless provided, will ask interactively
    --server=   unless provided, will ask interactively

"""

import os
import sys
import getopt

from dialog_wrapper import Dialog
from executil import system

def usage(s=None):
    if s:
        print >> sys.stderr, "Error:", s
    print >> sys.stderr, "Syntax: %s [options]" % sys.argv[0]
    print >> sys.stderr, __doc__
    sys.exit(1)

DEFAULT_BASE="dc=example,dc=com"
DEFAULT_SERVER='127.0.0.1'

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h",
                                       ['help', 'base=', 'binddn=', 'pass=', 'server='])
    except getopt.GetoptError, e:
        usage(e)

    ldap_base = ""
    ldap_user = ""
    server = ""
    password = ""
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt == '--pass':
            password = val
        elif opt == '--server':
            server = val
        elif opt == '--base':
            ldap_base = val
        elif opt == '--binddn':
            ldap_user = val

    if not ldap_base:
        d = Dialog('TurnKey Linux - First boot configuration')

        ldap_base = d.get_input(
            "LDAP Base",
            "Enter the LDAP Base.",
            DEFAULT_BASE)

    if ldap_base == "DEFAULT":
        ldap_base = DEFAULT_BASE

    if not ldap_user:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')

        ldap_user = d.get_input(
            "LDAP User",
            "Enter the LDAP User for connecting.",
            "cn=nss_pam," + ldap_base)

    if not password:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')

        password = d.get_password(
            "LDAP User Password",
            "Enter new password for the LDAP user account.")

    if not server:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')

        server = d.get_input(
            "LDAP Server",
            "Enter the LDAP Server URI.",
            DEFAULT_SERVER)

    script = os.path.join(os.path.dirname(__file__), 'nss_ldapd-reinit.sh')
    system(script, server, ldap_base, ldap_user, password)

if __name__ == "__main__":
    main()

