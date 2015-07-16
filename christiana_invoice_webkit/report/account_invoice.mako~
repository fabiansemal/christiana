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
    font-size:12;
    font-weight:bold;
    padding-right:3px;
    padding-left:3px;
}
.list_invoice_table td {
    border-top : thin solid #EEEEEE;
    text-align:left;
    font-size:12;
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
    	text=text.replace('0.', '')
    	return text.replace('0,', '')
    %>
    <%
    def convert_num_to_tekst(text):
    	text=text.replace('0','-NUL-')
    	text=text.replace('1','-EEN-')
    	text=text.replace('2','-TWEE-')
    	text=text.replace('3','-DRIE-')
    	text=text.replace('4','-VIER-')
    	text=text.replace('5','-VIJF-')
    	text=text.replace('6','-ZES-')
    	text=text.replace('7','-ZEVEN-')
    	text=text.replace('8','-ACHT-')
    	text=text.replace('9','-NEGEN-')
    	text=text.replace(',','-KOMMA-')
    	text=text.replace('.','-KOMMA-')
    	return text.replace('--','-')
    %>

    
    
    %for inv in objects:
	    <% setLang(inv.partner_id.lang) %>
	    <br/>
	    <br/>
	    <div class="address">
	      %if hasattr(inv, 'commercial_partner_id'):
	        <table class="recipient">
	            %if inv.partner_id.id != inv.commercial_partner_id.id:
	            <tr><td class="name">${inv.commercial_partner_id.name or ''}</td></tr>
	            <tr><td>${inv.partner_id.title and inv.partner_id.title.name or ''} ${inv.partner_id.name }</td></tr>
	            %else:
	            <tr><td class="name">${inv.partner_id.title and inv.partner_id.title.name or ''} ${inv.partner_id.name }</td></tr>
	            %endif
	            %if inv.partner_id.for_attn_of:
	            	<tr><td>${inv.partner_id.for_attn_of}</td></tr>
	            %else:
	            	<tr><td>t.a.v. de boekhouding</td></tr>
	            %endif
	            %if inv.partner_id.parent_id:
	            <% address_lines = inv.partner_id.contact_address.split("\n")[1:] %>
	            %else:
	            <% address_lines = inv.partner_id.contact_address.split("\n") %>
	            %endif
	            %for part in address_lines:
	                %if part:
	                <tr><td>${part}</td></tr>
	                %endif
	            %endfor
	        </table>
	      %else:
	        <table class="recipient">
	            %if inv.partner_id.parent_id:
	            <tr><td class="name">${inv.partner_id.parent_id.name or ''}</td></tr>
	            <tr><td>${inv.partner_id.title and inv.partner_id.title.name or ''} ${inv.partner_id.name }</td></tr>
	            <% address_lines = inv.partner_id.contact_address.split("\n")[1:] %>
	            %else:
	            <tr><td class="name">${inv.partner_id.title and inv.partner_id.title.name or ''} ${inv.partner_id.name }</td></tr>
	            <% address_lines = inv.partner_id.contact_address.split("\n") %>
	            %endif
	            %for part in address_lines:
	                %if part:
	                <tr><td>${part}</td></tr>
	                %endif
	            %endfor
	        </table>
	      %endif
	    </div>
	    <br/>
	    <br/>
	    <h1 style="clear: both; padding-top: 20px;">
	        %if inv.type == 'out_invoice' and inv.state == 'proforma2':
	            ${_("PRO-FORMA")}
	        %elif inv.type == 'out_invoice' and inv.state == 'draft':
	            ${_("Draft FACTUUR")}
	        %elif inv.type == 'out_invoice' and inv.state == 'cancel':
	            ${_("Geannulleerde FACTUUR")}
	        %elif inv.type == 'out_invoice':
	            ${_("FACTUUR")}
	        %elif inv.type == 'in_invoice':
	            ${_("Supplier Invoice")}
	        %elif inv.type == 'out_refund':
	            ${_("Refund")} ${inv.number or ''}
	        %elif inv.type == 'in_refund':
	            ${_("Supplier Refund")}
	        %endif
	    </h1>
	
	    <table class="basic_table" width="100%">
	        <tr>
	        	<th style="text-align:left;">${_("Nummer")}</th>
	            <th class="date">${_("Datum")}</th>
	            <th class="date">${_("Vervaldatum")}</th>
	            <th style="text-align:left">${_("BTW Klant")}</th>
	        </tr>
	        <tr>
	        	<td style="text-align:left;">${inv.number}</td>
	            <td class="date">${formatLang(inv.date_invoice, date=True)}</td>
	            <td class="date">${formatLang(inv.date_due, date=True)}</td>
	            <td style="text-align:left">${inv.partner_id.vat or ''}</td>
	        </tr>
	    </table>

	    <div>
	    %if inv.del_addr_id.id:
			%if inv.del_addr_id.invoice_text:
				<table class="basic_table" width="100%">
					<tr>
						<th style="text-align:left;width:100px;">${_("Uw referentie")}:</th>
			    		<td style="text-align:left;"> ${inv.del_addr_id.invoice_text | n}</td>
			    	</tr>
		    	</table>
			%endif
	    %elif inv.partner_id.invoice_text:
	    	<table class="basic_table" width="100%">
	    		<tr>
	    			<th style="text-align:left;width:100px;">${_("Uw referentie")}:</th>
	        		<td style="text-align:left;"> ${inv.partner_id.invoice_text | n}</td>
	        	</tr>
        	</table>
	    %endif
	    </div>
	
	    <div>
	    %if inv.note1 :
	        <p class="std_text"> ${inv.note1 | n} </p>
	    %endif
	    </div>
	
	    <table class="list_invoice_table" width="100%" style="margin-top: 20px;" >
	        <thead>
	            <tr>
	                <th style="text-align:left;">${_("Pakbon")}</th>
	                <th style="text-align:center;width:45px;">${_("BTW")}</th>
	                <th style="text-align:center;width:45px;">${_("Totaal")}</th>
	            </tr>
	        </thead>
	        <tbody>
	        %for line in inv.invoice_line :
	            <tr >
	                <td VALIGN="top">${line.name and line.name or ''}</td>
	                <%
	                tot = (line.price_unit - (line.price_unit * line.discount / 100)) * line.quantity
	                %>
	                <td style="text-align:center" VALIGN="top">${ ', '.join([ formatLang(tax.amount, digits=get_digits(dp='Account')) for tax in line.invoice_line_tax_id ])| convert_percentage} %</td>
	                <td class="amount" VALIGN="top">${inv.currency_id.symbol} ${formatLang(tot, digits=get_digits(dp='Account'))}</td>
	            </tr>
	            %if line.formatted_note:
	            <tr>
	              <td class="formatted_note">
	                ${line.formatted_note| n}
	              </td>
	            </tr>
	            %endif
	        %endfor
	        </tbody>
	        <tfoot class="totals">
	            <tr>
	                <td colspan="2" style="text-align:right;border-right: thin solid  #ffffff ;border-left: thin solid  #ffffff ;">
	                    <b>${_("Netto :")}</b>
	                </td>
	                <td class="amount" style="border-right: thin solid  #ffffff ;border-left: thin solid  #ffffff ;">
	                    ${inv.currency_id.symbol} ${formatLang(inv.amount_untaxed, digits=get_digits(dp='Account'))}
	                </td>
	            </tr>
	            <tr class="no_bloc">
	                <td colspan="2" style="text-align:right; border-top: thin solid  #ffffff ; border-right: thin solid  #ffffff ;border-left: thin solid  #ffffff ;">
	                    <b>${_("BTW:")}</b>
	                </td>
	                <td class="amount" style="border-right: thin solid  #ffffff ;border-top: thin solid  #ffffff ;border-left: thin solid  #ffffff ;">
	                    ${inv.currency_id.symbol} ${formatLang(inv.amount_tax, digits=get_digits(dp='Account'))}
	                </td>
	            </tr>
	            <tr>
	                <td colspan="2" style="border-right: thin solid  #ffffff ;border-top: thin solid  #ffffff ;border-left: thin solid  #ffffff ;border-bottom: thin solid  #ffffff ;text-align:right;">
	                    <b>${_("Totaal:")}</b>
	                </td>
	                <td class="amount" style="border-right: thin solid  #ffffff ;border-top: thin solid  #ffffff ;border-left: thin solid  #ffffff ;border-bottom: thin solid  #ffffff ;">
	                    <b>${inv.currency_id.symbol} ${formatLang(inv.amount_total, digits=get_digits(dp='Account'))}</b>
	                </td>
	            </tr>
	        </tfoot>
	    </table>
	        <br/>
	    <table class="list_invoice_table" width="60%" style="margin-top: 20px;" >      
	        %if inv.tax_line :
	        <tr>
	            <th style="text-align:left;">${_("BTW %")}</th>
	            <th>${_("Base")}</th>
	            <th>${_("Tax")}</th>
	        </tr>
	        %for t in inv.tax_line :
	            <tr>
	                <td style="text-align:left;">${t.name}</td>
	                <td class="amount">${inv.currency_id.symbol} ${ formatLang(t.base, digits=get_digits(dp='Account')) }</td>
	                <td class="amount">${inv.currency_id.symbol} ${ formatLang(t.amount, digits=get_digits(dp='Account')) }</td>
	            </tr>
	        %endfor
	        %endif
	    </table>
	        <br/>   
	        <br/>Waar en echt verklaard voor de som van ${formatLang(inv.amount_total, digits=get_digits(dp='Account'))} € (${ formatLang(inv.amount_total, digits=get_digits(dp='Account'))| convert_num_to_tekst } EURO)
	        <br/>
	    %if inv.reference :
	        <p class="std_text">${_("Gelieve te betalen met volgende mededeling:")} ${inv.reference| n}</p>
	    %endif
	        <br/>
	        <br/>
	        
	    <%
	      inv_bank = inv.partner_bank_id
	    %>
<!--
	    <table class="list_bank_table" width="100%" >
	        <tr>
	            <th style="width:20%;">${_("Bank")}</th>
	            <td style="width:30%;text-align:left;">${inv_bank and inv_bank.bank_name or '-' } </td>
	            %if inv.partner_id and inv.partner_id.vat :
	            <th style="width:20%;">${_("Customer VAT No")}</th>
	            <td style="width:30%;">${inv.partner_id.vat or '-'}</td>
	            %else:
	            <td style="width:20%;"></td>
	            <td style="width:30%;"></td>
	            %endif
	        </tr>
	        <tr>
	            <th style="width:20%;">${_("Bank account")}</th>
	            <td style="width:50%;text-align:left;">${ inv_bank and inv_bank.acc_number or '-' }</td>
	            <th style="width:20%;">${_("Our VAT No")}</th>
	            <td style="width:30%;" class="vat">${inv.company_id.partner_id.vat or '-'}</td>
	        </tr>
	        <tr>
	            <th width="20%">${_("BIC")}</th>
	            <td style="width:30%;">${inv_bank and inv_bank.bank_bic or '-' }</td>
	        </tr>
	    </table>
-->
	    <br/>
	    %if inv.comment :
	        <p class="std_text">${inv.comment | carriage_returns}</p>
	    %endif
	    %if inv.note2 :
	        <p class="std_text">${inv.note2 | n}</p>
	    %endif
	    %if inv.fiscal_position.note :
	        <br/>
	        <p class="std_text">
	        ${inv.fiscal_position.note | n}
	        </p>
	    %endif
	    <p style="page-break-after:always"> </p>
	 	   
    %endfor
</body>
</html>
