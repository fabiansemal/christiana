#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##############################################################################
#
##############################################################################

from openerp.osv import osv, fields
from datetime import date

class stock_reservation(osv.osv):
    _inherit = 'stock.reservation'

    _columns = {
    }

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
                invoice = invoice_obj.browse(cr, uid, invoice_id)
                invoice_vals_group = self._prepare_invoice_group(cr, uid, reservation, partner, invoice, context=context)

                if not invoice.del_addr_id.id == reservation.partner_id.id:
                	invoice_vals_group['del_addr_id'] = None
                
                invoice_obj.write(cr, uid, [invoice_id], invoice_vals_group, context=context)
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
				invoice_vals['currency_id'] = partner.property_account_receivable.currency_id
				invoice_vals['journal_id'] = 1
				invoice_vals['fiscal_position'] = reservation.line_ids[0].so_id.fiscal_position.id
				invoice_vals['payment_term'] = reservation.line_ids[0].so_id.payment_term.id
				invoice_vals['user_id'] = reservation.line_ids[0].so_id.user_id.id
				invoice_vals['name'] = reservation.line_ids[0].so_id.client_order_ref or ''
#                 invoice_vals = self._prepare_invoice(cr, uid, reservation, partner, inv_type, journal_id, context=context)
				invoice_vals['del_addr_id'] = reservation.partner_id.id
				invoice_id = invoice_obj.create(cr, uid, invoice_vals, context=context)
				invoices_group[partner.id] = invoice_id
            res[reservation.id] = invoice_id
            print 'INVOICE VALS:', invoice_vals['type']
            if invoice_vals['type'] in ('out_invoice'):
# VERKOOPORDERS
# Toevoegen lijn aan 6% BTW
                sql_stat = """
select stock_reservation.name as pakbon,
       stock_reservation_line.so_price,
       stock_reservation_line.so_discount,
       stock_reservation_line.qty_to_deliver,
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
                    bedrag += round(((line['so_price'] * (100 - line['so_discount']) / 100) * line['qty_to_deliver']), 2)
                    name = pakbon + ' - ' + so
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

# Toevoegen lijn aan 21% BTW
                sql_stat = """
select stock_reservation.name as pakbon,
       stock_reservation_line.so_price,
       stock_reservation_line.so_discount,
       stock_reservation_line.qty_to_deliver,
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
                    bedrag += round(((line['so_price'] * (100 - line['so_discount']) / 100) * line['qty_to_deliver']), 2)
                    name = pakbon + ' - ' + so
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
#         self.write(cr, uid, res.keys(), {
#             'invoice_state': 'invoiced',
#             }, context=context)
        return res

stock_reservation()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

