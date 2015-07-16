# -*- coding: utf-8 -*-
##############################################################################
#
#    Smart Solution bvba
#    Copyright (C) 2010-Today Smart Solution BVBA (<http://www.smartsolution.be>).
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

from osv import osv, fields
from datetime import datetime
import csv
import base64
from tools.translate import _

class purchase_order_lines_import_wizard(osv.TransientModel):

    _name = "purchase.order.lines.import.wizard"

    _columns = {
        'lines_file': fields.binary('Purchase Order Lines File', required=True),
    }

    def purchase_order_lines_import(self, cr, uid, ids, context=None):
        """Import sale order lines from a file"""
        po = self.pool.get('purchase.order')
        po_rec = po.browse(cr, uid, context['active_id'])
        partner_id = po_rec.partner_id.id
        fiscal_pos_obj = self.pool.get('account.fiscal.position')

        print "WIZ IDS:",ids
        print "WIZ CONTEXT:",context

        obj = self.browse(cr, uid, ids)[0]

        fname = '/tmp/csv_temp_' + datetime.today().strftime('%Y%m%d%H%M%S') + '.csv'
        fp = open(fname,'w+')
        fp.write(base64.decodestring(obj.lines_file))
        fp.close()
        fp = open(fname,'rU')
        reader = csv.reader(fp, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        entry_vals = []

        warning = False
        title = ''
        message = ''

        product_product = self.pool.get('product.product')
        res_partner = self.pool.get('res.partner')
        account_tax = self.pool.get('account.tax')
        account_fiscal_position = self.pool.get('account.fiscal.position')
        
        for row in reader:
            print "READLINE:",reader.line_num
            if reader.line_num <= 1:
                continue
            print "ROW:",row

            # Find the company
            company = self.pool.get('res.users').browse(cr, uid, uid).company_id.id             

            # Find the product id and product name
            product_id = False
            if row[0] != "":
                print "PRODUCT:",row[0]
                product_ids = self.pool.get('product.product').search(cr, uid, [('default_code','=',row[0].replace('-','').replace(' ','').replace('_','').replace('.',''))]) 
                print "PRODUCTS:",product_ids
                if product_ids:
                    if len(product_ids) > 1:
                        raise osv.except_osv(_('Multiple Products found !'), _('Several products where found for that code %s'%(row[0])))
                else:
                    # If no product found
                    raise osv.except_osv(_('Product not found !'), _('Product %s is not found'%(row[0])))

                product_id = product_ids[0]
                context_partner = context.copy()
                if partner_id:
                    lang = res_partner.browse(cr, uid, partner_id).lang
                    context_partner.update( {'lang': lang, 'partner_id': partner_id} )
                product = product_product.browse(cr, uid, product_id, context=context_partner)
                taxes = account_tax.browse(cr, uid, map(lambda x: x.id, product.supplier_taxes_id))
                fpos = False
                taxes_ids = account_fiscal_position.map_tax(cr, uid, fpos, taxes)

                quantity = 1.00
                if row[1] != "":
                    quantity = float(row[1].replace(',','.'))

                vals = {
                    'name': product.name_template,
                    'date_order': po_rec.date_order,
                    'date_planned': po_rec.date_order,
                    'invoiced': False,
                    'state': 'draft',
                    'company_id': po_rec.company_id.id,
                    'order_id': po_rec.id,
                    'partner_id': product.seller_id.id,
                    'price_subtotal': 0.00,
                    'price_unit': product.standard_price,
                    'product_id': product_id,
                    'product_qty': quantity,
                    'product_uom': product.product_tmpl_id.uom_id.id,
                    'taxes_id': taxes_ids,
                    'isbn_number': product.default_code,
                    
                }
                entry_vals.append(vals)

        print "ENTRYVALS:",entry_vals
        for line_vals in entry_vals:
            line_id = self.pool.get('purchase.order.line').create(cr, uid, line_vals)

        if message != '':
            raise osv.except_osv(_(title), message)

        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
