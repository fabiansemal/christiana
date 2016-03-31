# -*- encoding: utf-8 -*-

# from mx import DateTime
# import time

from datetime import date
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
# from gdata.apps.organization.data import CUSTOMER_ID

class stock_scan_current(osv.osv):
	_name = "stock.scan.current"

	_columns = {
		'isbn': fields.char('ISBN'),
	}

stock_scan_current()

class stock_scan(osv.osv):
	_name = "stock.scan"
	_order = "id desc"

	_columns = {
		'name': fields.char('Pakbon'),
		'partner_id': fields.many2one('res.partner', 'Geleverd door', select=True),
		'line_ids': fields.one2many('stock.scan.line', 'scan_id', 'Ontvangsten'),
		'date_created': fields.date('Datum Ontvangst'),
		'state': fields.selection([['draft','Draft'],['done','Verwerkt']],'Status',readonly=True,track_visibility='onchange'),
		'zichtzending': fields.boolean('Zichtzending'),
		'delnote_supplier': fields.char('Pakbonnr. Leverancier', select=True),
	}

	_defaults={
		'date_created': date.today(), #.strftime('%Y-%m-%d'),
		'state': 'draft',
		'zichtzending': False,
	}

	def create(self, cr, uid, vals, context=None):
		"""Add the np sequence reference"""
		seq_id = self.pool.get('ir.sequence').search(cr, uid, [('name','=','stock.scan')])
		vals['name'] = self.pool.get('ir.sequence').next_by_id(cr, uid, seq_id, context)
		vals['date_created'] = date.today().strftime('%Y-%m-%d')
		res = super(stock_scan, self).create(cr, uid, vals, context=context)
		sql_stat = "delete from stock_scan_current"
		cr.execute(sql_stat)
		return res

	def write(self, cr, uid, ids, vals, context=None):
		res = super(stock_scan, self).write(cr, uid, ids, vals, context=context)
		sql_stat = "delete from stock_scan_current"
		cr.execute(sql_stat)
		return res

	def action_load(self, cr, uid, ids, context=None):
		sql_stat = "delete from stock_scan_current"
		cr.execute(sql_stat)
		cr.commit()
		for ss in self.browse(cr, uid, ids, context=context):
			for ssl in ss.line_ids:
				sql_stat = "insert into stock_scan_current (isbn) values ('%s')" % (ssl.name, )
				cr.execute(sql_stat)
				cr.commit()
		return True
				
	def action_confirm(self, cr, uid, ids, context=None):
# PROCESS PO RECEIPTS
# 		print 'RECEIPT'
		for ss in self.browse(cr, uid, ids, context=context):
			if ss.state != 'draft':
				raise osv.except_osv(('Fout !'),_('Deze ontvangst is reeds verwerkt'))
				return

			for ssl in ss.line_ids: 
				if ssl.po_line_ids:
					for sslp in ssl.po_line_ids:
						if sslp.qty_scan > 0:
# 							print 'CREATE PARTIAL MOVE: ',sslp.po_line_id.product_id.default_code
							pm = self.pool.get('stock.partial.move')
							pm_id = pm.create(cr, uid, {
								'date': date.today(),
							},context=context)
							mv_id = 0
							if sslp.po_line_id:
								sql_stat = "select id from stock_move where purchase_line_id = %d and state in ('assigned','confirmed')" % (sslp.po_line_id.id, )
								cr.execute(sql_stat)
								for sql_res in cr.dictfetchall():
									mv_id = sql_res['id']
									pm_line = pm.browse(cr, uid, pm_id)
									pml = self.pool.get('stock.partial.move.line')
									if sslp.product_id.product_tmpl_id.uom_id:
										uom_id = sslp.product_id.product_tmpl_id.uom_id.id
									else:
										uom_id = 1
									pml_id = pml.create(cr, uid, {
										'update_cost': False,
										'product_id': sslp.product_id.id,
										'product_uom': uom_id,
										'wizard_id': pm_line.id,
										'location_dest_id': 12,
										'location_id': 8,
										'move_id': mv_id,
										'quantity': sslp.qty_scan,
									},context=context)
# 									print 'DO PARTIAL'
									pm_rec = pm.do_partial(cr, uid, [pm_line.id], context=context)

# 		print 'CHANGE STATUS'
# 		self.write(cr, uid, ids, {'state': 'done'})

# PROCESS SO RESERVATION
# 		print 'RESERVATION'
		for ss in self.browse(cr, uid, ids, context=context):
			old_customer_id = 0
			sql_stat = '''
select stock_scan_line.name, stock_scan_line_so.product_id, stock_scan_line_so.so_line_id, stock_scan_line_so.so_id, stock_scan_line_so.partner_id as customer_id, partner_shipping_id, stock_scan_line_so.qty_scan as qty_to_deliver, stock_scan_line_so.so_price, stock_scan_line_so.so_discount, sale_order.zichtzending, stock_scan_line.combined_vat, stock_scan_line.vat06, stock_scan_line.vat21, awso_code
from stock_scan_line, stock_scan_line_so, sale_order 
where scan_id = %d 
  and scan_line_id = stock_scan_line.id 
  and stock_scan_line_so.qty_scan > 0 
  and sale_order.id = stock_scan_line_so.so_id 
group by customer_id, stock_scan_line_so.product_id, stock_scan_line_so.name, stock_scan_line_so.so_line_id, stock_scan_line_so.so_id, stock_scan_line_so.so_price, stock_scan_line_so.so_discount, sale_order.zichtzending, stock_scan_line_so.qty_scan, partner_shipping_id, stock_scan_line.name, stock_scan_line.combined_vat, stock_scan_line.vat06, stock_scan_line.vat21, awso_code
order by customer_id, stock_scan_line_so.product_id''' % (ss.id, )
# 			print 'SQL STAT:',sql_stat
			cr.execute(sql_stat)
			for sql_res in cr.dictfetchall():
				name = sql_res['name']
				product_id = sql_res['product_id']
				so_line_id = sql_res['so_line_id']
				so_id = sql_res['so_id']
				customer_id = sql_res['customer_id']
				qty_to_deliver = sql_res['qty_to_deliver']
				so_price = sql_res['so_price']
				so_discount = sql_res['so_discount']
				zichtzending = sql_res['zichtzending']
				scan_id = ss.id
				partner_shipping_id = sql_res['partner_shipping_id']
				combined_vat = sql_res['combined_vat']
				vat06 = sql_res['vat06']
				vat21 = sql_res['vat21']
				awso_code = sql_res['awso_code']

# 				print 'OLD CUSTOMER:', old_customer_id
# 				print 'CUSTOMER:', customer_id
		
				if old_customer_id != customer_id:
					old_customer_id = customer_id
					sr_line_id = 0
					if zichtzending:
						sql_stat = "select id from stock_reservation where partner_id = %d and state = 'draft' and zichtzending = True" % (customer_id, )
					else:
						sql_stat = "select id from stock_reservation where partner_id = %d and state = 'draft' and zichtzending = False" % (customer_id, )
					cr.execute(sql_stat)
					for sql_res in cr.dictfetchall():
						sr_line_id = sql_res['id']
					if sr_line_id == 0:
# 						print 'CREATE STOCK RESERVATION'
						sr = self.pool.get('stock.reservation')
						sr_id = sr.create(cr, uid, {
							'name': ('Levering'),
							'date_created': date.today(),
							'partner_id': customer_id,
							'partner_shipping_id': partner_shipping_id,
							'state': 'draft',
							'scan_id': scan_id,
							'zichtzending': zichtzending,
						}, context=context)
						sr_line = sr.browse(cr, uid, sr_id)
						sr_line_id = sr_line.id

				sql_stat = "select id from stock_move where sale_line_id = %d" % (so_line_id, )
# 				print 'SQL:',sql_stat
				cr.execute(sql_stat)
				for sql_res in cr.dictfetchall():
					mv_id = sql_res['id']

				line_id = 0
				qty_del = 0.00
				sql_stat = "select id, qty_to_deliver from stock_reservation_line where product_id = %d and reservation_id = %d and so_line_id = %d" % (product_id, sr_line_id, so_line_id, )
				cr.execute(sql_stat)
				for sql_res in cr.dictfetchall():
					line_id = sql_res['id']
					qty_del = sql_res['qty_to_deliver']

				srl = self.pool.get('stock.reservation.line')
				if line_id == 0:
# 					print 'CREATE STOCK RESERVATION LINE', name, sr_line_id
					srl_id = srl.create(cr, uid, {
						'name': name,
						'reservation_id': sr_line_id,
						'product_id': product_id,
						'so_line_id': so_line_id,
						'so_id': so_id,
						'customer_id': customer_id,
						'qty_to_deliver': qty_to_deliver,
						'so_price': so_price,
						'so_discount': so_discount,
						'zichtzending': zichtzending,
						'move_id': mv_id,
# 						'scan_procedure': True,
						'combined_vat': combined_vat,
						'vat06': vat06,
						'vat21': vat21,
						'awso_code': awso_code,
					}, context=context)
				else:
					qty_del = qty_del + qty_to_deliver
					srl.write(cr, uid, [line_id], {'qty_to_deliver': qty_del}, context=context)
# 					sql_stat = 'update stock_reservation_line set qty_to_deliver = %d where id = %d' % (qty_del, line_id, )
# 					cr.execute(sql_stat)

# 		print 'CHANGE STATUS'
		return self.write(cr, uid, ids, {'state': 'done'})

stock_scan()

class stock_scan_line(osv.osv):
	_name = "stock.scan.line"

	_columns = {
		'name': fields.char('Barcode', required=True),
		'scan_id': fields.many2one('stock.scan', 'Pakbon'),
		'product_id': fields.many2one('product.product', 'Product'),
		'so_line_id': fields.many2one('sale.order.line', 'Verkooplijn'),
		'po_line_id': fields.many2one('purchase.order.line', 'Aankooplijn'),
		'so_id': fields.many2one('sale.order', 'Verkooporder', readonly=True),
		'po_id': fields.many2one('purchase.order', 'Aankooporder', readonly=True),
		'customer_id': fields.related('so_id', 'partner_id', type='many2one', relation='res.partner', string='Klant', readonly=True),
		'qty_received': fields.float('Hoev.'),
		'so_price': fields.float('Verkoopprijs'),
		'so_discount': fields.float('Korting'),
		'zichtzending': fields.boolean('Zichtzending'),
		'zichtzending_po': fields.related('po_id', 'zichtzending', string='Zichtzending Aankoop', type='boolean'),
		'po_line_ids': fields.one2many('stock.scan.line.po', 'scan_line_id', 'Aankooporders'),
		'so_line_ids': fields.one2many('stock.scan.line.so', 'scan_line_id', 'Verkooporders'),
		'retrieve_lines': fields.boolean('Lijnen Ophalen'),
		'combined_vat': fields.boolean('Gecombineerde BTW'),
		'vat06': fields.float('Bedrag BTW 6%'),
		'vat21': fields.float('Bedrag BTW 21%'),
		'awso_code': fields.selection((('A','Algemeen'),('W','Wetenschappelijk'),('S','Studie'),('O','Overige')),'AWSO Code'),
		'vat': fields.char('BTW %'),
	}

	_sql_constraints = [('name_uniq','unique(name,scan_id)','Dubbele barcode in deze pakbon'),]
	
	def onchange_awso_code(self, cr, uid, ids, awso_code, so_line_ids, context=None):
		res = {}
		if awso_code and so_line_ids:
# 			print 'so line ids:', so_line_ids
			so_line_ids_list = []
			for soline in so_line_ids:
# 				print 'soline:', soline[1]
				so_line_ids_list.append(soline[1])
				sql_stat = 'select partner_id from stock_scan_line_so where id = %d' % (soline[1], )
				cr.execute(sql_stat)
				for sql_res in cr.dictfetchall():
					sql_stat = "select discount_pct from res_partner_discount where partner_id = %d and awso_code = '%s'" % (sql_res['partner_id'], awso_code, )
# 					print sql_stat
					cr.execute(sql_stat)
					for sql_res in cr.dictfetchall():
						sql_stat = "update stock_scan_line_so set so_discount = %d where id = %d" % (sql_res['discount_pct'], soline[1], )
						cr.execute(sql_stat)
# 						print sql_stat
			res['so_line_ids'] = so_line_ids_list			
#			for ssl in self.browse(cr, uid, ids, context=context):
#				if ssl.so_line_ids:
#					for sol in ssl.so_line_ids:
#						so_line_ids.append(sol.id)
#						sql_stat = "select discount_pct from res_partner_discount where partner_id = %d and awso_code = '%s'" % (sol.partner_id.id, awso_code, )
#						print sql_stat
#						cr.execute(sql_stat)
#						for sql_res in cr.dictfetchall():
#							sql_stat = "update stock_scan_line_so set so_discount = %d where id = %d" % (sql_res['discount_pct'], sol.id, )
#							cr.execute(sql_stat)
#							print sql_stat
#					res['so_line_ids'] = so_line_ids
		return {'value':res}

	def onchange_barcode(self, cr, uid, ids, name, context=None):
		res = {}
		isbn_found = False

		if name:
			sql_stat = "select isbn from stock_scan_current where isbn = '%s'" % (name, )
			cr.execute(sql_stat)
			sql_res = cr.dictfetchone()
			if sql_res:
				raise osv.except_osv(('Waarschuwing !'),_(('Boek met ISBN barcode %s is reeds gescanned in deze scan-procedure') % (name, )))
				return {'value':res}
			else:
				sql_stat = "insert into stock_scan_current (isbn) values ('%s')" % (name, )
				cr.execute(sql_stat)
				cr.commit()

		if name:
			sql_stat = "select id, awso_code, combined_vat from product_product where default_code = '%s'" % (name, )
			cr.execute(sql_stat)
			for sql_res in cr.dictfetchall():
				isbn_found = True
				product_id = sql_res['id']
				awso_code = sql_res['awso_code']
				combined_vat = sql_res['combined_vat']
				res['product_id'] = product_id
				res['awso_code'] = awso_code
				res['combined_vat'] = combined_vat
				res['qty_received'] = 1
			sql_stat = '''select tax_id from product_taxes_rel, product_product
where default_code = '%s' and product_tmpl_id = prod_id''' % (name, )
			cr.execute(sql_stat)
			for sql_res in cr.dictfetchall():
				if sql_res['tax_id'] == 2:
					res['vat'] = '21'
				else:
					res['vat'] = '6'

		if name and not isbn_found:
			raise osv.except_osv(('Waarschuwing !'),_(('Boek met ISBN barcode %s bestaat niet in de data base') % (name, )))

		return {'value':res}

	def onchange_qty(self, cr, uid, ids, product_id, qty_received, zichtzending, context=None):
		res = {}
		po_found = False
		so_found = False
		po_line_ids = []
		so_line_ids = []
		qty_error = False

		if product_id:
			sql_stat = '''
select sum (product_qty) as qty_to_receive 
from purchase_order_line, purchase_order 
where order_id = purchase_order.id 
  and product_id = %d and purchase_order_line.state = 'confirmed' 
  and purchase_order.zichtzending = %s''' % (product_id, zichtzending, )
			cr.execute(sql_stat)
			for sql_res in cr.dictfetchall():
				if sql_res['qty_to_receive'] < qty_received:
					raise osv.except_osv(('Waarschuwing !'),_('Grotere hoeveelheid ontvangen dan openstaande aankooporders'))

			qty_rec_scan = qty_received
			if qty_rec_scan > 0:
				sql_stat = '''
select purchase_order_line.id, order_id, purchase_order.zichtzending, product_qty, date_planned, purchase_order.partner_id, 
(select sum(qty_scan) from stock_scan_line_po where po_line_id = purchase_order_line.id and not(scan_line_id IS NULL)) as qty_scanned 
from purchase_order_line, purchase_order 
where order_id = purchase_order.id 
  and product_id = %d and purchase_order_line.state = 'confirmed' 
  and purchase_order.zichtzending = %s 
order by date_planned''' % (product_id, zichtzending, )
				cr.execute(sql_stat)
				for sql_res in cr.dictfetchall():
					po_found = True
					po_line_id = sql_res['id']
					po_id = sql_res['order_id']
					zz = sql_res['zichtzending']
					qty_ordered = sql_res['product_qty']
					qty_scanned = sql_res['qty_scanned']
					if qty_scanned and qty_ordered > qty_scanned:
						qty_to_scan = qty_ordered - qty_scanned
					else:
						if not qty_scanned:
							qty_to_scan = qty_ordered
						else:
							qty_to_scan = 0
					qty_scan = 0
					if qty_rec_scan < qty_to_scan:
						qty_scan = qty_rec_scan
						qty_rec_scan = 0
					else:
						qty_scan = qty_to_scan
						qty_rec_scan = qty_rec_scan - qty_to_scan
					date_planned = sql_res['date_planned']
					partner_id = sql_res['partner_id']

					if qty_to_scan > 0:
						vals = {
							'name': product_id,
							'product_id': product_id,
#							'scan_line_id': ,
							'po_line_id': po_line_id,
							'po_id': po_id,
							'qty_ordered': qty_ordered,
							'qty_scanned': qty_scanned,
							'qty_to_scan': qty_to_scan,
							'qty_scan': qty_scan,
							'date_planned': date_planned,
							'partner_id': partner_id,
							'zichtzending': zz,
						}
						sslp_id = self.pool.get('stock.scan.line.po').create(cr, uid, vals)
						po_line_ids.append(sslp_id)

			qty_rec_scan = qty_received
			if qty_rec_scan > 0:
				sql_stat = '''
select sale_order_line.id, order_id, sale_order.zichtzending, product_uom_qty as product_qty, sale_order_line.create_date as date_planned, sale_order.partner_id, sale_order_line.price_unit, sale_order_line.discount, 
(select sum(qty_scan) from stock_scan_line_so where so_line_id = sale_order_line.id and not(scan_line_id IS NULL)) as qty_scanned 
from sale_order_line, sale_order, stock_move 
where order_id = sale_order.id 
  and sale_order_line.product_id = %d 
  and sale_order_line.state = 'confirmed' 
  and sale_order.zichtzending = %s 
  and sale_order_line.id = stock_move.sale_line_id
  and not(stock_move.state in ('done','cancel'))
order by sale_order_line.create_date''' % (product_id, zichtzending, )
				cr.execute(sql_stat)
				for sql_res in cr.dictfetchall():
					so_found = True
					so_line_id = sql_res['id']
					so_id = sql_res['order_id']
					zichtzending = sql_res['zichtzending']
					qty_ordered = sql_res['product_qty']
					qty_reserved = sql_res['qty_scanned']
					if qty_reserved and qty_ordered > qty_reserved:
						qty_to_reserv = qty_ordered - qty_reserved
					else:
						if not qty_reserved:
							qty_to_reserv = qty_ordered
						else:
							qty_to_reserv = 0
					qty_scan = 0
					if qty_rec_scan < qty_to_reserv:
						qty_scan = qty_rec_scan
						qty_rec_scan = 0
					else:
						qty_scan = qty_to_reserv
						qty_rec_scan = qty_rec_scan - qty_to_reserv
					date_planned = sql_res['date_planned']
					partner_id = sql_res['partner_id']
					price_unit = sql_res['price_unit']
					discount = sql_res['discount']

					if qty_to_reserv > 0:
						vals = {
							'name': product_id,
							'product_id': product_id,
#							'scan_line_id': ,
							'so_line_id': so_line_id,
							'so_id': so_id,
							'qty_ordered': qty_ordered,
							'qty_reserved': qty_reserved,
							'qty_to_reserv': qty_to_reserv,
							'qty_scan': qty_scan,
							'date_planned': date_planned,
							'partner_id': partner_id,
							'zichtzending': zichtzending,
							'so_price': price_unit,
							'so_discount': discount
						}
						ssls_id = self.pool.get('stock.scan.line.so').create(cr, uid, vals)
						so_line_ids.append(ssls_id)

		res['po_line_ids'] = po_line_ids
		res['so_line_ids'] = so_line_ids

		return {'value':res}

	def create(self, cr, uid, vals, context=None):
# 		print 'CREATE SCAN LINE VALS:',vals
		
		if 'name' in vals:
			sql_stat = "select id from product_product where default_code = '%s'" % (vals['name'], )
			cr.execute(sql_stat)
			for sql_res in cr.dictfetchall():
				product_id = sql_res['id']
				vals['product_id'] = product_id
			sql_stat = '''select tax_id from product_taxes_rel, product_product
where default_code = '%s' and product_tmpl_id = prod_id''' % (vals['name'], )
			cr.execute(sql_stat)
			for sql_res in cr.dictfetchall():
				if sql_res['tax_id'] == 2:
					vals['vat'] = '21'
				else:
					vals['vat'] = '6'

		po_line_ids = vals['po_line_ids']
		so_line_ids = vals['so_line_ids']
		sumpo = 0.0
		sumso = 0.0
		if 'po_line_ids' in vals:
			po_line_ids = vals['po_line_ids']
			for pol in po_line_ids:
				if pol[2] == False:
					pol1 = self.pool.get('stock.scan.line.po').browse(cr, uid, pol[1], context=context)
					sumpo += pol1.qty_scan
				else:
					if 'qty_scan' in pol[2]:
						sumpo += pol[2]['qty_scan']
					else:
						pol1 = self.pool.get('stock.scan.line.po').browse(cr, uid, pol[1], context=context)
						sumpo += pol1.qty_scan
# 		else:
# 			for pol in ssl.po_line_ids:
# 				sumpo += pol.qty_scan
		if 'so_line_ids' in vals:
			so_line_ids = vals['so_line_ids']
			for sol in so_line_ids:
				if sol[2] == False:
					sol1 = self.pool.get('stock.scan.line.so').browse(cr, uid, sol[1], context=context)
					sumso += sol1.qty_scan
				else:
					if 'qty_scan' in sol[2]:
						sumso += sol[2]['qty_scan']
					else:
						sol1 = self.pool.get('stock.scan.line.so').browse(cr, uid, sol[1], context=context)
						sumso += sol1.qty_scan
# 		else:
# 			for sol in ssl.so_line_ids:
# 				sumso += sol.qty_scan
		if sumpo > vals['qty_received'] or sumso > vals['qty_received']:
			raise osv.except_osv(('Fout!'),_(('Te grote hoeveelheid op PO of SO voor %d') % (product_id )))
			return False			

		if sumpo < vals['qty_received']:
			raise osv.except_osv(('Fout!'),_(('Te kleine hoeveelheid op PO voor %d') % (product_id )))
			return False			

		res = super(stock_scan_line, self).create(cr, uid, vals, context=context)
		scan = self.browse(cr, uid, res)
		
# 		print 'PO LINE IDS:',po_line_ids
		for po in po_line_ids:
# 			print 'PO:',po
			sql_stat = "update stock_scan_line_po set scan_line_id = %d where id = %d" % (scan.id, po[1], )
# 			print sql_stat
			cr.execute(sql_stat)
# 		print 'SO LINE IDS:',scan.so_line_ids
		for so in so_line_ids:
			sql_stat = "update stock_scan_line_so set scan_line_id = %d where id = %d" % (scan.id, so[1], )
			cr.execute(sql_stat)
# 			print sql_stat
		return res

	def write(self, cr, uid, ids, vals, context=None):
# 		print "write stock_scan_line", ids, vals
		for id in ids:
			ssl = self.browse(cr, uid, id, context=context)
			lijnhoev = ssl.qty_received
			if 'qty_received' in vals:
				lijnhoev = vals['qty_received']
			sumpo = 0.0
			sumso = 0.0
			if 'po_line_ids' in vals:
				po_line_ids = vals['po_line_ids']
				for pol in po_line_ids:
					if pol[2] == False:
						pol1 = self.pool.get('stock.scan.line.po').browse(cr, uid, pol[1], context=context)
						sumpo += pol1.qty_scan
					else:
						if 'qty_scan' in pol[2]:
							sumpo += pol[2]['qty_scan']
						else:
							pol1 = self.pool.get('stock.scan.line.po').browse(cr, uid, pol[1], context=context)
							sumpo += pol1.qty_scan
			else:
				for pol in ssl.po_line_ids:
					sumpo += pol.qty_scan
			if 'so_line_ids' in vals:
				so_line_ids = vals['so_line_ids']
				for sol in so_line_ids:
					if sol[2] == False:
						sol1 = self.pool.get('stock.scan.line.so').browse(cr, uid, sol[1], context=context)
						sumso += sol1.qty_scan
					else:
						if 'qty_scan' in sol[2]:
							sumso += sol[2]['qty_scan']
						else:
							sol1 = self.pool.get('stock.scan.line.so').browse(cr, uid, sol[1], context=context)
							sumpo += sol1.qty_scan
			else:
				for sol in ssl.so_line_ids:
					sumso += sol.qty_scan
			if sumpo > lijnhoev or sumso > lijnhoev:
				raise osv.except_osv(('Fout!'),_(('Te grote hoeveelheid op PO of SO voor %d') % (ssl.product_id )))
				return False			
				
		return super(stock_scan_line, self).write(cr, uid, ids, vals, context=context)
		
stock_scan_line()

class stock_scan_line_po(osv.osv):
	_name = "stock.scan.line.po"

	_columns = {
		'name': fields.char('Barcode', required=True),
		'scan_line_id': fields.many2one('stock.scan.line', 'Pakbonlijn'),
		'product_id': fields.many2one('product.product', 'Product'),
		'po_line_id': fields.many2one('purchase.order.line', 'Aankooplijn'),
		'po_id': fields.many2one('purchase.order', 'Aankooporder', readonly=True),
		'qty_ordered': fields.float('Hoev. Besteld'),
		'qty_scanned': fields.float('Hoev. Vorige Scans'),
		'qty_to_scan': fields.float('Hoev. Open'),
		'qty_scan': fields.float('Hoev. Deze Scan'),
		'zichtzending': fields.related('po_id', 'zichtzending', string='ZZ', type='boolean'),
		'partner_id': fields.many2one('res.partner', 'Leverancier'),
		'date_planned': fields.date('Datum Gepland'),
	}

	def create(self, cr, uid, vals, context=None):
# 		print 'VALSPO:',vals
		if 'scan_line_id' in vals:
			del vals['scan_line_id']
		if 'name' in vals:
			return super(stock_scan_line_po, self).create(cr, uid, vals, context=context)
		else:
			return True

	def write(self, cr, uid, ids, vals, context=None):
# 		print 'VALSPO:',vals
		if 'scan_line_id' in vals:
			del vals['scan_line_id']
		return super(stock_scan_line_po, self).write(cr, uid, ids, vals, context=context)

	def onchange_qty(self, cr, uid, ids, qty1, qty2, qty_received, context=None):
# 		print "on change po qty", ids, qty1, qty2, qty_received
		error = False

		if qty1 > qty2 or qty1 > qty_received:
			error = True

		if error:
			raise osv.except_osv(('Fout!'),_(('Gescande hoeveelheid (%d) is groter dan wat mag gescand worden(%d)') % (qty1, qty2, )))
			return False

		return True

stock_scan_line_po()

class stock_scan_line_so(osv.osv):
	_name = "stock.scan.line.so"

	_columns = {
		'name': fields.char('Barcode', required=True),
		'scan_line_id': fields.many2one('stock.scan.line', 'Pakbonlijn'),
		'product_id': fields.many2one('product.product', 'Product'),
		'so_line_id': fields.many2one('sale.order.line', 'Verkooplijn'),
		'so_id': fields.many2one('sale.order', 'Verkooporder', readonly=True),
		'qty_ordered': fields.float('Hoev. Besteld'),
		'qty_reserved': fields.float('Hoev. Vorige Res.'),
		'qty_to_reserv': fields.float('Hoev. Open'),
		'qty_scan': fields.float('Hoev. Deze Scan'),
		'zichtzending': fields.related('so_id', 'zichtzending', string='ZZ', type='boolean'),
		'so_price': fields.float('Verkoopprijs'),
		'so_discount': fields.float('Korting'),
		'partner_id': fields.many2one('res.partner', 'Klant'),
		'date_planned': fields.date('Datum Gepland'),
	}

	def create(self, cr, uid, vals, context=None):
# 		print 'VALSSO:',vals
		if 'scan_line_id' in vals:
			del vals['scan_line_id']
		if 'name' in vals:
			return super(stock_scan_line_so, self).create(cr, uid, vals, context=context)
		else:
			return True

	def write(self, cr, uid, ids, vals, context=None):
# 		print 'VALSSO:',vals
		if 'scan_line_id' in vals:
			del vals['scan_line_id']
		return super(stock_scan_line_so, self).write(cr, uid, ids, vals, context=context)

	def onchange_qty(self, cr, uid, ids, qty1, qty2, qty_received, context=None):
# 		print "on change so qty", ids, qty1, qty2, qty_received
		error = False
		if qty1 > qty2 or qty1 > qty_received:
			error = True

		if error:
			raise osv.except_osv(('Fout!'),_(('Gescande hoeveelheid (%d) is groter dan wat mag gescand worden(%d)') % (qty1, qty2, )))
			return False

		return True

stock_scan_line_so()

class stock_reservation_current(osv.osv):
	_name = "stock.reservation.current"

	_columns = {
		'userid': fields.integer('user'),
		'partner_id': fields.integer('partner'),
		'zichtzending': fields.boolean('zichtzending')
	}

stock_scan_current()

class stock_reservation(osv.osv):
	_name = "stock.reservation"
	_order = "id desc"

	def _book_count(self, cr, uid, ids, name, arg, context=None):
		res = {}
		for id in ids:
			sql_stat = '''select sum(qty_to_deliver - qty_retour) as aantal from stock_reservation_line
 inner join stock_reservation on stock_reservation.id = stock_reservation_line.reservation_id
 where stock_reservation.id = %d
 group by stock_reservation.id ''' % (id, )
			cr.execute(sql_stat)
			sql_res = cr.dictfetchone()
			if sql_res:
				res[id] = sql_res['aantal']
			else:
				res[id] = 0
				
		return res

	def _receipt_count(self, cr, uid, ids, name, arg, context=None):
		res = {}
		for id in ids:
			sql_stat = '''select sum(qty_confirmed) as aantal from stock_reservation_line
 inner join stock_reservation on stock_reservation.id = stock_reservation_line.reservation_id
 where stock_reservation.id = %d
 group by stock_reservation.id ''' % (id, )
			cr.execute(sql_stat)
			sql_res = cr.dictfetchone()
			if sql_res:
				res[id] = sql_res['aantal']
			else:
				res[id] = 0
				
		return res

	def _sent_count(self, cr, uid, ids, name, arg, context=None):
		res = {}
		for id in ids:
			sql_stat = '''select sum(qty_sent) as aantal from stock_reservation_line
 inner join stock_reservation on stock_reservation.id = stock_reservation_line.reservation_id
 where stock_reservation.id = %d
 group by stock_reservation.id ''' % (id, )
			cr.execute(sql_stat)
			sql_res = cr.dictfetchone()
			if sql_res:
				res[id] = sql_res['aantal']
			else:
				res[id] = 0
				
		return res

	def action_res_scan(self, cr, uid, ids, context=None):

		view_id = self.pool.get('ir.ui.view').search(cr, uid, [('model','=','res.scan'),
															('name','=','view.res.scan.form')])

		pakbon = self.browse(cr, uid, ids)[0]
		context['default_pakbon'] = pakbon.name
		context['default_boek'] = None

		return {
			'type': 'ir.actions.act_window',
			'name': 'Scan zending',
			'view_mode': 'form',
			'view_type': 'form',
			'view_id': view_id[0],
			'res_model': 'res.scan',
			'target': 'new',
			'context': context,
			}

	_columns = {
		'name': fields.char('Pakbon'),
		'partner_id': fields.many2one('res.partner', 'Klant', select=True),
		'partner_shipping_id': fields.many2one('res.partner', 'Levering bij', select=True),
		'line_ids': fields.one2many('stock.reservation.line', 'reservation_id', 'Reservaties'),
		'date_created': fields.date('Datum Ontvangst'),
		'state': fields.char('Status'),
		'scan_id': fields.many2one('stock.scan', 'Scan-procedure', readonly=True),
		'zichtzending': fields.boolean('Zichtzending'),
		'comment': fields.text('Opmerking'),
		'invoice_type_id': fields.many2one('sale_journal.invoice.type', 'Invoice Type', readonly=True),
		'receipt_state': fields.char('Ontvangst status'),
		'book_count': fields.function(_book_count, string="Aantal boeken", type='integer'),
		'receipt_count': fields.function(_receipt_count, string="Aantal ontvangen", type='integer'),
		'sent_count': fields.function(_sent_count, string="Aantal verzonden", type='integer'),
	}

	_defaults={
		'date_created': date.today(), #.strftime('%Y-%m-%d'),
		'state': 'draft',
		'zichtzending': False,
		'invoice_type_id': None,
		'receipt_state': 'open',
	}

	def onchange_partner(self, cr, uid, ids, partner_id, zichtzending, context=None):
		res = {}
# 		print "onchange partner", zichtzending, partner_id
		if partner_id:
			sql_stat = "delete from stock_reservation_current where userid = '%d'" % (uid )
			cr.execute(sql_stat)
			cr.commit()
			sql_stat = "insert into stock_reservation_current (userid, partner_id, zichtzending) values ('%d', '%d', '%s')" % (uid, partner_id, zichtzending)
			cr.execute(sql_stat)
			cr.commit()
		return res

	def onchange_zichtzending(self, cr, uid, ids, zichtzending, partner_id, context=None):
		res = {}
# 		print "onchange zichtzending", zichtzending, partner_id
		if partner_id:
			sql_stat = "delete from stock_reservation_current where userid = '%d'" % (uid )
			cr.execute(sql_stat)
			cr.commit()
			sql_stat = "insert into stock_reservation_current (userid, partner_id, zichtzending) values ('%d', '%d', '%s')" % (uid, partner_id, zichtzending)
			cr.execute(sql_stat)
			cr.commit()
		return res
	
	def create(self, cr, uid, vals, context=None):
		"""Add the np sequence reference"""
		seq_id = self.pool.get('ir.sequence').search(cr, uid, [('name','=','stock.reservation')])
		vals['name'] = self.pool.get('ir.sequence').next_by_id(cr, uid, seq_id, context)
		return super(stock_reservation, self).create(cr, uid, vals, context=context)

	def action_confirm(self, cr, uid, ids, context=None):
# PROCESS SO SHIPMENT
		for sr in self.browse(cr, uid, ids, context=context):
			if sr.state != 'draft':
				raise osv.except_osv(('Fout !'),_('Deze verzending is reeds verwerkt'))
				return

			sql_stat = """
select stock_reservation_line.move_id, stock_reservation_line.product_id, stock_reservation_line.qty_to_deliver, 
stock_reservation_line.so_id, stock_reservation_line.so_line_id,
stock_move.picking_id, product_template.uom_id
from stock_reservation_line
inner join stock_move on stock_move.id = stock_reservation_line.move_id
inner join product_product on product_product.id = stock_reservation_line.product_id
inner join product_template on product_template.id = product_product.product_tmpl_id
where reservation_id = %d
order by so_id, so_line_id
;""" % (sr.id, )
			cr.execute (sql_stat)
			prev_so_id = 0
			prev = 0
			for srl in cr.dictfetchall():
				if srl['so_line_id']:
					
					if srl['so_id'] != prev_so_id:
						if prev_so_id != 0:
							pm_rec = pm.do_partial(cr, uid, [pm_id], context=context)
# 							print "return from do partial:", pm_rec						
						create_hdr = False
						pm = self.pool.get('stock.partial.picking')
						pm_id = pm.create(cr, uid, {
							'date': date.today(),
							'picking_id': srl['picking_id']
						},context=context)
						prev_so_id = srl['so_id']
					pml = self.pool.get('stock.partial.picking.line')
					pml_id = pml.create(cr, uid, {
						'update_cost': False,
						'product_id': srl['product_id'],
						'product_uom': srl['uom_id'],
						'wizard_id': pm_id,
						'location_dest_id': 9,
						'location_id': 12,
						'move_id': srl['move_id'],
						'quantity': srl['qty_to_deliver'],
					},context=context)
				sql_stat1 = """
update stock_move set qty_on_reservation = 0
where stock_move.id = %d
""" % (srl['move_id'])
				cr.execute(sql_stat1)
					
			pm_rec = pm.do_partial(cr, uid, [pm_id], context=context)
# 			print "return from do partial:", pm_rec	

# 			create_hdr = True
# 			for srl in sr.line_ids: 
# 				if srl.so_line_id:
# 					if create_hdr:
# 						create_hdr = False
# 						pm = self.pool.get('stock.partial.picking')
# 						pm_id = pm.create(cr, uid, {
# 							'date': date.today(),
# 							'picking_id': srl.move_id.picking_id.id
# 						},context=context)
# #					mv_id = 0
# #					if srl.so_line_id:
# #						sql_stat = "select id from stock_move where sale_line_id = %d" % (srl.so_line_id.id, )
# #						cr.execute(sql_stat)
# #						for sql_res in cr.dictfetchall():
# #							mv_id = sql_res['id']
# 					pml = self.pool.get('stock.partial.picking.line')
# 					pml_id = pml.create(cr, uid, {
# 						'update_cost': False,
# 						'product_id': srl.product_id.id,
# 						'product_uom': srl.product_id.product_tmpl_id.uom_id.id,
# 						'wizard_id': pm_id,
# 						'location_dest_id': 9,
# 						'location_id': 12,
# #						'move_id': mv_id,
# 						'move_id': srl.move_id.id,
# 						'quantity': srl.qty_to_deliver,
# 					},context=context)
# 			pm_rec = pm.do_partial(cr, uid, [pm_id], context=context)

# 		print 'CHANGE STATUS'
		self.write(cr, uid, ids, {'state': 'done'})

		return True

	def action_retour(self, cr, uid, ids, context=None):
		wf_service = netsvc.LocalService("workflow")
		for sr in self.browse(cr, uid, ids, context=context):
			if sr.state != 'done':
				raise osv.except_osv(('Fout !'),_('Deze verzending heeft niet de status "done"'))
				return

			hdr_created = False

			for line in sr.line_ids:
				if line.qty_retour > 0.00:
					if not hdr_created:
 						pm = self.pool.get('stock.picking')
						sm = self.pool.get('stock.move')
 						pm_id = pm.create(cr, uid, {
							'origin': sr.name,
 							'date': date.today(),
							'min_date': date.today(),
 							'partner_id': sr.partner_id.id,
							'move_type': 'direct',
							'company_id': 1,
							'invoice_state': 'none',
							'state': 'draft',
							'max_date': date.today(),
							'auto_picking': False,
							'type': 'in',
 						},context=context)
						hdr_created = True
					sm_id = sm.create(cr, uid, {
						'origin': sr.name,
						'product_uos_qty': line.qty_retour,
						'date_expected': date.today(),
						'product_uom': 1,
						'price_unit': 0.00,
						'date': date.today(),
						'product_qty': line.qty_retour,
						'product_uos': 1,
						'partner_id': sr.partner_id.id,
						'name': line.product_id.name_template,
						'product_id': line.product_id.id,
						'auto_validate': False,
						'location_id': 9,
						'company_id': 1,
						'picking_id': pm_id,
#						'priority': 1,
						'state': 'draft',
						'location_dest_id': 12,
						'distributeur_search': line.product_id.distributeur,
						'title': line.product_id.name_template,
					},context=context)
			
			if hdr_created:
				wf_service.trg_validate(uid, 'stock.picking', pm_id, 'button_confirm', cr)
				pm.force_assign(cr, uid, [pm_id], context)

# 		print 'CHANGE STATUS'
		self.write(cr, uid, ids, {'state': 'returned'})

		return True

	def action_invoice_create(self, cr, uid, ids, journal_id=False,
			group=False, type='out_invoice', context=None):
		""" Creates invoice based on the invoice state selected for picking.
		@param journal_id: Id of journal
		@param group: Whether to create a group invoice or not
		@param type: Type invoice to be created
		@return: Ids of created invoices for the pickings
		"""
		if context is None:
			context = {}

		invoice_obj = self.pool.get('account.invoice')
		invoice_line_obj = self.pool.get('account.invoice.line')
		partner_obj = self.pool.get('res.partner')
		invoices_group = {}
		res = {}

		inv_type = type
		for reservation in self.browse(cr, uid, ids, context=context):
			if reservation.state != 'done' and reservation.state != 'returned':
				continue
			partner_id = reservation.line_ids[0].so_id.partner_invoice_id.id
			partner = partner_obj.browse(cr, uid, [partner_id], context=context)[0]
#
#   see _prepare_invoice in sales_stock and stock for original

			if group and partner.id in invoices_group:
				invoice_id = invoices_group[partner.id]
# 				invoice = invoice_obj.browse(cr, uid, invoice_id)
# 				invoice_vals_group = self._prepare_invoice_group(cr, uid, reservation, partner, invoice, context=context)
# 
# 				if not invoice.del_addr_id.id == reservation.partner_id.id:
# 					invoice_vals_group['del_addr_id'] = None
# 				
# 				invoice_obj.write(cr, uid, [invoice_id], invoice_vals_group, context=context)
			else:
				account_id = partner.property_account_receivable.id
				payment_term = partner.property_payment_term.id or False
				invoice_vals = {
					'name': reservation.name,
					'origin': (reservation.name or ''),
					'type': inv_type,
					'account_id': account_id,
					'partner_id': partner.id,
# 					'payment_term': payment_term,
# 					'fiscal_position': partner.property_account_position.id,
# 					'date_invoice': context.get('date_inv', False),
					'date_invoice': date.today().strftime('%Y-%m-%d'),
					'company_id': 1,
# 					'user_id': uid,
				}
				invoice_vals['currency_id'] = 1
				invoice_vals['journal_id'] = 1
				invoice_vals['fiscal_position'] = reservation.line_ids[0].so_id.fiscal_position.id
				invoice_vals['payment_term'] = reservation.line_ids[0].so_id.payment_term.id
				invoice_vals['user_id'] = reservation.line_ids[0].so_id.user_id.id
				invoice_vals['name'] = reservation.line_ids[0].so_id.client_order_ref or ''
#				 invoice_vals = self._prepare_invoice(cr, uid, reservation, partner, inv_type, journal_id, context=context)
				invoice_vals['del_addr_id'] = reservation.partner_id.id
				invoice_id = invoice_obj.create(cr, uid, invoice_vals, context=context)
				invoices_group[partner.id] = invoice_id
			res[reservation.id] = invoice_id
# 			print 'INVOICE VALS:', invoice_vals['type']
			if invoice_vals['type'] in ('out_invoice'):
# VERKOOPORDERS
# Toevoegen lijn aan 6% BTW
				sql_stat = """
select stock_reservation.name as pakbon,
	   stock_reservation_line.so_price,
	   stock_reservation_line.so_discount,
	   stock_reservation_line.qty_to_deliver,
	   stock_reservation_line.qty_retour,
	   6 as vat,
	   sale_order.name as so,
	   sale_order.invoice_text
from stock_reservation, stock_move, stock_reservation_line, sale_order_line, sale_order, sale_order_tax, account_tax
where stock_reservation.id = %d
  and stock_reservation.id = stock_reservation_line.reservation_id
  and stock_move.id = stock_reservation_line.move_id
  and sale_order_line.id = stock_reservation_line.so_line_id
  and sale_order.id = sale_order_line.order_id
  and sale_order_line.id = sale_order_tax.order_line_id
  and account_tax.id = sale_order_tax.tax_id
  and account_tax.id = 6
  and stock_reservation_line.vat06 = 0
  and stock_reservation_line.vat21 = 0
union all
select stock_reservation.name as pakbon,
	   stock_reservation_line.vat06 as so_price,
	   stock_reservation_line.so_discount,
	   stock_reservation_line.qty_to_deliver,
	   stock_reservation_line.qty_retour,
	   6 as vat,
	   sale_order.name as so,
	   sale_order.invoice_text
from stock_reservation, stock_move, stock_reservation_line, sale_order_line, sale_order
where stock_reservation.id = %d
  and stock_reservation.id = stock_reservation_line.reservation_id
  and stock_move.id = stock_reservation_line.move_id
  and sale_order_line.id = stock_reservation_line.so_line_id
  and sale_order.id = sale_order_line.order_id
  and stock_reservation_line.vat06 <> 0
;""" % (reservation.id, reservation.id, )
				cr.execute (sql_stat)
				pakbon = None
				so = None
				bedrag = 0.00
				vat = 6
				account_id = 822
				for line in cr.dictfetchall():
					pakbon = line['pakbon']
					so = line['so']
					bedrag += round(((line['so_price'] * (100 - line['so_discount']) / 100) * (line['qty_to_deliver'] - line['qty_retour'])), 2)
					name = pakbon
					if line['invoice_text']:
						name = name + ' - ' + line ['invoice_text']
# 					print line['pakbon'], line['so_discount'], line['qty_to_deliver'], line['qty_retour'], round(((line['so_price'] * (100 - line['so_discount']) / 100) * (line['qty_to_deliver'] - line['qty_retour'])), 2)
				if bedrag <> 0.00:
					line_vals = {
						'name': name,
						'invoice_id': invoice_id,
						'uos_id': 1,
						'product_id': None,
						'account_id': account_id,
						'price_unit': bedrag,
						'discount': 0.00,
						'quantity': 1.00,
						'invoice_line_tax_id': [(6, 0, [vat])],
						'account_analytic_id': None,
					}
					invoice_line_id = invoice_line_obj.create(cr, uid, line_vals, context=context)

# Toevoegen lijn aan 21% BTW
				sql_stat = """
select stock_reservation.name as pakbon,
	   stock_reservation_line.so_price,
	   stock_reservation_line.so_discount,
	   stock_reservation_line.qty_to_deliver,
	   stock_reservation_line.qty_retour,
	   2 as vat,
	   sale_order.name as so,
	   sale_order.invoice_text
from stock_reservation, stock_move, stock_reservation_line, sale_order_line, sale_order, sale_order_tax, account_tax
where stock_reservation.id = %d
  and stock_reservation.id = stock_reservation_line.reservation_id
  and stock_move.id = stock_reservation_line.move_id
  and sale_order_line.id = stock_reservation_line.so_line_id
  and sale_order.id = sale_order_line.order_id
  and sale_order_line.id = sale_order_tax.order_line_id
  and account_tax.id = sale_order_tax.tax_id
  and account_tax.id = 2
  and stock_reservation_line.vat06 = 0
  and stock_reservation_line.vat21 = 0
union all
select stock_reservation.name as pakbon,
	   stock_reservation_line.vat21 as so_price,
	   stock_reservation_line.so_discount,
	   stock_reservation_line.qty_to_deliver,
	   stock_reservation_line.qty_retour,
	   2 as vat,
	   sale_order.name as so,
	   sale_order.invoice_text
from stock_reservation, stock_reservation_line, stock_move, sale_order_line, sale_order
where stock_reservation.id = %d
  and stock_reservation.id = stock_reservation_line.reservation_id
  and stock_move.id = stock_reservation_line.move_id
  and sale_order_line.id = stock_reservation_line.so_line_id
  and sale_order.id = sale_order_line.order_id
  and stock_reservation_line.vat21 <> 0
;""" % (reservation.id, reservation.id, )
				cr.execute (sql_stat)
				pakbon = None
				so = None
				bedrag = 0.00
				vat = 2
				account_id = 822
				for line in cr.dictfetchall():
					pakbon = line['pakbon']
					so = line['so']
					bedrag += round((round((line['so_price'] * (100 - line['so_discount']) / 100),2) * (line['qty_to_deliver'] - line['qty_retour'])), 2)
					name = pakbon
					if line['invoice_text']:
						name = name + ' - ' + line ['invoice_text']
				if bedrag <> 0.00:
					line_vals = {
						'name': name,
						'invoice_id': invoice_id,
						'uos_id': 1,
						'product_id': None,
						'account_id': account_id,
						'price_unit': bedrag,
						'discount': 0.00,
						'quantity': 1.00,
						'invoice_line_tax_id': [(6, 0, [vat])],
						'account_analytic_id': None,
					}
					invoice_line_id = invoice_line_obj.create(cr, uid, line_vals, context=context)

			invoice_obj.button_compute(cr, uid, [invoice_id], context=context,
					set_total=(inv_type in ('in_invoice', 'in_refund')))
			self.write(cr, uid, [reservation.id], {
				'state': 'invoiced',
				}, context=context)
# TO DO: STOCK_PICKING op invoiced zetten 
#		 self.write(cr, uid, res.keys(), {
#			 'invoice_state': 'invoiced',
#			 }, context=context)
			sql_stat = "update stock_picking set invoice_state = 'invoiced' where reservation_id = %d" % (reservation.id)
			cr.execute (sql_stat)

		return res

stock_reservation()

class stock_reservation_line(osv.osv):
	_name = "stock.reservation.line"

	def onchange_sale_order(self, cr, uid, ids, so_id, product_id, context=None):
		res = {}
		if so_id:
			so_obj = self.pool.get('sale.order')
			so = so_obj.browse(cr, uid, so_id, context=context)
			res['customer_id'] = so.partner_id.id
			res['zichtzending'] = so.zichtzending
			sql_stat = "select sale_order_line.id from sale_order_line where product_id = %d and sale_order_line.state = 'confirmed' and sale_order_line.order_id = %d order by sale_order_line.create_date" % (product_id, so_id, )
			cr.execute(sql_stat)
			for sql_res in cr.dictfetchall():
				so_found = True
				so_line_id = sql_res['id']
		return {'value':res}

	def onchange_sale_order_line(self, cr, uid, ids, so_line_id, context=None):
		res = {}
		if so_line_id:
			so_obj = self.pool.get('sale.order.line')
			so = so_obj.browse(cr, uid, so_line_id, context=context)
			res['so_price'] = so.price_unit
			res['so_discount'] = so.discount
			res['so_id'] = so.order_id.id
		return {'value':res}

	def onchange_barcode(self, cr, uid, ids, name, partner_id, zichtzending, context=None):
		
		res = {}
# 		sql_stat = "select partner_id, zichtzending from stock_reservation_current where userid = '%d'" % (uid, )
# 		cr.execute(sql_stat)
# 		for sql_res in cr.dictfetchall():
# 			customer_id = sql_res['partner_id']
# 			zichtzending = sql_res['zichtzending']
# 			res['customer_id'] = customer_id
# 			res['zichtzending'] = zichtzending

		customer_id = partner_id
		res['customer_id'] = customer_id
		res['zichtzending'] = zichtzending			
# 		print 'onchange barcode', ids, name, customer_id, zichtzending
		
		isbn_found = False
		po_found = False
		so_found = False

		if name:
			sql_stat = "select id, awso_code from product_product where default_code = '%s'" % (name, )
			cr.execute(sql_stat)
			for sql_res in cr.dictfetchall():
				isbn_found = True
				product_id = sql_res['id']
				awso_code = sql_res['awso_code']
				res['product_id'] = product_id
				res['awso_code'] = awso_code

			if isbn_found:
				sql_stat = "select sale_order_line.id, order_id from sale_order_line, sale_order where product_id = %d and sale_order.partner_id = %d and sale_order_line.state = 'confirmed' and order_id = sale_order.id and sale_order.zichtzending = '%s' order by sale_order.zichtzending desc, sale_order.create_date" % (product_id, customer_id, zichtzending )
				cr.execute(sql_stat)
				for sql_res in cr.dictfetchall():
					so_found = True
					so_line_id = sql_res['id']
					so_id = sql_res['order_id']
					res['so_line_id'] = so_line_id
					res['so_id'] = so_id

		if not isbn_found:
			raise osv.except_osv(('Waarschuwing !'),_(('Boek met ISBN barcode %s bestaat niet in de data base') % (name, )))
#			return
		if isbn_found and not so_found:
			raise osv.except_osv(('Waarschuwing !'),_(('Voor het boek met ISBN barcode %s bestaat geen verkooporder') % (name, )))
#			return

		return {'value':res}

	def create(self, cr, uid, vals, context=None):
		if not ('scan_procedure' in vals):
# 			print 'RESERVATION LINE CREATE VALS:',vals
#			vals['qty_to_deliver'] = 1.00
			
			sql_stat = "select id from stock_move where not(state = 'done') and sale_line_id = %d" % (vals['so_line_id'], )
			cr.execute(sql_stat)
			for sql_res in cr.dictfetchall():
				vals['move_id'] = sql_res['id']
			
			sql_stat1 = """
update stock_move set qty_on_reservation = (qty_on_reservation + %d)
where stock_move.id = %d
""" % (vals['qty_to_deliver'], vals['move_id'])
			cr.execute(sql_stat1)

			sql_stat2 = """
update stock_reservation set invoice_type_id = (select invoice_type_id from sale_order, sale_order_line where sale_order_line.order_id = sale_order.id and sale_order_line.id = %d)
where stock_reservation.id = %d
""" % (vals['so_line_id'], vals['reservation_id'])
			cr.execute(sql_stat2)

			sql_stat3 = """
select order_id, sale_order.partner_id, sale_order.zichtzending from sale_order, sale_order_line where sale_order_line.order_id = sale_order.id and sale_order_line.id = %d
""" % (vals['so_line_id'])
			cr.execute(sql_stat3)
			sql_res = cr.dictfetchone()
			if sql_res:
				vals['so_id'] = sql_res['order_id']
				vals['partner_id'] = sql_res['partner_id']
				vals['zichtzending'] = sql_res['zichtzending']
				
		return super(stock_reservation_line, self).create(cr, uid, vals, context=context)

	def write(self, cr, uid, ids, vals, context=None):
# 		print 'RESERVATION LINE WRITE VALS', vals
# 		print 'RESERVATION LINE WRITE ids', ids
		if 'qty_to_deliver' in vals:
			for id in ids:
				sql_stat = """
select stock_move.id, stock_move.qty_on_reservation, stock_reservation_line.qty_to_deliver from stock_move, stock_reservation_line 
where stock_reservation_line.id = %d and stock_move.id = stock_reservation_line.move_id
""" % (id)
			cr.execute(sql_stat)
			for sql_res in cr.dictfetchall():
				move_id = sql_res['id']
				old_qty_on_reservation = sql_res['qty_on_reservation']
				old_qty_to_deliver = sql_res['qty_to_deliver']
# 				print "data", move_id, old_qty_on_reservation, old_qty_to_deliver, vals['qty_to_deliver']
				qty_on_reservation = old_qty_on_reservation - old_qty_to_deliver + vals['qty_to_deliver']
	
				sql_stat1 = """
update stock_move set qty_on_reservation = %d
where stock_move.id = %d
""" % (qty_on_reservation, move_id)
				cr.execute(sql_stat1)
		
		return super(stock_reservation_line, self).write(cr, uid, ids, vals, context=context)

	def unlink(self, cr, uid, ids, context=None):
		for id in ids:
			sql_stat = """
select stock_move.id, stock_move.qty_on_reservation, stock_reservation_line.qty_to_deliver from stock_move, stock_reservation_line 
where stock_reservation_line.id = %d and stock_move.id = stock_reservation_line.move_id
""" % (id)
			cr.execute(sql_stat)
			for sql_res in cr.dictfetchall():
				move_id = sql_res['id']
				old_qty_on_reservation = sql_res['qty_on_reservation']
				old_qty_to_deliver = sql_res['qty_to_deliver']
# 				print "data", move_id, old_qty_on_reservation, old_qty_to_deliver
				qty_on_reservation = old_qty_on_reservation - old_qty_to_deliver
	
			sql_stat1 = """
update stock_move set qty_on_reservation = %d
where stock_move.id = %d
""" % (qty_on_reservation, move_id)
			cr.execute(sql_stat1)
			
		return super(stock_reservation_line, self).unlink(cr, uid, ids, context=context)
	
	
	def _function_title(self, cr, uid, ids, name, arg, context=None):
		res = {}
		for sr in self.browse(cr, uid, ids):
			if sr.product_id:
				res[sr.id] = sr.product_id.name_template
		return res

	def _calc_amount(self, cr, uid, ids, name, arg, context=None):
		res = {}
		for sr in self.browse(cr, uid, ids):
			if sr.combined_vat:
				res[sr.id] = round(((sr.vat06 * (100 - sr.so_discount) / 100) * (sr.qty_to_deliver - sr.qty_retour)), 2) + round(((sr.vat21 * (100 - sr.so_discount) / 100) * (sr.qty_to_deliver - sr.qty_retour)), 2)
			else:
				res[sr.id] = round(((sr.so_price * (100 - sr.so_discount) / 100) * (sr.qty_to_deliver - sr.qty_retour)), 2)
		return res

	_columns = {
		'name': fields.char('Barcode', required=True),
		'reservation_id': fields.many2one('stock.reservation', 'Reservatie'),
		'product_id': fields.many2one('product.product', 'Product'),
		'so_line_id': fields.many2one('sale.order.line', 'Verkooplijn'),
		'so_id': fields.many2one('sale.order', 'Verkooporder'),
		'customer_id': fields.related('so_id', 'partner_id', type='many2one', relation='res.partner', string='Klant'),
		'qty_to_deliver': fields.float('Hoev.'),
		'so_price': fields.float('Verkoopprijs'),
		'so_discount': fields.float('Korting'),
		'zichtzending': fields.related('so_id', 'zichtzending', string='Zichtzending', type='boolean'),
		'move_id': fields.many2one('stock.move', 'Move Id'),
 		'title': fields.function(_function_title, string='Titel', type='char', store=True),
		'combined_vat': fields.boolean('Gecombineerde BTW'),
		'vat06': fields.float('Bedrag BTW 6%'),
		'vat21': fields.float('Bedrag BTW 21%'),
#		'awso_code': fields.related('product_id', 'awso_code', type='char', relation='product.product', string='AWSO Code'),
		'awso_code': fields.selection((('A','Algemeen'),('W','Wetenschappelijk'),('S','Studie'),('O','Overige')),'AWSO Code'),
		'state': fields.related('reservation_id', 'state', string='Status', type='char'),
		'qty_retour': fields.float('Hoev. Retour'),
		'to_invoice_vat_incl': fields.function(_calc_amount, string="Fact.Bedrag", type='float'),
		'qty_confirmed': fields.float('Hoev. Ontv.'),
		'qty_sent': fields.float('Hoev. Verzonden'),
	}

	_defaults = {
		'qty_to_deliver': 1.00,
		'qty_retour': 0.00,
		'qty_confirmed': 0.00,
		'qty_sent': 0.00,
	}

	_order = "title"

stock_reservation_line()

class stock_move(osv.osv):
	_inherit = "stock.move"
	_order = "date_expected desc, title"

	_columns = {
		'title': fields.related('product_id', 'name_template', string='Titel', type='char', store=True),
		'qty_on_reservation': fields.float('Op reservatie'),
	}

	_defaults = {
		'qty_on_reservation': 0.00,
	}

stock_move()

#class stock_partial_picking_line(osv.osv):
#    _inherit = "stock.partial.picking.line"
#
#    def create(self, cr, uid, vals, context=None):
#        print 'VALS:',vals
#        return super(stock_partial_picking_line, self).create(cr, uid, vals, context=context)
#
#stock_partial_picking_line()

class sale_order_line(osv.osv):
	_inherit = "sale.order.line"

	def name_get(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		if isinstance(ids, (int, long)):
			ids = [ids]
		if not len(ids):
			return []

		res = []
		for line in self.browse(cr, uid, ids, context=context):
			if line.product_id:
				name = '[%s] %s' % (line.order_id.name, line.product_id.default_code)
			else:
				name = line.name
			res.append((line.id,name))
		return res

sale_order_line()

class purchase_order_line(osv.osv):
	_inherit = "purchase.order.line"

	def name_get(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		if isinstance(ids, (int, long)):
			ids = [ids]
		if not len(ids):
			return []

		res = []
		for line in self.browse(cr, uid, ids, context=context):
			if line.product_id:
				name = '[%s] %s' % (line.order_id.name, line.product_id.default_code)
			else:
				name = line.name
			res.append((line.id,name))
		return res

sale_order_line()

class stock_picking(osv.osv):
	_inherit = "stock.picking"

	def _get_price_unit_invoice(self, cr, uid, move_line, type, context=None):
		""" Gets price unit for invoice
		@param move_line: Stock move lines
		@param type: Type of invoice
		@return: The price unit for the move line
		"""
		if context is None:
			context = {}

		if type in ('in_invoice', 'in_refund'):
			# Take the user company and pricetype
			context['currency_id'] = move_line.company_id.currency_id.id
			amount_unit = move_line.product_id.price_get('standard_price', context=context)[move_line.product_id.id]
			return amount_unit
		else:
			price_unit = move_line.product_id.list_price
			if move_line.id:
				sql_stat = "select so_price from stock_reservation_line where move_id = %d" % (move_line.id, )
				cr.execute(sql_stat)
				for sql_res in cr.dictfetchall():
					price_unit = sql_res['so_price']
			return price_unit

	def _get_discount_invoice(self, cr, uid, move_line):
		'''Return the discount for the move line'''
		discount = 0.0
		if move_line.id:
			sql_stat = "select so_discount from stock_reservation_line where move_id = %d" % (move_line.id, )
			cr.execute(sql_stat)
			for sql_res in cr.dictfetchall():
				discount = sql_res['so_discount']
		return discount

stock_picking()

class stock_invoice_reservation(osv.osv_memory):
	_name = "stock.invoice.reservation"
	_description = "Stock Invoice Reservation"

	_columns = {
		}

	def open_invoice(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		invoice_ids = []
		data_pool = self.pool.get('ir.model.data')
		res = self.create_invoice(cr, uid, ids, context=context)
		invoice_ids += res.values()
		inv_type = context.get('inv_type', False)
		action_model = False
		action = {}
		if not invoice_ids:
			raise osv.except_osv(_('Error!'), _('Please create Invoices.'))
		if inv_type == "out_invoice":
			action_model,action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree1")
		elif inv_type == "in_invoice":
			action_model,action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree2")
		elif inv_type == "out_refund":
			action_model,action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree3")
		elif inv_type == "in_refund":
			action_model,action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree4")
		if action_model:
			action_pool = self.pool.get(action_model)
			action = action_pool.read(cr, uid, action_id, context=context)
			action['domain'] = "[('id','in', ["+','.join(map(str,invoice_ids))+"])]"
		return action

	def create_invoice(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		reservation_pool = self.pool.get('stock.reservation')
		active_ids = context.get('active_ids', [])
		res = reservation_pool.action_invoice_create(cr, uid, active_ids,
													journal_id = False,
													group = True,
													type = 'out_invoice',
													context=context)
		return res

stock_invoice_reservation()

class res_scan(osv.osv_memory):
	_name = "res.scan"
	_description = "Scannen zending"

	_columns = {
        'pakbon': fields.char('Pakbon', size=8),
        'boek': fields.char('ISBN', size=13),
        }

	def boek_change(self, cr, uid, ids, pakbon, boek, context=None):
		res = {}
		if boek == False or boek == None:
			return res
		boek_found = False
		pakbon_found = False
		line_found = False

		sql_stat = """
select id
from product_product
where default_code = '%s';
""" % (boek, )
		cr.execute (sql_stat)
		for sql_res in cr.dictfetchall():
			boek_found = True
			product_id = sql_res['id']

		if boek_found:        
			sql_stat = """
select id
from stock_reservation
where name = '%s';
""" % (pakbon, )
		cr.execute (sql_stat)
		for sql_res in cr.dictfetchall():
			pakbon_found = True
			pakbon_id = sql_res['id']

		if pakbon_found:        
			sql_stat = """
select id, qty_to_deliver, qty_retour, qty_sent
from stock_reservation_line
where product_id = %d and reservation_id = %d;
""" % (product_id, pakbon_id)
			cr.execute (sql_stat)
			for sql_res in cr.dictfetchall():
				line_found = True
				line_id = sql_res['id']
				qty_to_deliver = sql_res['qty_to_deliver']
				qty_retour = sql_res['qty_retour']
				qty_sent = sql_res['qty_sent']

		if line_found and qty_sent < qty_to_deliver - qty_retour:        
			sql_stat = """
update stock_reservation_line set qty_sent = qty_sent + 1
where id = %d;
""" % (line_id, )
			cr.execute (sql_stat)
			cr.commit()
			res['boek'] = None
		else:
			print "select 2"
			sql_stat = """
select id, qty_to_deliver, qty_retour, qty_sent
from stock_reservation_line
where product_id = %d and reservation_id = %d and qty_sent < qty_to_deliver - qty_retour;
""" % (product_id, pakbon_id)
			cr.execute (sql_stat)
			for sql_res in cr.dictfetchall():
				line_found = True
				line_id = sql_res['id']
				qty_to_deliver = sql_res['qty_to_deliver']
				qty_retour = sql_res['qty_retour']
				qty_sent = sql_res['qty_sent']

			if line_found and qty_sent < qty_to_deliver - qty_retour:		
				sql_stat = """
update stock_reservation_line set qty_sent = qty_sent + 1
where id = %d;
""" % (line_id, )
				cr.execute (sql_stat)
				cr.commit()
				res['boek'] = None

		if not boek_found:
			raise osv.except_osv(('Waarschuwing !'),_(('Boek met ISBN barcode %s bestaat niet in de data base') % (boek, )))
		if not pakbon_found:
			raise osv.except_osv(('Waarschuwing !'),_(('Pakbon %s bestaat niet') % (pakbon, )))
		if boek_found and pakbon_found and not line_found:
			raise osv.except_osv(('Waarschuwing !'),_(('Boek %s komt niet voor in pakbon %s') % (boek, pakbon, )))
		if line_found and not(qty_sent < qty_to_deliver - qty_retour):
			raise osv.except_osv(('Waarschuwing !'),_(('U zou meer verzenden dan op de pakbon voorzien')))

		return {'value':res}

res_scan()

