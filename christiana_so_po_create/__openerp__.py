#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##############################################################################
#
#
##############################################################################
{
    "name" : "Christiana SO PO Create",
    "version" : "1.0",
    "author" : "SmartSolution",
    "category" : "Base",
    "description": """
""",
    "depends" : ["base","sale","purchase"],
#    "init_xml" : [],
    "update_xml" : [
        'christiana_so_po_create_view.xml',
#        'security/ir.model.access.csv'
        ],
    "active": False,
    "installable": True
}
