<html>
<body>
 Dit is een test
</body>
</html><html>
<head>
     <style type="text/css">
                ${css}
            </style>
</head>
<body>
    %for o in objects:
    <% setLang(o.partner_id.lang) %>
		<table class="shipping_address" width="100%">
        	<tr>
        		<td width="70%">
                    <b>${_("Shipping address :")}</b>
                    ${ (o.partner_shipping_id and o.partner_id.title and o.partner_shipping_id.title.name) or ''}</br>
                    ${ (o.partner_shipping_id and o.partner_shipping_id.name) or '' }</br>
                    ${o.partner_shipping_id.street or ''|entity}</br>
           			%if o.partner_shipping_id.street2 :
               			${o.partner_shipping_id.street2 or ''|entity}</br>
          			%endif
           				${o.partner_shipping_id.zip or ''|entity}, ${o.partner_shipping_id.city or ''|entity}</br>
          			%if o.partner_shipping_id.country_id :
               			${o.partner_shipping_id.country_id.name or ''|entity}</br></br>
          			%endif
          		</td>
             </tr>
		</table>
		</br>
		</br>
		<table class="tr_bottom_line">
			<tr>
				<td width="10%">
					<b>${_("Datum")}</b>
				</td>
				<td width="40%">
					<b>${_("Naam")}</b>
				</td>
				<td width="10%">
					<b>${_("Code")}</b>
				</td>
				<td width="10%">
					<b>${_("Template")}</b>
				</td>
				<td width="10%" align="right">
					<b>${_("EH Prijs")}</b>
				</td>
				<td width="10%" align="right">
					<b>${_("Hoev")}</b>
				</td>
			</tr>
		</table>
    
    %for line in o.line_ids:
    	<table class="tr_bottom_line_dark_grey">
    		<tr>
    			<td width="10%"> 
    				${ o.date_created }
    			</td>
    			<td width="40%">
    				${ o.scan_id.partner_id.name }
    			</td>
    			<td width="10%">
    				${ line.product_id.default_code }
    			</td>
    			<td width="10%">
    				${ line.product_id.name_template }
    			</td>
    			<td width="10%" style="text-align:right">
    				${ formatLang(line.so_price , digits=get_digits(dp='Product Price')) }
    			</td>
    			<td width="10%" style="text-align:right">
    				${ formatLang(line.qty_to_deliver, digits=get_digits(dp='Account')) }
    			</td>
    		</tr>
    	</table>
    %endfor
    	 <p style="page-break-after:always"></p>
   %endfor
</body>
</html>

