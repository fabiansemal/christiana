<html>
<head>
    <style type="text/css">
        ${css}

.list_invoice_table {
    border:thin solid #E3E4EA;
    text-align:center;
    border-collapse: collapse;
}
.list_invoice_table th {
    background-color: #EEEEEE;
    border: thin solid #000000;
    text-align:center;
    font-size:8;
    font-weight:bold;
    padding-right:3px;
    padding-left:3px;
}
.list_invoice_table td {
    border-top : thin solid #EEEEEE;
    text-align:left;
    font-size:8;
    padding-right:3px;
    padding-left:3px;
    padding-top:3px;
    padding-bottom:3px;
}
.list_invoice_table thead {
    display:table-header-group;
}

.list_invoice_det_table {
    border:thin solid #E3E4EA;
    text-align:center;
    border-collapse: collapse;
}
.list_invoice_det_table th {
    background-color: #EEEEEE;
    border: thin solid #000000;
    text-align:center;
    font-size:6;
    font-weight:bold;
    padding-right:3px;
    padding-left:3px;
}
.list_invoice_det_table td {
    border-top : thin solid #EEEEEE;
    text-align:left;
    font-size:6;
    padding-right:3px;
    padding-left:3px;
    padding-top:3px;
    padding-bottom:3px;
}
.list_invoice_det_table thead {
    display:table-header-group;
}

td.formatted_note {
    text-align:left;
    border-right:thin solid #EEEEEE;
    border-left:thin solid #EEEEEE;
    border-top:thin solid #EEEEEE;
    padding-left:10px;
    font-size:11;
}


.list_bank_table {
    text-align:center;
    border-collapse: collapse;
}
.list_bank_table th {
    background-color: #EEEEEE;
    text-align:left;
    font-size:12;
    font-weight:bold;
    padding-right:3px;
    padding-left:3px;
}
.list_bank_table td {
    text-align:left;
    font-size:12;
    padding-right:3px;
    padding-left:3px;
    padding-top:3px;
    padding-bottom:3px;
}


.list_tax_table {
}
.list_tax_table td {
    text-align:left;
    font-size:12;
}
.list_tax_table th {
}
.list_tax_table thead {
    display:table-header-group;
}


.list_total_table {
    border:thin solid #E3E4EA;
    text-align:center;
    border-collapse: collapse;
}
.list_total_table td {
    border-top : thin solid #EEEEEE;
    text-align:left;
    font-size:12;
    padding-right:3px;
    padding-left:3px;
    padding-top:3px;
    padding-bottom:3px;
}
.list_total_table th {
    background-color: #EEEEEE;
    border: thin solid #000000;
    text-align:center;
    font-size:12;
    font-weight:bold;
    padding-right:3px
    padding-left:3px
}
.list_total_table thead {
    display:table-header-group;
}


.no_bloc {
    border-top: thin solid  #ffffff ;
}

.right_table {
    right: 4cm;
    width:"100%";
}

.std_text {
    font-size:12;
}

tfoot.totals tr:first-child td{
    padding-top: 15px;
}

th.date {
    width: 140px;
}

td.amount, th.amount {
    text-align: right;
    white-space: nowrap;
}
.header_table {
    text-align: center;
    border: 1px solid lightGrey;
    border-collapse: collapse;
}
.header_table th {
    font-size: 12px;
    border: 1px solid lightGrey;
}
.header_table td {
    font-size: 12px;
    border: 1px solid lightGrey;
}

td.date {
    white-space: nowrap;
    width: 90px;
}

td.vat {
    white-space: nowrap;
}
.address .recipient {
    font-size: 12px;
    margin-right: 120px; 
    float: right;
}

    </style>
</head>
<body>
    <%page expression_filter="entity"/>
    <%
    def carriage_returns(text):
        return text.replace('\n', '<br />')
    %>
    <%
    def replace_description(text):
        text=carriage_returns(text)
        return text.replace('- 100%', '')
    %>
    <%
    def convert_percentage(text):
    	return text.replace('0,', '')
    %>
    <% import datetime %>
    
    %for inv in objects:
	    <% setLang(inv.partner_id.lang) %>
	    <div class="address">
	        <table class="recipient">
	            <tr><td class="name">${inv.partner_id.parent_id.name or ''}</td></tr>
	            <tr><td>${inv.partner_shipping_id.title and inv.partner_shipping_id.title.name or ''} ${inv.partner_shipping_id.name }</td></tr>
	            <% address_lines = inv.partner_shipping_id.contact_address.split("\n")[1:] %>
	            %for part in address_lines:
	                %if part:
	                <tr><td>${part}</td></tr>
	                %endif
	            %endfor
	        </table>
	    </div>
	    <br/>
	    <% zicht = inv.line_ids[0].zichtzending %>
	    <h1 style="clear: both; padding-top: 20px;">
			%if zicht:
	            ${_("ZICHTZENDING")} ${inv.name}
	        %else:
	            ${_("VERZEND-NOTA")} ${inv.name}
	        %endif
	    </h1>
	    <br/>
	    ${_("Datum")}: ${formatLang( str(datetime.datetime.today()), date=True)}


	    <table class="list_invoice_table" width="100%" style="margin-top: 20px;" >
	        <thead>
	            <tr>
	                <th style="text-align:center;width:20px;">${_("ISBN")}</th>
	                <th>${_("Titel/Subtitel")}</th>
	                <th>${_("Auteur")}</th>
	                <th style="text-align:center;width:30px;">${_("Soort")}</th>
	                <th style="text-align:center;width:50px;">${_("Aantal")}</th>
	                <th style="text-align:center;width:50px;">${_("EH Prijs")}</th>
	                <th style="text-align:center;width:50px;">${_("Korting")}</th>
	                <th style="text-align:center;width:50px;">${_("VP incl BTW")}</th>
	            </tr>
	        </thead>
	        <tbody>
	        <% 
	        totaal = 0.00
	        aantal = 0.00
	        %>
            %for line in inv.line_ids :
                <% lineqty = line.qty_to_deliver - line.qty_retour %>
                %if lineqty > 0.00 :
                    <%
                    tot = round(((line.so_price * (100 - line.so_discount) / 100) * lineqty), 2)
                    totaal += tot
                    aantal += lineqty
                    %>
               
                    <tr >
                        <td VALIGN="top">${line.product_id and line.product_id.default_code or ''}</td>
                        <td VALIGN="top">${line.product_id and line.product_id.product_tmpl_id and  line.product_id.product_tmpl_id.name or ''}
                            %if line.product_id.ondertitel:
                                <br/>${line.product_id and line.product_id.ondertitel}
                            %endif
                        </td>   
                        <td VALIGN="top">
                            %if line.product_id.author_id:
                                ${line.product_id and line.product_id.author_id.name}
                            %endif
                        </td>
                        <td style="text-align:center;" VALIGN="top">${line.awso_code or ''}</td>
                        <td class="amount" VALIGN="top">${formatLang(lineqty or 0.0,digits=get_digits(dp='Account'))}</td>
                        <td class="amount" VALIGN="top">${formatLang(line.so_price, digits=get_digits(dp='Account'))}</td>
                        <td class="amount" VALIGN="top">${formatLang(line.so_discount, digits=get_digits(dp='Account'))} %</td>
                        <td class="amount" VALIGN="top">${formatLang(tot, digits=get_digits(dp='Account'))}</td>
                    </tr>
                %endif
            %endfor

	        </tbody>
	    </table>
	        <br/>
	        <h3>Totaal te faktureren bedrag: ${formatLang(totaal, digits=get_digits(dp='Account'))} EUR</h3>
	        <h3>Aantal boeken: ${formatLang(aantal, digits=get_digits(dp='Account'))}</h3>
	        <br/>
	    %if inv.comment :
	        <p>${inv.comment | carriage_returns}</p>
	    %endif
	        
	    <p style="page-break-after:always"> </p>
	 	   
    %endfor
</body>
</html>

