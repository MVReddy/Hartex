// Displaying the details of work order in grid
function work_order_grid()
{	
	$('#container_pane').load("/purchasemanager/work_order/wo_details", function(){
		div_height("container_pane");
	});
}
// Craeting the new work order
function create_wo(){
	$('#container_pane').load("/purchasemanager/work_order/create_wo", function(){
		div_height("container_pane");
	});	
}
function ok_wo_grid(){

}
// ###   FOR PURCHASE TYPE MASTER	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
/*SHOW GRID AS PER OPTIONS*/
var search_wo_uuid = {} // This  help for next and previus button
function ok_wo_grid(div, section){
		$.unblockUI(); 
		
		search_wo_uuid = {}
		var found_ptype = "false"
		//data = $("#grid_option").find('input[type=radio]:checked').parent().parent().fastSerialize()
		data = $("#grid_option").fastSerialize()
		$.getJSON("/purchasemanager/work_order/total_wo_uuid.json/?find_item_uuid=true", data, 
		function(json)
		{	
			search_wo_uuid = JSON.stringify(json['search_wo_uuid'])
			show_wo_grid(div);
		});
}
function show_wo_grid(div){
		$("#"+div).load("/purchasemanager/work_order/show_wo_grid?search_wo_uuid="+encodeURIComponent(search_wo_uuid), function()
		{
			return true;
		});
}

function next_prev_wo(wo_no,  view_mode, status){
		/*
		Id = table id 
		status = "next", or "prev"
		tmpl = tmpl name
		*/
		spinner()
		var url = "/purchasemanager/work_order/next_prev_wo?status="+status
		url = url + "&wo_no="+encodeURIComponent(wo_no);
		url = url + "&view_mode="+encodeURIComponent(view_mode);
		url = url + "&search_wo_uuid="+encodeURIComponent(search_wo_uuid);
		$("#container_pane").load(url,
		function (){
			if(view_mode == 'true'){
				$("#container_pane").find('input:not([id=prev],[id=next],[id=cancel_wo]),select,option,textarea').attr('disabled',true);
			}
			div_height("container_pane");
			spinner()
		});
	
}


// Finding the details of rc_no, from select button 
function rc_no_details(rc_no, obj){
	var t = $('#wo_form').find('input:[name=irv_st]').val()
	var w = $('#wo_form').find('input:[name=irv_cs]').val()
	var y = $('#wo_form').find('input:[name=irv_dt]').val()
	//var x = $('#wo_form').find('input:[name=irv_t]').val()
	//$('#create_wo').removeAttr('disabled')
	
	if(t == "purchase confirm"){
		if(rc_no != ""){
		
		
		document.getElementById('department').disabled = false;
		document.getElementById('rc_no').disabled = false;
		document.getElementById('cost_centre').disabled = false;
		document.getElementById('section').disabled = false;
		//document.getElementById('rc_date').value = x;
		document.getElementById('rc_no').value = rc_no;
		document.getElementById('employee_name').disabled = false;
		
		//document.getElementById('department').value = y;
		//document.getElementById('cost_centre').value = w;
		$.getJSON("/purchasemanager/work_order/irv_no_details1.json?rc_no="+encodeURIComponent(rc_no), function(json){
			if(json != ""){
				$("#rc_no").val(json['irv_no']);
				//$("#employee_name").val(json['employee_name']);
				//$("#return_before").val('');
				$("#rc_date").val(json['irv_date']);
				//$("#vendor_name").val(json['vendor_name']);	
				//$("#vendor_code").val(json['vendor_code']);
				$("#department").val(json['department_select']);	
				$("#section").val(json['section_select']);
				$("#cost_centre").val(json['cost_select']);
				//$("#wo_value").val('');
				//$("#payment_mode").val('');
				//$("#payment_terms").val('');

				
				//vendor_details(json['vendor_name']);
				//get_materials_details1(rc_no);
				//$("#containerpane").load("/purchasemanager/workorder/get_materials_details1?rc_no="+encodeURIComponent(rc_no)+"&ref_no="+encodeURIComponent(ref));

				}});
		
		

		}
	}
	else if(rc_no != ""){	
			
		$.getJSON("/purchasemanager/work_order/rc_no_details.json?rc_no="+encodeURIComponent(rc_no), function(json){
			if(json != ""){
				$("#rc_no").val(json['rc_nrc_no']);
				$("#employee_name").val(json['employee_name']);
				$("#return_before").val('');
				$("#rc_date").val(json['rc_nrc_date']);
				$("#vendor_name").val(json['vendor_name']);	
				$("#vendor_code").val(json['vendor_code']);
				$("#department").val(json['department']);	
				$("#section").val(json['section']);
				$("#cost_centre").val(json['cost_centre']);
				$("#wo_value").val('');
				$("#payment_mode").val('');
				$("#payment_terms").val('');

				
				vendor_details(json['vendor_name']);
				rc_item_details(rc_no)
			}
			else{
				$('#wo_form').each(function(){
						this.reset();
				});				
			}
		});	
	}
	else{
		$('#wo_form').each(function(){
				this.reset();
		});
	}	
	// ELSE HIDE THE ITEM TABLE
}

/**  Finding the vendor details ***/
function vendor_details(vendor_name){
	$.getJSON("/purchasemanager/work_order/vendor_details.json?vendor_name="+encodeURIComponent(vendor_name), function(json){
		if(json != ""){
			$("#vendor_code").val(json['vendor_code']);
			$("#payment_mode").val(json['payment_mode']);
			$("#payment_terms").val(json['payment_terms']);
		}
		else{
			$("#vendor_code").val('');
			$("#payment_mode").val('');
			$("#payment_terms").val('');
		}
	});
}

function rc_item_details(rc_no){
	$('#rc_item_details').load("/purchasemanager/work_order/rc_item_details?rc_no="+encodeURIComponent(rc_no), function(){
	});	
}
// Saving the work order value
function save_wo(obj){
	var string_validation = new Array("vendor_name");
	var empty_validation = new Array("job_desc", "job_qty", "job_rate", "return_before","payment_mode","payment_terms","wo_value","rc_no","vendor_name");
	var no_validation = new Array("job_qty", "job_rate", "rate","value","wo_value");
	var validate=validation(obj.form,string_validation,empty_validation,no_validation)
	if(validate != "false"){
		var vendor_code = $("#vendor_code").val()
		$('#container_pane').load("/purchasemanager/work_order/save_wo1?vendor_code="+encodeURIComponent(vendor_code), $("#wo_form").serializeArray(), function(data){
			div_height("container_pane");
		});	
	}
}
// caculating the 'po qty' and 'po value'
function find_wo_value(tab,obj,rate)
	{	
		var total_po_qty = 0.0
		var w_value = 0.0
		//var po_value_total = $("#"+id2)[0].value
		var allrows = $("#"+tab)[0].getElementsByTagName('tr');
		//var rate = document.getElementById('rate').value
		if(isNaN(rate) || parseFloat(rate) < 0){
			new Notification("Rate should be positive Number only");
			 obj.value = ""
			//document.getElementById('rate').value =''
			//var temp_value = $('#'+tab).find('input:[name=value]')
			var temp_value = $('#'+tab).find('input:[name=value]')
			for(i=0;i<temp_value.length;i++)
			{
				temp_value[i].value = ''
			}
			return false;
		}
		for(var i=2;i<allrows.length;i++) // i is start from 2 because of that from 2 row input field is there
			{	
				var t_po_qty = allrows[i].getElementsByTagName("input")[4].value
				//var rate = allrows[i].getElementsByTagName("input")[3].value
				var t_rate = allrows[i].getElementsByTagName("input")[5].value
				//if(parseFloat(t_po_qty) > 0  && parseFloat(rate) > 0  && parseFloat(t_value) > 0)
				if(parseFloat(t_po_qty) > 0  && parseFloat(rate) > 0 )
					{	
						var item_value = t_po_qty * t_rate
						allrows[i].getElementsByTagName("input")[6].value = item_value
						
						w_value+=item_value
					}
			}
			//This is updating from job description
			//$("#wo_value")[0].value = w_value
			
			//$("#"+id2)[0].value = parseFloat(po_value_total) - parseFloat(prev_value_ofthis_item) + parseFloat(value)				
	}

var uuid_checked
function edit_wo(){
	var len_checked = $('#wo_grid_details').find('input:checked').length;
	if (len_checked == 1){
			uuid_checked = $('#wo_grid_details').find('input:checked').val();
			//var url = "/hartex/requisitions/edit_requisitions?current_department="+encodeURIComponent(current_department)
			$('#container_pane').load("/purchasemanager/work_order/edit_wo?wo_uuid="+encodeURIComponent(uuid_checked), function(){
				div_height("container_pane");
			});
		}

	else{
	new Notification("Select only one checked Box");
	}	
}

function update_wo(obj, wo_uuid){
	var string_validation = new Array("vendor_name");
	var empty_validation = new Array("return_before","payment_mode","payment_terms","wo_value","rc_no","vendor_name");
	var no_validation = new Array("rate","value","wo_value");
	var validate=validation(obj.form,string_validation,empty_validation,no_validation)
	if(validate != "false"){
	//alert(uuid_checked)
		var url = "/purchasemanager/work_order/update_wo?wo_uuid="+encodeURIComponent(wo_uuid)
		$('#container_pane').load(url, $("#wo_form").serializeArray(), function(data){
			div_height("container_pane");
		});	
	}
}

function view_wo(wo_uuid){
		uuid_checked = $('#wo_grid_details').find('input:checked').val();
		var url = "/purchasemanager/work_order/edit_wo?wo_uuid="+encodeURIComponent(wo_uuid);
		url = url + "&view_mode=true";
		$('#container_pane').load(url, function(){
			$("#container_pane").find('input:not([id=prev],[id=next],[id=cancel_wo]),select,option,textarea').attr('disabled',true);
			div_height("container_pane");
		});
}

//Posting the data
function post_wo(id)
{
	/*
	This function is posting the 'po details'. the selected checked box.
	*/
	parent_div = $("#"+id)
	child = parent_div.find('input[type=checkbox]:checked')
	id_list = new Array()
	for (x=0;x<child.length;x++)
	{
		id_list.push({'name':'ids','value':$(child[x]).val()})
	}
	if (id_list.length > 0)
	{
		$("#container_pane").load("/purchasemanager/work_order/post_wo/",id_list);
		div_height("container_pane");	
	}
	else
	{
		new Notification("No records selected to post");
	}
}
function work_job_description_value(){
		var temp_rate = $('#job_description').find('input:[name=job_rate]')
		var temp_qty = $('#job_description').find('input:[name=job_qty]')
		var temp_value = $('#job_description').find('input:[name=job_value]')
		var w_value = 0;
		for(i=0;i<temp_qty.length;i++)
		{			
			var jobqty = temp_qty[i].value 
			var jobrate = temp_rate[i].value
			/*
			if(isNaN(jobqty) || isNaN(jobrate)){
				temp_qty[i].value = ''
				temp_rate[i].value = ''
				temp_value[i].value = ''
			
			}
			else */
			if(isNaN(jobqty) || isNaN(jobrate)){
				new Notification("Qty and Rate numbers Only");
				temp_qty[i].value = ''
				temp_rate[i].value = ''
				temp_value[i].value = ''
			}
			else{
				if(parseFloat(jobqty) > 0 && parseFloat(jobrate) > 0){
					var job_value =  parseFloat(jobqty) * parseFloat(jobrate);
					temp_value[i].value = job_value;
					w_value = parseFloat(w_value) + parseFloat(job_value);
				}
				else{
					temp_value[i].value = 0;
				}
			}
			
		}
		$("#wo_value")[0].value = parseFloat(w_value);

	
}

function get_material(obj,val)
{	
	
 	var t = $('#wo_form').find('input:[name=rc_no]').val();
	
	$("#rc_item_details").load("/purchasemanager/work_order/get_materials_details1?ref_no="+encodeURIComponent(t)+"&ref_doc="+encodeURIComponent(val));
	
}
	
