import xmlrpclib

server = 'localhost'
port = '8069'
secure = False
username = 'admin'
password = 'admin'
dbname = 'sale_promotions'

url = 'http' + (secure and 's' or '') + '://' + server + ':' + port
common = xmlrpclib.ServerProxy(url + '/xmlrpc/common')
uid = common.login(dbname, username, password)
object = xmlrpclib.ServerProxy(url + '/xmlrpc/object')
#object.execute(dbname, uid, password,'promos.rules', 'evaluate', 1, 3) #TODO: evaluate def need object, not ID values
object.execute(dbname, uid, password, 'promos.rules', 'apply_promotions', 3)
