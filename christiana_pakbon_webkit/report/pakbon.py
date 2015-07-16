# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2013 Serpent Consulting Services (<http://www.serpentcs.com>)
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
############################################################################
import time
from openerp.osv import fields, osv, orm
from openerp.report import report_sxw

class stock_reservation(osv.osv):
    _inherit = 'stock.reservation'
    
    def pakbon_print(self, cr, uid, ids, context=None):
         datas = {
              'ids': ids,
              'model': 'stock.reservation',
              'form': self.read(cr, uid, ids[0], context=context)
         }
         return {
             'type': 'ir.actions.report.xml',
             'report_name': 'pakbon_webkit',
             'datas': datas,
             'nodestroy' : True
         }
 
stock_reservation()

class pakbon(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(pakbon, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time, 
            'cr': cr,
            'uid': uid,
        })

report_sxw.report_sxw('report.pakbon_webkit', 'stock.reservation', 'addons/christiana_pakbon_webkit/report/pakbon.mako', parser=pakbon, header="external")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

