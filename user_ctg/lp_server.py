##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

from launchpadlib.launchpad import Launchpad, STAGING_SERVICE_ROOT
from launchpadlib.credentials import Credentials
import os

class LP_Server(object):
    cachedir = ".launchpad/cache/"
    credential_file = ".launchpad/lp_credential.txt"    
    application = 'openobject'
    def get_lp(self):
        if not os.path.isdir(self.cachedir):            
            os.makedirs(self.cachedir)
            
        if not os.path.isfile(self.credential_file):        
            launchpad = Launchpad.get_token_and_login(self.application, STAGING_SERVICE_ROOT, self.cachedir)        
            launchpad.credentials.save(file(self.credential_file, "w"))
        else:        
            credentials = Credentials()
            credentials.load(open(self.credential_file))
            launchpad = Launchpad(credentials, STAGING_SERVICE_ROOT, self.cachedir)
        return launchpad

    def get_lp_people_info(self, launchpad, users):    
        res = {}
        if not isinstance(users,list):
            users = [users]
        for user in users:
            result = {}            
            for person in launchpad.people.find(text=user):
                result['karma'] = person.karma                       
                result['name'] = person.name
            res[user] = result    
        return res

if __name__ == '__main__':
    lp_server = LP_Server()
    lp = lp_server.get_lp()
    print lp_server.get_lp_people_info(lp, 'hmo-tinyerp')
    

        

