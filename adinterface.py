import ldaplib


class ADInterface(object):

    def __init__(self, config):
        """config must be a dictionary of items (use GetConfig)"""
        self.config = config
        self.connect()

    def connect(self):
        """Connect to AD thru LDAP"""
        self.l = ldaplib.ldap_connection((self.config['host'], int(self.config['port'])))
        x = self.l.bind(self.config['binddn'], self.config['bindpw'])
        if x is not None:
            print 'bind error:', x.resultcode, 'error:', x.errorMessage
            sys.exit(x)

    def makepassword(self, pw):
        """Make a unicodePwd String for Windows AD junk."""
        unicode1 = unicode("\"" + pw + "\"", "iso-8859-1")
        unicode2 = unicode1.encode("utf-16-le")
        password_value = unicode2
        del pw
        return password_value

    def modify(self, dn, attr, values, mode='replace'):
        """values must be a []"""
        # [[operation,type,[vals]],[operation,type,[vals]]]
        # print 'Modify called:',dn,attr,values,mode
        x = self.l.modify(dn, [[mode, attr, values]])
        if x.errorMessage:
            # ['__doc__', '__init__', '__module__', 'app_code', 'args', 'buffer', 'decode', 'decode_sequence', 'encode', 'errorMessage', 'keyvals', 'matcheddn', 'messageid', 'myargs', 'resultcode']
            print 'dn:', dn
            print 'Modify Operation failure res:', x.resultcode, 'error:', x.errorMessage
            # print 'buffer:',x.buffer,'decode',x.decode()
            # print dir(x)
        return True

    def findUser(self, name):
        userDN = None
        x = self.l.search('sAMAccountName=%s' % (name), self.config['searchdn'], attributes=['distinguishedName'])
        # print 'num results:',len(x)
        if len(x) > 1:
            # print 'returned:',x[0].keyvals
            userDN = x[0].keyvals['distinguishedName'][0]
        return userDN

    # Begin API Calls
    def changepass(self, user, passwd):
        """call with string, user and passwd """
        passwd = self.makepassword(passwd)
        user = self.findUser(user)
        if not user:
            raise Exception('Invalid Username, user not found.')
        self.modify(user, 'unicodePwd', [passwd])
