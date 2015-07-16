# -*- encoding: utf-8 -*-
{
	"name" : "Christiana Customizations",
	"version" : "1.0",
	"author" : "Smart Solution",
	"description" : '''This module extends OpenERP for the needs of Boekbedrijf Christiana''',
	"website" : "http://",
	"category" : "product",
	"depends" : ["product","sale","account","warning","stock","christiana_reservation"],
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : ["christiana_custom_view.xml"],
	"installable": True
}
