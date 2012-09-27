	/*THIS FUNCTION SHOW WAIT ICON*/
	function spinner()
	{
		/*obj = $("#container_pane")[0]
		h = ((document.documentElement.clientHeight / 2)+50).toFixed(1)+ 'px'
		w = ((document.documentElement.clientWidth)-(parseInt($("#container_pane").width(),'10')/2)-40).toFixed(1) + 'px'*/
		
		w = parseInt($.clientCoords()['w'],"10")
		l = Math.round((parseInt($.clientCoords()['w'])-360)/2,2)+'px'
		
		
		if($('#spinner').length==0)
		{
			ingra_list = $("<img id='spinner' alt='Loading' style='display:none' src='/qatech/resources/images/loading.gif'/>").appendTo("body")
			//ingra_list.css("display","")
			$.blockUI({ message: ingra_list, css: {width:'340px',height:'auto',top:'40%',left:l,backgroundColor:'#e8e8e8'},allowBodyStretch:true,cursor:'arrow'});
		}
		else if ($('#spinner').css('display')=='none')
		{
			//$('#spinner').css('display','')
			$.blockUI({ message: ingra_list, css: {width:'340px',height:'auto',top:'40%',left:l,backgroundColor:'#e8e8e8'},allowBodyStretch:true,cursor:'arrow'}); 
		}
		else
		{
			//$("#spinner").hide()
			$.unblockUI(); 
			return true;
		}
	}
	
	/*THIS FUNCTION THE HEIGHT AND WIDTH OF THE CLIENT*/
	$.clientCoords = function()
	{
	    if(window.innerHeight || window.innerWidth){
	        return {w:window.innerWidth, h:window.innerHeight}
	    }
	    return {
	        w:document.documentElement.clientWidth,
	        h:document.documentElement.clientHeight
	    }
	}
	
	/*THIS FUNCTION ACCEPT THE DIV AND MAKE IT 100% TO THE AVAILABLE SPACE; PARAMS-->div object */	
	function div_height(div)
	{
		$("#contain_pane").attr("height","100%")
		wh = document.documentElement.clientHeight
		dh = $("#"+div)[0].offsetHeight
		if (parseInt(wh,"10") >= parseInt(dh,"10"))
		{$("#"+div).css("height",wh+"px")}
		else
		{$("#"+div).css("height","100%")}
		
		/*This Code will mark all the field in the transaction whose master is deleted*/
		//$('select').find('option[master=no]').parent().css('color','red')
		$('select').find('option[master=no]').parent().css('background-color','#f97156')
	}

$.fn.fastSerialize = function() {
   var a = [];
   $('input,textarea,select,button', this).each(function() {
       var n = this.name;
       var t = this.type;
       if ( !n || this.disabled || t == 'reset' ||
			(t == 'radio') && this.checked ||
           (t == 'checkbox') && !this.checked ||
           (t == 'submit' || t == 'image' || t == 'button') && this.form.clicked != this ||
           this.tagName.toLowerCase() == 'select' && this.selectedIndex == -1)
           return;
       if (t == 'image' && this.form.clicked_x)
           return a.push(
               {name: n+'_x', value: this.form.clicked_x},
               {name: n+'_y', value: this.form.clicked_y}
           );
       if (t == 'select-multiple') {
           $('option:selected', this).each( function() {
               a.push({name: n, value: this.value});
           });
           return;
       }
       a.push({name: n, value: this.value});
   });
   return a;
};

function validation(obj,string_validation,empty_validation,no_validation)
{	
	
	var mob=/^\d+$/;
	var flt=/^((\d+(\.\d*)?)|((\d*\.)?\d+))$/;

	var return_type="true"
	for(i=0;i<obj.length;i++) 
		{	
		
			for(j=0;j<string_validation.length;j++) 
			{
				if(obj[i].name==string_validation[j])
					{	
						if(mob.test(obj[i].value))
							{
							//alert(string_validation[j]+" field should be charecter");
							new Notification(string_validation[j]+" field should be charecter");
							obj.elements[i].focus();
							return_type= "false"	
							break;
							}
					}
			}
		for(k=0;k<empty_validation.length;k++) 
			{
				if(obj[i].name==empty_validation[k])
					{	
						obj[i].value = obj[i].value.replace(/^\s+/g,"");//remove heading whitespace
						obj[i].value = obj[i].value.replace(/\s+$/g,"");//remove trailing whitespace

						if(obj[i].value.length < 1)
							{
							//alert(empty_validation[k]+" can't be left empty");
							new Notification(empty_validation[k]+" can't be left empty");
							obj.elements[i].focus();
							return_type= "false"
							break;								
							}
							
					}
			}
			
		for(k=0;k<no_validation.length;k++) 
			{
				if(obj[i].name==no_validation[k])
					{	
						if(obj[i].value!="")
						{
						
						if(!flt.test(obj[i].value) && !mob.test(obj[i].value))
							{
							
							//alert(no_validation[k]+" should be number");
							new Notification(no_validation[k]+" should be number");
							obj.elements[i].focus();
							return_type= "false";
							break;								
							}
						}	
							
					}
			}
		
			
		
			if(return_type=='false')
				break;
		}
return return_type
}

function delete_row(tr_element,v)
	{	
		var root=tr_element.parentNode;
		var allrows = root.getElementsByTagName('tr');
		if(allrows.length>parseInt(v))
			{
				if (confirm('Do you want to delete this row?'))
					$(tr_element).remove();
				else
					return false;
			}
		else
			new Notification("you can't remove this row");
	}
function addrow_inhartex(id,e,id2,v)
	{	
		var key;
		var v=parseInt(v);
		if (e=='plus')
			key=13
		
		else if(window.event)
			key = window.event.keycode;//IE
		else
			key = e.which;//firefox
		if(key == 13)
			{
				var root = id;//the root
				var allrows = root.getElementsByTagName('tr');
				var crow = allrows[v].cloneNode(true)
				var cInp = crow.getElementsByTagName('input');
				for(var i=0;i<cInp.length;i++)
					{
						if(cInp[i].name.indexOf('date')>=0)
							{
								bind_date_box(cInp[i],root)	
							}
						cInp[i].value='';
					}
				if (id2=='last')
					root.appendChild(crow);
				else
					{
					$(crow).insertBefore($('#'+id2))	
					}
				return true;
			}	
		else
			return false;
	}
	
	
function bind_date_box(obj,root)	
	{
		$(obj).removeClass()
		//var tr_element=$(obj.parentNode.parentNode).siblings()
		var _id=$(root).find("tr:last-child").find('input[name='+obj.name+']')[0].id
		obj.id=(obj.id).split('__')[0]+"__"+(parseInt(_id.split('__')[1])+1)
		new Widgets.Input($(obj), {"datepicker": true, "dateFormat": "yy-mm-dd"})
	}
	
/*show search option*/
function search_option(section, width, top, subsection)
{
	w = parseInt($.clientCoords()['w'],"10")
	l = Math.round((parseInt($.clientCoords()['w'])-(parseInt(width)+20))/2,2)+'px'
	if (!subsection)
	{ 
		$.get(section, function(data){
			$.blockUI({ message: data, css: {width:width+'px',height:'auto',top:top+'%',left:l,backgroundColor:'#e8e8e8'},allowBodyStretch:true,cursor:'pointer'});
			$("div.ac_results").css("z-index", 1001)
		});
	}
	else
	{
		$.get(section+"?subsection="+subsection, function(data){
			$.blockUI({ message: data, css: {width:width+'px',height:'auto',top:top+'%',left:l,backgroundColor:'#e8e8e8'},allowBodyStretch:true,cursor:'pointer'});
			$("div.ac_results").css("z-index", 1001)
		});
	}
}
/*THIS FUNCTION THE HEIGHT AND WIDTH OF THE CLIENT*/
$.clientCoords = function()
{
	if(window.innerHeight || window.innerWidth){
		return {w:window.innerWidth, h:window.innerHeight}
	}
	return {
		w:document.documentElement.clientWidth,
		h:document.documentElement.clientHeight
	}
}
/*SHOW GRID AS PER OPTIONS*/
function ok_grid(div, section)
{
	//data = $("#grid_option").find('input[type=radio]:checked').parent().parent().fastSerialize()
	// var x = $("#grid_option").find('input[type=radio]:checked').val()
	// if(x){
		data = $("#grid_option").fastSerialize()
		//$("#"+div).load("/purchasemanager/"+section+"/show_grid", data, function()
		$("#"+div).load(section, data, function()
			{
				$.unblockUI(); 
				return true;
			});
	// }
	// else{
		// new Notification("Select Radio Box");
	// }

}

/*CANCEL THE BLOCK UI*/
function cancel_grid(module, func)
{
	//display("container_pane", module, func)
	$.unblockUI(); 
	return true;
}
