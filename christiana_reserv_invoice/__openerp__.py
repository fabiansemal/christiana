#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##############################################################################
#
#
##############################################################################
{
    "name" : "Christiana Reservation Invoicing",
    "version" : "1.0",
    "author" : "SmartSolution",
    "category" : "Base",
    "description": """
""",
    "depends" : ["sale","stock","christiana_custom"],
#    "init_xml" : [],
    "update_xml" : [
        'christiana_reserv_invoice_view.xml',
#        'security/ir.model.access.csv'
        ],
    "active": False,
    "installable": True
}
