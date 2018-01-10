#!/usr/bin/env python
"""adpasswd.py Command line interface to change Active Directory Passwords via LDAP.
Copyright 2009 Craig Sawyer
email: csawyer@yumaed.org
license: GPLv2 see LICENSE.txt
"""
import os
import sys
import ConfigParser
import getpass

from adinterface import ADInterface

CONFIG_FILENAME = '.adpasswd.cfg'


class InvalidConfigException(Exception):
    pass


def GetConfig():
    cf = None
    if os.path.exists(CONFIG_FILENAME):
        configfile = CONFIG_FILENAME
    else:
        configfile = os.path.join('/etc', CONFIG_FILENAME)
        if not os.path.exists(configfile):
            homedrive = None
            if os.name == 'posix':
                path = os.environ['HOME']
            elif os.name == 'nt':
                if 'HOMEPATH' in os.environ:
                    homedrive = os.environ['HOMEDRIVE']
                    path = os.environ['HOMEPATH']
            configfile = os.path.join(homedrive, path, CONFIG_FILENAME)
    if os.path.exists(configfile):
        fd = open(configfile, 'r')
        config = ConfigParser.ConfigParser()
        config.readfp(fd)
        if config.has_section('ad'):
            cf = dict()
            for name, value in config.items('ad'):
                cf[name] = value
        else:
            raise InvalidConfigException()
            print 'Config file seems misconfigured.. no [ad] section'
    else:
        print "we need a config file here %s or the cwd. " % (configfile)
        print """example config:
        [ad]
    host: ad.blah.com
    port: 636
    binddn: cn=Administrator,CN=Users,DC=ad,DC=blah,DC=com
    bindpw: changemequickly
    searchdn: DC=ad,DC=blah,DC=com
        """
        raise InvalidConfigException()
        print "No valid config file. Quitting."
    return cf


def Main():
    user = None
    password = None
    if len(sys.argv) == 3:
        user = sys.argv[1]
        password = sys.argv[2]
    if len(sys.argv) == 2:
        user = sys.argv[1]
        password = getpass.getpass()
    if user and password:
        cf = GetConfig()
        print cf
        l = ADInterface(cf)
        l.changepass(user, password)
    else:
        print "adpasswd.py: You must specify <username> and (optionally) <password>"
        print "usage: adpasswd.py username [password]"
        sys.exit(1)


if __name__ == "__main__":
    Main()
