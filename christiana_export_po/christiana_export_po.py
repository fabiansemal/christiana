# -*- encoding: utf-8 -*-

from mx import DateTime
import time
from datetime import datetime
import base64

from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _

class export_purchase_order(osv.osv_memory):
#     _inherit = 'purchase.order'
	""" Export purchase order """
	_name = "export.purchase.order"
	_description = "Export purchase order"

	def _get_filename(self, cr, uid, context=None):
		print "DEFAULT CONTEXT:",context
		if context.get('active_id', False):
			po = self.pool.get('purchase.order').browse(cr, uid, context['active_id'])
			fname = po.name.lower()
			if po.partner_id.name == 'CB':
				ftype = '.opd'
			else:
				ftype = '.csv'
			return fname + ftype
		return ''
    
	def _get_filedata(self, cr, uid, context=None):
		if context.get('filedata', False):
			return base64.encodestring(context['filedata'].encode('utf8'))
		return ''
    
	_columns = {
		'filename': fields.char('File Name', size=32),
		'msg': fields.text('File created', size=64, readonly=True),
		'filedata': fields.binary('Save File'),
	}

	_defaults = {
		'msg': 'Save the File.',
		'filedata': _get_filedata,
		'filename': _get_filename,
	}
    
	def create_file(self, cr, uid, ids, context=None):
		this = self.browse(cr, uid, ids)[0]

		obj_purchase_order = self.pool.get('purchase.order')
		mod_obj = self.pool.get('ir.model.data')

		po = obj_purchase_order.browse(cr, uid, context['active_id'])

		if context is None:
			context = {}
		print "CONTEXT:",context
#         data  = self.read(cr, uid, ids)[0]
        
		if po.partner_id.name == 'CB':
			type = 'CB'
		else:
			type = 'BB'
        
		fname = po.name.lower()
		if po.partner_id.name == 'CB':
			ftype = '.opd'
		else:
			ftype = '.csv'

		if type == 'CB':
			filedata = {
				'po_name': po.name,
				'id_christiana': '9522060',
				'id_cb': '8894126',
				'opdr_dat': datetime.now().strftime('%Y%m%d'),
			}
			data_of_file = """#00010#0002OPDNAW#00030301#0004%(opdr_dat)s#00051200#0006%(po_name)s#00071#00080
#00011#0009AFZ#0010%(id_christiana)s#0011CB
#00011#0009ONTV#0010%(id_cb)s#0011CB
#00012#0400LNORM#0401%(opdr_dat)s#0411N
#00013#0009AFN#0010%(id_christiana)s#0011CB""" % (filedata)
			count_lines = 0
			for lines in po.order_line:
				lines_data = {
					'isbn': lines.product_id.default_code,
					'aant': int(lines.product_qty),
					'po': po.name,
				}
				print lines_data
				data_of_file += '\n#00014#0200%(isbn)s#0430%(aant)s#0431DIO#0434J#0435J#0441%(po)s' % (lines_data)
				count_lines += 1
			counters = {'lines': str(int(count_lines)), 'po_name': po.name}
			data_of_file += '\n#00019#00151#00161#0017%(lines)s#00180#00190#0006%(po_name)s' % (counters)

		if type == 'BB':
			filedata = {
				'po_name': po.name,
				'id_christiana': '0874',
				'opdr_dat': datetime.now().strftime('%d/%m/%Y'),
			}
			data_of_file = ""
			counter = 0
			for lines in po.order_line:
				lines_data = {
					'po_name': po.name,
					'id_christiana': '0874',
					'opdr_dat': datetime.now().strftime('%d/%m/%Y'),
					'isbn': lines.product_id.default_code,
					'aant': int(lines.product_qty),
				}
				if counter != 0:
					data_of_file += '\n'
				data_of_file += '"%(id_christiana)s";"%(opdr_dat)s";"";"";"";"%(isbn)s";%(aant)s;"G";"";"%(po_name)s";"";0;""' % (lines_data)
# laatste veld (na ;): wat met voorkeursdistributeur?
				counter += 1

		print 'BEFORE OUT'
		out = base64.encodestring(data_of_file.encode('utf8'))
		print 'AFTER OUT'
		this.name = "%s%s" % (fname, ftype)
		self.write(cr, uid, ids, {'filedata': out, 'filename': fname + ftype}, context=context)

		model_data_ids = mod_obj.search(cr, uid, [('model', '=', 'ir.ui.view'), ('name', '=', 'view_purch_order_save')], context=context)
		resource_id = mod_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
		context['filedata'] = data_of_file
		context['filename'] = fname + ftype
		print 'CONTEXT:',context
#	print data_of_file
#	print fname + ftype
#	file_ = open(fname + ftype, 'w')
#	file_.write(data_of_file)
#	file_.close()

		return {
			'name': _('Save purchase order file'),
			'context': context,
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'export.purchase.order',
			'res_id': this.id,
			'views': [(resource_id, 'form')],
			'view_id': 'view_purch_order_save',
			'type': 'ir.actions.act_window',
			'target': 'new',
		}

export_purchase_order()



