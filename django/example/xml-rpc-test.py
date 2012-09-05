import xmlrpclib

server = 'localhost'
port = '8069'
secure = False
username = 'admin'
password = 'admin'
dbname = 'django'

url = 'http' + (secure and 's' or '') + '://' + server + ':' + port
common = xmlrpclib.ServerProxy(url + '/xmlrpc/common')
uid = common.login(dbname, username, password)
object = xmlrpclib.ServerProxy(url + '/xmlrpc/object')


username = 'yourusername'
email = 'user@email.com'
values = {'name':'Zikzakmedia','customer': True,'supplier':False}
partner = object.execute(dbname, uid, password, 'res.partner', 'dj_check_partner', username, email, values)
print partner

values = {'name':'Esteve','zip':'08720','email': 'user@email.com'}
address_id = ''
address = object.execute(dbname, uid, password, 'res.partner', 'dj_check_partner_address', username, email, values, address_id)
print address
