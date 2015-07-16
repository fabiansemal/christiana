#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##############################################################################
#
#
##############################################################################
{
    "name" : "Christiana Discount",
    "version" : "1.0",
    "author" : "SmartSolution",
    "category" : "Base",
    "description": """
""",
    "depends" : ["base","sale","product","christiana_custom"],
#    "init_xml" : [],
    "update_xml" : [
        'christiana_so_discount_view.xml',
#        'security/ir.model.access.csv'
        ],
    "active": False,
    "installable": True
}
