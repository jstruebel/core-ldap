#!/bin/bash -e

fatal() {
    echo "fatal: $@" 1>&2
    exit 1
}

usage() {
cat<<EOF
Syntax: $(basename $0) server base binddn password
Re-initialize NSS/PAM LDAPD

Arguments:
    server          # LDAP server
    base            # LDAP directory base
    binddn          # LDAP user
    password        # LDAP user password

EOF
    exit 1
}

if [[ "$#" != "4" ]]; then
    usage
fi

LDAP_SERVER=$1
LDAP_BASEDN=$2
LDAP_BINDDN=$3
LDAP_PASS=$4

NSLCD_RUNNING=$(/etc/init.d/nslcd status > /dev/null; echo $?)

if [[ `uname -m` == "x86_64" ]]; then
    ARCH=amd64
else
    ARCH=i386
fi

# rename nslcd.conf to force new config
CONF=/etc/nslcd.conf
mv $CONF ${CONF}_bak

# re-configure libnss-ldapd
debconf-set-selections << EOF
nslcd nslcd/ldap-starttls boolean false
nslcd nslcd/ldap-base string $LDAP_BASEDN
nslcd nslcd/ldap-auth-type select none
nslcd nslcd/ldap-uris string $LDAP_SERVER
libnss-ldapd:$ARCH libnss-ldapd/nsswitch multiselect group, passwd, shadow
libnss-ldapd:$ARCH libnss-ldapd/clean-nsswitch boolean false
EOF

DEBIAN_FRONTEND=noninteractive dpkg-reconfigure nslcd libnss-ldapd

# add rootpwmoddn to nslcd.conf
CONF=/etc/nslcd.conf
sed -i "s|#rootpwmoddn.*|rootpwmoddn $LDAP_BINDDN\nrootpwmodpw $LDAP_PASS|" $CONF
chmod og-rwx $CONF

# restart nslcd if it was running, or stop it
if [ "$NSLCD_RUNNING" == "0" ]; then
    /etc/init.d/nslcd restart
else
    /etc/init.d/nslcd stop
fi

[ -e $INITHOOKS_CONF ] && exit 0

cat $INITHOOKS_CONF << EOF
export LDAP_BASEDN=$LDAP_BASEDN
export LDAP_SERVER=$LDAP_SERVER
EOF

