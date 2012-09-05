# -*- encoding: utf-8 -*-
#########################################################################
#
#    Kettle connector for OpenERP
#    Copyright (C) 2010 Sébastien Beau <sebastien.beau@akretion.com>
#    Copyright (C) 2011 Akretion (http://www.akretion.com). All Rights Reserved
#    @author Alexis de Lattre <alexis.delattre@akretion.com> : some enhancements
#    @author Raphaël Valyi <raphael.valyi@akretion.com> : added Carte server execution mode
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
#########################################################################

# TODO :
# Use this to create KTR temp file http://docs.python.org/dev/library/tempfile.html
# When starting the transfo by the wizard, switch to a scroll bar, like when we do an "update modules" in the administration menu
# Can we avoid the "Read from filesystem" bool on the kettle.transfo obj ?

from osv import fields,osv
import os
import sys
import netsvc
import time
import datetime
import base64
from installer import installer
import tools
from tools import config
from tools.translate import _
import zipfile
from mako.template import Template
import httplib
import urllib
from lxml import etree
import socket
import subprocess 
import shutil

class kettle_server(osv.osv):
    _name = 'kettle.server'
    _description = 'kettle server'

    def button_install(self, cr, uid, ids, context=None):
        inst = installer()
        inst.install(self.read(cr, uid, ids, ['kettle_dir'])[0]['kettle_dir'].replace('data-integration', ''))
        return True

    def button_update_terminatooor(self, cr, uid, ids, context=None):
        inst = installer()
        inst.update_terminatoor(self.read(cr, uid, ids, ['kettle_dir'])[0]['kettle_dir'].replace('data-integration', ''))
        return True

    _columns = {
        'name': fields.char('Server name', size=64, required=True),
        'kettle_dir': fields.char('Kettle installation directory', size=256, required=True),
        'url': fields.char('Kettle URL', size=64, help='URL of Kettle server if any (can be localhost)'),
        'user': fields.char('Kettle server user', size=32),
        'password': fields.char('Kettle server password', size=32),
        }

    _defaults = {
        'kettle_dir': lambda *a: tools.config['addons_path'].replace('/addons', '/data-integration'),
        }

kettle_server()



class kettle_transformation(osv.osv):
    _name = 'kettle.transformation'
    _description = 'kettle transformation'

    _columns = {
        'name': fields.char('Transformation / Job name', size=64, required=True),
        'file': fields.binary('File'),
        'read_from_filesystem': fields.boolean('Read from filesystem', help="If active, OpenERP will read the file from the filesystem. Otherwise, it will read the file from the 'File' field."),
        'filename': fields.char('Filename', size=128, help="If the Kettle file is attached, enter the filename. If the Kettle file is read from the filesystem, enter the relative or absolute path to the file."),
        'type': fields.selection([('trans', 'Transformation'), ('job', 'Job')], "Type", required=True),
        }

    def _get_type(self, vals):
        if vals.get('filename', False):
            extension = os.path.splitext(vals['filename'].lower())[1]
            if extension == '.ktr':
                vals['type'] = 'trans' 
            elif extension == '.kjb':
                vals['type'] = 'job'
        return vals

    def create(self, cr, uid, vals, context=None):
        return super(kettle_transformation, self).create(cr, uid, self._get_type(vals), context)

    def write(self, cr, uid, ids, vals, context=None):
        return super(kettle_transformation, self).write(cr, uid, ids, self._get_type(vals), context)

    _defaults = {
        'type': 'trans',
    }

kettle_transformation()


class kettle_trans_log_table(osv.osv):
    _name = 'kettle.trans.log.table'
    _description = 'Kettle Transformation and Job Logs' #NB: we deliberately use the same log table to make it simpler


    def _get_step_log_ids(self, cr, uid, ids, name, args, context=None):
        res = {}
        for trans_log in self.browse(cr, uid, ids):
            res[trans_log.id] = self.pool.get('kettle.step.log.table').search(cr, uid, [('transname', '=', trans_log.transname), ('id_batch', '=', trans_log.id_batch)])
        return res


    _columns = {
        'id_batch': fields.integer('Batch ID', select=True),
        'id_job': fields.integer('Batch ID', select=True),
        'channel_id': fields.char('Channel ID', size=64),
        'transname': fields.char('Transformation Name', size=64, select=True),
        'jobname': fields.char('Transformation Name', size=64, select=True),
        'status': fields.char('Status', size=16, select=True),
        'lines_read': fields.integer('Lines Read'),
        'lines_written': fields.integer('Lines Written'),
        'lines_updated': fields.integer('Lines Updated'),
        'lines_input': fields.integer('Lines Input'),
        'lines_output': fields.integer('Lines Output'),
        'lines_rejected': fields.integer('Lines Rejected'),
        'errors': fields.integer('Errors', select=True),
        'startdate': fields.datetime('Start Date', select=True),
        'enddate': fields.datetime('End Date'),
        'logdate': fields.datetime('Log Date'),
        'depdate': fields.datetime('Dependency Date'),
        'replaydate': fields.datetime('Replay Date'),
        'log_field': fields.text('Execution Log'),
        'step_log_ids': fields.function(_get_step_log_ids, method=True, type='one2many', relation="kettle.step.log.table", string='Step details'),
        }

    _rec_name = 'transname'
    _order = 'enddate desc, transname, jobname'


kettle_trans_log_table()


class kettle_step_log_table(osv.osv):
    _name= 'kettle.step.log.table'
    _description = 'Kettle Step log table'

    _columns = {
        'id_batch': fields.integer('Batch ID', select=True),
        'channel_id': fields.char('Channel ID', size=64),
        'log_date': fields.datetime('Log Date'),
        'transname': fields.char('Transformation Name', size=64, select=True),
        'stepname': fields.char('Step Name', size=64, select=True),
        'step_copy': fields.integer('Step Copy'),
        'lines_read': fields.integer('Lines Read'),
        'lines_written': fields.integer('Lines Written'),
        'lines_updated': fields.integer('Lines Updated'),
        'lines_input': fields.integer('Lines Input'),
        'lines_output': fields.integer('Lines Output'),
        'lines_rejected': fields.integer('Lines Rejected'),
        'errors': fields.integer('Errors', select=True),
    }

    _rec_name = 'stepname'

kettle_step_log_table()


class kettle_task(osv.osv):
    _name = 'kettle.task'
    _description = 'kettle task'

    def _url(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for task in self.browse(cr, uid, ids, context=context):
            if task.carte_id and task.server_id and task.server_id.url:
                encoded_name = urllib.urlencode({'key': task.transformation_id.name}).replace('key=', '')
                res[task.id] = task.server_id.url + '/kettle/' + (task.transformation_id.type == 'trans' and 'transStatus' or 'jobStatus') + '/?name=' + encoded_name
            else:
                res[task.id] = False
        return res

    def _related_logs(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for task in self.browse(cr, uid, ids, context=context):
            res[task.id] = self.pool.get('kettle.trans.log.table').search(cr, uid, ['|', ('transname', '=', task.transformation_id.name), ('jobname', '=', task.transformation_id.name)])
        return res


    _columns = {
        'name': fields.char('Task name', size=64, required=True),
        'server_id': fields.many2one('kettle.server', 'Server', required=True),
        'transformation_id': fields.many2one('kettle.transformation', 'Transformation / Job', required=True),
        'scheduler': fields.many2one('ir.cron', 'Scheduler', readonly=True),
        'upload_file': fields.boolean('Upload file', help="If active, OpenERP will propose to give a file as input for the transformation/job when starting the task"),
        'output_file' : fields.boolean('Output file', help="If active, OpenERP will store as an attachement the file that has been generated by the Kettle transformation/job"),
        'active_python_code' : fields.boolean('Active Python code'),
        'python_code_before' : fields.text('Python code executed before transformation'),
        'python_code_after' : fields.text('Python code executed after transformation'),
        'last_date' : fields.datetime('Last execution'),
        'parameter_ids': fields.one2many('kettle.parameter', 'task_id'),
        'carte_id': fields.char('Carte ID', size=64),
        'url': fields.function(_url, method=True, string='Link', type='char', size=128, help='The Carte URL to see the logs live'),
        'related_logs': fields.function(_related_logs, method=True, string='Related Logs', type='one2many', relation="kettle.trans.log.table"),
    }

    def attach_file_to_task(self, cr, uid, id, datas_fname, attach_name, delete = False, context = None):
        if not context:
            context = {}
        context.update({'default_res_id' : id, 'default_res_model': 'kettle.task'})
        datas = base64.encodestring(open(os.path.join(context['kettle_dir'], datas_fname), 'rb').read())
        os.remove(os.path.join(context['kettle_dir'], datas_fname))
        attachment_id = self.pool.get('ir.attachment').create(cr, uid, {'name': attach_name, 'datas': datas, 'datas_fname': os.path.basename(datas_fname)}, context)
        return attachment_id


    def attach_output_file_to_task(self, cr, uid, id, datas_fname, attach_name, delete = False, context = None):
        filename_completed = False
        filename = os.path.basename(datas_fname)
        dir = os.path.join(context['kettle_dir'], 'openerp_tmp')
        files = os.listdir(dir)
        for file in files:
            if filename in file:
                filename_completed = file
        if filename_completed:
            self.attach_file_to_task(cr, uid, id, os.path.join('openerp_tmp', filename_completed), attach_name, delete, context)
        else:
            raise osv.except_osv(_('Error'), _('The output file was not found. Are you sure that your transformation/job was supposed to generate an output file?'))


    def execute_python_code(self, cr, uid, id, position, context):
        logger = netsvc.Logger()
        task = self.read(cr, uid, id, ['active_python_code', 'python_code_' + position], context)
        if task['active_python_code'] and task['python_code_' + position]:
            logger.notifyChannel('kettle-connector', netsvc.LOG_INFO, "execute python code " + position +" kettle task")
            exec(task['python_code_' + position])
            logger.notifyChannel('kettle-connector', netsvc.LOG_INFO, "python code executed")
        return context


    def error_wizard(self, cr, uid, id, context):
        error_description = self.pool.get('ir.attachment').read(cr, uid, id, ['description'], context)['description']
        if error_description and "USER_ERROR" in error_description:
            raise osv.except_osv('USER_ERROR', error_description)
        else:
            raise osv.except_osv('KETTLE ERROR', 'An error occurred, please look in the kettle log')

    def transfo_execution_configuration(self, cr, uid, id, transfo_name, params, context):
        conf_template = Template("""<transformation_execution_configuration>
    <exec_local>N</exec_local>
    <variables>
    % for key, value in params.items():
        <variable><name>${key}</name><value>${value}</value></variable>
    % endfor
    </variables>
    <parameters>
    % for key, value in params.items():
        <parameter><name>${key}</name><value>${value}</value></parameter>
    % endfor
    </parameters>
    <replay_date/>
    <safe_mode>N</safe_mode>
    <log_level>Debug</log_level>
    <clear_log>Y</clear_log>
</transformation_execution_configuration>""")
        return conf_template.render(name=transfo_name, params=params)

    def job_execution_configuration(self, cr, uid, id, job_name, params, context):
        conf_template = Template("""<job_execution_configuration>
    <exec_local>N</exec_local>
    <variables>
    % for key, value in params.items():
        <variable><name>${key}</name><value>${value}</value></variable>
    % endfor
    </variables>
    <parameters>
    % for key, value in params.items():
        <parameter><name>${key}</name><value>${value}</value></parameter>
    % endfor
    </parameters>
    <replay_date/>
    <safe_mode>N</safe_mode>
    <log_level>Debug</log_level>
    <clear_log>Y</clear_log>
</job_execution_configuration>""")
        return conf_template.render(name=job_name, params=params)


    def kettle_pg_connection(self, cr, uid, id, context):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        logger = netsvc.Logger()
        if not (config['db_password']):
            msg = """it seems you are using Postgres 'same ident' authentication method (hey good!)
But then you should set the config['db_password'] or parameters['db_password'] in the Kettle parameters
for kettle_connector to be able to log!"""
            logger.notifyChannel('kettle-connector', netsvc.LOG_ERROR, msg)
            return False
        template = Template("""<connection>
    <name>openerpdb</name>
    <server>${config['db_port'] or 'localhost'}</server>
    <type>POSTGRESQL</type>
    <access>Native</access>
    <database>${cr.dbname}</database>
    <port>${config['db_port'] or 5432}</port>
    <username>${config['db_user'] or user.login}</username>
    <password>${config['db_password']}</password>
    <servername/>
    <data_tablespace/>
    <index_tablespace/>
    <attributes>
      <attribute><code>FORCE_IDENTIFIERS_TO_LOWERCASE</code><attribute>N</attribute></attribute>
      <attribute><code>FORCE_IDENTIFIERS_TO_UPPERCASE</code><attribute>N</attribute></attribute>
      <attribute><code>IS_CLUSTERED</code><attribute>N</attribute></attribute>
      <attribute><code>PORT_NUMBER</code><attribute>5432</attribute></attribute>
      <attribute><code>QUOTE_ALL_FIELDS</code><attribute>N</attribute></attribute>
      <attribute><code>SUPPORTS_BOOLEAN_DATA_TYPE</code><attribute>N</attribute></attribute>
      <attribute><code>USE_POOLING</code><attribute>N</attribute></attribute>
    </attributes>
  </connection>""")
        return template.render(cr=cr, user=user, config=config)

    def kettle_tranfo_logs(self, cr, uid, id, context):
        template = Template("""<log>
<trans-log-table><connection>openerpdb</connection>
<schema>public</schema>
<table>kettle_trans_log_table</table>
<size_limit_lines/>
<interval/>
<timeout_days/>
<field><id>ID_BATCH</id><enabled>Y</enabled><name>ID_BATCH</name></field><field><id>CHANNEL_ID</id><enabled>Y</enabled><name>CHANNEL_ID</name></field><field><id>TRANSNAME</id><enabled>Y</enabled><name>TRANSNAME</name></field><field><id>STATUS</id><enabled>Y</enabled><name>STATUS</name></field><field><id>LINES_READ</id><enabled>Y</enabled><name>LINES_READ</name><subject/></field><field><id>LINES_WRITTEN</id><enabled>Y</enabled><name>LINES_WRITTEN</name><subject/></field><field><id>LINES_UPDATED</id><enabled>Y</enabled><name>LINES_UPDATED</name><subject/></field><field><id>LINES_INPUT</id><enabled>Y</enabled><name>LINES_INPUT</name><subject/></field><field><id>LINES_OUTPUT</id><enabled>Y</enabled><name>LINES_OUTPUT</name><subject/></field><field><id>LINES_REJECTED</id><enabled>Y</enabled><name>LINES_REJECTED</name><subject/></field><field><id>ERRORS</id><enabled>Y</enabled><name>ERRORS</name></field><field><id>STARTDATE</id><enabled>Y</enabled><name>STARTDATE</name></field><field><id>ENDDATE</id><enabled>Y</enabled><name>ENDDATE</name></field><field><id>LOGDATE</id><enabled>Y</enabled><name>LOGDATE</name></field><field><id>DEPDATE</id><enabled>Y</enabled><name>DEPDATE</name></field><field><id>REPLAYDATE</id><enabled>Y</enabled><name>REPLAYDATE</name></field><field><id>LOG_FIELD</id><enabled>Y</enabled><name>LOG_FIELD</name></field></trans-log-table>

<step-log-table><connection>openerpdb</connection>
<schema>public</schema>
<table>kettle_step_log_table</table>
<timeout_days/>
<field><id>ID_BATCH</id><enabled>Y</enabled><name>ID_BATCH</name></field><field><id>CHANNEL_ID</id><enabled>Y</enabled><name>CHANNEL_ID</name></field><field><id>LOG_DATE</id><enabled>Y</enabled><name>LOG_DATE</name></field><field><id>TRANSNAME</id><enabled>Y</enabled><name>TRANSNAME</name></field><field><id>STEPNAME</id><enabled>Y</enabled><name>STEPNAME</name></field><field><id>STEP_COPY</id><enabled>Y</enabled><name>STEP_COPY</name></field><field><id>LINES_READ</id><enabled>Y</enabled><name>LINES_READ</name></field><field><id>LINES_WRITTEN</id><enabled>Y</enabled><name>LINES_WRITTEN</name></field><field><id>LINES_UPDATED</id><enabled>Y</enabled><name>LINES_UPDATED</name></field><field><id>LINES_INPUT</id><enabled>Y</enabled><name>LINES_INPUT</name></field><field><id>LINES_OUTPUT</id><enabled>Y</enabled><name>LINES_OUTPUT</name></field><field><id>LINES_REJECTED</id><enabled>Y</enabled><name>LINES_REJECTED</name></field><field><id>ERRORS</id><enabled>Y</enabled><name>ERRORS</name></field><field><id>LOG_FIELD</id><enabled>N</enabled><name>LOG_FIELD</name></field></step-log-table>
</log>
""")
        return template.render()


    def kettle_job_logs(self, cr, uid, id, context):
        template = Template("""<job-log-table><connection>openerpdb</connection>
<schema>public</schema>
<table>kettle_trans_log_table</table>
<size_limit_lines/>
<interval/>
<timeout_days/>
<field><id>ID_JOB</id><enabled>Y</enabled><name>ID_JOB</name></field><field><id>CHANNEL_ID</id><enabled>Y</enabled><name>CHANNEL_ID</name></field><field><id>JOBNAME</id><enabled>Y</enabled><name>JOBNAME</name></field><field><id>STATUS</id><enabled>Y</enabled><name>STATUS</name></field><field><id>LINES_READ</id><enabled>Y</enabled><name>LINES_READ</name></field><field><id>LINES_WRITTEN</id><enabled>Y</enabled><name>LINES_WRITTEN</name></field><field><id>LINES_UPDATED</id><enabled>Y</enabled><name>LINES_UPDATED</name></field><field><id>LINES_INPUT</id><enabled>Y</enabled><name>LINES_INPUT</name></field><field><id>LINES_OUTPUT</id><enabled>Y</enabled><name>LINES_OUTPUT</name></field><field><id>LINES_REJECTED</id><enabled>Y</enabled><name>LINES_REJECTED</name></field><field><id>ERRORS</id><enabled>Y</enabled><name>ERRORS</name></field><field><id>STARTDATE</id><enabled>Y</enabled><name>STARTDATE</name></field><field><id>ENDDATE</id><enabled>Y</enabled><name>ENDDATE</name></field><field><id>LOGDATE</id><enabled>Y</enabled><name>LOGDATE</name></field><field><id>DEPDATE</id><enabled>Y</enabled><name>DEPDATE</name></field><field><id>REPLAYDATE</id><enabled>Y</enabled><name>REPLAYDATE</name></field><field><id>LOG_FIELD</id><enabled>Y</enabled><name>LOG_FIELD</name></field></job-log-table>""")
        return template.render()



    def run_kettle_task(self, cr, uid, task, parameters, log_file_name, attachment_id, context):
        '''Execute the Kettle transfo/job'''
        kettle_dir = task.server_id.kettle_dir
        if not os.path.exists(kettle_dir):
            raise osv.except_osv(_('Error :'), _("The directory for Kettle '%s' doesn't exist on the filesystem.") % kettle_dir)
        if not os.path.isfile(os.path.join(kettle_dir, u'pan.sh')) or not os.path.isfile(os.path.join(kettle_dir, u'kitchen.sh')):
            raise osv.except_osv(_('Error :'), _("The directory for Kettle '%s' should contain at least the files kitchen.sh and pan.sh.") % kettle_dir)
        transfo = task.transformation_id
        logger = netsvc.Logger()

        if transfo.read_from_filesystem:
            if os.path.exists(transfo.filename):
                path_to_file = transfo.filename
            elif os.path.exists(os.path.join(config['addons_path'], transfo.filename)):
                path_to_file = os.path.abspath(os.path.join(config['addons_path'], transfo.filename))
            else:
                raise osv.except_osv(_('Error :'), _("The filename '%s' is not an absolute path nor a relative path that can be accessed from the addons directory.") % transfo.filename)

        else:
            file_temp = base64.decodestring(transfo.file)
            filename = cr.dbname + '_' + str(config['xmlrpc_port']) + '_' + str(context['default_res_id']) + '_' + str(task.id) + '_' + '_DATE_' + context['start_date'].replace(' ', '_') + os.path.split(transfo.filename)[1]
            path_to_file = os.path.join(kettle_dir, 'openerp_tmp', filename)
            file_temp_fd = open(path_to_file, 'w')
            try:
                file_temp_fd.write(file_temp)
            except Exception, e:
                logger.notifyChannel('kettle-connector', netsvc.LOG_WARNING, "Can't write Kettle job/transformation '%s' in temporary file '%s'" % (transfo.name, path_to_file))
                logger.notifyChannel('kettle-connector', netsvc.LOG_WARNING, str(e))
                raise osv.except_osv(_('Error :'), _("Can't write Kettle job/transformation '%s' in temporary file '%s'" % (transfo.name, path_to_file)))
            finally:
                file_temp_fd.close()


        if task.server_id.url:
            return self.start_carte_execution(cr, uid, [task.id], transfo, log_file_name, attachment_id, kettle_dir, path_to_file, parameters, context)


        #else it's a command line based execution:
        cmd_params = ''
        if parameters:
            for key, value in parameters.items():
                cmd_params += u' -param:' + key + u'=' + value

        if transfo.type == 'kjb':
            kettle_exec = u'kitchen.sh'
        else:
            kettle_exec = u'pan.sh'

        logfilename = os.path.join(kettle_dir, 'openerp_tmp', log_file_name)
        logger.notifyChannel('kettle-connector', netsvc.LOG_INFO, "Starting Kettle task : you can open Kettle logs with 'tail -f %s'" % logfilename)
        # We need to 'cd' to the install dir of Kettle until PDI 4.1.1
        # cf http://jira.pentaho.com/browse/PDI-5076
        cmd = u'cd ' + kettle_dir + u'; nohup sh ' + kettle_exec + u" -file=" + path_to_file + cmd_params  + u" > " + logfilename + u" 2>&1"

        os_result = os.system(cmd.encode(sys.stdout.encoding or 'UTF-8', 'replace'))

        if os_result != 0:
            prefixe_log_name = "[ERROR]"
        else:
            note = self.pool.get('ir.attachment').read(cr, uid, attachment_id, ['description'], context)['description']
            if note and 'WARNING' in note:
                prefixe_log_name = "[WARNING]"
            else:
                prefixe_log_name = "[SUCCESS]"

        self.pool.get('ir.attachment').write(cr, uid, [attachment_id], {'datas': base64.encodestring(open(logfilename, 'rb').read()), 'datas_fname': 'Task.log', 'name' : prefixe_log_name + 'TASK_LOG_'+context['start_date']}, context)
        cr.commit()
        os.remove(logfilename)
        if os_result != 0:
            self.error_wizard(cr, uid, attachment_id, context)
        logger.notifyChannel('kettle-connector', netsvc.LOG_INFO, "Kettle task successfully executed")
        return True


    def start_carte_execution(self, cr, uid, ids, transfo, log_file_name, attachment_id, kettle_dir, path_to_file, parameters, context=None):
        logger = netsvc.Logger()
        for task in self.browse(cr, uid, ids):
            logger.notifyChannel('kettle-connector', netsvc.LOG_INFO, "Assuming a Carte Kettle server execution")
            username = task.server_id.user or 'cluster'
            password = task.server_id.password or 'cluster'
            base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
            conn = httplib.HTTPConnection(task.server_id.url.replace('http://', ''))

            carte_id = task.carte_id
            file_type = task.transformation_id.type
            encoded_name = urllib.urlencode({'key': task.transformation_id.name}).replace('key=', '')

            if context.get('restart_carte', False) and not context.get('tried_restarting_carte', False):
                logger.notifyChannel('kettle-connector', netsvc.LOG_INFO, "Trying to restart the Carte server...")
                args = ['sh', 'carte.sh', '127.0.0.1', '8080']
                p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=kettle_dir)
                time.sleep(6)
                context.update({'tried_restarting_carte': True})

            try:
                #FIXME we force a flush due to what seems to be a Kettle bug
                if carte_id and file_type == 'job':
                    headers = {"Content-type": "text/xml;charset=UTF-8", "Authorization": "Basic %s" % base64string}
                    conn.request("GET", str("%s/kettle/removeJob/?name=%s&xml=Y&id=%s" % (task.server_id.url, task.transformation_id.name, carte_id,)), "", headers)
                    conn.close()
                    carte_id == False
                
                if context.get('force_upload', False) or not carte_id:

                    logger.notifyChannel('kettle-connector', netsvc.LOG_INFO, "uploading job %s to Carte" % task.transformation_id.name)

                    if zipfile.is_zipfile(path_to_file):
                        zin = zipfile.ZipFile(path_to_file, "a" )
                        file_tuples = [(item.filename, zin.read(item.filename)) for item in zin.infolist()]
                        zin.close()
                    else:
                        file = open(path_to_file, "r")
                        file_tuples = [(path_to_file.split("/")[-1], file.read())]
                       
                    #we will here fix a few things in the Kettle trans or job XML files, like file paths
                    job_files = []
                    trans_files = []
                    trans_name_candidate = False
                    job_name_candidate = False
                    zout = zipfile.ZipFile(path_to_file + '_hacked', 'w', zipfile.ZIP_DEFLATED)
                    #TODO use an in-memory zip file, see http://www.kompato.com/in-memory-zip-in-python
                    for file_tuple in file_tuples:
                        filename = file_tuple[0]
                        buffer = file_tuple[1]
                        doc = etree.fromstring(buffer)

                        extension = os.path.splitext(filename.lower())[1]
                        if extension == '.ktr':
                           trans_files.append(filename)
                           trans_name_candidate = doc.xpath("//transformation/info/name")[0].text


                           pg_connection = self.kettle_pg_connection(cr, uid, task.id, context)
                           if pg_connection:
                               if len(doc.xpath("//transformation/info/log")) != 0:
                                   for log_node in doc.xpath("//transformation/info/log"):
                                       doc.xpath("//transformation/info")[0].remove(log_node)
                               if len(doc.xpath("//transformation/info/log")) == 0:
                                   info_node = doc.xpath("//transformation/info")[0]
                                   info_node.append(etree.fromstring(self.kettle_tranfo_logs(cr, uid, task.id, context)))

#                               if len(doc.xpath("//transformation/connection")) != 0:#FIXME remove connection only if same name as the logging one
#                                   doc.xpath("//transformation")[0].remove(doc.xpath("//transformation/connection")[0])
                               transfo_node = doc.xpath("//transformation")[0]
                               transfo_node.append(etree.fromstring(pg_connection))


                        elif extension == '.kjb':
                           job_files.append(filename)
                           job_name_candidate = doc.xpath("//job/name")[0].text

                           pg_connection = self.kettle_pg_connection(cr, uid, task.id, context)
                           if pg_connection:
                               if len(doc.xpath("//job/job-log-table")) != 0:
                                   doc.xpath("//job")[0].remove(doc.xpath("//job/job-log-table")[0])
                               if len(doc.xpath("//job/job-log-table")) == 0:
                                   job_node = doc.xpath("//job")[0]
                                   job_node.append(etree.fromstring(self.kettle_job_logs(cr, uid, task.id, context)))

                               job_node = doc.xpath("//job")[0]
                               job_node.append(etree.fromstring(pg_connection))

                        l = doc.xpath("//*/file/name")
                        for e in l:
                            if False:#"DATA_PATH_" in e.text: #when creating an export, Spoon probably made the file paths relative to local installation...
                                for x in e.getparent().getparent().iterchildren():
                                    if x.tag == 'type':
                                        if 'out' in x.text or 'Out' in x.text or 'OUT' in x.text:
                                            e.text = '${file_out}'
                                            break
                                        elif 'in' in x.text or 'In' in x.text or 'IN' in x.text:
                                            e.text = '${file_in_nodate}'
                                            break

                        #print etree.tostring(doc)
                        zout.writestr(filename, etree.tostring(doc))
#                    zin.close()

                    #heuristic to detect if it's a job or a transformation (and correct possible errors):
                    trans_name = False
                    job_name = False
                    if len(trans_files) == 1 and len(job_files) == 0:
                        file_type = 'trans'
                        file_name = trans_files[0]
                        trans_name = trans_name_candidate
                    elif len(job_files) == 1:
                        file_type = 'job'
                        file_name = job_files[0]
                        job_name = job_name_candidate
                    elif len(transfo.filename) > 4 and transfo.filename[-3:].lower() == 'kjb': #TODO refactor with previous kettle_exec detection
                        file_type = 'job'
                        file_name = transfo.filename
                        job_name = transfo.name
                    else:
                        file_type = 'trans'
                        file_name = transfo.filename
                        trans_name = transfo.name


                    self.pool.get('kettle.transformation').write(cr, uid, [transfo.id], {'type': file_type, 'file_name': file_name, 'name': job_name or trans_name})
                    encoded_name = urllib.urlencode({'key': job_name or trans_name}).replace('key=', '')


                    #create the Kettle execution configuration file and add it to the zip:
                    if file_type == 'job':
                        zout.writestr("__job_execution_configuration__.xml", self.job_execution_configuration(cr, uid, id, job_name, parameters, context))
                    else:
                        zout.writestr("__job_execution_configuration__.xml", self.transfo_execution_configuration(cr, uid, id, trans_name, parameters, context))
                    zout.close()

                                        

                    #upload the zip execution archive to Carte:
                    f = open(path_to_file + '_hacked', 'rb')
                    params = f.read()
                    headers = {"Content-Type": "binary/zip", "Authorization": "Basic %s" % base64string}

                    if file_type == 'job':
                        conn.request("POST", str("%s/kettle/addExport/?type=job&load=%s" % (task.server_id.url, file_name)), params, headers)
                    else:
                        print str("%s/kettle/addExport/?type=trans&load=%s" % (task.server_id.url, encoded_name)), type(params)
                        conn.request("POST", str("%s/kettle/addExport/?type=trans&load=%s" % (task.server_id.url, file_name)), params, headers)

                    response = conn.getresponse()
                    data = response.read()
                    print "data", data
                    xml = etree.fromstring(data)
                    carte_id = xml.xpath("//id")[0].text
                    self.write(cr, uid, task.id, {'carte_id': carte_id})
                    conn.close()



                #prepare and execute the job or transformation:
                headers = {"Content-type": "text/xml;charset=UTF-8", "Authorization": "Basic %s" % base64string}
                if file_type == 'job':
                    logger.notifyChannel('kettle-connector', netsvc.LOG_INFO, "Starting %s job execution on Carte server" % task.transformation_id.name)
                    conn.request("GET", str("%s/kettle/startJob/?name=%s&xml=Y&id=%s" % (task.server_id.url, encoded_name, carte_id,)), "", headers)
                else: # it's a task
                    print str("%s/kettle/prepareExec/?name=%s&xml=Y&id=%s" % (task.server_id.url, encoded_name, carte_id,))
                    logger.notifyChannel('kettle-connector', netsvc.LOG_INFO, "Starting %s transformation execution on Carte server" % task.transformation_id.name)
                    conn.request("GET", str("%s/kettle/prepareExec/?name=%s&xml=Y&id=%s" % (task.server_id.url, encoded_name, carte_id,)), "", headers)
                    response = conn.getresponse()
                    data = response.read()
                    print "response", response
                    print "data", data
                    conn.close()
                    conn.request("GET", str("%s/kettle/startExec/?name=%s&xml=Y&id=%s" % (task.server_id.url, encoded_name, carte_id,)), "", headers)
                response = conn.getresponse()
                print "response", response
                data = response.read()
                print "data", data
                conn.close()
                if 'could not be found' in data: #hacky way to detect the job/transfo has not been found on the server
                     self.write(cr, uid, task.id, {'carte_id': False})
                     context.update({'force_upload': True})
                     return self.run_kettle_task(cr, uid, task, parameters, log_file_name, attachment_id, context)

            except socket.error as e:
                if not context.get('restart_carte', False):
                    context.update({'restart_carte': True})
                    return self.run_kettle_task(cr, uid, task, parameters, log_file_name, attachment_id, context)

            return True


    def start_kettle_task(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        logger = netsvc.Logger()
        user = self.pool.get('res.users').browse(cr, uid, uid, context)
        for task in self.browse(cr, uid, ids, context=context):
            context.update({'default_res_id' : task.id, 'default_res_model': 'kettle.task', 'start_date' : time.strftime('%Y-%m-%d_%H:%M:%S')})
            log_file_name = 'TASK_LOG_ID' + str(task.id) + '_DATE_' + context['start_date'].replace(' ', '_') + ".log"
            attachment_id = self.pool.get('ir.attachment').create(cr, uid, {'name': log_file_name}, context)
            cr.commit()

            parameters = {}
            parameters['oerp_db'] = cr.dbname
            parameters['oerp_user'] = user.login
            parameters['oerp_pwd'] = user.password
            parameters['oerp_host'] = 'localhost'
            parameters['oerp_port'] = str(config['xmlrpc_port'])

            parameters['kettle_task_id'] = str(task.id)
            parameters['task_attachment_id'] = str(attachment_id)

            parameters['kettle_dir'] = task.server_id.kettle_dir
            context['kettle_dir'] = task.server_id.kettle_dir
            parameters['gempath'] = os.path.join(task.server_id.kettle_dir, 'plugins', 'steps', 'Ruby', 'gems')

            parameters['file_path'] = os.path.join(task.server_id.kettle_dir, 'openerp_tmp')
            for i in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10): #to comply with relative path in trans/jobs exports, see http://www.ibridge.be/?p=159
                parameters["DATA_PATH_%s" % (i,)] = parameters['file_path']

            parameters['file_path'] = os.path.join(task.server_id.kettle_dir, 'openerp_tmp')
            parameters['file_name'] = os.path.join('out_' + task.name + context['start_date'])
            parameters['file_name_nodate'] = os.path.join('out_' + task.name)
            parameters['file_out'] = os.path.join(parameters['file_path'], parameters['file_name'])

            if task.last_date:
                parameters['last_date'] = task.last_date

            if task.upload_file:
                if not (context and context.get('input_filename', False)):
                    logger.notifyChannel('kettle-connector', netsvc.LOG_INFO, "The task %s can't be executed because the anyone File was uploaded" % task.name)
                    continue
                else:
                    parameters['file_in'] = context['input_filename']
                    parameters['file_in_nodate'] = os.path.join(parameters['file_path'], 'in_' + task.name)
                #TODO make that work with DATA_PATH

            context = self.execute_python_code(cr, uid, task.id, 'before', context)

            # Add the params defined on the task. Note that it may override default params
            # defined above
            for parameter in task.parameter_ids:
                if parameter.value:
                    parameters[parameter.name] = parameter.value

            if context.get('input_filename', False):
                shutil.copyfile(context['input_filename'], os.path.join(parameters['file_path'], 'in_' + task.name + context['start_date']))
                shutil.copyfile(context['input_filename'], parameters['file_in_nodate'])
                if not task.carte_id:
                    self.attach_file_to_task(cr, uid, task.id, context['input_filename'], '[FILE IN] FILE IMPORTED ' + context['start_date'], True, context=context)

            self.run_kettle_task(cr, uid, task, parameters, log_file_name, attachment_id, context)

            context = self.execute_python_code(cr, uid, task.id, 'after', context)

            if task['output_file'] and not task.server_id.url:#not task.carte_id:
                self.attach_output_file_to_task(cr, uid, task.id, parameters['file_out'], '[FILE OUT] FILE IMPORTED ' + context['start_date'], True, context=context)

            self.write(cr, uid, [task.id], {'last_date' : context['start_date']})
        return True

kettle_task()


class kettle_parameter(osv.osv):
    _name = "kettle.parameter"
    _description = "Kettle parameters"

    _columns = {
        'task_id': fields.many2one('kettle.task', 'Task'),
        'name': fields.char('Name', size=128, required="True", help="Name of the parameter"),
        'value': fields.char('Value', size=256, help="Value of the parameter."),
        'user_id': fields.many2one('res.users', 'User', help="Only visible for this user. This can be usefull for password fields."),
        }

kettle_parameter()


class kettle_wizard(osv.osv_memory):
    _name = 'kettle.wizard'
    _description = 'kettle wizard'

    _columns = {
        'upload_file': fields.boolean("Upload file?"),
        'file': fields.binary('File'),
        'filename': fields.char('Filename', size=64),
    }

    def _get_add_file(self, cr, uid, context):
        return self.pool.get('kettle.task').read(cr, uid, context['active_id'], ['upload_file'])['upload_file']

    _defaults = {
        'upload_file': _get_add_file,
    }

    def _save_file(self, cr, uid, id, vals, context):
        # TODO : the "id" argument is never used !
        kettle_dir = self.pool.get('kettle.task').browse(cr, uid, context['active_id'], context).server_id.kettle_dir
        filename = os.path.join(kettle_dir, 'openerp_tmp', vals['filename'])
        fp = open(filename,'wb+')
        fp.write(base64.decodestring(vals['file']))
        fp.close()
        return filename#os.path.join('openerp_tmp', vals['filename'])

    def action_start_task(self, cr, uid, id, context):
        wizard = self.read(cr, uid, id,context=context)[0]
        if wizard['upload_file']:
            if not wizard['file']:
                raise osv.except_osv('Error !', 'You have to select a file before starting the task')
            else:
                context['input_filename'] = self._save_file(cr, uid, id, wizard, context)
        self.pool.get('kettle.task').start_kettle_task(cr, uid, [context['active_id']], context)
        return {'type': 'ir.actions.act_window_close'}

kettle_wizard()
