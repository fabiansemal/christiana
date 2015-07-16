#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##############################################################################
#
##############################################################################

from openerp.osv import osv, fields

class procurement_order(osv.osv):
    _inherit = 'procurement.order'

    def create(self, cr, uid, vals, context=None):
        res = super(procurement_order, self).create(cr, uid, vals, context=context)
        prc = self.browse(cr, uid, res)
        if prc.move_id.sale_line_id:
            product_qty = 0.00
            product_qty = prc.product_qty
            product_qoh = prc.product_id.qty_available - prc.product_id.reservation_count
            print 'PRODUCT QTY1:',product_qty
            print 'VIRTUAL AVAILABLE:', prc.product_id.virtual_available
            print 'QOH:', product_qoh
            if product_qoh > 0.00:
                product_qty = product_qty - product_qoh
            print 'PRODUCT QTY2:',product_qty
            if product_qty > 0.00 and not prc.move_id.sale_line_id.order_id.zichtzending:
                print 'geen zichtzending, dus offerte wordt aangemaakt'
                po = self.pool.get('purchase.order')
                po_obj = po.create(cr, uid, {
#                    'name': '/',
                    'date_order': prc.move_id.date,
                    'partner_id': prc.product_id.seller_id.id,
                    'pricelist_id': 2,
                    'zichtzending': False,
                    'state': 'draft',
                    'invoice_method': 'picking',
                    'company_id': prc.company_id.id,
                    'location_id': prc.move_id.location_id.id,
                    'amount_tax': 0.00,
                    'amount_total': 0.00,
                    'amount_untaxed': 0.00,
                    'currency_id': 1,
                    'origin': prc.move_id.sale_line_id.order_id.name,
                    'distributeur': prc.product_id.distributeur,
                },context=context)
                po_id = po.browse(cr, uid, po_obj, context=context)
                print 'DISTR:',prc.product_id.distributeur

                pol = self.pool.get('purchase.order.line')
                pol_obj = pol.create(cr, uid, {
                    'name': prc.product_id.name_template,
                    'date_order': prc.move_id.date,
                    'date_planned': prc.move_id.date,
                    'invoiced': False,
                    'state': 'draft',
                    'company_id': prc.company_id.id,
                    'move_dest_id': prc.move_id.id,
                    'order_id': po_id.id,
                    'partner_id': prc.product_id.seller_id.id,
                    'price_subtotal': 0.00,
                    'price_unit': 0.00,
                    'product_id': prc.product_id.id,
                    'product_qty': product_qty,
                    'product_uom': prc.product_id.product_tmpl_id.uom_id.id,
                    'taxes_id': [],
                    'isbn_number': prc.product_id.default_code,
                },context=context)

                sql_stat = "update purchase_order set distributeur = '%s' where id = %d" % (prc.product_id.distributeur, po_id.id, )
                cr.execute(sql_stat)

        return res

procurement_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

