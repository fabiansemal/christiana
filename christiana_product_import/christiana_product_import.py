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

#. module: web
#. openerp-web
#: code:addons/web/static/src/js/view_form.js:4981
#, python-format
#msgid "The selected file exceed the maximum file size of %s."
#msgstr ""
#
# Aanpassing nodig voor max file size
#        this.max_upload_size = 25 * 1024 * 1024; // 25Mo

from osv import osv, fields
from datetime import datetime
import csv
import base64
from tools.translate import _

class supplier_import_wizard(osv.TransientModel):
    _name = "supplier.import.wizard"

    _columns = {
        'suppliers_file': fields.binary('Bestand Uitgevers', required=True),
    }

    def supplier_import(self, cr, uid, ids, context=None):
        """Import suppliers from a file"""

        obj = self.browse(cr, uid, ids)[0]

        fname = '/tmp/csv_temp_' + datetime.today().strftime('%Y%m%d%H%M%S') + '.csv'
        fp = open(fname,'w+')
        fp.write(base64.decodestring(obj.suppliers_file))
        fp.close()
        fp = open(fname,'rU')
        reader = csv.reader(fp, delimiter=";", quotechar='"')

        nbr_lines = 0
        nbr_lines_1000 = 0

        print 'Import suppliers started'
        for row in reader:
            if reader.line_num <= 1:
                continue

            if row[0] == '':
                continue

            isbn = row[0]
            naam = row[1]
            straat = row[2].upper()
            postcode = row[3]
            gemeente = row[4]
            land = row[5]
            telefoon = row[6]
            fax = row[7]

            country_id = 21
            if land == 'Nederland': 166
            if land == 'Frankrijk': 76
            if land == 'Denemarken': 60
            if land == 'Duitsland': 58
            if land == 'Albanië': 6
            if land == 'Armenië': 7
            if land == 'Australië': 14
            if land == 'Bolivia': 30
            if land == 'Bulgarije': 23
            if land == 'Canada': 39
            if land == 'China': 49
            if land == 'Colombia': 50
            if land == 'Griekenland': 89
            if land == 'Groot-Brittanië': 233
            if land == 'Hong Kong': 98
            if land == 'Ierland': 102
            if land == 'India': 105
            if land == 'Indonesië': 101
            if land == 'Iran': 108
            if land == 'Israel': 103
            if land == 'Italië': 110
            if land == 'Japan': 114
            if land == 'Luxemburg': 134
            if land == 'Maleisië': 158
            if land == 'Mexico': 157
            if land == 'Monaco': 138
            if land == 'Nederlandse Antillen': 8
            if land == 'Nieuw Zeeland': 172
            if land == 'Nigeria': 164
            if land == 'Noord-Korea': 121
            if land == 'Noorwegen': 167
            if land == 'Oekraïne': 231
            if land == 'Oostenrijk': 13
            if land == 'Polen': 180
            if land == 'Portugal': 185
            if land == 'Rusland': 192
            if land == 'Singapore': 199
            if land == 'Spanje': 69
            if land == 'Suriname': 208
            if land == 'Thailand': 219
            if land == 'Tsjechië': 57
            if land == 'Turkije': 226
            if land == 'Uruguay': 236
            if land == 'Verenigde Staten': 235
            if land == 'Zuid-Afrika': 250

# SUPPLIERS
            supplier_id = None
            if naam != "":
                supplier_found = False
                supplier_search = self.pool.get('res.partner').search(cr, uid, [('name','=',naam)])
                for supplier_rec in self.pool.get('res.partner').browse(cr, uid, supplier_search):
                    supplier_id = supplier_rec.id
                    supplier_found = True
                if not supplier_found:
                    vals = {
                        'ref': isbn,
                        'name': naam,
                        'lang': 'nl_BE',
                        'company_id': 1,
                        'color': 0,
                        'use_parent_address': False,
                        'active': True,
                        'street': straat,
                        'supplier': True,
                        'city': gemeente,
                        'zip': postcode,
                        'country_id': country_id,
                        'employee': False,
                        'type': 'contact',
                        'fax': fax,
                        'phone': telefoon,
                        'customer': False,
                        'is_company': True,
                        'notification_email_send': 'none',
                        'opt_out': False,
                        'vat_subjected': True,
                        'purchase_warn': 'no-message',
                        'sale_warn': 'no-message',
                        'invoice_warn': 'no-message',
                        'picking_warn': 'no-message',
                    }
                    supplier_id = self.pool.get('res.partner').create(cr, uid, vals) 
              
            nbr_lines = nbr_lines + 1
            nbr_lines_1000 = nbr_lines_1000 + 1
            if nbr_lines_1000 == 1000:
                print "Number of lines processed: ", nbr_lines
                nbr_lines_1000 = 0

        print "End of Import Job - Number of lines processed: ", nbr_lines
        cr.commit()
        raise osv.except_osv(_('Verwerkt'), _('Number of lines processed: ' + str(nbr_lines)))
        return True

class author_import_wizard(osv.TransientModel):
    _name = "author.import.wizard"

    _columns = {
        'author_file': fields.binary('Bestand Boekenbank', required=True),
    }

    def author_import(self, cr, uid, ids, context=None):
        """Import authors from a file"""

        obj = self.browse(cr, uid, ids)[0]

        fname = '/tmp/csv_temp_' + datetime.today().strftime('%Y%m%d%H%M%S') + '.csv'
        fp = open(fname,'w+')
        fp.write(base64.decodestring(obj.author_file))
        fp.close()
        fp = open(fname,'rU')
        reader = csv.reader(fp, delimiter=";", quotechar='"')

        # Find the company
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id.id             

        # Find boekenbank.be
        nbr_lines = 0
        nbr_lines_1000 = 0

        nbr_authors = 0
        nbr_co_authors = 0

        print 'Import authors started'
        for row in reader:
            nbr_lines = nbr_lines + 1
            nbr_lines_1000 = nbr_lines_1000 + 1
            if nbr_lines_1000 == 1000:
                print "Number of lines processed: ", nbr_lines
                nbr_lines_1000 = 0

            if reader.line_num <= 1:
                continue

            if row[0] == '':
                continue

            auteur = row[1].upper()
            co_auteur = row[2].upper()
            distributeur = row[4]

            if distributeur == 'ZWA':
                continue

# AUTEURS
            auteur_id = None
            if auteur != "":
                auteur_found = False
                auteur_search = self.pool.get('res.author').search(cr, uid, [('name','=',auteur)])
                for auteur_rec in self.pool.get('res.author').browse(cr, uid, auteur_search):
                    auteur_id = auteur_rec.id
                    auteur_found = True
                if not auteur_found:
                    vals = {
                        'name': auteur,
                    }
                    auteur_id = self.pool.get('res.author').create(cr, uid, vals) 
                    nbr_authors = nbr_authors + 1    

# CO-AUTEURS
            co_auteur_id = None
            if co_auteur != "":
                co_auteur_found = False
                co_auteur_search = self.pool.get('res.co.author').search(cr, uid, [('name','=',co_auteur)])
                for co_auteur_rec in self.pool.get('res.co.author').browse(cr, uid, co_auteur_search):  
                    co_auteur_id = co_auteur_rec.id
                    co_auteur_found = True
                if not co_auteur_found:
                    vals = {
                        'name': co_auteur,
                    }
                    co_auteur_id = self.pool.get('res.co.author').create(cr, uid, vals)   
                    nbr_co_authors = nbr_co_authors + 1  
            
        print "End of Import Job - Number of lines processed: ", nbr_lines
        print "Nbr of authors added: ", nbr_authors
        print "Nbr of co_authors added: ", nbr_co_authors
        cr.commit()
        raise osv.except_osv(_('Verwerkt'), _('Number of lines processed: ' + str(nbr_lines)))
        return True

class product_import_wizard(osv.TransientModel):
    _name = "product.import.wizard"

    _columns = {
        'product_file': fields.binary('Bestand Boekenbank', required=True),
    }

    def product_import(self, cr, uid, ids, context=None):
        """Import products from a file"""

        obj = self.browse(cr, uid, ids)[0]

        fname = '/tmp/csv_temp_' + datetime.today().strftime('%Y%m%d%H%M%S') + '.csv'
        fp = open(fname,'w+')
        fp.write(base64.decodestring(obj.product_file))
        fp.close()
        fp = open(fname,'rU')
        reader = csv.reader(fp, delimiter=";", quotechar='"')

        # Find the company
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id.id             

        # Find boekenbank.be
#        supplier_found = False
#        supplier_search = self.pool.get('res.partner').search(cr, uid, [('name','=','Boekenbank vzw')])
#        for supplier_rec in self.pool.get('res.partner').browse(cr, uid, supplier_search):  
#            supplier_id = supplier_rec.id
#            supplier_found = True

        nbr_lines = 0
        nbr_lines_1000 = 0

        nbr_product_categs = 0
        nbr_product_template_a = 0
        nbr_product_product_a = 0
        nbr_product_template_c = 0
        nbr_product_product_c = 0

        print 'Import products started'
        for row in reader:
            nbr_lines = nbr_lines + 1
            nbr_lines_1000 = nbr_lines_1000 + 1
            if nbr_lines_1000 == 1000:
                print "Number of lines processed: ", nbr_lines
                nbr_lines_1000 = 0

            if reader.line_num <= 1:
                continue

            if row[0] == '':
                continue

            verkorte_titel = row[0]
            auteur = row[1].upper()
            co_auteur = row[2].upper()
            uitgevernummer = row[3]
            distributeur = row[4]
            druknummer = row[5]
            verschijningsdatum = row[6][0:2] + '/' + row[6][2:4] + '/' + row[6][4:8]
            fondscode = row[7]
            reeksnummer = row[8]
            nugi_code = row[9]
            awso_code = row[10]
            artikel_status = row[11]
            uitgavesoort = row[12]
            uitvoering = row[13]
            voorraadcode = row[14]
            netwerkcode = row[15]
            bestellen_boekhandel = row[16]
            btw_code = row[17]
            isbn_nummer = row[18]
            ean_code = row[19]
            if row[20] == '':
                formaat = ''
            else:
                formaat = row[20][0:2] + 'x' + row[20][2:4] + 'x' + row[20][4:6]
            gewicht = row[21].replace(",",".")
            btw21 = row[22].replace(",",".")
            verkoopprijs = row[23].replace(",",".")
            paginas = row[24]
            if row[25] == 'J':
                illustraties = True
            else:
                illustraties = False
            min_bestelaantal = row[26]
            historisch = row[27]
            depotnummer = row[28]
            co_edities = row[29]
            substituut_isbn = row[30]
            nur1 = row[31]
            nur2 = row[32]
            hoofdtitel = row[33]
            ondertitel = row[34]
            sectietitel = row[35]
            deeltitel = row[36]
            nummer_binnen_reeks = row[37]
            bijlage = row[38]
            taalcode = row[39]
            oorspronkelijke_taal = row[40]
            oorspronkelijke_titel = row[41]
            bijkomende_prijsinfo = row[42]
            avi_niveau = row[43]
            jaar_1ste_verschijning = row[44]
            imprint = row[45]
            set_code = row[46]
            if btw_code == '2':
                combined_vat = True
            else:
                combined_vat = False

            if not (awso_code == 'A' or awso_code == 'W' or awso_code == 'S' or awso_code == 'O' or awso_code == ''):
                print 'AWSO CODE:', awso_code
                awso_code = 'O'
            if not (artikel_status == '1' or artikel_status == '2' or artikel_status == '3' or artikel_status == '4' or artikel_status == '5' or artikel_status == '6' or artikel_status == '7' or artikel_status == '8' or artikel_status == '9' or artikel_status == ''):
                print 'ARTIKEL STATUS:', artikel_status
                artikel_status = '5'
            if not (uitgavesoort == 'B' or uitgavesoort == 'K' or uitgavesoort == 'D' or uitgavesoort == 'C' or uitgavesoort == 'V' or uitgavesoort == 'A' or uitgavesoort == 'Z' or uitgavesoort == 'P' or uitgavesoort == 'S' or uitgavesoort == 'I' or uitgavesoort == 'E' or uitgavesoort == 'X' or uitgavesoort == 'DG' or uitgavesoort == ''):
                print 'UITGAVE SOORT:', uitgavesoort
                uitgavesoort = 'D'
            if not (uitvoering == 'GB' or uitvoering == 'PB' or uitvoering == 'PK' or uitvoering == 'LB' or uitvoering == 'GL' or uitvoering == 'SP' or uitvoering == 'AA' or uitvoering == '' or uitvoering == 'EDB' or uitvoering == 'BUB' or uitvoering == 'PZ' or uitvoering == 'AK' or uitvoering == 'EZD' or uitvoering == 'HT' or uitvoering == 'EAD' or uitvoering == 'PA' or uitvoering == 'PD' or uitvoering == 'EAB' or uitvoering == 'EZB'):
                print 'UITVOERING:', uitvoering
                uitvoering = 'AA'
            if not (voorraadcode == 'V' or voorraadcode == 'S' or voorraadcode == 'I' or voorraadcode == 'P' or voorraadcode == 'N' or voorraadcode == 'O' or voorraadcode == 'T' or voorraadcode == ''):
                print 'VOORRAADCODE:', voorraadcode
                voorraadocde = 'V'
            if not (netwerkcode == 'J' or netwerkcode == 'N' or netwerkcode == ''):
                print 'NETWERKCODE:', netwerkcode
                netwerkcode = 'J'
            if not (sectietitel == 'WB' or sectietitel == 'HB' or sectietitel == 'HL' or sectietitel == 'DO' or sectietitel == ''):
                print 'SECTIETITEL:', sectietitel
                sectietitel = ''
            if bijlage == 'DV':
                bijlage = 'DVD' 
            if not (bijlage == 'CD' or bijlage == 'DVD' or bijlage == 'DI' or bijlage == 'P' or bijlage == ''):
                print 'BIJLAGE:', bijlage
                bijlage = ''

# PRODUCT CATEGORIEN   
            nur1_id = None
            if nur1 != "":
                nur1_found = False
                nur1_search = self.pool.get('product.category').search(cr, uid, [('name','=',nur1)])
                for nur1_rec in self.pool.get('product.category').browse(cr, uid, nur1_search):
                    nur1_id = nur1_rec.id
                    nur1_found = True
                if not nur1_found:
                    vals = {
                        'name': nur1,
                        'type': 'normal',
                        'parent_id': 1,
                    }
                    nur1_id = self.pool.get('product.category').create(cr, uid, vals)   
                    nbr_product_categs = nbr_product_categs + 1  

# AUTEURSS
            auteur_id = None
            if auteur != "":
                auteur_found = False
                auteur_search = self.pool.get('res.author').search(cr, uid, [('name','=',auteur)])
                for auteur_rec in self.pool.get('res.author').browse(cr, uid, auteur_search):
                    auteur_id = auteur_rec.id
                    auteur_found = True
# CO-AUTEURS
            co_auteur_id = None
            if co_auteur != "":
                co_auteur_found = False
                co_auteur_search = self.pool.get('res.co.author').search(cr, uid, [('name','=',co_auteur)])
                for co_auteur_rec in self.pool.get('res.co.author').browse(cr, uid, co_auteur_search):  
                    co_auteur_id = co_auteur_rec.id
                    co_auteur_found = True

# PRODUCT TEMPLATE   
            if btw_code == 0 or btw_code == 1 or btw_code == 2:
                supplier_btw_code_id = 20
            else:
                supplier_btw_code_id = 14
            if btw_code == 0 or btw_code == 1 or btw_code == 2:
                cust_btw_code_id = 6
            else:
                cust_btw_code_id = 2

            product_template_id = None
            if isbn_nummer != "":
                product_template_found = False
                product_template_search = self.pool.get('product.template').search(cr, uid, [('unique_name','=',isbn_nummer)])
                for product_template_rec in self.pool.get('product.template').browse(cr, uid, product_template_search):
                    product_template_id = product_template_rec.id
                    product_template_found = True
                if not product_template_found:
                    vals = {
                        'uos_id': 1,
                        'mes_type': 'fixed',
                        'uom_id': 1,
                        'cost_method': 'standard',
                        'uos_coeff': 1.00,
                        'volume': 0,
                        'sale_ok': True,
                        'company_id': 1,
                        'produce_delay': 0.00,
                        'uom_po_id': 1,
                        'rental': False,
                        'type': 'product',
                        'sale_delay': 0.00,
                        'supply_method': 'buy',
                        'procure_method': 'make_to_stock',
                        'purchase_ok': True,
                        'unique_name': isbn_nummer,
                        'list_price': verkoopprijs,
                        'description': verkorte_titel,
                        'weight': gewicht,
                        'weight_net': gewicht,
                        'standard_price': verkoopprijs,
                        'categ_id': nur1_id,
                        'name': verkorte_titel[:128],
                        'supplier_taxes_id': [supplier_btw_code_id],
                        'taxes_id': [cust_btw_code_id],
                    }
                    product_template_id = self.pool.get('product.template').create(cr, uid, vals)   
                    nbr_product_template_a = nbr_product_template_a + 1  
                else:
                    vals = {
                        'list_price': verkoopprijs,
                        'description': verkorte_titel,
                        'weight': gewicht,
                        'weight_net': gewicht,
                        'standard_price': verkoopprijs,
                        'categ_id': nur1_id,
                        'name': verkorte_titel[:128],
                    }
                    product_template_upd = self.pool.get('product.template').write(cr, uid, [product_template_id], vals)   
                    nbr_product_template_c = nbr_product_template_c + 1  

# PRODUCT PRODUCT   
            product_product_id = None
            if isbn_nummer != "":
                product_product_found = False
                product_product_search = self.pool.get('product.product').search(cr, uid, [('default_code','=',isbn_nummer)])
                for product_product_rec in self.pool.get('product.product').browse(cr, uid, product_product_search):
                    product_product_id = product_product_rec.id
                    product_product_found = True
                if not product_product_found:
                    vals = {
                        'active': True,
                        'product_tmpl_id': product_template_id,
                        'track_outgoing': False,
                        'track_incoming': False,
                        'valuation': 'manual_periodic',
                        'track_production': False,
                        'sale_line_warn': 'no-message',
                        'purchase_line_warn': 'no-message',
                        'ean13': ean_code,
                        'default_code': isbn_nummer,
                        'name_template': verkorte_titel[:128],
                        'print_number': druknummer,
                        'release_date': verschijningsdatum,
                        'artikel_status': artikel_status,
                        'voorraadcode': voorraadcode,
                        'jaar_release1': jaar_1ste_verschijning,
                        'illustraties': illustraties,
                        'uitgave_soort': uitgavesoort,
                        'co_editie': co_edities,
                        'awso_code': awso_code,
                        'netwerkcode': netwerkcode,
                        'uitvoering': uitvoering,
                        'substituut_isbn': substituut_isbn,
                        'set_isbn': set_code,
                        'nbr_paginas': paginas,
                        'sectietitel': sectietitel,
                        'hoofdtitel': hoofdtitel,
                        'oorsprtitel': oorspronkelijke_titel,
                        'imprint': imprint,
                        'deeltitel': deeltitel,
                        'ondertitel': ondertitel,
                        'reeksnaam': reeksnummer,
                        'reeksnummer': nummer_binnen_reeks,
                        'depotnummer': depotnummer[:32],
                        'avi_niveau': avi_niveau,
                        'bijlage': bijlage,
                        'formaat': formaat,
                        'oorsprtaal': oorspronkelijke_taal[:32],
                        'distributeur': distributeur[:32],
                        'taalcode': taalcode[:32],
                        'uitgevernummer': uitgevernummer[:32],
                        'fondscode': fondscode[:32],
                        'btw21': btw21,
                        'co_author_id': co_auteur_id,
                        'author_id': auteur_id,
                        'co_author_temp': co_auteur,
                        'author_temp': auteur,
                        'combined_vat': combined_vat,
                        'btw_code_file': btw_code,
                    }
                    product_product_id = self.pool.get('product.product').create(cr, uid, vals)   
                    nbr_product_product_a = nbr_product_product_a + 1  

#                    if supplier_found:
#                        vals = {
#                            'name': supplier_id,
#                            'sequence': 1,
#                            'company_id': 1,
#                            'qty': 1.00,
#                            'delay': 1,
#                            'min_qty': 1.00,
#                            'product_id': product_product_id,
#                        }
#                        product_supplier_id = self.pool.get('product.supplierinfo').create(cr, uid, vals)
                    sql_stat = 'insert into product_taxes_rel (prod_id, tax_id) values(%d, %d)' % (product_template_id, cust_btw_code_id)
                    cr.execute(sql_stat)
                    sql_stat = 'insert into product_supplier_taxes_rel (prod_id, tax_id) values(%d, %d)' % (product_template_id, supplier_btw_code_id)
                    cr.execute(sql_stat)


                else:
                    vals = {
                        'ean13': ean_code,
                        'default_code': isbn_nummer,
                        'name_template': verkorte_titel[:128],
                        'print_number': druknummer,
                        'release_date': verschijningsdatum,
                        'artikel_status': artikel_status,
                        'voorraadcode': voorraadcode,
                        'jaar_release1': jaar_1ste_verschijning,
                        'illustraties': illustraties,
                        'uitgave_soort': uitgavesoort,
                        'co_editie': co_edities,
                        'awso_code': awso_code,
                        'netwerkcode': netwerkcode,
                        'uitvoering': uitvoering,
                        'substituut_isbn': substituut_isbn,
                        'set_isbn': set_code,
                        'nbr_paginas': paginas,
                        'sectietitel': sectietitel,
                        'hoofdtitel': hoofdtitel,
                        'oorsprtitel': oorspronkelijke_titel,
                        'imprint': imprint,
                        'deeltitel': deeltitel,
                        'ondertitel': ondertitel,
                        'reeksnaam': reeksnummer,
                        'reeksnummer': nummer_binnen_reeks,
                        'depotnummer': depotnummer[:32],
                        'avi_niveau': avi_niveau,
                        'bijlage': bijlage,
                        'formaat': formaat,
                        'oorsprtaal': oorspronkelijke_taal[:32],
                        'distributeur': distributeur[:32],
                        'taalcode': taalcode[:32],
                        'uitgevernummer': uitgevernummer[:32],
                        'fondscode': fondscode[:32],
                        'btw21': btw21,
                        'co_author_id': co_auteur_id,
                        'author_id': auteur_id,
                        'co_author_temp': co_auteur,
                        'author_temp': auteur,
                        'combined_vat': combined_vat,
                        'btw_code_file': btw_code,
                    }
                    product_product_upd = self.pool.get('product.product').write(cr, uid, [product_product_id], vals)   
                    nbr_product_product_c = nbr_product_product_c + 1  

            cr.commit()
              
        print "End of Import Job - Number of lines processed: ", nbr_lines
        print "Nbr of product categories added: ", nbr_product_categs
        print "Nbr of product templates added: ", nbr_product_template_a
        print "Nbr of product templates changed: ", nbr_product_template_c
        print "Nbr of product products added: ", nbr_product_product_a
        print "Nbr of product products changed: ", nbr_product_product_c
        cr.commit()
        raise osv.except_osv(_('Verwerkt'), _('Number of lines processed: ' + str(nbr_lines)))
        return True

class supplier_init_wizard(osv.TransientModel):
    _name = "supplier.init.wizard"

    _columns = {
    }

    def supplier_init(self, cr, uid, ids, context=None):
        print 'START SUPPLIER INIT'
        nbr_books = 0
        nbr_books_1000 = 0
        nbr_suppliers_added = 0
        nbr_suppliers_deleted = 0

        result = {}
        sql_stat = "select default_code, product_tmpl_id, distributeur from product_product"
        cr.execute(sql_stat)

        prodsupp_obj = self.pool.get('product.supplierinfo')
        print 'START BROWSE'

        for sql_res in cr.dictfetchall():
            nbr_books = nbr_books + 1
            nbr_books_1000 = nbr_books_1000 + 1

            default_code = sql_res['default_code']
            distributor = sql_res['distributeur']
            product_tmpl_id = sql_res['product_tmpl_id']

            distributor_found = False
            supplier = 0
      	    sql_stat = "select supplier_id from res_distributor where name = '%s'" % (distributor, )
            cr.execute(sql_stat)
            for sql_res in cr.dictfetchall():
                supplier = sql_res['supplier_id']
                distributor_found = True

            if distributor_found and not(supplier == 0):
                sql_stat = "select id from product_supplierinfo where name = %d and product_id = %d" % (supplier, product_tmpl_id, )
                cr.execute(sql_stat)
                prodsupp_found = False
                for sql_res in cr.dictfetchall():
                    prodsupp_found = True
                if not prodsupp_found:
                    vals = {
                        'name': supplier,
                        'sequence': 1,
                        'company_id': 1,
                        'qty': 1.00,
                        'delay': 1,
                        'min_qty': 1.00,
                        'product_id': product_tmpl_id,
                    }
                    product_supplier_id = self.pool.get('product.supplierinfo').create(cr, uid, vals)
                    nbr_suppliers_added = nbr_suppliers_added + 1
            else:
                sql_stat = "select id from product_supplierinfo where name = %d and product_id = %d" % (supplier, product_tmpl_id, )
                cr.execute(sql_stat)
                for sql_res in cr.dictfetchall():
                    sql_stat = "delete from product_supplierinfo where id = %d" % (sql_res['id'])
                    cr.execute(sql_stat)
                    nbr_suppliers_deleted = nbr_suppliers_deleted + 1

            if nbr_books_1000 > 999:
                print 'Nbr books: ',nbr_books,' (',nbr_suppliers_added,'-',nbr_suppliers_deleted,')'
                nbr_books_1000 = 0

        print 'END SUPPLIER INIT'
        print 'Nbr books: ',nbr_books
        print 'Nbr suppliers added: ',nbr_suppliers_added
        print 'Nbr suppliers deleted: ',nbr_suppliers_deleted
        cr.commit()
        raise osv.except_osv(_('Verwerkt'), _('Number of lines processed: ' + str(nbr_books)))
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: