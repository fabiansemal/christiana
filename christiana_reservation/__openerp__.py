# -*- encoding: utf-8 -*-
{
	"name" : "Christiana Stock Reservation",
	"version" : "1.0",
	"author" : "Smart Solution",
	"description" : '''This module extends OpenERP for make stock reservation for sales orders at Boekbedrijf Christiana''',
	"website" : "http://",
	"category" : "stock",
	"depends" : ["product","sale","sale_journal","stock","purchase","procurement"],
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : ["christiana_reservation_view.xml"],
	"installable": True
}
