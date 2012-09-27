# pylint: disable-msg=W0312, C0301, C0321, C0111, C0103, R0902, R0904, R0911, R0912, R0913, R0914, W0104, W0142
'''
This module is handling the 'po details'
'''
from __future__ import division
import time, cgi
import os
from  string import replace, join
from  datetime import date

import iris, aphrodite
from plugins.CheetahPlugin import CheetahRender
import json, hermes
from idea import Idea
from bwquery import bwQuery;

from apps.purchasemanager.modules.update_scaler import update_scaler
from apps.hartex.modules.python.hartex_module import hartex
from apps.hartex.modules.inventory import inventory
from apps.edp.modules import hartex_users

import pprint 
dic = []
__copyright__ = "Copyright 2005-2008 Brainwave Corp."
__license__ = "Proprietary"

class purchase(object):
	'''
	This class is handling the 'po details' of purchase manger.
	'''
	path = os.path.join(os.getcwd(), 'apps', 'purchasemanager', 'modules', 'purchase', 'resources', 'views')
	def __init__(self):
		self.aphrodite = aphrodite.Aphrodite('purchasemanager')
		
	@iris.expose
	@hartex_users.hartex_access_validate(module='purchasemanager')
	def default(self, *args, **kwargs):
		'''
		By default pass
		'''
		pass
	
	#Convert a dictinary with list as values to a list of dictionaries
	def convert_to_list_of_dict(self, *args, **kwargs):
		"""
		This function can accept list of columns with data dictionary or only the data dictionary.
		If both list of columns and data dictionary passed, it will return the list of dictionaries
		only containing those columns in the list
		
		If only data dictionary is passed, it will return the list of dictionaries with all the columns
		in the dictionary.
		
		@param args: is a list of keys of the kwargs dictionary
		@type object: a tuple
		
		@param kwargs: A dictionary with values as list, to be converted into list of dictionaries
		@type object: a dictionary
		
		@rtype: list
		@return: List of dictionaries
		"""
		return_list = []
		if len(args)>0 and len(kwargs)>0:
			if isinstance(kwargs.items()[0][1], list):
				for x in range(len(kwargs.items()[0][1])):
					return_dict = {}
					for y in args:
						return_dict[y] = kwargs[y][x]
					return_list.append(return_dict)
			else:
				return_dict = {}
				for y in args:
					return_dict[y] = kwargs[y]
				return_list.append(return_dict)
		elif len(kwargs) > 0:
			if isinstance(kwargs.items()[0][1], list):
				for x in range( len( kwargs.items()[0][1] )):
					return_dict = {}
					for y in kwargs.keys():
						return_dict[y] = kwargs[y][x]
					return_list.append(return_dict)
			else:
				return_list.append(kwargs)		
		return return_list
			
	@iris.expose
	def po_grid_option(self):
		'''
		For Displaying the po search input.
		'''
		return CheetahRender(data = {}, template = os.path.join(self.path, "po_grid_option.tmpl"))
	
	@iris.expose
	@hermes.service()		
	def total_po_uuid(self, **kwargs):
		'''
		Finding the all po uuid mased on given keywords
		po_uuid = {'po_no':"po_uuid"}
		return:{'searchg_po_uuid':{po_uuid}}
		'''
		p = iris.findObject('poseidon')
		search_po_uuid = {}
		data_header = []		
		if not kwargs['from']:
			kwargs['from'] = "2000-00-00"
		if not kwargs['to']:
			kwargs['to'] = time.strftime("%Y-%m-%d", time.localtime())
		if kwargs.get('post_status') == 'unposted':
			data_header.extend([{'name':'check', 'display':"check"}, 
								{'name':'edit', 'display':"edit"}])
			#temp_query = "subjects(subjects(subjects(*, 'is a', 'po'), 'post_status', 'unposted'), 'po date', %(from)s:%(to)s)"%(kwargs)
			temp_query = "subjects(subjects(*, 'post_status', 'unposted'), 'is a', 'po')"
		elif kwargs.get('post_status') == 'posted':
			#temp_query = "subjects(subjects(subjects(*, 'is a', 'po'), 'post_status', 'posted'), 'po date', %(from)s:%(to)s)"%(kwargs)
			temp_query = "subjects(subjects(*, 'post_status', 'posted'), 'is a', 'po')"
			data_header.append({'name':'veiw', 'display':"veiw"})
		else:
			data_header.extend([{'name':'po no', 'display':"po no"}, \
						{'name':'purchase type', 'display':"purchase type"}, \
						{'name':'vendor name', 'display':"vendor name"}, \
						{'name':'po date', 'display':"po date"},\
						{'name':'freight', 'display':"freight"}])
			po_temp_data = []
			grid_id = iris.root.set_control_data(po_temp_data)
			return CheetahRender(data={'data_header':data_header, 'grid_id':grid_id}, template = os.path.join(self.path, "grid.tmpl"))
		
		if kwargs.get('vendor_name'): # searching the data based on  vendor name
			r = "subjects(*, 'vendor name', '%s')" % (kwargs['vendor_name'])
			temp_query = replace(temp_query, "*", r)
		if kwargs.get('purchase_type'): # searching the data based on  purchase_type
			r = "subjects(*, 'purchase type', '%s')" % (kwargs['purchase_type'])
			temp_query = replace(temp_query, "*", r)
			
		if kwargs.get('po no'): # searching the data based on  po no, if not based on given date
			r = "subjects(*, 'po no', '%s')" % (kwargs['po no'])
			temp_query = replace(temp_query, "*", r)
		else:
			r = "subjects(*, 'po date' or 'ppo date', %(from)s:%(to)s)" % (kwargs)
			temp_query = replace(temp_query, "*", r)
		try:
			po_data = list(set( p.query("ids(%s)" %(temp_query)) ))
		except:
			po_data = []
		#print "temp_query ", temp_query	
		search_po_uuid = {}
		#print po_data
		for x in po_data:
			temp = bwQuery(x).val()[0]
			#pprint.pprint(temp)
			#search_po_uuid[temp.get('po no', ['NA'])[0]] = "%s" %bwQuery(x).ids()[0]
			if len(temp.get('ppo no', [''])[0]) < 1:
				search_po_uuid[temp.get('po no', [''])[0]] = "%s" %bwQuery(x).ids()[0]
			else:
				search_po_uuid[temp.get('ppo no', [''])[0]] = "%s" %bwQuery(x).ids()[0]
			#search_po_uuid[temp.get('po no', temp.get('ppo no', ['NA']))[0]] = "%s" %bwQuery(x).ids()[0] 	
		print "??? "*11
		print search_po_uuid
		return {'search_po_uuid':search_po_uuid}
	
	
	@iris.expose
	def show_po_grid(self, **kwargs):
		'''
		
		'''
		p = iris.findObject('poseidon')
		def edit(id):
			'''
			Making the edit link
			'''
			return '''
				<a href='#'><img src='/purchasemanager/resources/images/edit.png' onclick="edit_po_no('%(id)s')" class='imgbut' style='width:20px;height:20px;'/></a>
			''' % {"id":id}
			
		def show_details_ppo_no(id):
			'''
			Making the Link for details of ppo_no 
			'''
			return '''
				<a href='#'><img src='/purchasemanager/resources/images/revisionasd.png' onclick="ppo_no_details('%(id)s')" class='imgbut' style='width:20px;height:20px;'/></a>
			''' % {"id":id}	
		print "kwargs*************************************", kwargs
		data_header = []
		po_temp_data = []
		search_uuid = json.loads(kwargs.get('search_po_uuid', '{}'))
		temp = {}
		for uuid in search_uuid.values():
			temp = update_scaler.make_scaler(bwQuery(uuid).val()[0])
			print "::::::::::::::::::::::::::::::::::::::::::::::", str(temp.get('po no', 'NA'))
			print "uuid:::::::::::::::::::::::::::::::::::::::::::::::::::", uuid
			temp['po no'] = "<a href='javascript:show_po_report(\"%s\")'> %s </a>" %(uuid, str(temp.get('po no', 'NA')))
			if temp['post_status'] == "unposted" :
				temp['check'] = "<input type='checkbox' style='margin-top:0.4em' value='%s'></input>" %bwQuery(uuid).ids()[0]
				#temp['edit'] = "<a href='#'><img src='/purchasemanager/resources/images/edit.png' class='imgbut' style='width:20px;height:20px;'/></a>"
				temp['edit'] = edit(uuid)				
			else:
				temp['veiw'] = show_details_ppo_no(uuid)				
			po_temp_data.append(temp)				
		po_temp_data.sort(reverse=True)
		#po_temp_data.reverse()	
		#po_temp_data = [po_temp_data[x][1] for x in xrange( len(po_temp_data) )]		
		grid_id = iris.root.set_control_data(po_temp_data)
		#This is defining here because of edit and check button will come first
		if temp.get('post_status') == "unposted" :
			data_header.extend([{'name':'check', 'display':"check"}, 
									{'name':'edit', 'display':"edit"}])
		else:
			data_header.append({'name':'veiw', 'display':"veiw"})
		data_header.extend([{'name':'po no', 'display':"po no"}, \
					{'name':'purchase type', 'display':"purchase type"}, \
					{'name':'vendor name', 'display':"vendor name"}, \
					{'name':'po date', 'display':"po date"},\
					{'name':'freight', 'display':"freight"}])
		return CheetahRender(data={'data_header':data_header, 'grid_id':grid_id}, template = os.path.join(self.path, "grid.tmpl"))
		
	#Search the query based on given search option 
	@iris.expose
	def po_show_grid(self, **kwargs):
		'''
		Displaying the data into the grid, when user is clicking on ok.
		'''
		p = iris.findObject('poseidon')
		def edit(id):
			'''
			Making the edit link
			'''
			return '''
				<a href='#'><img src='/purchasemanager/resources/images/edit.png' onclick="edit_po_no('%(id)s')" class='imgbut' style='width:20px;height:20px;'/></a>
			''' % {"id":id}
			
		def show_details_ppo_no(id):
			'''
			Making the Link for details of ppo_no 
			'''
			return '''
				<a href='#'><img src='/purchasemanager/resources/images/revisionasd.png' onclick="ppo_no_details('%(id)s')" class='imgbut' style='width:20px;height:20px;'/></a>
			''' % {"id":id}		
		data_header = []		
		if not kwargs['from']:
			kwargs['from'] = "2000-00-00"
		if not kwargs['to']:
			kwargs['to'] = time.strftime("%Y-%m-%d", time.localtime())
		if kwargs.get('post_status') == 'unposted':
			data_header.extend([{'name':'check', 'display':"check"}, 
								{'name':'edit', 'display':"edit"}])
			temp_query = "subjects(subjects(subjects(*, 'post_status', 'unposted'), 'po date', %(from)s:%(to)s), 'is a', 'po')"%(kwargs)
		elif kwargs.get('post_status') == 'posted':
			temp_query = "subjects(subjects(subjects(*, 'po date', %(from)s:%(to)s), 'post_status', 'posted'), 'is a', 'po')"%(kwargs)
			data_header.append({'name':'veiw', 'display':"veiw"})
		else:
			data_header.extend([{'name':'po no', 'display':"po no"}, \
						{'name':'purchase type', 'display':"purchase type"}, \
						{'name':'vendor name', 'display':"vendor name"}, \
						{'name':'po date', 'display':"po date"},\
						{'name':'freight', 'display':"freight"}])
			po_temp_data = []
			grid_id = iris.root.set_control_data(po_temp_data)
			return CheetahRender(data={'data_header':data_header, 'grid_id':grid_id}, template = os.path.join(self.path, "grid.tmpl"))
		
		if kwargs.get('vendor_name'): # searching the data based on  vendor name
			r = "subjects(*, 'vendor name', '%s')" % (kwargs['vendor_name'])
			temp_query = replace(temp_query, "*", r)
		if kwargs.get('purchase_type'): # searching the data based on  purchase_type
			r = "subjects(*, 'purchase type', '%s')" % (kwargs['purchase_type'])
			temp_query = replace(temp_query, "*", r)
		try:
			po_data = list(set( p.query("ids(%s)" %(temp_query)) ))
		except:
			po_data = []
		po_temp_data = []
		for id in po_data:
			temp = update_scaler.make_scaler(bwQuery(id).val()[0])
			temp['po no'] = "<a href='javascript:show_po_report(\"%s\")'> %s </a>" %(id, str(temp.get('po no', 'NA')))
			if temp['post_status'] == "unposted" :
				temp['check'] = "<input type='checkbox' style='margin-top:0.4em' value='%s'></input>" %bwQuery(id).ids()[0]
				#temp['edit'] = "<a href='#'><img src='/purchasemanager/resources/images/edit.png' class='imgbut' style='width:20px;height:20px;'/></a>"
				temp['edit'] = edit(id)				
			else:
				temp['veiw'] = show_details_ppo_no(id)
			# temp['po qty']=str(temp.get('po qty'))+" "+temp['uom']		
			# temp['value(rs)']=temp.get('value')
			#po_temp_data.append((str(temp['po no']), temp))				
			po_temp_data.append(temp)				
		po_temp_data.sort(reverse=True)
		#po_temp_data.reverse()	
		#po_temp_data = [po_temp_data[x][1] for x in xrange( len(po_temp_data) )]		
		grid_id = iris.root.set_control_data(po_temp_data)
		#This is defining here because of edit and check button will come first
		data_header.extend([{'name':'po no', 'display':"po no"}, \
					{'name':'purchase type', 'display':"purchase type"}, \
					{'name':'vendor name', 'display':"vendor name"}, \
					{'name':'po date', 'display':"po date"},\
					{'name':'freight', 'display':"freight"}])
		return CheetahRender(data={'data_header':data_header, 'grid_id':grid_id}, template = os.path.join(self.path, "grid.tmpl"))
	
	@iris.expose
	def next_prev_ptype(self, **kwargs):
		'''
			Desc:Showing the item details in 'edit' or 'revised' mode, depend on tmpl given, 
				when user will click 'next' or 'prev' button,
			Parameter:'status': as a 'next' or 'prev', 'tmpl': for edit or revised 
					'ptype_code': item code  of the item
			return: Data as a dict type to the given tmpl
		'''
		p = iris.findObject('poseidon')
		
		search_uuid = json.loads(kwargs.get('search_po_uuid', '{}'))

		total_icode = search_uuid.keys()
		total_icode.sort()
		pos = total_icode.index(kwargs['po_no']) # position of the given item
		if kwargs['status'] == "prev":
			if pos == 0:
				show_icode = total_icode[-1] #showing the last item code, here we can send same data also if prev button end at 1 item only
			else:
				prev_item = pos - 1
				show_icode = total_icode[prev_item]
		else:
			if pos == len(total_icode) - 1 :
				show_icode = total_icode[0] # showing the first item code, here last data also we can send if next button should not come the first item level
			else:
				next_item = total_icode.index(kwargs['po_no']) + 1
				show_icode = total_icode[next_item]
		
		#This 2 line is prev one-- search_item_uuid - {'ptype_code':"uuid of that code"}
		#uuid = p.query("ids(subjects(subjects(*, 'is a', 'item master'), 'item code', '%s'))" % (show_icode))
		#kwargs['id'] = uuid[0]
		
		kwargs['id'] = search_uuid[show_icode]
	
		# if kwargs.get('tmpl') == "revise_item_master":
			# return  self.revise_item_master(**kwargs)
		return  self.create_or_edit(**kwargs)

	
#   **********************    START  INDENTS DATA **************************************	
	#for view indent from po
	@iris.expose
	def view_indents_po(self, **kwargs):
		'''
		This is displaying indents data into the grid
		'''
		p = iris.findObject('poseidon')
		current_department = "kjhskhjk"
		department_select = p.query("names(objects(subjects(*, 'is a', 'department master'),'department name', *))")
		department_select.sort()

		requisition_type = p.query("names(objects(subjects(subjects(subjects(*, \
						'department name', 'Purchase'), 'master', 'requisition type'), 'is a', 'other code master'), 'value', *))")
		requisition_type.sort()
		grid_data = self.view_indents_grid()
		return CheetahRender(data={'current_department':current_department, 'department_select':department_select, \
		'requisition_type':requisition_type, 'data_header':grid_data[0], 'grid_id':grid_data[1]},template = os.path.join(self.path, "view_indents_po.tmpl"))
	
	# Creating the indent grid
	@iris.expose
	def view_indents_grid(self,  **kwargs):
		'''
		This is displaying the indents data into grid.
		'''	
		p = iris.findObject('poseidon')
		req_temp_data = []
		temp_req = []
		if kwargs.has_key('department') and kwargs.has_key('requisition_type'):
			temp_req = p.query("ids(subjects(subjects(subjects(subjects(subjects(*, 'department', '%s'), 'requisition_type', '%s'), 'pirv_no', *), 'status', 'closed'), 'is a', 'requisition'))" \
			% (str(kwargs['department']), str(kwargs['requisition_type'])))
		
		for uid in temp_req:
			#uid=p.query("ids(subjects(subjects(subjects(*, 'is a','vendor_master'),'revision_no','%s'),'vendor_registration_no','%s'))"%(revision_no,vendor_registration_no))
			temp = update_scaler.make_scaler(bwQuery(uid).val()[0])	
			#temp['check'] = "<input type='checkbox' name='uuid' id='uuid' style='margin-top:0.4em' value='%s'></input>" %bwQuery(uid).ids()[0]
			req_temp_data = req_temp_data + [temp]
		data_header = [{'name':'check', 'display':'Check'}, {'name':'spi_no', 'display':'SPI No'},
		{'name':'spi_date', 'display':'SPI Date'}, {'name':'requisition_type', 'display':'Req Type'},
		{'name':'department', 'display':'Department'}, {'name':'indent_status', 'display':'Status'}]
		
		grid_id = iris.root.set_control_data(req_temp_data)
		return [data_header, grid_id]	
		
	
	#Finding the indent qty based on 'item name' and uuid og indent  no
	@iris.expose
	def item_indents_qty_details(self, **kwargs):
		'''
		Desc: Find the all 'indent no' and 'indent qty' for taking the 'po Qty'. Based on 'item name'
		and uuid of 'indent no'
		Parameter: kwargs['item_name']-- 'item name' and kwargs['ids']--list or string of uuid of 'indent no'
		kwargs['total_item']
		return :
		'''
		p = iris.findObject('poseidon')
		#Finding the item code based on given uuid of indents
		item_list = []
		indent_data = []
		if kwargs.has_key('ids') and kwargs.get('item_name'):
			if not isinstance(kwargs.get('ids'), list):	#if kwargs.get('ids') may be string if uuid is one other wise list, so i am converting into list	
				kwargs['ids'] = [kwargs['ids']]
			
			for indent_uuid in kwargs['ids']:				
				schedule_uuid = p.query("ids( subjects( subjects( objects( subjects( subjects(subjects( *, 'cost_select', '%s'), 'item_name', '%s'), 'is a','requisition_item'), 'schedule_data', *), 'po_status', 'pending'), 'indent_data', '%s'))" % (str(kwargs.get('cost_select')),  str(kwargs.get('item_name')), str(indent_uuid)))
				#schedule_uuid = p.query("ids(subjects(subjects(*, 'po_status','pending'), 'indent_data', '%s'))" % (str(indent_uuid)) )
				#p.query("ids(subjects(objects(subjects(*, 'is a', 'requisition_item'), 'schedule_data', *), \
				#'indent_data','%s'))"%(str(indent_uuid)))				
				for sh_uuid in schedule_uuid :			
					req_uuid = p.query("ids( subjects( subjects( subjects( *, 'item_name', '%s'), 'schedule_data', '%s'), 'is a', 'requisition_item'))" %(str(kwargs.get('item_name')), str(sh_uuid) ) )

					req_item_data = update_scaler.make_scaler( bwQuery(req_uuid).val()[0])
					temp_indent_data = {}
					temp_indent_data['cost_select'] = req_item_data['cost_select']
					temp_indent_data['uom'] = req_item_data['reqested_uom']
					temp_indent_data['section_select'] = req_item_data['section_select']
					
					sh_data = update_scaler.make_scaler( bwQuery(sh_uuid).val()[0])
					
					#print "sh_data"*9
					#print	type(sh_data)
					#pprint.pprint(sh_data)
					#print
					#print "sh_data"*9
					temp_indent_data['sh_uuid'] = sh_uuid
					temp_indent_data['indent_no'] = sh_data['indent_data'][0]['spi_no']
					temp_indent_data['schedule_date'] = sh_data['schedule_date']
					temp_indent_data['indent_qty'] = sh_data['issue_qty'] # indent qty is nothing but issue qty for req_class -indent req
					
					#temp_indent_data['req_specifications'] = sh_data.get('req_specifications', '')  
					#temp_indent_data['req_make'] = sh_data.get('req_make', '') 
					temp_indent_data['po_specifications'] = sh_data.get('indent_specifications', sh_data.get('req_specifications', 'NA'))
					temp_indent_data['po_make'] = sh_data.get('indent_make', sh_data.get('req_make', 'NA') ) 
					temp_indent_data['pending_qty'] = temp_indent_data['indent_qty'] 
					
					arg_data={'requisition_class': 'Issue Requisition', "material_type":req_item_data['material_type'], 'item_name':kwargs['item_name'], 'requisition_type':req_item_data['requisition_type']}
					#temp_indent_data['current stock'] = inventory.get_current_stock(**arg_data)
					temp_indent_data['current stock'] = 0#for the time being
					
					temp_indent_data['po_qty'] = sh_data.get('po_qty')

					temp_indent_data['rate'] = sh_data.get('rate') 
					temp_indent_data['value'] = sh_data.get('value')
					
					indent_data = indent_data + [temp_indent_data]
		ip = iris.request.remote.ip
		item_uuid = p.query("ids(subjects(subjects(subjects(*, 'is a', 'temp_po_items'), 'item description' , '%s'), 'ip', '%s'))" % (str(kwargs.get('item_name')), ip) )
		if len(item_uuid) > 0:
			item_details = update_scaler.make_scaler( bwQuery(item_uuid[0]).val()[0])
		else:
			item_details = {}

		item_name = kwargs['item_name']
		item_data = [i for i in list(kwargs['total_item'].split(',')) if len(i) > 0]  # making the list of item if name is greater than 0
		find_tax = self.tax()
		#print "indent"
		#pprint.pprint(indent_data)
		return CheetahRender(data={'tax':find_tax, 'type':"new_po_items", 'item_name':item_name, 'item_data':item_data, 'item_details':item_details, 'indent_data':indent_data},template = os.path.join(self.path, "item_indents_qty_details.tmpl"))
	
	# Creating the indent grid
	@iris.expose
	def indents_grid(self, **kwargs):
		'''
		This is displaying the indents data into grid.
		'''	
		p = iris.findObject('poseidon')
		req_temp_data = []
		if kwargs.has_key('department') and kwargs.has_key('requisition_type'):
			temp_req = p.query("ids(subjects(subjects(subjects(subjects(subjects(*, 'department', '%s'), 'requisition_type', '%s'), 'pirv_no',*), 'post_status', 'posted'), 'is a', 'requisition'))" % (str(kwargs['department']), str(kwargs['requisition_type'])))
		else:
			temp_req = p.query("ids(subjects(subjects(*, 'indent_status', 'confirm'), 'is a', 'indent'))")
		for uid in temp_req:
			#uid=p.query("ids(subjects(subjects(subjects(*, 'is a','vendor_master'),'revision_no','%s'),'vendor_registration_no','%s'))"%(revision_no,vendor_registration_no))
			temp = update_scaler.make_scaler(bwQuery(uid).val()[0])	
			temp['check'] = "<input type='checkbox' name='uuid' id='uuid' style='margin-top:0.4em' value='%s'></input>" %bwQuery(uid).ids()[0]
			req_temp_data = req_temp_data + [temp]
		data_header = [{'name':'check', 'display':'Check'}, {'name':'spi_no', 'display':'SPI No'},
		{'name':'spi_date', 'display':'SPI Date'}, {'name':'requisition_type', 'display':'Req Type'},
		{'name':'department', 'display':'Department'}, {'name':'indent_status', 'display':'Status'}]
		
		grid_id = iris.root.set_control_data(req_temp_data)
		return [data_header, grid_id]	
	
	# Displaying ithe data for finding the indents details 
	@iris.expose
	@hartex_users.hartex_access_validate(module='purchasemanager',allow='purchasemanager_purchaseorder_add')
	def indents_details_for_po(self):
		'''
		This is displaying indents data into the grid
		'''
		p = iris.findObject('poseidon')
		#department_select = list(set(p.query("names( objects( subjects(*, 'is a', 'department master'), 'department name', *))")))
		department_select = list(set( p.query("names(objects(subjects(subjects(*, 'schedule_data', subjects(subjects(*, 'po_status', 'pending'), 'is a', 'schedule_qty_data')), 'is a', 'requisition_item'), 'department_select', *))")  ))
		department_select.sort()

		# requisition_type = list(set(p.query("names( objects( subjects( subjects( subjects( *, 'is a', 'other code master'), \
						# 'department name', 'Purchase'), 'master','requisition type'),'value', *))")))
		# requisition_type.sort()
		requisition_type = []
		
		#vendor_name = list(set(p.query("(names( objects( subjects( subjects(subjects( *, 'is a', 'vendor_master'), 'vendor_approve', 'yes'), 'active', 'yes'), 'vendor_name', *)))")))
		#vendor_name.sort()
		vendor_name = [] # vendor will come on selecting the department and req_type
		
		#grid_data = self.indents_grid()
		global dic
		dic.append(department_select)
		print "dic DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD", dic
		return CheetahRender( data = {'heading':"Purchase Order", 'vendor_name':vendor_name, 'department_select':department_select, 'requisition_type':requisition_type, 'data_header':[], 'grid_id':[]}, template = os.path.join(self.path, "indents_details_for_po"))
	
	
	#POSTING ths indents
	@iris.expose	
	def confirm_indents(self, **kwargs):
		'''
		This is posting the new 'indents'. 'indent_status' is 'posted'
		This is taking  id as list or unicode.Example-
		{'ids': u'!132b7014b143bbab56458b8df1d7e28d'}
		{'ids': [u'!f06df0b0e6623782ccd1850a88775aea',u'!132b7014b143bbab56458b8df1d7e28d']}
		return :----indents_details_for_po()
		'''
		if isinstance(kwargs['ids'], list): 
			for uuid in kwargs.get('ids'):
				bwQuery(uuid).attr('indent_status', 'confirm').save()	
				
		else: # ids is list type
			bwQuery(kwargs.get('ids')).attr('indent_status', 'confirm').save()	
			
		return self.indents_details_for_po()
	
	
	#Fetching the cost name for given department
	@hermes.service()
	@iris.expose
	def find_cost_centre(self, **kwargs): 
		'''
		Finding the all cost centre based on given department
		'''
		p = iris.findObject('poseidon')
		cost_centre = []
		try:
			# cost_centre = list(set( p.query("names(objects(objects(subjects(subjects(*, 'is a', 'department master'), \
			# 'department name', '%s'), 'cost centre details', *), 'cost centre description', *))" % (kwargs.get('department', ''))) ))
			cost_centre = list(set( p.query("names(objects(subjects(subjects(subjects(subjects(subjects(*, 'requisition_head', '%s'), 'item_name', '%s'), 'department_select', '%s'), 'schedule_data', subjects(subjects(*,'po_status', 'pending'), 'is a', 'schedule_qty_data')), 'is a','requisition_item'), 'cost_select', *))" %(kwargs.get('requisition_head'), kwargs.get('item_name'), kwargs.get('department'))) ))
			cost_centre.sort()
		except:
			pass
		data = []
		for head in cost_centre:
			data = data + [cgi.escape(head, quote=True)]
		return data

	#Fetching the requisition_head name for given department
	@hermes.service()
	@iris.expose
	def find_rh_type(self, **kwargs): 
		'''
		Finding the all requisition_head based on given department
		'''
		p = iris.findObject('poseidon')
		requisition_head = []
		try:
			'''
			requisition_head = list(set( p.query("names(objects(subjects(subjects(subjects(subjects(*, 'is a', \
			'requisition_item'), 'item_name', '%s'), 'department_select', '%s'), 'schedule_data', subjects(subjects(*, 'is a', 'schedule_qty_data'), \
			'po_status', 'pending')), 'requisition_head', *))" %(kwargs.get('item_name'), kwargs.get('department'))) ))
			'''
			requisition_head = list(set( p.query("names(objects(subjects(subjects(subjects(subjects(*, 'item_name', '%s'), 'department_select', '%s'),'is a', 'requisition_item'), 'schedule_data', subjects(subjects(subjects(*, 'indent_data', subjects(subjects(*, 'indent_status','confirm'), 'is a', 'indent')), 'po_status', 'pending'), 'is a', 'schedule_qty_data')), 'requisition_head', *))" %(kwargs.get('item_name'), kwargs.get('department')))))
			requisition_head.sort()
		except:
			print "some error in given keywords for find_r_type"
			pass
		data = []
		for head in requisition_head:
			data = data + [cgi.escape(head, quote=True)]
		return data		
	#Fetching the requisition_type name for given department
	@hermes.service()
	@iris.expose
	def find_r_type(self, **kwargs): 
		'''
		Finding the all requisition_type based on given department
		'''
		p = iris.findObject('poseidon')
		requisition_type = []
		try:
			requisition_type = list(set( p.query("names(objects(subjects(subjects(subjects(subjects(*, 'item_name', '%s'), 'department_select', '%s'), 'schedule_data', subjects(subjects(*,'po_status', 'pending'), 'is a', 'schedule_qty_data')), 'is a','requisition_item'), 'requisition_type', *))" %(kwargs.get('item_name'), kwargs.get('department'))) ))
			requisition_type.sort()
		except:
			print "some error in given keywords for find_r_type"
			pass
		data = []
		for type in requisition_type:
			data = data + [cgi.escape(type, quote=True)]
		return data	
		
	#Fetching the vendor based on department and requisition type or item
	@hermes.service()
	@iris.expose		
	def find_vendor(self, **kwargs): 
		'''For reducing the performace use these type of query
		p.query("ids(subjects(subjects(*, 'is a', 'vendor_items'), 'vend_reg', objects(subjects(subjects(*, 'is a', 'vendor_master'), 'vendor_name', 'RN  BAJAJ'), 'vendor_registration_no', *)))")
		this is done if any thing went wrong plz uncomment the line
		
		
		Finding the all vendor name those have the item related to given requisition type
		'''
		p = iris.findObject('poseidon')
		#item_code = list(set( p.query("names( objects(subjects(subjects(subjects(*, 'is a', 'requisition_item'), \
		#'requisition_type', '%s'), 'department_select', '%s'), 'item_code', *) )" % (kwargs.get('requisition_type'), kwargs.get('department')) ) ))
		#item_name = []
		# in this query i am finding the all item code, which is related to the indent but  'po_status' is 'pending'
		if kwargs.has_key('item_name') and len(kwargs.get('item_name')) > 0: # here i have that the item name , but if user may be  change the department and req_type, 
			'''
			item_name = list(set( p.query("names( objects(subjects( \
																	subjects(subjects(*, 'is a', 'requisition_item'), 'department_select', '%s'), \
																	'schedule_data', \
																	subjects( 	subjects(subjects(subjects(*, 'is a', 'schedule_qty_data'), 'po_status', 'pending'), \
																						'indent_qty', 'confirm'), \
																				'indent_data', \
																				subjects(subjects(*, 'is a', 'indent'), 'indent_status', 'confirm') \
																			)  \
																	), \
																'item_name', '%s') \
												)" % (kwargs.get('department'), kwargs.get('item_name'),) \
											)\
							))
			'''
			#vendor_name = list(set(p.query("names( objects(subjects(subjects(subjects(*, 'vendor_approve', 'yes'), 'vendor_registration_no',objects(subjects(subjects(*, 'item_name', objects(subjects(subjects(subjects(*, 'department_select', '%s'), 'is a', 'requisition_item'), 'schedule_data', subjects(subjects(subjects(subjects(*, 'po_status', 'pending'), 'indent_qty', 'confirm'), 'indent_data', subjects(subjects(*, 'indent_status', 'confirm'), 'is a', 'indent')), 'is a', 'schedule_qty_data')), 'item_name', '%s')), 'is a', 'vendor_items'), 'vend_reg', *)), 'is a', 'vendor_master'), 'vendor_name', *) )"% (kwargs.get('department', ''), kwargs.get('item_name', '')))))
			vendor_name = list(set(p.query("names(objects(subjects(subjects(*,'vendor_registration_no', objects(subjects(subjects(*, 'item_name', '%s'), 'is a', 'vendor_items'), 'vend_reg', *)),'is a','vendor_master'), 'vendor_name', *) )"% (kwargs.get('item_name', '')))))
			
		else:	# here find all the item name	
			'''
			item_name = list(set( p.query("names( objects(subjects( \
																	subjects(subjects(*, 'is a', 'requisition_item'), 'department_select', '%s'), \
																	'schedule_data', \
																	subjects( 	subjects(subjects(subjects(*, 'is a', 'schedule_qty_data'), 'po_status', 'pending'), \
																						'indent_qty', 'confirm'), \
																				'indent_data', \
																				subjects(subjects(*, 'is a', 'indent'), 'indent_status', 'confirm') \
																			)  \
																	), \
																'item_name', *) \
												)" % (kwargs.get('department')) \
											)\
							))
			'''
			#vendor_name = list(set(p.query("names( objects(subjects(subjects(subjects(*, 'vendor_approve', 'yes'), 'is a', 'vendor_master'), 'vendor_registration_no',    objects(subjects(subjects(*, 'item_name', objects(subjects(subjects(subjects(*, 'department_select', '%s'), 'schedule_data', subjects(subjects(subjects(subjects(*, 'po_status', 'pending'), 'indent_qty', 'confirm'), 'indent_data', subjects(subjects(*, 'indent_status', 'confirm'), 'is a', 'indent')), 'is a', 'schedule_qty_data')), 'is a', 'requisition_item'), 'item_name', *)), 'is a', 'vendor_items'), 'vend_reg', *) ), 'vendor_name', *) )"% (kwargs.get('department')) ) ))
			vendor_name = list(set(p.query("names(objects(subjects(*, 'is a', 'vendor_items'), 'item_name', *))")))			
		'''
		vendor_registration_no = []
		for itname in item_name:
			vendor_registration_no = vendor_registration_no + list(set(p.query("names( objects(\
										subjects(subjects(*, 'is a', 'vendor_items'), 'item_name', '%s'), \
										'vend_reg', *) )" % (itname) )))
		vendor_registration_no = list(set(vendor_registration_no))
		
		vendor_name = []
		for ven_reg_no in vendor_registration_no:
			vendor_name = vendor_name + p.query("names( objects(subjects(subjects(subjects(*, 'is a', 'vendor_master'), \
						'vendor_approve', 'yes'), 'vendor_registration_no', '%s'), 'vendor_name', *) )" %(ven_reg_no))
		'''
		data = []
		for vendor in vendor_name:
			data = data + [cgi.escape(vendor, quote=True)]
		return list(set(data))
	
	#finding the item name based on Department,  cost_centre, and req type;
	@hermes.service()
	@iris.expose
	def find_item_name(self, **kwargs): 
		'''
		like find_vendor we can optimize this code also.
		Finding the item name based on department and requisition type
		parameter: kwargs['department'], kwargs['cost_centre'], kwargs['requisition_type']
		return : [item_name]
		'''
		p = iris.findObject('poseidon')
		# in this query i am finding the all item code, which is related to the pending indent but  'po_status' is 'pending'
		
		item_name = []
		if kwargs.get('cost_centre') and kwargs.get('requisition_head') and kwargs.get('department'):
			
			item_name = list(set(p.query("names(objects(subjects(subjects(subjects(subjects(subjects(*,'cost_select','%s'),'requisition_head','%s'),'department_select','%s'),'schedule_data',subjects(subjects(subjects(subjects(*,'po_status','pending'),'indent_qty','confirm'),'indent_data',subjects(subjects(*, 'indent_status', 'confirm'), 'is a', 'indent')), 'is a','schedule_qty_data')), 'is a', 'requisition_item'),'item_name', *))" % (kwargs.get('cost_centre', ''), kwargs.get('requisition_head', ''), kwargs.get('department', '')))))
		elif kwargs.get('cost_centre') and kwargs.get('requisition_type') and kwargs.get('department'):
			
			item_name = list(set(p.query("names(objects(subjects(subjects(subjects(subjects(subjects(*,'cost_select','%s'),'requisition_type','%s'),'department_select','%s'),'schedule_data',subjects(subjects(subjects(subjects(*,'po_status','pending'),'indent_qty','confirm'),'indent_data',subjects(subjects(*, 'indent_status', 'confirm'), 'is a', 'indent')), 'is a','schedule_qty_data')), 'is a', 'requisition_item'),'item_name', *))" % (kwargs.get('cost_centre', ''), kwargs.get('requisition_type', ''), kwargs.get('department', '')))))
		else:
			
			item_name = list(set( p.query("names( objects(subjects(subjects(subjects(*,'department_select', '%s'),'schedule_data',subjects(subjects(subjects(subjects(*, 'po_status', 'pending'),'indent_qty', 'confirm'), 'is a', 'schedule_qty_data'),'indent_data',subjects(subjects(*,'indent_status', 'confirm'), 'is a', 'indent'))),'is a','requisition_item'),'item_name', *))" % (kwargs.get('department')))))
			print "ttttttttttttttttttttttttttttttttttttttttttttttttttt", item_name	
		# Here we can fetch the data based on Given vendor, if given
		if kwargs.get('vendor_name'):
			try:
				ven_reg_no = list(set( p.query("names( objects(subjects(subjects(subjects(*, 'vendor_approve', 'yes'), 'vendor_name', '%s'), 'is a', 'vendor_master'), 'vendor_registration_no', *) )" %(kwargs.get('vendor_name'))) ))
				vendor_item = p.query("names( objects(subjects(subjects(*, 'vend_reg', '%s'), 'is a', 'vendor_items'),'item_name', *) )" % (ven_reg_no[0]) )
				
				item_name = list( set.intersection( set(vendor_item), set(item_name) ))
			except:
				print 
				print "error coming in find_item_name for given keywords"
				print kwargs
				print
				pass
		data = []
		for item in item_name:
			data = data + [cgi.escape(item, quote=True)]
		return data
	
	@hermes.service()
	@iris.expose
	def pending_indent_uuid(self, **kwargs):
		'''
		Finding the pending indent uuid for creating the new 'po'.
		parameter: kwargs['department'], kwargs['cost_centre'], kwargs['requisition_type'], 
				kwargs['vendor_name']
		return : [indent_uuid]
		'''
		p = iris.findObject('poseidon')
		find_data = []
		print "kwargs::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::",kwargs

		#if kwargs.get('refrence') == 'INDENTS' :
		temp_query = "subjects(subjects(*, 'indent_status','confirm'), 'is a', 'indent')"
		
		# Making SEARCH QUERY
		if kwargs.get('requisition_type'): # searching the data based on  requisition_type
			r = "subjects(*, 'requisition_type', '%s')" % (kwargs['requisition_type'])
			temp_query = replace(temp_query, "*", r)	
		
		if kwargs.get('requisition_head'): # searching the data based on  requisition_type
			r = "subjects(*, 'requisition_head', '%s')" % (kwargs['requisition_head'])
			print "r:::::::::::::::::::::::::::::::::::::", r
			temp_query = replace(temp_query, "*", r)	
			print "temp_query:::::::::::::::::::::::::::::::::::::::", temp_query		
		
		if kwargs.get('indent_status'):  # searching the data based on indent_status
			r = "subjects(*, 'indent_status', '%s')" % (kwargs['indent_status'])
			temp_query = replace(temp_query, "*", r)
			
		#*if kwargs.get('department'): # searching the data based on department
			#r = "subjects(*, 'department', '%s')" % (kwargs['department'])
			#temp_query = replace(temp_query, "*", r)
		# if kwargs.get('item_name'): # searching the data based on item name also
			# temp_query = "ids(objects(objects( \
										# subjects(subjects(subjects(*, 'is a', 'requisition_item'), 'cost_select', '%s'), 'item_name', '%s'), \
										# 'schedule_data', \
										# subjects(subjects(*, 'is a', 'schedule_qty_data'), 'po_status', 'pending') \
										# ), \
									# 'indent_data', \
									# %s \
								# ))" %(kwargs.get('cost_centre'), kwargs.get('item_name'), temp_query)
		# el
		if kwargs.get('vendor_name'): # with out item name			
			
			''' By default we cant show the all items, because of vendor
			# temp_query = "ids(objects(objects( \
										# subjects(subjects(subjects(*, 'is a', 'requisition_item'), 'cost_select', '%s'), 'item_name', *), \
										# 'schedule_data', \
										# subjects(subjects(*, 'is a', 'schedule_qty_data'), 'po_status', 'pending') \
										# ), \
									# 'indent_data', \
									# %s \
								# ))" %(kwargs.get('cost_centre'), temp_query)
			'''
			# Here Also Find only those item based on vendor
			item_name = self.find_item_name(**kwargs)
			print "item_name::::::::::::::::::::::::::::::::::::::::", item_name
			q_or_condition = "''".join(item_name).replace("''", "' or '")
			print "q_or_condition::::::::::::::::::::::::::::", q_or_condition
			
			temp_query = "ids(objects(objects(subjects(subjects(subjects(*, 'cost_select', '%s'), 'item_name', '%s'), 'is a', 'requisition_item'),'schedule_data',subjects(subjects(*, 'po_status', 'pending'), 'is a', 'schedule_qty_data')),'indent_data',%s))" %(kwargs.get('cost_centre'), q_or_condition, temp_query)
		# End  SEARCH query
		#temp_query = "ids(" + temp_query + ")"
		try:
			print "tempCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC", temp_query
			data_uuid = list(set( p.query(temp_query) ))
			print "data_uuidDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD", data_uuid
		except:
			print "Some Error found"
			data_uuid = []
		#print 
		#print "data_uuid", data_uuid
		#print
		
		return data_uuid
	# For SEARCHING  'INDENTS Details' data based on given data, for creating the new po no..
	@iris.expose
	def search_po_indents(self, **kwargs): # here dont show the item schedule date those have the po number
		'''
		Description : Searching the requisition data. Based on given keywords 
		parameter : kwargs
		Return : grid
		'''
		#{'department': u'Purchase', 'item_name': u'CARBON HAF - 339', 'vendor_name': u'hartex', 'refrence': u'INDENTS', 'requisition_type': u'gm'}
		#s = {'department': u'Stores', 'item_name': u'', 'vendor_name': u'temp', 'cost_centre': u'sed', 'requisition_type': u'gm'}
		p = iris.findObject('poseidon')
		find_data = []
		#if kwargs.get('refrence') == 'INDENTS' :
		temp_query = "subjects(subjects(*, 'indent_status','confirm'), 'is a', 'indent')"
		
		# Making SEARCH QUERY
		if kwargs.get('requisition_type'): # searching the data based on  requisition_type
			r = "subjects(*, 'requisition_type', '%s')" % (kwargs['requisition_type'])
			temp_query = replace(temp_query, "*", r)	
			
		if kwargs.get('indent_status'):  # searching the data based on indent_status
			r = "subjects(*, 'indent_status', '%s')" % (kwargs['indent_status'])
			temp_query = replace(temp_query, "*", r)
			
		if kwargs.get('department'): # searching the data based on department
			r = "subjects(*, 'department', '%s')" % (kwargs['department'])
			temp_query = replace(temp_query, "*", r)
		if kwargs.get('item_name'): # searching the data based on item name also
			temp_query = "ids(objects(objects(subjects(subjects(subjects(*, 'cost_select', '%s'), 'item_name', '%s'), 'is a', 'requisition_item'),'schedule_data',subjects(subjects(*, 'po_status', 'pending'), 'is a', 'schedule_qty_data')),'indent_data',%s))" %(kwargs.get('cost_centre'), kwargs.get('item_name'), temp_query)
		elif kwargs.get('vendor_name'): # with out item name			
			
			''' By default we cant show the all items, because of vendor
			# temp_query = "ids(objects(objects( \
										# subjects(subjects(subjects(*, 'is a', 'requisition_item'), 'cost_select', '%s'), 'item_name', *), \
										# 'schedule_data', \
										# subjects(subjects(*, 'is a', 'schedule_qty_data'), 'po_status', 'pending') \
										# ), \
									# 'indent_data', \
									# %s \
								# ))" %(kwargs.get('cost_centre'), temp_query)
			'''
			# Here Also Find only those item based on vendor
			item_name = self.find_item_name(**kwargs)
			q_or_condition = "''".join(item_name).replace("''", "' or '")
			
			temp_query = "ids(objects(objects(subjects(subjects(subjects(*, 'cost_select', '%s'), 'item_name', '%s'), 'is a', 'requisition_item'),'schedule_data',subjects(subjects(*, 'po_status', 'pending'), 'is a', 'schedule_qty_data')),'indent_data',%s))" %(kwargs.get('cost_centre'), q_or_condition, temp_query)
		# End  SEARCH query
		#temp_query = "ids(" + temp_query + ")"

		try:
			data_uuid = list(set( p.query(temp_query) ))
		except:
			print "Some Error found"
			data_uuid = []
		for uid in data_uuid:
			#uid=p.query("ids(subjects(subjects(subjects(*, 'is a','vendor_master'),'revision_no','%s'),'vendor_registration_no','%s'))"%(revision_no,vendor_registration_no))
			temp = update_scaler.make_scaler( bwQuery(uid).val()[0] )	
			#print kwargs['indent_status']
			if temp.get('indent_status') == 'confirm':
				temp['check'] = "<input type='checkbox' name='uuid' id='uuid' style='margin-top:0.4em' value='%s'></input>" %bwQuery(uid).ids()[0]
			find_data = find_data + [temp]
		data_header = [{'name':'check', 'display':'Check'}, {'name':'spi_no', 'display':'SPI No'},
		{'name':'spi_date', 'display':'SPI Date'}, {'name':'requisition_type', 'display':'Req Type'},
		{'name':'department', 'display':'Department'}, {'name':'indent_status', 'display':'Status'}]
		grid_id = iris.root.set_control_data(find_data)
		return CheetahRender(data={'data_header':data_header, 'grid_id':grid_id}, template = os.path.join(self.path, "grid.tmpl"))



#   	**********************    END INDENTS DATA **************************************	
	#FINDING  tha all TAX defined in other code master...
	def tax(self):
		'''
		Finding the all tax and discount from other code master. purchase master
		'''
		p = iris.findObject('poseidon')
		tax = {}
		tax['tot'] = list(set(p.query("names( objects( subjects( subjects( subjects( *, 'department name', 'Purchase'),'master', 'turnover tax'), 'is a', 'other code master'), 'value', *))")))
		tax['cess'] = list(set(p.query("names( objects( subjects( subjects( subjects( *, 'department name', 'Purchase'),'master', 'cess'), 'is a', 'other code master'), 'value', *))")))
		tax['vat'] = list(set(p.query("names( objects( subjects( subjects( subjects( *, 'department name', 'Purchase'),'master', 'vat'), 'is a', 'other code master'), 'value', *))")))
		tax['p_and_f'] = list(set(p.query("names( objects( subjects( subjects( subjects( *, 'department name', 'Purchase'),'master', 'p and f'), 'is a', 'other code master'), 'value', *))")))
		tax['excise_duty'] = list(set(p.query("names( objects( subjects( subjects( subjects( *, 'department name', 'Purchase'),'master', 'excise duty'),'is a', 'other code master'), 'value', *))")))
		tax['sale_tax'] = list(set(p.query("names( objects( subjects( subjects( subjects( *, 'department name', 'Purchase'),'master', 'sale tax'),'is a', 'other code master'), 'value', *))")))
		tax['discount'] = list(set(p.query("names( objects( subjects( subjects( subjects( *, 'department name', 'Purchase'),'master', 'discount'),'is a', 'other code master'), 'value', *))")))
		tax['surcharge'] = list(set(p.query("names( objects( subjects( subjects( subjects( *, 'department name', 'Purchase'),'master', 'surcharge'),'is a', 'other code master'), 'value', *))")))
		return tax
		
	#Finding the indent qty based on 'item name' and uuid of 'po no'
	@iris.expose	
	def item_po_qty_details(self, **kwargs): 
		'''
		Desc: Find the all 'indent no' and 'indent qty' for taking the 'po Qty'. Based on 'item name'
		and uuid of 'indent no'
		Parameter: kwargs['item_name']-- 'item name' and kwargs['ids']--list or string of uuid of 'indent no'
		kwargs['total_item']
		return :
		'''
		p = iris.findObject('poseidon')
		
		#Finding the item code based on given uuid of indents
		item_list = []
		indent_data = []

		schedule_uuid = p.query("names(objects(objects('%s', 'po_items',  subjects(*, 'item description', '%s')), 'sh_uuid', *))" % (kwargs.get('po_uuid'), kwargs.get('item_name')))		
		for sh_uuid in schedule_uuid :
			sh_uuid = sh_uuid[1:] # removimg the '_' from the uuid '_!45dr4cf3yjvfhin'
			req_uuid = p.query("ids( subjects( subjects( subjects( *, 'item_name', '%s'), 'schedule_data', '%s'), 'is a', 'requisition_item'))" %( str(kwargs.get('item_name')), str(sh_uuid) ) )

			req_item_data = update_scaler.make_scaler( bwQuery(req_uuid).val()[0])
			temp_indent_data = {}
			temp_indent_data['cost_select'] = req_item_data['cost_select']
			temp_indent_data['uom'] = req_item_data['reqested_uom']
			temp_indent_data['section_select'] = req_item_data['section_select']
			
			sh_data = update_scaler.make_scaler( bwQuery(sh_uuid).val()[0])

			temp_indent_data['sh_uuid'] = sh_uuid
			temp_indent_data['indent_no'] = sh_data['indent_data'][0]['spi_no']
			temp_indent_data['schedule_date'] = sh_data['schedule_date']
			temp_indent_data['indent_qty'] = sh_data['issue_qty']
			#temp_indent_data['req_specifications'] = sh_data.get('req_specifications', '')
			#temp_indent_data['req_make'] = sh_data.get('req_make', '') 
			
			'''
			try:
				temp_indent_data['po_specifications'] = sh_data['po_specifications']
				temp_indent_data['po_make'] = sh_data['po_make'] 
			except:
				temp_indent_data['po_specifications'] = sh_data.get('req_specifications', '')
				temp_indent_data['po_make'] = sh_data.get('req_make', '') 
			'''
			temp_indent_data['po_specifications'] = sh_data.get('po_specifications', sh_data.get('indent_specifications', 'NA'))
			temp_indent_data['po_make'] = sh_data.get('po_make', sh_data.get('indent_make', 'NA') ) 
			
			temp_indent_data['pending_qty'] = temp_indent_data['indent_qty'] 
			
			arg_data={'requisition_class': 'Issue Requisition', "material_type":req_item_data['material_type'], 'item_name':kwargs['item_name'], 'requisition_type':req_item_data['requisition_type']}
			#temp_indent_data['current stock'] = inventory.get_current_stock(**arg_data)
			temp_indent_data['current stock'] = 0#for the time being
			
			temp_indent_data['po_qty'] = sh_data.get('po_qty')
			temp_indent_data['rate'] = sh_data.get('rate') 
			temp_indent_data['value'] = sh_data.get('value')
			
			indent_data = indent_data + [temp_indent_data]		
		item_name = kwargs['item_name']
		po_items_uuid = p.query("ids(objects('%s', 'po_items', subjects(subjects(*, 'item description', '%s'), 'is a', 'po_items')))" %(kwargs.get('po_uuid'), kwargs.get('item_name')) )
		if len(po_items_uuid) > 0:
			item_details = update_scaler.make_scaler( bwQuery(po_items_uuid[0]).val()[0])
		else:
			item_details = {}

		item_data = p.query("names(objects(objects('%s', 'po_items', *), 'item description', *))" %(kwargs.get('po_uuid'))) # making the list of item if name is greater than 0

		if kwargs.get('po_no_dis') == "false": # opening the data in edit mode
			type = "edit_po_items"
		else: # view mode 
			type = "view_po_items"
		find_tax = self.tax()
		#print "item_details"*5
		#pprint.pprint(item_details)
		#print "item detailsIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", item_details
		return CheetahRender(data={'tax':find_tax, 'type':type, 'item_name':item_name, 'item_data':item_data, 'item_details':item_details, 'indent_data':indent_data},template = os.path.join(self.path, "item_indents_qty_details.tmpl"))
			
	# SAVING the item for New po
	@iris.expose
	def save_item_indent_qty(self, *args, **kwargs):
		'''
		saving the item details for one 'po', 'is a'-'po_items'
		'''
		#print "save 830"*5
		#pprint.pprint(kwargs)
		p = iris.findObject('poseidon')
		print "kwargs in saveSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS", kwargs
		po_schedule_key = ['po_item_schedule_date',  'po_item_schedule_qty']
		po_schedule_data = hartex.make_list_dic(*po_schedule_key, **kwargs)
		kwargs['po_schedule_data'] = po_schedule_data
		try:
			del kwargs['po_item_schedule_date']
			del kwargs['po_item_schedule_qty']
		except:
			pass
		#item_key = ['sh_uuid', 'po_qty', 'req_make', 'req_specifications']
		item_key = ['sh_uuid', 'po_qty', 'po_make', 'po_specifications']
		item_data = hartex.make_list_dic(*item_key, **kwargs)
		sh_item_uuid = []
		try:
			#this for req level only
			del kwargs['schedule_date']
		except:
			pass
		for sh_data in item_data:
			uuid = sh_data.get('sh_uuid')
			sh_data['po_date'] = time.strftime("%Y-%m-%d")
			del sh_data['sh_uuid']
			try:
				po_qty = int(sh_data.get('po_qty'))
				#value = int(sh_data.get('value'))
				rate = float(kwargs.get('rate'))
			except:
				po_qty = 0
				#value = 0
				rate = 0
			if( (po_qty != 0)  and (rate != 0) ) :
				sh_item_uuid = sh_item_uuid + [uuid]
				p.setObject(uuid, sh_data)
			else:
				sh_data['po_qty'] = ''
				#sh_data['value'] = ''
				sh_data['po_status'] = 'pending'
				p.setObject(uuid, sh_data)
				#bwQuery.select(where={'po_status':'pending'}).removeAttr('indent_data')
				bwQuery(uuid).removeAttr('po_qty').removeAttr('value').removeAttr('po_date').removeAttr('rate')
				
		ip = iris.request.remote.ip
		if str(kwargs.get('tag')) == "po_items": #After saving the 'po' means Edit mode
			po_item_uuid = p.query("ids(objects('%s', 'po_items', subjects(subjects(*, 'is a', 'po_items'), 'item description', '%s') ))" % (kwargs.get('po_uuid'), kwargs.get('item description')))
		else:#Means before saving the 'po' item is saved
			po_item_uuid = p.query("ids(subjects(subjects(subjects(*, 'is a', 'temp_po_items'), 'item description', '%s'), 'ip', '%s'))" % ( str(kwargs.get('item description')), ip) )	
		kwargs['sh_uuid'] = sh_item_uuid
		del kwargs['po_qty']
		#del kwargs['rate']
		#del kwargs['value']
		#del kwargs['schedule_date']
		del kwargs['indent_qty']
		kwargs['is a'] = kwargs['tag']  # this tag may be 'po_items' or 'temp_po_items'
		del kwargs['tag']
		
		kwargs['ip'] = ip
		kwargs['mrn_status'] = "open"
		kwargs['item description'] = kwargs.get('item description')
		#print "???"*12
		#print
		#pprint.pprint(kwargs)
		#print
		if len(po_item_uuid) > 0:
			try:
				del kwargs['po_uuid']
			except KeyError:
				pass
			p.setObject(po_item_uuid[0], kwargs)
		else:
			#pprint.pprint(kwargs)
			p.addObject(kwargs)
		#print "893"*12  
		#pprint.pprint(kwargs)
		# Updating the item master details of given item... NO NEED updating from po level
		#item_name_uuid = p.query("ids(subjects(subjects(*, 'is a', 'item master'), \
				#'item description', '%s'))" % (kwargs.get('item description')) )
		return None
		
	@iris.expose
	def po_grid(self, *args, **kwargs):
		'''
		This is displaying the data in grid.
		'''
		def edit(id):
			'''
			Making the edit link
			'''
			return '''
				<a href='#'><img src='/purchasemanager/resources/images/edit.png' onclick="edit_po_no('%(id)s')" class='imgbut' style='width:20px;height:20px;'/></a>
			''' % {"id":id}
			
		def show_details_ppo_no(id):
			'''
			Making the Link for details of ppo_no 
			'''
			return '''
				<a href='#'><img src='/purchasemanager/resources/images/revisionasd.png' onclick="ppo_no_details('%(id)s')" class='imgbut' style='width:20px;height:20px;'/></a>
			''' % {"id":id}
			
		p = iris.findObject('poseidon')
		if kwargs.has_key('posted'):
			po_data = p.query("ids(subjects(subjects(subjects(*, 'po date', %(from)s:%(to)s), 'is a', 'po'), 'post_status', 'posted'))"%(kwargs))
			#po_data = p.query("ids(subjects(subjects(*, 'is a', 'po'), 'post_status', 'posted'))")
		elif kwargs.has_key('unposted'):
			po_data = p.query("ids(subjects(subjects(subjects(*, 'po date', %(from)s:%(to)s), 'is a', 'po'), 'post_status', 'unposted'))"%(kwargs))
		else:
			po_data = p.query("ids(subjects(subjects(*, 'post_status', 'unposted'), 'is a', 'po'))")
		po_temp_data = []
		for id in po_data:
			temp = update_scaler.make_scaler(bwQuery(id).val()[0])
			temp['po no'] = "<a href='javascript:show_po_report(\"%s\")'> %s </a>" %(id,str(temp.get('po no','NA')))
			#pprint.pprint(temp)
			if temp['post_status'] == "unposted" : # here i am not displaying the those have 'ppo no'.....
				temp['check'] = "<input type='checkbox' style='margin-top:0.4em' value='%s'></input>" %bwQuery(id).ids()[0]
				#temp['edit'] = "<a href='#'><img src='/purchasemanager/resources/images/edit.png' class='imgbut' style='width:20px;height:20px;'/></a>"
				temp['edit'] = edit(id)				
			else:
				temp['veiw'] = show_details_ppo_no(id)
			# temp['po qty']=str(temp.get('po qty'))+" "+temp['uom']		
			# temp['value(rs)']=temp.get('value')
			
			#po_temp_data.append((str(temp['po no']), temp))
			po_temp_data.append(temp)
				
		#po_temp_data.sort(reverse=False)
		#po_temp_data.sort(reverse=False)
		#po_temp_data.reverse()	
		#po_temp_data = [ po_temp_data[x][1] for x in xrange( len(po_temp_data) )] , for performance...	
		#data_header = ['edit','po no', 'ppo no', 'po date','po type','item code','item description','vendor_name','po qty','value(rs)','e duty','s tax','freight','schedule date','delv qty','pending qty']
		data_header = ['check', 'edit', 'po no', 'purchase type', 'ppo no', 'po date', 'vendor name', 'freight']
		
		grid_id = iris.root.set_control_data(po_temp_data)
		return [data_header, grid_id]
	
	@iris.expose
	def fetch_posted(self, *args, **kwargs):
		'''
		This will show the all posted data. it will take from,to.date format is 'yy-mm-dd' 
		'''
		kwargs['posted'] = "posted"

		if not kwargs['from']:
			kwargs['from'] = "2000-00-00"
		if not kwargs['to']:
			kwargs['to'] = time.strftime("%Y-%m-%d", time.localtime())
		grid_data = self.po_grid( **kwargs)
		data_header = ['veiw', 'po no', 'po date', 'purchase type', 'vendor name', 'e duty', 's tax', 'freight', 'delv qty', 'pending qty']
		return CheetahRender(data = {'data_header':data_header, 'grid_id':grid_data[1], }, template = os.path.join(self.path, "po_details_grid.tmpl"))

	
	@iris.expose
	def fetch_unposted(self, *args, **kwargs):
		'''
		This will show the all Unposted data. it will take from,to.date format is 'yy-mm-dd' 
		'''
		if not kwargs['from']:
			kwargs['from'] = "2000-00-00"
		if not kwargs['to']:
			kwargs['to'] = time.strftime("%Y-%m-%d", time.localtime())
		kwargs['unposted'] = "unposted"
		grid_data = self.po_grid( **kwargs)
		data_header = ['check', 'edit', 'po no', 'purchase type', 'po type', 'vendor name', 'e duty', 's tax', 'freight', 'delv qty', 'pending qty']
		return CheetahRender(data={'data_header':data_header, 'grid_id':grid_data[1],}, template = os.path.join(self.path, "po_details_grid.tmpl"))
	
	@iris.expose
	def make_dict(self, id, *args, **kwargs):
		'''
		Description:
			This is taking id and removing the unique code and return dict
		parameter:
		Dict with key and value(value only list len is 1)
		return --- Dict type
		'''
		temp_data = bwQuery(id).val()[0]
		data = {}
		for key in temp_data.keys():
			data[key] = temp_data[key][0]
		return data
		
	@iris.expose
	def max_po_no(self, purchase_type):
		'''*****
		Description:
			This function  is generating the unique and max 'po no'. This purchase_type is nothing but requisition_head. so from purchase
			type master we can get the requisition_type. based on that requisition_type number will be increament.
		return - string format of  'po no'.
		'''	
		#import pdb
		#pdb.set_trace()
		p = iris.findObject('poseidon')
		#dont modify this line 
		#po_data = p.query("names( objects( subjects( *, 'is a', 'po'), 'po no', *))")
		
		#max_po = 100000 + len(po_data)
		
		if date.today().month < 4:
			#year_form = str(date.today().year - 1)[2:] + "-" + str(date.today().year)[2:]
			year_form = str(date.today().year - 1)[2:]
			search_date = str(date.today().year - 1) + "-04-01"
		else:
			#year_form = str(date.today().year)[2:] + "-" + str(date.today().year + 1)[2:]
			year_form = str(date.today().year)[2:]
			search_date = str(date.today().year) + "-04-01"
		today = time.strftime("%Y-%m-%d") 
		#~~~~~~~~ search_date  Finacial year starting date, Today is current date  
		po_data = p.query("names( objects( subjects(subjects( *, 'po date', %s:%s), 'is a', 'po'),'po no', *))" %(search_date, today))
		max_po = 1000 + len(po_data)
		#po_formate = "hrpl/po/" + purchase_type + "/" + year_form + "/" + str(max_po)
		#s = p.query("select_one(subjects(subjects(*, 'is a', 'purchase_type_master'), 'purchase_type_desc', '%s'))" %(repr(str(purchase_type))) )
		s = p.query("select_one(subjects(subjects(*, 'purchase_type_desc', %s), 'is a', 'purchase_type_master'))" %(repr(str(purchase_type))))
		requisition_type = ''
		if len(s) > 0:
			requisition_type = s[0]['_value']['purchase_type'][0]
		else:
			#iris.error("requisition_type is not found in purchase type master for this %s requisition_head"%(repr(str(purchase_type))))
			iris.message("requisition_type is not found in purchase type master for this %s requisition_head"%(repr(str(purchase_type))))
		po_formate =  year_form + requisition_type + str(max_po)
		return po_formate	
	
	# For creating the 'po' or 	EDITING the 'po'
	@iris.expose
	def create_or_edit(self, *args, **kwargs):
		'''***************
		Description:
			This function is displaying the all 'po no' and 'ppo no' details.
			For Edit mode if id is there other-wise blank tmpl will be show for input
		''' 
		p = iris.findObject('poseidon')
		edit_po = {}
		item_list = []
		if kwargs.has_key('id'): # this is for edit the any po_no when user will clicke on edit link
			#id = kwargs['id']
			po_id = kwargs['id']
			po_data = bwQuery(po_id).val()[0]
			#po_data = update_scaler.make_scaler( bwQuery(po_id).val()[0] )

			item_data = po_data['po_items']
			del po_data['po_items']
			''' I thinke this code is not required.. if any thing goes wrong unblock it
			data = {}
			for key in po_data.keys():
				data[key] = po_data[key][0]
			'''
			for item in item_data:
				x = {}
				x['id'] = item['_id']
				x['item description'] = item['_value']['item description'][0]

				#po_items = po_items + [self.make_dict(id)]
				item_list = item_list + [x]

			edit_po = update_scaler.make_scaler( bwQuery(po_id).val()[0] )
			edit_po['uuid'] = po_id
			#here we are checking , if ppo no have po no is assign or not....
			if len(edit_po.get('po no')) < 1 and len(edit_po.get('ppo no')) > 6:
				'''
				try:
					#this line is comment 
					t_ppo = edit_po['ppo no'].split('/')
					po_no = t_ppo[0] + "/po/" + str(edit_po.get('purchase type')) \
							+ "/" + t_ppo[2] + "/" + t_ppo[3] location
					#edit_po['po no'] = self.max_po_no(edit_po.get('purchase type')) # return only 'po no' to the template
					edit_po['po no'] = po_no
					# end commented line
					edit_po['po no'] = self.max_po_no(edit_po.get('purchase type')) # This purchase type here is req_head
				except:
					pass
				'''
				edit_po['po date'] = time.strftime("%Y-%m-%d")
		else:
			#po_items = []
			#edit_po['po no'] = self.max_po_no(kwargs.get('requisition_type')) # return only 'po no' to the template
			edit_po['po no'] = self.max_po_no(kwargs.get('requisition_head')) # return only 'po no' to the template
			edit_po['cost_select'] = kwargs.get('cost_centre')
			edit_po['vendor name'] = kwargs.get('vendor_name')
			#Finding the market type
			#edit_po['market'] = ['domestic','international']
			#edit_po['purchase type'] = kwargs.get('requisition_type')  #at po level req_type becomes purchase type
			edit_po['purchase type'] = kwargs.get('requisition_head')  #at po level req_head becomes purchase type
			vendor_uuid =  p.query("ids(subjects(subjects(*, 'vendor_name', '%s'), 'is a', 'vendor_master'))" % (kwargs.get('vendor_name')))
			vendor_data = update_scaler.make_scaler( bwQuery(vendor_uuid).val()[0] )
			edit_po['vendor code'] = vendor_data['vendor_code']
			#edit_po['payment mode'] = bwQuery.select({'is a':'other code master','department name':'purchase','master':'payment mode'}).attr('value').names()
			#edit_po['payment terms'] = bwQuery.select({'is a':'other code master','department name':'purchase','master':'payment terms'}).attr('value').names()

		#self.find_path = os.path.join(os.getcwd(), 'apps', 'purchasemanager', 'modules', 'purchase', 'resources', 'views')	
		
		#p.putObject(kwargs)
		''' This code is  blocked by jitendra wriiten by krish.... if any thing going wrong unblock it
		po_data = bwQuery.types('po') 
		total_len = int(len(po_data))
		total_page = total_len//3
		if( total_len - total_page*3 > 0 ):
			total_page += 1
		p_no = 1
		str_no = (p_no-1)*3
		end_no = (p_no)*3
		grid_data = self.po_grid()
		'''
		
		#'''added by Krish'''
		temp_po = {}
		temp_po['market'] = ['domestic','international']
		temp_po['payment mode'] = bwQuery.select({'is a':'other code master','department name':'purchase','master':'payment mode'}).attr('value').names()
		temp_po['payment terms'] = bwQuery.select({'is a':'other code master','department name':'purchase','master':'payment terms'}).attr('value').names()
		temp_po['delivery location'] = bwQuery.select({'is a':'other code master','department name':'purchase','master':'delivery location'}).attr('value').names()
		temp_po['price basis'] = bwQuery.select({'is a':'other code master','department name':'purchase','master':'price basis'}).attr('value').names()
		temp_po['signature_type'] = bwQuery.select({'is a':'other code master','department name':'purchase','master':'signature_type'}).attr('value').names()
		'''
		item_data = bwQuery.types('item master')
		item_list=[]
		for x in item_data:
			item_dic={"_id":x.get('_id')}
			item_dic.update(update_scaler.make_scaler(bwQuery(x).val()[0]))
			item_list.append(item_dic)
		item_list.sort(reverse=True)
		'''
		#'''added by Krish'''
		#Finding the item code based on given uuid of indents., only for time the creating the 'po no'
		
		if kwargs.has_key('ids'): # means opening for create new po
			if not isinstance(kwargs.get('ids'), list):	#if kwargs.get('ids') placemay be string if uuid is one other wise list	
				kwargs['ids'] = [kwargs['ids']]
			for indent_uuid in kwargs['ids']:
				#here we have to write 'po_status' = pending
				schedule_uuid = p.query("ids(subjects(subjects(objects(subjects(subjects(*, 'cost_select', '%s'), 'is a', 'requisition_item'),'schedule_data', *), 'po_status', 'pending'), 'indent_data', '%s'))" % (kwargs.get('cost_centre', ''), str(indent_uuid)))
				#schedule_uuid = p.query("ids(subjects(objects(subjects(*, 'is a', 'requisition_item'), 'schedule_data', *), \
				#'indent_data','%s'))"%(str(indent_uuid)))
				for sh_uuid in schedule_uuid :
					if kwargs.has_key('item_name') and len(str(kwargs.has_key('item_name'))) > 0:
						item_name = str(kwargs.get('item_name'))
						item_list = [item_name]
						#item_name = list( set( p.query("names( objects( subjects( subjects( *, 'is a', 'requisition_item'), 'schedule_data', \
						#'%s'), 'item_name', '%s'))" % (str(sh_uuid), kwargs.get('item_name')) ) ) )
					else:	
						item_name = list( set( p.query("names( objects( subjects( subjects( *, 'schedule_data','%s'), 'is a', 'requisition_item'), 'item_name', *))" % (str(sh_uuid)) ) ) )
						if item_name[0] not in item_list:
							item_list = item_list + item_name
			kwargs['vendor_name'] = edit_po.get('vendor name')	
			item_list = self.find_item_name(**kwargs)
		item_list.sort( reverse = True )
		o = {}
		# here i am deleting  the 'temp_po_item'  this junk data created when if user not clicking on main save po button
		if not kwargs.has_key('id'): # means we are opening in create mode
			ip = iris.request.remote.ip
			for item_name in item_list:
				junk_uuid = p.query("ids(subjects(subjects(subjects(*, 'is a', 'temp_po_items'), 'item description', '%s'), 'ip', '%s'))" % (item_name, ip))
				for j_uuid in junk_uuid:
					sh_uuid = p.query("ids(objects('%s', 'sh_uuid', *))" %(j_uuid))					
					for s_uuid in sh_uuid: 
						bwQuery(s_uuid).removeAttr('po_qty').removeAttr('value').removeAttr('po_date') #removing 'po qty' at scheduling level
					p.removeObject(j_uuid)		
		# End Junk data delete
		today = time.strftime("%Y-%m-%d")
		if kwargs.has_key('mode'):
			mode = kwargs['mode']
		else:
			mode = 'view'
		#pprint.pprint(edit_po)
		#pprint.pprint(item_list)
		print "TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT", temp_po
		print "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE", edit_po

		return CheetahRender( data = {'mode':mode, 'today':today, 'edit_data':edit_po, 'o':o, 'item_data':item_list, 'temp_po':temp_po}, template = os.path.join(self.path, "create_or_edit.tmpl"))

	@iris.expose
	@hartex_users.hartex_access_validate(module='purchasemanager',allow='purchasemanager_purchaseorder_edit')
	def edit_po_no(self, **kwargs):
		'''********
		Description:
			This function is displaying the details of given id( id of 'po no' or 'ppo no')
		paramter:
			uuid as a id
		return :
			purchase_order()
		'''
		po_id = kwargs['id']
		print "kwargs:::::::::::::::::::::::::::::::::::::::::::", kwargs	
		#return self.create_or_edit(id = po_id) // before next_prev
		return self.create_or_edit( **kwargs)
		
	@iris.expose
	def purchase_details(self, *args, **kwargs):
		'''***************
		Description:
			This function is displaying the all 'po no' and 'ppo no' details in grid.
		'''
		self.find_path = os.path.join(os.getcwd(), 'apps', 'purchasemanager', 'modules', 'purchase', 'resources', 'views')	
		'''added by Krish
		po_data = bwQuery.types('po') 
		total_len = int( len( po_data) )
		total_page = total_len//3
		if(total_len - total_page*3>0):
			total_page += 1
		p_no = 1
		str_no = (p_no-1)*3
		end_no = (p_no)*3
		grid_data = self.po_grid()
		
		# item_data = bwQuery.types('item master')
		# item_list=[]
		# for x in item_data:
			# item_dic={"_id":x.get('_id')}
			# item_dic.update(update_scaler.make_scaler(bwQuery(x).val()[0]))
			# item_list.append(item_dic)
		
		added by Krish'''
		o = {}
		grid_id = iris.root.set_control_data([])
		data_header = ['check', 'edit', 'po no', 'purchase type', 'po type', 'vendor name']
		
		return CheetahRender( data = {'o':o, 'data_header':data_header, \
		'grid_id':grid_id, 'heading':"Purchase Order"}, template = os.path.join(self.path, "purchase_details.tmpl"))

	@iris.expose
	def update_po_not_req(self, *args, **kwargs):
		'''********** 
		This function is not required check it 
		This is updating the 'po no' Details.
		return - purchase_details
		'''
		print "update 1142"*9
		print 
		pprint.pprint(kwargs)
		print 
		p = iris.findObject('poseidon')
		uuid_po = kwargs['po_id']
		del kwargs['po_id']
		#if p.setObject(uuid_po, kwargs):
		main_data = {}
		main_data = {"is a":['po', 'pending'],
					"po no":kwargs["po no"],
					"po type":kwargs["po type"],
					"po date":kwargs["po date"],
					"ppo no":kwargs["ppo no"],
					"vendor_code":kwargs["vendor_code"],
					"vendor_name":kwargs["vendor_name"],
					"ref no":kwargs["ref no"],			
					"ref date":kwargs["ref date"],
					"purchase type":kwargs["purchase type"],
					"commission":kwargs["commission"],
					"delivery place":kwargs["delivery location"],				
					"other taxes":kwargs["other taxes"],	
					"brokerage":kwargs["brokerage"],
					"mode of transport":kwargs["mode of transport"],
					"turnover":kwargs["turnover"],
					"rc":kwargs["rc"],				
					"indent no":kwargs["indent no"],
					"e duty":kwargs["e duty"],
					"s tax":kwargs["s tax"],
					"freight":kwargs["freight"],
					"signature_type":kwargs["signature_type"]	,
					}
		main_data['pending qty'] = 0.0
		main_data['delv qty'] = 0.0
		main_data['post_status'] = 'unposted'
		#Formatting items
		
		items = {"is a":kwargs["is a"],
				"item code":kwargs["item code"],
				"item description":kwargs["item description"],
				"uom":kwargs["uom"],
				"po qty":kwargs["po qty"],
				"rate":kwargs["rate"],
				"value":kwargs["value"],			
				"discount":kwargs["discount"],				
				"schedule date":kwargs["schedule date"]				
				}
		main_data["po_items"] = self.convert_to_list_of_dict(**items)
		
		if p.setObject(uuid_po, main_data):
			iris.message(main_data['po no'] + " has been UPDATED successfully")	
		return self.purchase_details()
	
	@iris.expose
	@hartex_users.hartex_access_validate(module='purchasemanager',allow='purchasemanager_purchaseorder_post')
	def post_po(self, *args, **kwargs):
		'''
		This is posting the new 'po no'. 'post_status' is 'posted'
		This is taking  id as list or unicode.Example-
		{'ids': u'!132b7014b143bbab56458b8df1d7e28d'}
		{'ids': [u'!f06df0b0e6623782ccd1850a88775aea',u'!132b7014b143bbab56458b8df1d7e28d']}
		Also updating the item data. pipe line qtyplace
		return :----purchase_details()
		'''
		'''

		'''
		'''
		if isinstance(kwargs['ids'], list): 
			for uuid in kwargs.get('ids'):
				bwQuery(uuid).attr('post_status', 'posted').save() 
				
		else: # ids is list type
			bwQuery(kwargs.get('ids')).attr('post_status', 'posted').save()
		'''
		p = iris.findObject("poseidon")
		if not isinstance(kwargs['ids'], list):
			kwargs['ids'] = [kwargs['ids']]
		po_post = {'post_status':"posted"}
		for po_uuid in kwargs.get('ids'):
			item_qty_data = {} #this {'item_code':"total_po_qty"}
			for data in p.getObject(po_uuid)[0]['_value']['po_items']:
				item_qty_data[data['_value']['item_code'][0]] = data['_value']['total_po_qty'][0]
			for item_code in item_qty_data.keys():
				item_uuid = p.query("ids(subjects(subjects(*, 'item code', '%splace'), 'is a', 'item master'))" % (item_code) )
				item_data  = update_scaler.make_scaler( bwQuery(item_uuid[0]).val()[0])
				try:
					pipe_line_quantity  = int(item_data['pipe line quantity']) + int(item_qty_data[item_code])
				except:
					pipe_line_quantity = int(item_qty_data[item_code])
				item_p_qty = {'pipe line quantity':str(pipe_line_quantity)}
				p.setObject(item_uuid[0], item_p_qty, save=False)
			p.setObject(po_uuid, po_post, save=False)
		if p.save():
			iris.message("PO data is posted")
		return self.purchase_details()

	# saving the 'po'
	@iris.expose
	def save_po_validation(self,  **kwargs): 
		'''
		Validation of 'po' for saving the data.
		'''
		p = iris.findObject('poseidon')
		main_data = {"is a":['po', 'pending'],
					"cost_select":kwargs.get("cost_select"),	
					"delivery place":kwargs.get("delivery location"),	
					"freight":kwargs.get("freight"),
					"mode of transport":kwargs.get("mode of transport"),
					"payment mode":kwargs.get("payment mode"),	
					"payment terms":kwargs.get("payment terms"),
					"po date":kwargs.get("po date"),					
					"po no":kwargs.get("po no"),
					"ppo no":kwargs.get("ppo no", ''),
					"purchase type":kwargs.get("purchase type"),
					"po_value":kwargs.get("po_value"),
					"quotation date":kwargs.get("quotation date"),			
					"quotation no":kwargs.get("quotation no"),			
					"vendor code":kwargs.get("vendor code"),
					"vendor name":kwargs.get("vendor name"),
					"price basis":kwargs.get("price basis")	,
					"insurance":kwargs.get("insurance")	,	
					"insurance_type":kwargs.get("insurance_type")	,	
					"signature_type":kwargs.get("signature_type")	,							
				}
		# main_data['pending qty'] = 0.0
		# main_data['delv qty'] = 0.0
		main_data['post_status'] = 'unposted'
		# 'is a' is 'po_items'
		'''
		items = {"is a":kwargs["is a"],
				"pending qty":kwargs['pending qty'],
				"delv qty":kwargs['delv qty'],
				"item code":kwargs["item code"],
				"item description":kwargs["item description"],
				"uom":kwargs["uom"],
				"po qty":kwargs["po qty"],
				"rate":kwargs["rate"],
				"value":kwargs["value"],			
				"discount":kwargs["discount"],				
				"schedule date":kwargs["schedule date"]				
				}
		'''
		#main_data["po_items"] = self.convert_to_list_of_dict(**items)

		main_data['ip'] = iris.request.remote.ip
		'''
		if kwargs.has_key('uuid_po'): # here updating the data
			uuid = kwargs['uuid_po']
			del main_data['po date'] # po date cant be change
			if p.setObject(uuid, main_data):
				iris.message(main_data['po no'] + " has been UPDATED successfully")
		else:
		'''
		all_po_date = p.query("names( objects( subjects(*, 'is a', 'po'), 'po date', *))") # in this if or esle we are checking 'po date' should be today date or 
		if len(all_po_date) > 0:
			last_po_date = max(all_po_date)
			if last_po_date > kwargs.get("po date"):
				#iris.error("Po date can not be lesser than   %s" %(last_po_date))
				#error = "true"
				return "Po date can not be lesser than   %s" %(last_po_date)
			if time.strftime("%Y-%m-%d") < kwargs.get("po date"):
				#iris.message("Po date can not be greater than   %s" %(time.strftime("%Y-%m-%d")))
				return "Po date can not be greater than   %s" %(time.strftime("%Y-%m-%d"))
				#error = "true"
		elif time.strftime("%Y-%m-%d") < kwargs.get("po date"):
			#iris.message("Po date can not be greater than   %s" %(time.strftime("%Y-%m-%d")))
			#error = "true"
			return "Po date can not be greater than   %s" %(time.strftime("%Y-%m-%d"))
		elif time.strftime("%Y-%m-%d") > kwargs.get("po date"):
			#iris.message("Po date can not be lesser than   %s" %(time.strftime("%Y-%m-%d")))
			return "Po date can not be lesser than   %s" %(time.strftime("%Y-%m-%d"))

		main_data['po_items'] = p.query("ids(subjects(subjects(*, 'is a', 'temp_po_items'), 'ip', '%s'))"  % (main_data['ip']))
		if len(main_data['po_items']) < 1:
			#iris.message("First Save the Item, Then  PO")
			return "First Save the Item, Then  PO"
		return "true"
	# saving the 'po'
	@iris.expose
	def save_po(self,  **kwargs): 
		'''************
		Description: This is saving the Data of New 'po no'.
		#If uuid_po is given then it is UPDATED the  data for that given uuid.
		#That uuid should be Unposted 'po no'.
		return : purchase_details()
		'''
		p = iris.findObject('poseidon')
		print "kwargsin po::::::::::::::::::::::::::::::::::::::::::::::::::::::::", kwargs
		
		main_data = {"is a":['po', 'pending'],
					"cost_select":kwargs.get("cost_select", ''),	
					"cash":kwargs.get("cash", ''),
					"imports":kwargs.get("imports", ''),
					"currency":kwargs.get("currency",''),	
					"delivery place":kwargs.get("delivery location", ''),	
					"freight":kwargs.get("freight", ''),
					"mode of transport":kwargs.get("mode of transport", ''),
					"market":kwargs.get("market", ''),
					"payment mode":kwargs.get("payment mode", ''),	
					"payment terms":kwargs.get("payment terms", ''),
					"po date":kwargs.get("po date"),					
					"po no":kwargs.get("po no"),
					"ppo no":kwargs.get("ppo no", ''),
					"purchase type":kwargs.get("purchase type", ''),
					"po_value":kwargs.get("po_value", ''),
					"quotation date":kwargs.get("quotation date", ''),			
					"quotation no":kwargs.get("quotation no", ''),			
					"vendor code":kwargs.get("vendor code"),
					"vendor name":kwargs.get("vendor name"),	
					"price basis":kwargs.get("price basis"),								
					"insurance":kwargs.get("insurance")	,
					"insurance_type":kwargs.get("insurance_type")	,
					"signature_type":kwargs.get("signature_type")	,
						}
		# main_data['pending qty'] = 0.0
		# main_data['delv qty'] = 0.0
		main_data['post_status'] = 'unposted'
		# 'is a' is 'po_items'
		'''
		items = {"is a":kwargs["is a"],
				"pending qty":kwargs['pending qty'],
				"delv qty":kwargs['delv qty'],
				"item code":kwargs["item code"],
				"item description":kwargs["item description"],
				"uom":kwargs["uom"],
				"po qty":kwargs["po qty"],
				"rate":kwargs["rate"],
				"value":kwargs["value"],			
				"discount":kwargs["discount"],				
				"schedule date":kwargs["schedule date"]				
				}
		'''
		#main_data["po_items"] = self.convert_to_list_of_dict(**items)

		main_data['ip'] = iris.request.remote.ip
		'''
		if kwargs.has_key('uuid_po'): # here updating the data
			uuid = kwargs['uuid_po']
			del main_data['po date'] # po date cant be change
			if p.setObject(uuid, main_data):
				iris.message(main_data['po no'] + " has been UPDATED successfully")
		else:
		'''
		all_po_date = p.query("names( objects( subjects(*, 'is a', 'po'), 'po date', *))") # in this if or esle we are checking 'po date' should be today date or 
		if len(all_po_date) > 0:
			last_po_date = max(all_po_date)
			if last_po_date > kwargs.get("po date"):
				iris.error("Po date can not be lesser than   %s" %(last_po_date))
				#error = "true"
				return None
			if time.strftime("%Y-%m-%d") < kwargs.get("po date"):
				iris.message("Po date can not be greater than   %s" %(time.strftime("%Y-%m-%d")))
				return None
				#error = "true"
		elif time.strftime("%Y-%m-%d") < kwargs.get("po date"):
			iris.message("Po date can not be greater than   %s" %(time.strftime("%Y-%m-%d")))
			#error = "true"
			return None	
		elif time.strftime("%Y-%m-%d") > kwargs.get("po date"):
			iris.message("Po date can not be lesser than   %s" %(time.strftime("%Y-%m-%d")))
			return None	

		main_data['po_items'] = p.query("ids(subjects(subjects(*, 'is a', 'temp_po_items'), 'ip', '%s'))"  % (main_data['ip']))
		if len(main_data['po_items']) < 1:
			iris.message("First Save the Item, Then  PO")
			return None
		else:
			#This line is not required, already while creating the po we sending the po number.
			main_data['po no'] = self.max_po_no(kwargs.get("purchase type"))

			sh_uuid = p.query("names( objects( subjects( subjects(*, 'is a', 'temp_po_items'), 'ip', '%s'), \
					'sh_uuid', *) )" % (main_data['ip']) ) 
			for uuid in sh_uuid: # here update only uuid those have po qty*************************************
				#[ 1:]  -- uuid='_!21kjkjjjkjkjh76766' removing the '_'
				p.setObject(uuid[1:],{'po_status':"confirm"}, save=False)  # updating the sh_uuid of the each item , ' po_staus' confirmed
			item_q = {'last po date':kwargs.get("po date"), 'last po number':kwargs.get("po no"), 'last po rate':''}					
			for uuid_po_items in main_data['po_items']:
				p.setObject(uuid_po_items, {'is a':"po_items"}, save=False)  # while clicking on ok button , saving the item 'is a':'temp_po_items', here i am assign the item to one 'po'				
				
				#Updating the 'item master' for this item
				po_item_data = update_scaler.make_scaler(bwQuery(uuid_po_items).val()[0])
				item_name_uuid = p.query("ids(subjects(subjects(*, 'is a', 'item master'), \
				'item description', '%s'))" % (po_item_data['item description']) )
				item_q['last po rate'] = po_item_data['rate']
				p.setObject(item_name_uuid[0], item_q, save=False)
				
			#bwQuery(main_data).save() # new data is given , 
			p.addObject(main_data, save=False)
			
			#Updating the vendor total po, always we get one data because vendor_code is unique
			venor_details = p.query("select_one(subjects(subjects(*, 'is a', 'vendor_master'), 'vendor_code', '%s'))" %(kwargs.get("vendor code")) )
			try:
				total_po = venor_details[0]['_value']['total_po'][0] + 1
				p.setObject(venor_details[0]['_id'], {'total_po':total_po}, save=False)
			except:
				pass
			
			p.save()
			iris.message(main_data['po no'] + " has been saved successfully")	
		return self.purchase_details()
		

	# Updating the PO NO 
	@iris.expose	
	def update_po(self, **kwargs):
		'''
		Updating the 'po no' header details, Along with item details in 'item master'
		'''
		#print "update 1401"*9
		#print 
		#pprint.pprint(kwargs)
		#print 
		p = iris.findObject('poseidon')
		if len(kwargs.get("po no", '')) < 1:
			kwargs['po no'] = self.max_po_no(kwargs.get('purchase type'))
			
		main_data = {"is a":['po', 'pending'],
					"cash":kwargs.get("cash", ''),
					"imports":kwargs.get("imports", ''),
					"currency":kwargs.get("currency",''),
					"delivery place":kwargs.get("delivery location"),	
					"freight":kwargs.get("freight"),
					"mode of transport":kwargs.get("mode of transport"),
					"payment mode":kwargs.get("payment mode"),	
					"payment terms":kwargs.get("payment terms"),					
					"po no":kwargs.get("po no"),
					"ppo no":kwargs.get("ppo no", ''),
					"purchase type":kwargs.get("purchase type"),
					"po_value":kwargs.get("po_value"),
					"market":kwargs.get("market"),
					"quotation date":kwargs.get("quotation date"),			
					"quotation no":kwargs.get("quotation no"),			
					"vendor code":kwargs.get("vendor code"),
					"vendor name":kwargs.get("vendor name"),
					"price basis":kwargs.get("price basis"),																	
					"insurance":kwargs.get("insurance")	,	
					"insurance_type":kwargs.get("insurance_type")	,	
					"signature_type":kwargs.get("signature_type")	,
					}
		#main_data['ip'] = iris.request.remote.ipcreate
		main_data['post_status'] = 'unposted'
		main_data['po date'] = time.strftime("%Y-%m-%d")
		pprint.pprint(main_data)
		
		if kwargs.has_key('uuid_po'): # here updating the data
			p.setObject(str(kwargs['uuid_po']), main_data)
			
			#Here i am updating the 'item master' for each last 'po_items' ---- 'po number' 'po date' 'po rate'
			#This  Keys is updating 
			item_q = {'last po date':main_data.get('po date', ''), 'last po number':kwargs.get("po no", ''), 'last po rate':''}
			po_items_uuid = p.query("names(objects('%s', 'po_items', *))" % (str(kwargs['uuid_po'])) )
			for uuid_item in po_items_uuid:
				po_item_data = update_scaler.make_scaler(bwQuery(uuid_item).val()[0])
				item_name_uuid = p.query("ids(subjects(subjects(*,'item description', '%s'), 'is a', 'item master'))" % (po_item_data['item description']) )
				item_q['last po rate'] = po_item_data['rate']
				try:
					print "updating>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
					p.setObject(item_name_uuid[0], item_q)
				except:
					print "This item %s is not updated at item master" %(po_item_data['item description'])
					pass
			#from here i am calling the create 'po no'
			#xml_data  = main_data
			#xml_data['uuid_po'] = kwargs['uuid_po']
			#self.make_xml.make_po_xml_files(kwargs['uuid_po'], update_scaler.make_scaler(bwQuery(kwargs['uuid_po']).val()[0]))
			return "true"
		else:
			return None

	@hermes.service()
	@iris.expose
	def item_code_uom(self, *args, **kwargs):
		'''
			Finding the item code and item uom based on item_name
		'''
		p = iris.findObject('poseidon')
		item_uuid = p.query("ids(subjects(subjects(*, 'item description', '%s'), 'is a', 'item master'))" % (kwargs.get('item_name', '')) )
		data = 	update_scaler.make_scaler(bwQuery(item_uuid).val()[0])
		return data	
	#   @@@@@@@@@@@@@@@@@@@    for confirm mis **************************************
	
	# Finding posted or unposted mis by purchase
	@iris.expose
	def posted_mis_purchase(self, *args, **kwargs):
		'''
		Finding the posted and unposted data mis_fresh or mis_return, based on given date
		'''
		#pprint.pprint(kwargs)
		p = iris.findObject('poseidon')
		if len(kwargs['from_date']) < 1:
			kwargs['from_date'] = time.strftime("%Y-%m-%d", time.localtime())
		if len(kwargs['to_date']) < 1:
			kwargs['to_date'] = time.strftime("%Y-%m-%d", time.localtime())
		'''
		data_header2 = ['check', 'mis no', 'vendor_name', 'po no', 'ppo no', 'mis date', 'dc no', 'dc date', \
		'po date', 'item description', 'procurement type', 'material type', 'qty received', 'invoice no', 'invoice date', 'teststatus', 'po status']
		'''
		data_header2 = ['check', 'mis no', 'vendor_name', 'mis date', 'dc no', 'dc date', \
		'item description', 'procurement type', 'material type', 'qty received', 'invoice no', 'invoice date', 'teststatus', 'accepted report', 'rejected report', 'po status']
		if kwargs.get('status') == "posted":
			grid_data2 = p.query("ids(subjects(subjects(subjects(subjects(*, 'po status', 'ok' or 'not ok' or 'no indent found'), 'posted_mis_by_purchase', '%(status)s'), 'mis date', %(from_date)s:%(to_date)s), 'is a', '%(mis)s'))" %(kwargs))
			#data_header2.remove('check')
		else:
			#All unposted data have the 'temp_po_status' which will assin the 'po status' at posting time
			grid_data2 = p.query("ids(subjects(subjects(subjects(subjects(*, 'temp_po_status', 'ok' or 'not ok' or 'no indent found'), 'posted_mis_by_purchase', '%(status)s'), 'mis date', %(from_date)s:%(to_date)s), 'is a', '%(mis)s'))" %(kwargs))
		# try:
			# grid_data2.extend( bwQuery.select( where = {'is a':"mis", 'posted_mis_by_purchase':"posted", 'po status':"ok"} )) 
			# grid_data2.extend( bwQuery.select( where = {'is a':"mis", 'posted_mis_by_purchase':"posted", 'po status':'no indent found'} )) 
			# grid_data2.extend( bwQuery.select( where = {'is a':"mis", 'posted_mis_by_purchase':"posted", 'po status':'not ok'} )) 
			##grid_data2.extend(bwQuery.select( where = {'is a':"mis", 'po status':'pending'})) 
		# except:
			# pass
		dat2 = []
		for x in grid_data2:
			temp = bwQuery(x).val()[0]
			#pprint.pprint(temp)
			if kwargs.get('status') == "unposted":
				temp['check'] = "<input type='checkbox' value='%s' 'name='process' onclick='javascript:flag_for_process_po(\"%s\")'></input>" % (x, x)
			else:
				temp['check'] = '''
						<a href='#'><img src='/purchasemanager/resources/images/revisionasd.png' onclick='javascript:view_mis_fresh(\"%s\")' class='imgbut' style='width:20px;height:20px;'/></a>
					''' %(x)
			temp['qty received'] = temp['qty received'][0] + " " + temp['item uom'][0]
			#temp['po qty']=str(temp['po qty'][0])+" "+temp['item uom'][0]
			try:
				temp['po qty'] = str(temp['po qty'][0])
			except:
				temp['po qty'] = ''
			temp['teststatus'] = temp.get('status')
			temp['total invoice amount'] = 'rs ' + str( temp['total invoice amount'][0] )
			if 'ref no' in temp:
				temp['rejected report']="<a href='javascript:fetch_reject_mis_store(\"%s\")'> %s </a>" %(x,str(temp.get('ref no',[''])[0]))
			temp['accepted report']="<a href='javascript:generate_report_fromstore_store(\"%s\")'> %s </a>" %(x,str(temp.get('test report no', [''])[0]))
			
			dat2.append(( str(temp['mis no']), temp))
		dat2.sort(reverse = True)
		
		dat2 = [ dat2[x][1] for x in xrange( len(dat2) ) ]	
		grid_id2 = iris.root.set_control_data(dat2)
		grid_length2 = len(dat2)
		return CheetahRender(data = {'data_header':data_header2, 'grid_id':grid_id2, }, template = os.path.join(self.path,  'grid_update.tmpl'))
	
	@iris.expose
	def po_status(self, *args, **kwargs):
		'''****
		This functin is return the grid 1('po status'is under process or process) and grid 2 data('po status' is ok or not ok)
		'''
		self.find_path = os.path.join(os.getcwd(), 'apps', 'purchasemanager', 'modules', 'purchase', 'resources', 'views')		
		#p = iris.findObject('poseidon')
		grid_data1 = self.grid_data_for_pending_mis()
		'''
		data_header2 = ['check', 'mis no', 'vendor_name', 'po no', 'ppo no', 'mis date', 'dc no', 'dc date', \
		'po date', 'item description', 'procurement type', 'material type', 'qty received', 'invoice no', 'invoice date', 'teststatus', 'po status']
		'''
		data_header2 = ['check', 'mis no', 'vendor_name', 'mis date', 'dc no', 'dc date', \
		'item description', 'procurement type', 'material type', 'qty received', 'invoice no', 'invoice date', 'teststatus', 'accepted report', 'rejected report', 'po status']
		
		grid_data2 = []
		try:
			#while comfim or reject the data .. value is assign to the 'temp_po_status', after the posting, assign to the 'po status'
			#grid_data2.extend( bwQuery.select( where = {'is a':"mis", 'posted_mis_by_purchase':"unposted", 'po status':"ok"} )) 
			grid_data2.extend( bwQuery.select( where = {'is a':"mis", 'posted_mis_by_purchase':"unposted", 'temp_po_status':"ok"} )) 
			#grid_data2.extend( bwQuery.select( where = {'is a':"mis", 'posted_mis_by_purchase':"unposted", 'po status':'no indent found'} )) 
			grid_data2.extend( bwQuery.select( where = {'is a':"mis", 'posted_mis_by_purchase':"unposted", 'temp_po_status':'no indent found'} )) 
			#grid_data2.extend( bwQuery.select( where = {'is a':"mis", 'posted_mis_by_purchase':"unposted", 'po status':'not ok'} )) 
			grid_data2.extend( bwQuery.select( where = {'is a':"mis", 'posted_mis_by_purchase':"unposted", 'temp_po_status':'not ok'} )) 
			
			#grid_data2.extend(bwQuery.select( where = {'is a':"mis", 'po status':'pending'})) 
		except:
			pass
		dat2 = []
		for x in grid_data2:
			temp = bwQuery(x).val()[0]
			temp['check'] = "<input type='checkbox' value='%s' onclick='javascript:flag_for_process_po(\"%s\") 'name='process'></input>" % (x.get('_id'), x.get('_id'))
			temp['qty received'] = temp['qty received'][0] + " " + temp['item uom'][0]
			#temp['po qty']=str(temp['po qty'][0])+" "+temp['item uom'][0]
			#temp['po qty'] = str(temp['po qty'][0])
			temp['po status'] = temp.get('temp_po_status', '') # after posting the data value is assign to the 'po status', what ever vale oh 'temp_po_status'
			temp['teststatus'] = temp.get('status')
			temp['total invoice amount'] = 'rs ' + str( temp['total invoice amount'][0] )
			if 'ref no' in temp:
				temp['rejected report'] = "<a href='javascript:fetch_reject_mis_store(\"%s\")'> %s </a>" %(x.get('_id', ''), str(temp.get('ref no',[''])[0]))
			temp['accepted report'] = "<a href='javascript:generate_report_fromstore_store(\"%s\")'> %s </a>" %(x.get('_id', ''), str(temp.get('test report no', [''])[0]))
			
			dat2.append(( str(temp['mis no']), temp))
		dat2.sort(reverse = True)
		
		dat2 = [ dat2[x][1] for x in xrange( len(dat2) ) ]	
		grid_id2 = iris.root.set_control_data(dat2)
		grid_length2 = len(dat2)
		return CheetahRender(data = {"purchase_type":[], "form_field":{"Purity":"Purity", "oil Absorb":"oil_Absorb", \
		"r Density":"r_density", 'Melt point':"melting_point"}, 'grid_id1':grid_data1[0], 'data_header1':grid_data1[1], \
		'grid_id2':grid_id2, 'data_header2':data_header2, 'heading':"Confirm Mis Fresh"}, template = os.path.join(self.path, "check_mis_po.tmpl"))
			

	@iris.expose
	def save_ppo(self, *args, **kwargs):
		'''*********
		Description :
			This functin is saving the new 'ppo no' and updating the mis details.
			Also Updating the that 'ppo no'.
		'''
		p = iris.findObject('poseidon')
		ip = iris.request.remote.ip
		item_key = ['cost_select', 'current stock', 'discount', 'excise_duty', 'indent_no', 'is a' \
					'item description', 'other_tax', 'po_item_schedule_date', 'rate', 'sale_tax', 'schedule_date', \
					'section_select', 'sh_uuid', 'total_po_qty', 'uom', 'vat']
		sh_key = ['alloted_qty', 'sh_uuid', 'po_qty', 'value']
		sh_data = hartex.make_list_dic(*sh_key, **kwargs)
		temp_sh_uuid = []
		today = time.strftime("%Y-%m-%d")
		for data in sh_data: 
			try:
				if len(data.get('po_qty')) > 0 and len(data.get('value')) > 0 and len(data.get('alloted_qty')) > 0:
					if int(str(data.get('po_qty'))) > 0 and int(str(data.get('value'))) > 0 and int(data.get('alloted_qty')) > 0:
						# update the sh_uuid data also po staus-- 
						temp_sh_uuid = temp_sh_uuid + [data['sh_uuid']]
						p.setObject(data['sh_uuid'], {'po_date':today, 'po_status':"confirm", 'po_qty':data.get('po_qty'), 'value':data.get('value')}, save=False)
			except:
				pass
		if len(temp_sh_uuid) == 0:
			iris.error("po qty, value, alloted qty not given")
			return  self.po_status()
		po_items = []
		temp_po_items = {
						  'ip': ip,
						  'is a': 'po_items',
						  'item description': kwargs.get('item description'),
						  'other_tax':" ",
						  'po_item_schedule_date': kwargs.get('po_item_schedule_date'),
						  'rate': kwargs.get('rate'),
						  
						  'sh_uuid': temp_sh_uuid,
						  'total_po_qty': kwargs.get('total_po_qty'),
						  
						  'mrn_status':"closed"
						 	}

		ppo_data = {
					'ip': ip,
					'is a': [u'po', u'pending'],
					
					'po date': today,
					'po no': kwargs.get('po no'),
					'ppo date': today,
					'ppo no': kwargs.get('ppo no'),
					'po_items': temp_po_items,
					'po_value': kwargs.get('po_value'),
					'post_status': [u'unposted'],
					'purchase type': kwargs.get('purchase type'),
					'quotation date': kwargs.get('quotation date'),
					'quotation no': kwargs.get('quotation no'),
					'vendor code': kwargs.get('vendor code'),
					'vendor name': kwargs.get('vendor name'),
						}
		p.addObject(ppo_data, save=False)
		kwargs['is a'] = "mis_items_details"
		po_item_key = ["alloted_qty",  "value", "ppo no"]
		po_items_details = hartex.make_list_dic(*po_item_key, **kwargs)
		for item in po_items_details:
			if len(item.get('alloted_qty')) > 0:
				item['is a'] = "mis_items_details"
				item['rate'] = kwargs.get('rate')
				item['ppo no'] = kwargs['ppo no']
				item['ppo date'] = today
			else:
				po_items_details.remove(item)  # this line is written for fixing the bug no 467
		#      else condition you have to write here 
		#' mis details' is upadting 
		#mis_data = {'purchase_type':kwargs['purchase type'], 'po status':"ok", "po_items_details":po_items_details}
		mis_data = {'purchase_type':kwargs['purchase type'], 'temp_po_status':"ok", "po_items_details":po_items_details}
		p.setObject(kwargs['mis_uuid'], mis_data,  save=False)
		'''
		return None
		main_data = {}
		main_data = {"is a":['po', 'pending'],
					"delivery place":kwargs.get("delivery location"),	
					"freight":kwargs.get("freight"),
					"mode of transport":kwargs.get("mode of transport"),
					"payment mode":kwargs.get("payment mode"),	
					"payment terms":kwargs.get("payment terms"),
					"po date":time.strftime("%Y-%m-%d"),					
					"po no":kwargs.get("po no"),
					"ppo no":kwargs.get("ppo no"),
					"purchase type":kwargs.get("purchase type"),
					"po_value":kwargs.get("po_value"),
					"quotation date":kwargs.get("quotation date"),			
					"quotation no":kwargs.get("quotation no"),			
					"vendor code":kwargs.get("vendor code"),
					"vendor name":kwargs.get("vendor name"),	
					"price basis":kwargs.get("price basis")	,									
					"insurance":kwargs.get("insurance")	,
					"insurance_type":kwargs.get("insurance_type")	,
					"signature_type":kwargs.get("signature_type")	,	}
		kwargs['pending qty'] = 0.0
		kwargs['delv qty'] = 0.0
		main_data['post_status'] = 'unposted'
		
		items = {"is a":kwargs["is a"],
				"item code":kwargs["item code"],
				"item description":kwargs["item description"],
				"uom":kwargs["uom"],
				"po qty":kwargs["po qty"],
				"rate":kwargs["rate"],
				"value":kwargs["value"],			
				"discount":kwargs["discount"],				
				"schedule date":kwargs["schedule date"],
				"pending qty":kwargs['pending qty'],
				"delv qty":kwargs['delv qty']
				}
		
		main_data["po_items"] = self.convert_to_list_of_dict(**items)
		try:
			ppo_id = p.query("ids(subjects(subjects(*, 'is a', 'po'), 'ppo no', '%s'))" %(kwargs['ppo no']))[0]
		except:
			ppo_id = []
		if ppo_id:  # updating the 'ppo no' here.. 
			p.setObject(ppo_id, main_data)
			iris.message("ppo no " + kwargs["ppo no"] + " is Updated sucessfully")
		else:
			p.putObject(main_data)
			#id = p.query("ids(subjects(subjects(*, 'is a','mis'), 'mis no', '%s'))"%(kwargs['mis_no']))[0]
			up_query = {'ppo no':kwargs['ppo no']}
			p.setObject(kwargs['mis_uuid'], up_query)
			p.save()
		'''
		p.save()
		iris.message("ppo no " + kwargs["ppo no"] + " is created sucessfully")
		return  self.po_status()
	

	@iris.expose
	def grid_data_for_pending_mis(self):
		p = iris.findObject('poseidon')
		data = []
		try:
			data.extend( bwQuery.select( where = {'is a':'mis', 'mis status':'posted', 'po status':'pending'}))
			data.extend( bwQuery.select( where = {'is a':'mis', 'mis status':'posted',  'po status':'under process'}))
		except:
			pass	
		dat1 = []
		for x in data:
			#item=update_scaler.make_scaler(bwQuery(x).val())
			item = bwQuery(x).val()[0]
			item['check'] = "<input type='radio' onclick='javascript:flag_for_process_po(\"%s\") 'name='process'></input>" %x.get('_id')
			item['qty received']=str(item['qty received'][0])+" "+str(item['item uom'][0])
			#item['po qty']=str(item['po qty'][0])+" "+str(item['item uom'][0])
			#item['po qty'] = str(item['po qty'][0])
			item['total invoice amount'] = 'rs ' + str(item['total invoice amount'][0])
			item['teststatus'] = item.get('status')
			if not item.has_key('temp_po_status'):
				dat1.append((str(item.get('mis no')),item))
		data_header1 = ['check', 'mis no', 'vendor_name', 'mis date', 'dc no', \
		'dc date', 'item description', 'procurement type', 'material type',  'qty received', 'invoice no', 'invoice date', 'po status', 'teststatus']
		'''
		data_header1 = ['check', 'mis no', 'vendor_name', 'ppo no', 'po no', 'mis date', 'dc no', \
		'dc date','po date',  'item description', 'procurement type', 'material type',  'qty received', 'invoice no', 'invoice date', 'po status', 'teststatus']
		'''
		dat1.sort(reverse = True)
		dat1 = [dat1[x][1] for x in xrange(len(dat1))]
		grid_id1 = iris.root.set_control_data(dat1)
		return [grid_id1, data_header1]
		
	
	@iris.expose
	def go_to_purchase_process(self, **kwargs):
		'''
		This function is updating the po status-process to under process.and return tha data to the tmpl
		with that 'mis details'
		return : fill_mis_details.tmpl
		parameter: 
		'''
		#DONT call while in edit mode of mis
		p = iris.findObject('poseidon')
		cid = kwargs['process_id']
		updateq = {"po status":'under process', "teststatus":''}
		new_id = p.setObject(cid, updateq)
		data = p.getObject(new_id)[0] 
		return CheetahRender(data = {'data':data['_value'], 'mis_id':new_id}, template = os.path.join(self.path, "fill_mis_details.tmpl"))
	
	@iris.expose
	def edit_to_purchase_process(self, **kwargs):
		'''
		This function is opening in editing mode of po details.and return tha data to the tmpl
		with that 'mis details'
		return : fill_mis_details.tmpl
		parameter: 
		'''
		p = iris.findObject('poseidon')
		cid = kwargs['process_id']
		data = p.getObject(cid)[0]
		return CheetahRender(data = {'data':data['_value'], 'mis_id':cid}, template = os.path.join(self.path, "fill_mis_details.tmpl"))
		
	@iris.expose
	def update_pending_mis_details(self):
		'''
		Description:
		This function is returning the  data.
		return :grid1 data. to the tmpl(grid_update.tmpl)
		parameter : none
		'''
		#p = iris.findObject('poseidon')
		grid_data1 = self.grid_data_for_pending_mis()
		return CheetahRender(data = {'grid_id':grid_data1[0], 'data_header':grid_data1[1]}, template = os.path.join(self.path, "grid_update.tmpl"))
	
	@hermes.service()
	@iris.expose
	def find_mis_purchase_type(self, **kwargs):
		'''
		Finding the purchase type based on given uuid_mis_no, 
		return : list of purchase_type
		Note: This purchase type at po level, nothing but requisition head
		'''
		p = iris.findObject('poseidon')
		purchase_type = []
		mis_data = update_scaler.make_scaler(bwQuery(kwargs.get('process_mis_id', '')).val()[0])
		if mis_data.has_key('po no'):
			if len(mis_data['po no']) > 0:
				purchase_type = p.query("names(objects(subjects(subjects(subjects(subjects(*, 'po no', '%s'), 'vendor name', '%s'), 'po_items', subjects(subjects(*, 'item description', '%s'), 'is a', 'po_items')), 'is a', 'po'), 'purchase type', *))" %(mis_data.get('po no'), mis_data.get('vendor_name'), mis_data.get('item description')))		
			else:	
				#purchase_type = p.query("names(objects(subjects(subjects(subjects(*, 'is a', 'po'), 'vendor name', '%s'), 'po_items', subjects(subjects(*, 'is a', 'po_items'), 'item description', '%s')), 'purchase type', *))" %(mis_data.get('vendor_name'), mis_data.get('item description')))		
				purchase_type = p.query("names(objects(subjects(subjects(subjects(*, 'vendor name', '%s'), 'po_items', subjects(subjects(subjects(*, 'mrn_status', 'open' or 'pending'), 'item description', '%s'), 'is a', 'po_items')), 'is a', 'po'), 'purchase type', *))" %(mis_data.get('vendor_name'), mis_data.get('item description')))		
		if len(purchase_type) > 0 :
			find_po = "true"
			purchase_type.sort()
		else: # we are searching if any pending indent is there or not for creating the 'ppo no'
			find_po = "false"
			#this is requisition head becomes purchase type
			#purchase_type = p.query("names(objects(objects(subjects(subjects(objects(subjects(subjects(*, 'is a', 'requisition_item'), 'item_name', '%s'), 'schedule_data',  subjects(*, 'is a', 'schedule_qty_data')), 'indent_qty', 'confirm'), 'po_status', 'pending'), 'indent_data', subjects(*, 'is a', 'indent')), 'requisition_type', *))" %(mis_data.get('item description')))
			purchase_type = p.query("names(objects(objects(subjects(subjects(objects(subjects(subjects(*, 'item_name', '%s'), 'is a', 'requisition_item'), 'schedule_data',  subjects(*, 'is a', 'schedule_qty_data')), 'indent_qty', 'confirm'), 'po_status', 'pending'), 'indent_data', subjects(*, 'is a', 'indent')), 'requisition_head', *))" %(mis_data.get('item description')))
			if len(purchase_type) < 1 :
				purchase_type = ["No Indent Found"]
				find_po = "no indent found"
		purchase_type = list(set(purchase_type))
		#This purchase type is nothing bur requisition head requisition
		return {'purchase_type':purchase_type, "find_po":find_po}
		
	@iris.expose
	def po_status_create(self, *args, **kwargs): #17-july 	
		'''
		This is taking the uuid of mis_no , those have 'po no' given or maybe available for po level
		'''
		#import pdb
		#pdb.set_trace()
		p = iris.findObject('poseidon')
		mis_data = update_scaler.make_scaler(bwQuery(kwargs.get('process_mis_id', '')).val()[0])
		po_item = []
		#pprint.pprint(mis_data)
		#print "?? "*12
		if mis_data.has_key('po no'):
			if len(mis_data['po no']) > 0: #this line is not required, there is no po no at mis level
				#purchase_type = p.query("names(objects(subjects(subjects(subjects(subjects(*, 'is a', 'po'), 'po no', '%s'), 'vendor name', '%s'), 'po_items', subjects(subjects(*, 'is a', 'po_items'), 'item description', '%s')), 'purchase type', *))" %(mis_data.get('po no'), mis_data.get('vendor_name'), mis_data.get('item description')))		
				pdata = p.query("select(subjects(subjects(subjects(*, 'po no', '%s'), 'vendor name', '%s'), 'is a', 'po'))" %(mis_data['po no'], mis_data['vendor_name']))
				# po_item = p.query("select( subjects( objects( subjects( subjects( *, 'is a', 'po'), \
				# 'po no', '%s'), 'po_items', *), 'item description', '%s'))" % (mis_data['po no'], mis_data['item description']) )
				temp_po_item_uuid = p.query("ids( subjects( objects( subjects( subjects( *, 'po no', '%s'), 'is a', 'po'), 'po_items', *), 'item description', '%s'))" % (mis_data['po no'], mis_data['item description']) )
				temp_po_item = update_scaler.make_scaler(bwQuery(temp_po_item_uuid[0]).val()[0])
				temp_po_item['po_no'] = mis_data['po no']
				temp_po_item['uuid_po'] = p.query("ids(subjects(subjects(*, 'po no', '%s'), 'is a', 'po'))" %(mis_data['po no']))[0]
				po_item = po_item + [temp_po_item]				
			else:	

				pdata = [] 
				#QQQQQQQQQQQQQQQQQ here you have to write base don item name, also pending po only
				#total_po_no = p.query("names(objects(subjects(subjects(subjects(*, 'is a', 'po'), 'purchase type', '%s'), 'vendor name', '%s'), 'po no', *))" %(kwargs.get('purchase_type'), mis_data['vendor_name']))
				#total_po_no = p.query("names(objects(subjects(subjects(subjects(subjects(*, 'is a', 'po'), 'purchase type', '%s'), 'po_items', subjects(subjects(*, 'is a', 'po_items'), 'item description', '%s')),  'vendor name', '%s'), 'po no', *))" %(kwargs.get('purchase_type'), mis_data['item description'], mis_data['vendor_name']))
				total_po_no = p.query("names(objects(subjects(subjects(subjects(subjects(*, 'purchase type', '%s'), 'po_items', subjects(subjects(subjects(*, 'mrn_status', 'open' or 'pending'), 'item description', '%s'), 'is a', 'po_items')),'vendor name', '%s'), 'is a', 'po'), 'po no', *))" %(kwargs.get('purchase_type'), mis_data['item description'], mis_data['vendor_name']))
				
				for po_no in total_po_no:
					temp_po_item_uuid = []
					temp_po_item = []
					temp_po_item_uuid = p.query("ids( subjects( objects( subjects( subjects( *,'po no', '%s'), 'is a', 'po'), 'po_items', *), 'item description', '%s'))" % (po_no, mis_data['item description']) )					
					temp_po_item = update_scaler.make_scaler(bwQuery(temp_po_item_uuid[0]).val()[0])
					temp_po_item['po_no'] = po_no
					temp_po_item['po_rate'] = temp_po_item['rate']  #rate is going as mis rate, this 'rate' at po level
					try:
						#mis_items_uuid = p.query("ids(objects('%s', 'po_items_details', subjects(subjects(*, 'is a', 'mis_items_details'), 'po_no', '%s')))" % (kwargs.get('process_mis_id', ''), po_no))
						mis_items_uuid = p.query("ids(objects('%s', 'po_items_details', subjects(*, 'po_no', '%s')))" % (kwargs.get('process_mis_id', ''), po_no))
						mis_items = update_scaler.make_scaler(bwQuery(mis_items_uuid).val()[0])
						temp_po_item['allotted_qty'] = mis_items.get('allotted_qty')
						temp_po_item['rate'] = mis_items.get('rate') #this rate at mis level
						temp_po_item['value'] = mis_items.get('value')
					except:
						#Means there is no mis items
						temp_po_item['allotted_qty'] = ''
						temp_po_item['rate'] = ''
						temp_po_item['value'] = ''
					temp_po_item['uuid_po'] = p.query("ids(subjects(subjects(*, 'po no', '%s'), 'is a', 'po'))" %(po_no))[0]
					po_item = po_item + [temp_po_item]
				#purchase_type = p.query("names(objects(subjects(subjects(subjects(*, 'is a', 'po'), 'vendor name', '%s'), 'po_items', subjects(subjects(*, 'is a', 'po_items'), 'item description', '%s')), 'purchase type', *))" %(mis_data.get('vendor_name'), mis_data.get('item description')))		
				purchase_type = p.query("names(objects(subjects(subjects(subjects(*, 'vendor name', '%s'), 'po_items', subjects(subjects(subjects(*, 'mrn_status', 'open' or 'pending'), 'item description', '%s'), 'is a', 'po_items')), 'is a', 'po'),'purchase type', *))" %(mis_data.get('vendor_name'), mis_data.get('item description')))		
		return 	CheetahRender(data = {'po_item':po_item}, template = os.path.join(self.path, "fill_po_details.tmpl"))
	
	@iris.expose
	def ppo_status_create(self, *args, **kwargs): 
		'''
		Also pass indent data for this ppo no based on indent
		'''
		p = iris.findObject('poseidon')
		data = update_scaler.make_scaler(bwQuery(kwargs.get('process_mis_id', '')).val()[0])
		if data.has_key('ppo no') and len(data['ppo no']) > 0:
			ppo_data = {}
			ppo_items_data = {}
			ppo_items = {}
			try:					
				ppo_data_temp = p.query("select( subjects( subjects( subjects( *, 'ppo no', '%s'), 'vendor_name', '%s'), 'is a', 'po' ))" % (data['ppo no'], data['vendor_name']) )[0]['_value']
				for key in ppo_data_temp.keys():
					ppo_data[key] = ppo_data_temp[key][0]

				ppo_items_data = p.query("select( subjects( objects( subjects( subjects(*, 'ppo no', '%s'), 'is a', 'po'), 'po_items', *), 'item code', '%s'))" % (data['ppo no'], data['item code']) )			
				ppo_items_temp = ppo_items_data[0]['_value']
				for key in ppo_items_temp.keys():
					ppo_items[key] = ppo_items_temp[key][0]
				ppo_items['id'] = ppo_items_data[0]['_id']			
			except:
				pass
			return 	CheetahRender(data = {'ppo_data':ppo_data, 'ppo_items':ppo_items}, template = os.path.join(self.path, "ppo_edit.tmpl"))
		else:
			# from here we are sending the data to the ppo_create.tmpl for creating the new 'ppo no'
			vendor_name = data['vendor_name']
			vendor_code = data['vendor_code']
			try:
				#mis_uuid = p.query("ids( subjects( subjects( subjects(subjects( *, 'mis no', '%s'), 'is a', 'mis'), 'vendor_name', '%s'), 'item code', '%s'))" % (data['mis no'], data['vendor_name'], data["item code"]) )
				mis_items = data
			except:
				pass
			#purchase_type = list(set( p.query("names(objects( subjects(subjects(subjects(*, 'is a', 'requisition_item'), 'item_code', '%s'), 'schedule_data', subjects(subjects(subjects(subjects(*, 'is a', 'schedule_qty_data'), 'indent_qty', 'confirm'), 'po_status', 'pending'), 'indent_data', subjects(subjects(*, 'is a', 'indent'), 'indent_status', 'confirm')) ), 'requisition_type', *))" % (data["item code"]) ) ))
			purchase_type = kwargs.get('purchase_type')
			ppo_no_unique = self.max_ppo_no()

			#Finding the item code based on given uuid of indents
			item_list = []
			indent_data = []
			'''
			total_indent_uuid = list(set( p.query("ids(objects(objects(subjects(subjects(*, 'is a', 'requisition_item'), \
			'item_name', '%s'), 'schedule_data', subjects(subjects(subjects(*, 'is a', 'schedule_qty_data'), 'indent_qty', \
			'confirm'), 'po_status', 'pending')), 'indent_data', subjects(subjects(subjects(*, 'is a', 'indent'), \
			'indent_status', 'confirm'), 'requisition_type', '%s') ))" %(kwargs.get('item_name'), kwargs.get('purchase_type'))) ))
			'''
			total_indent_uuid = list(set( p.query("ids(objects(objects(subjects(subjects(*,'item_name', '%s'), 'is a', 'requisition_item'), 'schedule_data', subjects(subjects(subjects(*, 'indent_qty','confirm'), 'po_status', 'pending'), 'is a', 'schedule_qty_data')), 'indent_data', subjects(subjects(subjects(*, 'indent_status', 'confirm'), 'requisition_head', '%s'), 'is a', 'indent')))" %(kwargs.get('item_name'), kwargs.get('purchase_type'))) ))
			for indent_uuid in total_indent_uuid:				
				schedule_uuid = list(set( p.query("ids( subjects( subjects( objects( subjects( subjects(*, 'item_name', '%s'), 'is a','requisition_item'), 'schedule_data', *), 'po_status', 'pending'), 'indent_data','%s'))" % ( str(kwargs.get('item_name')), str(indent_uuid)) ) ))
				#schedule_uuid = p.query("ids(subjects(subjects(*, 'po_status','pending'), 'indent_data', '%s'))" % (str(indent_uuid)) )
				#p.query("ids(subjects(objects(subjects(*, 'is a', 'requisition_item'), 'schedule_data', *), \
				#'indent_data','%s'))"%(str(indent_uuid)))				
				for sh_uuid in schedule_uuid :			
					req_uuid = p.query("ids( subjects( subjects( subjects( *,'item_name', '%s'), 'schedule_data', '%s'), 'is a', 'requisition_item'))" %( str(kwargs.get('item_name')), str(sh_uuid) ) )

					req_item_data = update_scaler.make_scaler( bwQuery(req_uuid).val()[0])
					temp_indent_data = {}
					temp_indent_data['cost_select'] = req_item_data['cost_select']
					temp_indent_data['uom'] = req_item_data['reqested_uom']
					temp_indent_data['section_select'] = req_item_data['section_select']
					
					sh_data = update_scaler.make_scaler( bwQuery(sh_uuid).val()[0])
					temp_indent_data['sh_uuid'] = sh_uuid
					temp_indent_data['indent_no'] = sh_data['indent_data'][0]['spi_no']
					temp_indent_data['schedule_date'] = sh_data['schedule_date']
					temp_indent_data['indent_qty'] = sh_data['issue_qty'] # indent qty is nothing but issue qty for req_class -indent req
					temp_indent_data['pending_qty'] = temp_indent_data['indent_qty'] 
					
					arg_data = {'requisition_class': 'Issue Requisition', "material_type":req_item_data['material_type'], 'item_name':kwargs['item_name'], 'requisition_type':req_item_data['requisition_type']}
					#temp_indent_data['current stock'] = inventory.get_current_stock(**arg_data)
					temp_indent_data['current stock'] = 0 #for the time being
					
					temp_indent_data['po_qty'] = sh_data.get('po_qty')
					temp_indent_data['rate'] = sh_data.get('rate') 
					temp_indent_data['value'] = sh_data.get('value')
					
					indent_data = indent_data + [temp_indent_data]
			
			vendor_data = p.query("select(subjects(subjects(*, 'vendor_code', '%s'), 'is a', 'vendor_master'))" %(vendor_code))
			payment_mode = vendor_data[0]['_value']['payment_mode'][0]
			payment_terms = vendor_data[0]['_value']['payment_terms'][0]
			return 	CheetahRender(data = {'edit_data':{'payment mode':payment_mode, 'payment terms':payment_terms, 'purchase_type':purchase_type, 'today':time.strftime("%Y-%m-%d")}, 'indent_data':indent_data, 'purchase_type':purchase_type, 'ppo_no':ppo_no_unique, 'vendor_code':vendor_code, 'vendor_name':vendor_name, 'item_details':mis_items}, template = os.path.join(self.path, "ppo_create.tmpl"))
	
	@iris.expose
	def po_status_create_old(self, *args, **kwargs): #16-july 
		'''
		Description:
			if 'po no' is not there for given uuid. then first it will create 'ppo no' before that it should be check
			there is 'indent no' is availbe or not.if not it will send message to the store department.
			then return the create _purchase.tmpl for creating the new 'ppo no'. otherwise return fill_po_details.tmpl
	
		parameter: uuid of 'mis details'
		return : tmpl
		'''
		p = iris.findObject('poseidon')
		#data = p.getObject(kwargs['process_mis_id'])[0].get('_value')
		data = update_scaler.make_scaler( bwQuery(kwargs['process_mis_id']).val()[0])
		pdata = []
		po_item = []
		# write the Query based on new database
		try:
			if data.has_key('po no') and len(data['po no']) > 0:
				#pdata = p.query("select(subjects(subjects(subjects(*, 'is a', 'po'), 'po no', '%s'), 'vendor_name', '%s'))"%(data['po no'][0], data['vendor_name'][0]))
				pdata = p.query("select(subjects(subjects(subjects(*, 'po no', '%s'), 'vendor name', '%s'), 'is a', 'po'))" %(data['po no'], data['vendor_name']))
				po_item = p.query("select( subjects( objects( subjects( subjects( *, 'po no', '%s'), 'is a', 'po'), 'po_items', *), 'item description', '%s'))" % (data['po no'], data['item description']) )
			else:
				pdata =  p.query("select(subjects(subjects(*, 'vendor name', '%s'), 'is a', 'po'))" %( data['vendor_name']))
				po_item = p.query("select(subjects(objects(subjects(subjects(*,'vendor name', '%s'), 'is a', 'po'), 'po_items', *), 'item description', '%s'))" %(kwargs['vendor_name'], kwargs['item description']))
		except KeyError:
			pass
		item_data = bwQuery.types('item master')
		item_list = []
		for x in item_data:
			item_dic = {"_id":x.get('_id')}
			item_dic.update( update_scaler.make_scaler( bwQuery(x).val()[0]))
			item_list.append(item_dic)
		if pdata == []:
			if data.has_key('ppo no') and len(data['ppo no']) > 0:
				ppo_data = {}
				ppo_items_data = {}
				ppo_items = {}
				try:					
					ppo_data_temp = p.query("select( subjects( subjects( subjects( *, 'ppo no','%s'), 'vendor_name', '%s'), 'is a', 'po' ))" % (data['ppo no'], data['vendor_name']) )[0]['_value']
					for key in ppo_data_temp.keys():
						ppo_data[key] = ppo_data_temp[key][0]

					ppo_items_data = p.query("select( subjects( objects( subjects( subjects(*,'ppo no', '%s'), 'is a', 'po'), 'po_items', *), 'item code', '%s'))" % (data['ppo no'], data['item code']) )			
					ppo_items_temp = ppo_items_data[0]['_value']
					for key in ppo_items_temp.keys():
						ppo_items[key] = ppo_items_temp[key][0]
					ppo_items['id'] = ppo_items_data[0]['_id']
					
				except:
					pass
				return 	CheetahRender(data = {'ppo_data':ppo_data, 'ppo_items':ppo_items}, template = os.path.join(self.path, "ppo_edit.tmpl"))
			else:
				# from here we are sending the data to the ppo_create.tmpl for creating the new 'ppo no'
				vendor_name = data['vendor_name']
				vendor_code = data['vendor_code']
				try:
					mis_items = p.query("select( subjects( subjects( subjects(subjects( *, 'mis no', '%s'), 'vendor_name', '%s'), 'item code', '%s'), 'is a', 'mis'))" % (data['mis no'], data['vendor_name'], data["item code"]) )
				except:
					pass
				purchase_type = list(set( p.query("names(objects( subjects(subjects(subjects(*, 'item_code', '%s'), 'schedule_data', subjects(subjects(subjects(subjects(*, 'indent_qty', 'confirm'), 'po_status', 'pending'), 'indent_data', subjects(subjects(*, 'indent_status', 'confirm'), 'is a', 'indent')), 'is a', 'schedule_qty_data') ), 'is a', 'requisition_item'), 'requisition_type', *))" % (data["item code"]) ) ))
				ppo_no_unique = self.max_ppo_no()
				return 	CheetahRender(data = {'edit_data':{}, 'purchase_type':purchase_type, 'ppo_no':ppo_no_unique, 'vendor_code':vendor_code, 'vendor_name':vendor_name, 'item_data':mis_items}, template = os.path.join(self.path, "ppo_create.tmpl"))
		else:
			return 	CheetahRender(data = {"po_data":pdata, 'po_item':po_item}, template = os.path.join(self.path, "fill_po_details.tmpl"))

	@iris.expose
	def max_ppo_no(self):
		'''
		This is return max and unique ppo_no format is HRPL/PPO/yy/00000
		'''	
		p = iris.findObject('poseidon')
		ppo_data = p.query("subjects(*, 'is a', 'po')")
		#max_ppo = 100000 + len(ppo_data)
		max_ppo = 1000 + len(ppo_data)
		if date.today().month < 4:
			#year_form = str(date.today().year - 1)[2:] + "-" + str(date.today().year)[2:]
			year_form = str(date.today().year - 1)[2:]
		else:
			#year_form = str(date.today().year)[2:] + "-" + str(date.today().year + 1)[2:]
			year_form = str(date.today().year)[2:]
		#ppo_formate = "hrpl/ppo/" + year_form + "/" + str(max_ppo)
		ppo_formate = year_form + "ppo" +  str(max_ppo)
		return ppo_formate

	@iris.expose
	def confirm_po_order(self, **kwargs):
		'''
		Descrption:Updating the Mis Details'.
		parameter:uuid of 'mis no' and uuid of item details of 'po no'.
		'''
		p = iris.findObject('poseidon')
		kwargs['is a'] = "mis_items_details"
		po_item_key = ["allotted_qty", "rate", "value", "po_no", "is a"]
		po_items_details = hartex.make_list_dic(*po_item_key, **kwargs)
		pprint.pprint(po_items_details)
		for data in po_items_details:
			try:
				if int(str(data['allotted_qty'])) <= 0 or int(str(data['rate'])) <= 0 or int(str(data['value'])) <= 0:
					po_items_details.remove(data)
			except:
				po_items_details.remove(data)
		if len(po_items_details) <= 0:
			iris.error("This Mis Details is not confirm, assign atleast one po no")
			return self.po_status()
		#' mis details' is upadting
		#mis_data = {'purchase_type':kwargs['mis_purchase_type'], 'po status':"ok", "po_items_details":po_items_details}
		mis_data = {'purchase_type':kwargs['mis_purchase_type'], 'temp_po_status':"ok", "po_items_details":po_items_details}
		p.setObject(kwargs['mis_id'], mis_data)
		iris.message("This Mis Details is Confirm")
		return self.po_status()

	@iris.expose
	def cancel_po_order(self, *args, **kwargs):
		'''
		Canceling the mis confirm po status is not ok
		'''
		p = iris.findObject('poseidon')
		#data = p.getObject(kwargs['mis_id'])[0]
		#del data['_value']['po status']
		#data['_value']['po status'] = 'not ok'
		#data.save()
		#p.setObject(kwargs['mis_id'], {'po status':"not ok"})
		p.setObject(kwargs['mis_id'], {'temp_po_status':"not ok"})
		p.save()
		return self.po_status()
	
	@iris.expose
	def no_indent_po_order(self, *args, **kwargs):
		'''
		If no indent found for this mis then po status is 'no indnet found'
		'''
		p = iris.findObject('poseidon')
		#p.setObject(kwargs['mis_id'], {'po status':"no indent found"})
		p.setObject(kwargs['mis_id'], {'temp_po_status':"no indent found"})
		return self.po_status()	
	
	@iris.expose
	def po_history(self, **kwargs):
		'''
		Finding the po history of given vendor and item name
		'''
		p = iris.findObject('poseidon')
		find_data = []
		if kwargs.get('vendor_name'):
			temp_query = "subjects(subjects(subjects(*,'vendor name', '%s'), 'post_status', 'posted'), 'is a', 'po')" %(kwargs['vendor_name'])
		else:
			temp_query = "subjects(subjects(*,'post_status', 'posted'), 'is a', 'po')"			
			
		if kwargs.get('item_name'):
			temp_query = "subjects(%s, 'po_items', subjects(subjects(*, 'item description', '%s'), 'is a', 'po_items'))" % (temp_query, kwargs['item_name'])
		temp_query = "ids(%s)" % (temp_query)
		try:
			data_uuid = list(set( p.query(temp_query) ))
		except:
			data_uuid = []
		for uid in data_uuid:
			temp = update_scaler.make_scaler( bwQuery(uid).val()[0] )	
			if temp.get('indent_status') == 'confirm':
				temp['check'] = "<input type='checkbox' name='uuid' id='uuid' style='margin-top:0.4em' value='%s'></input>" %bwQuery(uid).ids()[0]
			for items in temp.get('po_items'):
				if items.get('item description') == kwargs.get('item_name'):			
					temp['rate'] = items['rate']
					temp['total_po_qty'] = items['total_po_qty']
					temp['accepted_qty'] = items.get('accepted_qty', '0')
					try:
						temp['pending_qty'] = int(temp['total_po_qty']) - int(temp['accepted_qty'])
					except:
						temp['pending_qty'] = ''
			find_data = find_data + [temp]
		data_header = [{'name':'po no', 'display':'po no'},
						{'name':'po date', 'display':'po date'},
						{'name':'rate', 'display':'po rate'},
						{'name':'total_po_qty', 'display':'po qty'},
						{'name':'accepted_qty', 'display':'Received Qty'},
						{'name':'pending_qty', 'display':'Pending Qty'},
					]
		grid_id = iris.root.set_control_data(find_data)
		return CheetahRender(data={'data_header':data_header, 'grid_id':grid_id}, template = os.path.join(self.path, "history_grid.tmpl"))
	
	
	@iris.expose
	def item_history(self, **kwargs):
		'''
		item_history while creating the po... 
		'''
		p = iris.findObject('poseidon')
		find_data = []
		temp_query = "subjects(subjects(*, 'is a', 'po'),'post_status', 'posted')"			
			
		if kwargs.get('item_name'):
			temp_query = "subjects(%s, 'po_items', subjects(subjects(*,'item description', '%s'), 'is a', 'po_items'))" % (temp_query, kwargs['item_name'])
		temp_query = "ids(%s)" % (temp_query)
		try:
			data_uuid = list(set( p.query(temp_query) ))
		except:
			data_uuid = []
		#find_data = []
		for uid in data_uuid:
			#uid=p.query("ids(subjects(subjects(subjects(*, 'is a','vendor_master'),'revision_no','%s'),'vendor_registration_no','%s'))"%(revision_no,vendor_registration_no))
			temp = update_scaler.make_scaler( bwQuery(uid).val()[0] )	
			#print kwargs['indent_status']
			if temp.get('indent_status') == 'confirm':
				temp['check'] = "<input type='checkbox' name='uuid' id='uuid' style='margin-top:0.4em' value='%s'></input>" %bwQuery(uid).ids()[0]
			for items in temp.get('po_items'):
				if items.get('item description') == kwargs.get('item_name'):			
					temp['rate'] = items['rate']
					temp['total_po_qty'] = items['total_po_qty']
					temp['accepted_qty'] = items.get('accepted_qty', '0')
					try:
						temp['pending_qty'] = int(temp['total_po_qty']) - int(temp['accepted_qty'])
					except:
						temp['pending_qty'] = ''
			find_data = find_data + [temp]
		#pprint.pprint(find_data)
		data_header = [{'name':'vendor name', 'display':'vendor name'},
						{'name':'po date', 'display':'po date'},
						{'name':'po date', 'display':'po date'},
						{'name':'rate', 'display':'po rate'},
						{'name':'total_po_qty', 'display':'po qty'},
						{'name':'accepted_qty', 'display':'Received Qty'},
						{'name':'pending_qty', 'display':'Pending Qty'},
					]
		grid_id = iris.root.set_control_data(find_data)
		return CheetahRender(data={'data_header':data_header, 'grid_id':grid_id}, template = os.path.join(self.path, "history_grid.tmpl"))
	
	'''added by Krish'''
	@hermes.service()
	@iris.expose
	def get_po_item_details(self,  **kwargs):
		'''
		get_po_item_details
		'''
		#p = iris.findObject('poseidon')
		data_dic = {}
		if len(kwargs['item code']) > 0:
			data = bwQuery.select( where = {'is a':'item master', 'item description':str(kwargs['item code'])})
			try:
				data_dic = data.val()[0]
				data_dic['_id'] = data.ids()[0]
			except:
				pass
		return data_dic
	'''added by Krish'''
	
	@iris.expose
	def create_check_po(self, *args, **kwargs):
		'''
		create_check_po
		'''
		data = {}
		if kwargs['type'] == 'check':
			return 	CheetahRender( data = {'data':data}, template = os.path.join(self.path, "check_po.tmpl"))			
		elif kwargs['type'] == 'create':
			item_data = bwQuery.types('item master')
			item_list = []
			for x in item_data:
				item_dic = {"_id":x.get('_id')}
				item_dic.update( update_scaler.make_scaler(bwQuery(x).val()[0]) )
				item_list.append(item_dic)
			return 	CheetahRender( data = {'data':data, 'item_data':item_list}, template = os.path.join(self.path, "ppo_create.tmpl"))
			
	@iris.expose
	def search_po(self, **kwargs):
		'''
		Searching the 'po'
		'''
		#p = iris.findObject('poseidon')
		data = []
		try:
			if kwargs['supp'] != "" and kwargs['item'] != "" :
				data = bwQuery.select( where = {'is a':"po", 'vendor_name':kwargs['supp'], 'item code':kwargs['item']})
			elif kwargs['item'] != "" :
				data = bwQuery.select( where = {'type':"po", 'item code':kwargs['item']}) 
			elif kwargs['supp'] != "" :
				data = bwQuery.select( where = {'type':"po", 'vendor_name':kwargs['supp']}) 
		except KeyError:
			pass
		return CheetahRender(data = {'data':data}, template = os.path.join(self.path, "check_po.tmpl"))
		
	@iris.expose
	def get_item_description(self):
		'''
		finding the item_description
		'''		
		item_data = bwQuery.types('item master')
		item_list = []
		for x in item_data:
			item_dic = {"_id":x.get('_id')}
			item_dic.update( update_scaler.make_scaler( bwQuery(x).val()[0] ))
			item_list.append(item_dic)
		item_desc = {}
		for x in item_list:
			item_desc[x['item description']] = x.get('_id')		
		iris.json(item_desc)
		return ""
		
	@iris.expose
	def paginate(self, **kwargs):
		'''
		paginate, prev defined....
		'''
		self.find_path = os.path.join( os.getcwd(), 'apps', 'purchasemanager', 'modules', 'purchase', 'resources', 'views')	
		po_data = Idea.findAll('po') 
		total_len = len(po_data)
		total_page = total_len//3
		if( total_len - total_page*3>0):
			total_page += 1
		p_no = int(kwargs['page_no'])
		str_no = (p_no-1)*3
		end_no = (p_no)*3
		if end_no > total_len:
			end_no = total_len
		po_temp_data = []
		for x in range(str_no, end_no):
			temp = Idea.get_value(po_data[x])
			temp['check'] = "<input type='radio' 'name='process'></input>"
			temp['edit'] = "<a href='#'><img src='/purchasemanager/resources/images/edit.png' class='imgbut' style='width:20px;height:20px;'/></a>"
			temp['po date'] = time.strftime("%d/%m/%Y", time.localtime( float( str( po_data[x]['po date']))))	
			temp['schedule date'] = time.strftime("%d/%m/%Y", time.localtime( float( str(po_data[x]['schedule date']))))	
			temp['po no<br/>po date'] = temp.get('po no') + "<br />" + temp.get('po date')
			temp['item code<br />item description'] = temp['item code'] + "<br />" + temp['item description']
			temp['po qty'] = str(temp.get('po qty')) + " " + temp['uom']
			temp['value(rs)'] = temp['value']
			po_temp_data.append( (str(temp['po no']), temp))
		
		po_temp_data.sort(reverse=True)
		#po_temp_data.reverse()	
		po_temp_data = [po_temp_data[x][1] for x in xrange(len(po_temp_data))]	
			
		data_header = ['check', 'edit', 'po no<br />po date', 'po type', 'item code<br />item description', \
		'vendor_name', 'po qty', 'value(rs)', 'e duty', 's tax', 'freight', 'schedule date', 'delv qty', 'pending qty']
		grid_id = iris.root.analytics.grid.createGrid(po_temp_data, data_header)
		grid_length = len(po_data)
		return CheetahRender( data = {'total_page':total_page, 'grid_length':grid_length, 'grid_id':grid_id, }, template = os.path.join(self.path, "grid_update.tmpl"))
	
	@iris.expose
	def show_po_report(self, *args, **kwargs):
		'''
		show_po_report
		'''
		po = update_scaler.make_scaler(bwQuery(kwargs["po_id"]).val()[0])
		print "po::::::::::::::::::::::::::::::::::", po		
		#print po.get('vendor name')
		#print po.get('vendor code')
		v_reg_no = bwQuery.select(where={'vendor_name':po.get('vendor name'), 'vendor_code':po.get('vendor code'), 'is a':'vendor_master'}).attr('vendor_registration_no').names()[0]
		#print v_reg_no[0]
		v_addrs = update_scaler.make_scaler(bwQuery.select(where={'vendor_registration_no':str(v_reg_no), 'is a':'vendor_master_contact'}).val()[0])
		#import pprint
		#pprint.pprint(po)		
		#print " H "*20
		#pprint.pprint(v_addrs)
		return CheetahRender(data={'data':po, 'address':v_addrs}, template = os.path.join(self.path, "po_report.tmpl"))


	#  FOR DATA IMPORT OF PO
	@iris.expose
	def data_import(self):	
		'''
		This is importing the data from rasi data for po, import by data import application
		'''
		# Add all netrate to the total po value at the header level
		def findper(*kwargs, **kkwargs):
			'''
			For finding the % of tax, discount
			'''
			kwargs = kwargs[0]
			#print kwargs
			#print kwargs
			#kwargs = kwargs['kwargs']
			per_data = {}
			#print kkwargs
			total_value = float(kwargs['PD1POQTY'][0])*float(kwargs['PD1PRICE'][0]) 
			per_data['PD1DISCOUNT'] = "%.2f" %( float(kwargs['PD1DISCOUNT'][0])*100/total_value )
			dis_value = 100/(total_value - float(kwargs['PD1DISCOUNT'][0]) )
			
			per_data['PD1EXCISEDUTY'] = "%.2f" %( float(kwargs['PD1EXCISEDUTY'][0])*dis_value )
			per_data['PD1FREIGHT'] = "%.2f" %( float(kwargs['PD1FREIGHT'][0])*dis_value )
			per_data['PD1SALESTAX'] = "%.2f" %(  float(kwargs['PD1SALESTAX'][0])*dis_value ) 
			per_data['PD1CESS'] = "%.2f" %( float(kwargs['PD1CESS'][0])*100/dis_value )
			per_data['PD1SURCHARGE'] = "%.2f" %( float(kwargs['PD1SURCHARGE'][0])*dis_value )
			return per_data
			
			
		p = iris.findObject('poseidon')
		ip = iris.request.remote.ip
		print " PO  DATA IS IMPORTING    "
		requisition_data_dict =  {'department': 'Purchase',
							'is a': 'requisition',
							'pirv_date': '',
							'pirv_no': '',
							'post_status': 'posted',
							'imported': 'true',
							'requisition_data': [{'availability': [u''],
												  'bin': [u''],
												  'bom': [u''],
												  'cost_code': '0',
												  'cost_select': '0',
												  'current_department': 'Purchase',
												  'department_code': [122],
												  'department_select': 'Purchase',
												  'equipment': [u''],
												  'equipment_select': [u''],
												  'ip': ip,
												  'is a': [u'requisition_item'],
												  'item_code': '',
												  'item_name': '',
												  'item_uom': [u''],
												  'machine_code': [u''],
												  'machine_select': [u''],
												  'material_type': [u'N/A'],
												  'pmn': [u''],
												  'pp_no': [u''],
												  'project_code': [u''],
												  'project_select': [u''],
												  'purchase_type': [u''],
												  'purpose': [u''],
												  'repeat': [u'None'],
												  'reqested_qty': [u'0'],
												  'reqested_uom': [u''],
												  'requisition_class': [u'Indent Requisition'],
												  'requisition_no': '',
												  'requisition_type': '',
												  'requisition_head': '',
												  'schedule_data':'',
												  'section_code': [u''],
												  'section_select': [u'']}],
							'requisition_type': '',
							'status': 'Pending'}
		sh_data_dict = [{
				'indent_qty':"confirm",
				'is a': 'schedule_qty_data',
				'issue_date': '',
				'issue_qty': '',
				'po_date': '',
				'po_qty': '',
				'po_status': 'confirm',
				'schedule_date': '',
				'schedule_qty': '',
				'value': '',
				'indent_data':{
					'department': 'Production',
					'indent_status': 'confirm',
					'is a': 'indent',
					'imported': 'true',
					'requisition_type': '',
					'requisition_head': '',
					'spi_date': '',
					'spi_no': ''}
			}]
	
		po_items_data_dict = {'cost_select': '',
			'current stock': '',
			'discount': '',
			'excise_duty': '',
			'freight': '',
			'indent_no': '',
			'ip': ip,
			'is a': 'po_items',
			'imported': 'true',
			'item description': '',
			'other_tax': '',
			'po_item_schedule_date': '',
			'rate': '',
			'net_rate': '',
			'sale_tax': '',
			'section_select': '',
			'total_po_qty': '',
			'uom': '',
			'vat': '',
			'cess':'',
			'surcharge':'',					
			'sh_uuid':''
			}	
		po_data_dict = {'delivery place': '',
					'freight': '',
					'ip': ip,
					'is a': ['po', 'pending'],
					'imported': 'true',
					'mode of transport': '',
					'payment mode': '',
					'price basis': '',
					'insurance': '',
					'insurance_type':'',
					'payment terms': '',
					'po date': '',
					'po no': '',
					'po_value': '',
					'post_status': 'posted',
					'ppo no': '',
					'purchase type': '',
					'purchase type master': '',
					'purchase head': '',
					'quotation date': '',
					'quotation no': '',
					'vendor code': '',
					'vendor name': '',
					'po_items':''}			
		ip = iris.request.remote.ip
		po_import_data = p.query("select_one(subjects(*, 'is a', 'POHDR'))") #this table name is po header table  name pohdr.xls
		print "run"
		all_vendor_code = []
		vendor_data = []
		for  po_temp in  po_import_data:
			po_uuid = po_temp['_id']
			po_imp_data = po_temp['_value']
			indent_data = p.query("select_one(subjects(subjects(*, 'PD1PONO', '%s'), 'is a', 'PODTL'))" %(str(po_imp_data['PO NUMBER'][0])))  #this is po details of given header					
			#indent_data = p.query("select_one(subjects(subjects(*, 'is a', 'PODTL'), 'PD1PONO', '09DV0002'))")  #this is po details of given header					
			total_pi_im_uuid = []
			po_value = 0.0
			total_item = []
			for temp_pi_im_data in indent_data:
				pi_im_uuid = temp_pi_im_data['_id']
				pi_im_data = temp_pi_im_data['_value']
				#print type(pi_im_data) 
				#pprint.pprint(pi_im_data)
				per_data = findper(pi_im_data)
				sh_data = sh_data_dict
				sh_data[0]['issue_date'] = str(po_imp_data['PO DATE'][0]).replace('/', '-')
				sh_data[0]['indent_data']['requisition_type'] = po_imp_data['PURCHASE TYPE']
				sh_data[0]['indent_data']['spi_no'] = pi_im_data['PD1INDEN']
				sh_uuid = p.addObject(sh_data, save=False)
				
				total_pi_im_uuid = total_pi_im_uuid + [pi_im_uuid]
			
				requisition_data =  requisition_data_dict
				requisition_data['pirv_date'] = str(po_imp_data['PO DATE'][0]).replace('/', '-')
				requisition_data['pirv_no'] = pi_im_data['PD1INDEN']
				requisition_data['requisition_type']  = po_imp_data['PURCHASE TYPE']
				requisition_data['requisition_head']  = po_imp_data['PURCHASE TYPE MASTER']
				requisition_data['requisition_data'][0]['item_code'] =  pi_im_data['PD1ITE']
				#item_name = list(set( p.query("names(objects(subjects(subjects(*, 'is a', 'item master'), 'item code', '%s'),  'item description', *))" % (str(pi_im_data['PD1ITE']))) ))
				item_name = list(set( p.query("names(objects(subjects(subjects(*, 'item code', '%s'), 'is a', 'item master'), 'item description', *))" % (str(pi_im_data['PD1ITE'][0]))) ))
				if len(item_name) > 0:
					item_name = item_name[0]
				else:
					item_name = pi_im_data['PD1ITE']
				if pi_im_data['PD1ITE'] not in total_item:
					total_item = total_item + pi_im_data['PD1ITE'] #Adding item code
				#requisition_data['requisition_data'][0]['material_type'] =  item_name
				requisition_data['requisition_data'][0]['reqested_uom'] =  pi_im_data['PD1']
				requisition_data['requisition_data'][0]['item_name'] =  item_name
				requisition_data['requisition_data'][0]['requisition_no'] =  pi_im_data['PD1INDEN']
				requisition_data['requisition_data'][0]['requisition_type'] =  po_imp_data['PURCHASE TYPE']
				requisition_data['requisition_data'][0]['requisition_head'] =  po_imp_data['PURCHASE TYPE MASTER']
				requisition_data['requisition_data'][0]['schedule_data'] = sh_uuid
				
				p.addObject(requisition_data, save=False)
				po_items_data = po_items_data_dict
				po_items_data['indent_no'] = pi_im_data['PD1INDEN']
				po_items_data['net_value'] = pi_im_data['PD1NETRATE']
				po_items_data['total_po_qty'] = pi_im_data['PD1POQTY']
				po_items_data['uom'] =  pi_im_data['PD1']
				po_items_data['rate'] = pi_im_data['PD1PRICE']
				po_items_data['sh_uuid'] = sh_uuid
				po_items_data['item description'] = item_name	
				
				po_items_data['discount'] = per_data['PD1DISCOUNT']
				po_items_data['excise_duty'] = per_data['PD1EXCISEDUTY']
				po_items_data['freight'] = per_data['PD1FREIGHT']
				po_items_data['sale_tax'] = per_data['PD1SALESTAX']				
				po_items_data['cess'] = per_data['PD1CESS']
				po_items_data['surcharge'] = per_data['PD1SURCHARGE']					
				try:
					po_value = po_value + float(pi_im_data['PD1NETRATE'][0])
				except:
					pass
				p.removeObject(pi_im_uuid, save=False) #updating the same uuid 'is a':'po_items'
				p.setObject(pi_im_uuid, po_items_data, save=False)
			po_data = []
			if len(total_pi_im_uuid) >0:
				#date = po_imp_data['PO DATE'].replace('/', '-')
				po_data = po_data_dict
				po_data['po date'] =  str(po_imp_data['PO DATE'][0]).replace('/', '-')
				po_data['po no'] =  po_imp_data['PO NUMBER']
				#po_data['po_imported'] =  "true"
				po_data['po_value'] = str(po_value)
				po_data['purchase type'] =  po_imp_data['PURCHASE TYPE']
				po_data['purchase type master'] = po_imp_data['PURCHASE TYPE MASTER']
				po_data['quotation no'] = po_imp_data['VENDOR REF NO']
				po_data['vendor code'] = po_imp_data['VENDOR CODE']
				#print "!!!!"
				# print po_imp_data['VENDOR CODE']
				# print total_item
				# print type(po_imp_data['VENDOR CODE'])
				# print type(total_item)
				#print all_vendor_code
				if po_imp_data['VENDOR CODE'][0] not in all_vendor_code:
					all_vendor_code = all_vendor_code + po_imp_data['VENDOR CODE']
					vendor_data = vendor_data + [{po_imp_data['VENDOR CODE'][0]:total_item}]
				else:
					#append item to the that vendor
					for i in vendor_data:
						if i.has_key(po_imp_data['VENDOR CODE'][0]):
							# print "else"
							# print i[po_imp_data['VENDOR CODE'][0]]
							# print type(i[po_imp_data['VENDOR CODE'][0]])
							# print type(total_item)
							i[po_imp_data['VENDOR CODE'][0]] = set( list(i[po_imp_data['VENDOR CODE'][0]]) + total_item)							
							break
				vendor_name = list(set( p.query("names(objects(subjects(subjects(*, 'vendor_code', '%s'), 'is a', 'vendor_master'), 'vendor_name', *))" %(str(po_imp_data['VENDOR CODE'][0]))) ))
				if len(vendor_name) > 0:
					po_data['vendor name'] = vendor_name[0]
				else:
					po_data['vendor name'] = ""
				po_data['po_items'] = total_pi_im_uuid
				
				p.removeObject(po_uuid, save=False)
				p.setObject(po_uuid, po_data, save=False)
		print " adding item to the vendor "
		print "po is succe..."
		#print vendor_data
		vendor_items = {'basic_units': '',
						'is a':"vendor_items", 
							 'conversion':'',
							 'frieght_terms':'',
							 'item_code':'',
							 'item_name':'',
							 'lead_time':'',
							 'material_type':'',
							 'max_deliverable_value':'',
							 'min_deliverabler_qty':'',
							 'min_order_qty': '',
							 'min_order_value':'',
							 'revision_no':'0',
							 'packing_unit':'',
							 'per':'',
							 'price':'',
							 'shelf_life':'',
							 'uom':'',
							 'vend_reg':''}
		for vendor in vendor_data:
			vend_reg = list(set( p.query("names(objects(subjects(subjects(*, 'vendor_code', '%s'), 'is a', 'vendor_master'),  'vendor_registration_no', *))" %(vendor.keys()[0])) ))
			if len(vend_reg) > 0:
				for item in list(set( vendor[vendor.keys()[0]] )):
					# add item here , dont add those item who is already assign
					item_exit = p.query("ids(subjects(subjects(subjects(*, 'vend_reg', '%s'), 'item_code', '%s' ), 'is a', 'vendor_items'))" % (vend_reg[0], item)) 
					item_data = p.query("select_one(subjects(subjects(*, 'item code', '%s'), 'is a', 'item master'))" %(item))
					if len(item_exit) < 1 and len(item_data) > 0:
						
						vendor_items['item_code'] = item
						vendor_items['item_name'] = item_data[0]['_value']['item description']
						vendor_items['material_type'] = item_data[0]['_value']['material type']
						vendor_items['uom'] = item_data[0]['_value']['item uom']
						vendor_items['vend_reg'] = vend_reg
						p.addObject(vendor_items, save=False)
					else:
						print item
			else:
				print vendor[vendor.keys()[0]]
				#print vendor
				print "This vendor %s is not exit in vendor master" %(vendor.keys()[0])
		#for updating the total_po and total_mrn, at vendor master level, we can write this query in upper for loop
		vc = p.query("select_one(subjects(*, 'is a', 'vendor_master'))")
		for s in vc:
		    tpo = len(p.query("ids(subjects(subjects(*, 'vendor code', '%s'), 'is a', 'po'))"%(s['_value']['vendor_code'][0])))
		    tmrn = len(p.query("ids(subjects(subjects(*, 'vendor_code', '%s'), 'is a', 'mrn'))"%(s['_value']['vendor_code'][0])))
		    trej = len(p.query("ids(subjects(subjects(subjects(*, 'is a', 'reject mis by store'), 'vendor_code', '%s'), 'is a', 'mis'))"%(s['_value']['vendor_code'][0])))
		    p.setObject(s['_id'], {'total_po':tpo, 'total_mrn':tmrn, 'total_rejections':trej}, save=False)
		p.save()
		print "  PO DATA IMPORT IS DONE "
		print
		raise iris.HTTPRedirect("/purchasemanager")
		
	#  FOR DATA IMPORT OF PO
	@iris.expose
	def data_import_21(self):	#working fine we have to write the query for #486
		'''
		This is importing the data from rasi data, import by data import application
		'''
		# Add all netrate to the total po value at the header level
		p = iris.findObject('poseidon')
		print " PO  DATA IS IMPORTING    "
		ip = iris.request.remote.ip
		po_import_data = p.query("select_one(subjects(*, 'is a', 'POHDR'))") #this table name is po header table  name pohdr.xls
		print "run"
		for  po_temp in  po_import_data:
			po_uuid = po_temp['_id']
			po_imp_data = po_temp['_value']
			indent_data = p.query("select_one(subjects(subjects(*, 'PD1PONO', '%s'), 'is a', 'PODTL'))" %(str(po_imp_data['PO NUMBER'][0])))  #this is po details of given header					
			#indent_data = p.query("select_one(subjects(subjects(*, 'is a', 'PODTL'), 'PD1PONO', '09DV0002'))")  #this is po details of given header					
			total_pi_im_uuid = []
			po_value = 0
			for temp_pi_im_data in indent_data:
				pi_im_uuid = temp_pi_im_data['_id']
				pi_im_data = temp_pi_im_data['_value']
				
				sh_data = [{
						'indent_qty':"confirm",
						'is a': 'schedule_qty_data',
						'issue_date': str(po_imp_data['PO DATE'][0]).replace('/', '-'),
						'issue_qty': '',
						'po_date': '',
						'po_qty': '',
						'po_status': [u'confirm'],
						'schedule_date': '',
						'schedule_qty': '',
						'value': '',
						'indent_data':{
							'department': 'Production',
							'indent_status': 'confirm',
							'is a': 'indent',
							'requisition_type': po_imp_data['PURCHASE TYPE'],'insurance_type':'',
							'spi_date': '',
							'spi_no': pi_im_data['PD1INDEN']}
					}]
				
				sh_uuid = p.addObject(sh_data, save=False)
				total_pi_im_uuid = total_pi_im_uuid + [pi_im_uuid]
				requisition_data =  {'department': 'Purchase',
									'is a': 'requisition',
									'pirv_date': str(po_imp_data['PO DATE'][0]).replace('/', '-'),
									'pirv_no': pi_im_data['PD1INDEN'],
									'post_status': 'posted',
									'requisition_data': [{'availability': [u''],
														  'bin': [None],
														  'bom': [u''],
														  'cost_code': '',
														  'cost_select': '',
														  'current_department': 'Purchase',
														  'department_code': [122],
														  'department_select': 'Purchase',
														  'equipment': [u''],
														  'equipment_select': [u''],
														  'ip': ip,
														  'is a': [u'requisition_item'],
														  'item_code': pi_im_data['PD1ITE'],
														  'item_name': pi_im_data['PD1ITE'],
														  'item_uom': [u''],
														  'machine_code': [None],
														  'machine_select': [None],
														  'material_type': [u'raw material'],
														  'pmn': [None],
														  'pp_no': [None],
														  'project_code': [None],
														  'project_select': [None],
														  'purchase_type': [None],
														  'purpose': [u''],
														  'repeat': [u'None'],
														  'reqested_qty': [u'0'],
														  'reqested_uom': [u''],
														  'requisition_class': [u'Indent Requisition'],
														  'requisition_no': pi_im_data['PD1INDEN'],
														  'requisition_type': po_imp_data['PURCHASE TYPE'],
														  'schedule_data':sh_uuid,
														  'section_code': [u''],
														  'section_select': [u'']}],
									'requisition_type': po_imp_data['PURCHASE TYPE'],
									'status': [u'Pending']}
				
				p.addObject(requisition_data, save=False)
				po_items_data = {'cost_select': '',
					'current stock': '',
					'discount': pi_im_data['PD1DISCOUNT'],
					'excise_duty': pi_im_data['PD1EXCISEDUTY'],
					'freight': pi_im_data['PD1FREIGHT'],
					'indent_no': pi_im_data['PD1INDEN'],
					'ip': ip,
					'is a': 'po_items',
					'item description': pi_im_data['PD1ITE'],
					'other_tax': '',
					'po_item_schedule_date': '',
					'rate': pi_im_data['PD1PRICE'],
					'net_rate': pi_im_data['PD1NETRATE'],
					'sale_tax': pi_im_data['PD1SALESTAX'],
					'section_select': '',
					'total_po_qty': pi_im_data['PD1POQTY'],
					'uom': pi_im_data['PD1'],
					'vat': '',
					'cess':pi_im_data['PD1CESS'],
					'surcharge':pi_im_data['PD1SURCHARGE'],					
					'sh_uuid':sh_uuid
					}
				try:
					po_value = po_value + int(pi_im_data['PD1NETRATE'][0])
				except:
					pass
				p.removeObject(pi_im_uuid, save=False)
				p.setObject(pi_im_uuid, po_items_data, save=False)
			po_data = []
			if len(total_pi_im_uuid) >0:
				#date = po_imp_data['PO DATE'].replace('/', '-')
				po_data = {'delivery place': '',
							'freight': '',
							'ip': ip,
							'is a': [u'po', u'pending'],
							'mode of transport': '',
							'payment mode': '',
							'payment terms': '',
							'price basis': '',
							'insurance': '',
							'insurance_type':'',
							'signature_type':'',
							'po date': str(po_imp_data['PO DATE'][0]).replace('/', '-'),
							'po no': po_imp_data['PO NUMBER'],
							'po_value': po_value,
							'post_status': 'posted',
							'ppo no': '',
							'purchase type': po_imp_data['PURCHASE TYPE'],
							'purchase type master': po_imp_data['PURCHASE TYPE MASTER'],
							'quotation date': '',
							'quotation no': po_imp_data['VENDOR REF NO'],
							'vendor code': po_imp_data['VENDOR CODE'],
							'vendor name': '',
							'po_items':total_pi_im_uuid}
				p.removeObject(po_uuid, save=False)
				p.setObject(po_uuid, po_data, save=False)
		p.save()
		print "  PO DATA IMPORT IS DONE "
		print
		raise iris.HTTPRedirect("/purchasemanager")




	@hermes.service()
	@iris.expose
	def find_item_name1(self, **kwargs): 
		'''
		like find_vendor we can optimize this code also.
		Finding the item name based on department and requisition type
		parameter: kwargs['department'], kwargs['cost_centre'], kwargs['requisition_type']
		return : [item_name]
		'''
		p = iris.findObject('poseidon')
		# in this query i am finding the all item code, which is related to the pending indent but  'po_status' is 'pending'
		print "kwargs::::::::::::::::::::::::::::::::::::::::::::::::::::::", kwargs
		item_name = []
		if kwargs.get('cost_centre') and kwargs.get('requisition_head') and kwargs.get('department'):
			print "in ifFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
			item_name = list(set(p.query("names(objects(subjects(subjects(subjects(subjects(subjects(*,'cost_select','%s'),'requisition_head','%s'),'department_select','%s'),'schedule_data',subjects(subjects(subjects(subjects(*,'po_status','pending'),'indent_qty','confirm'),'indent_data',subjects(subjects(*, 'indent_status', 'confirm'), 'is a', 'indent')), 'is a','schedule_qty_data')), 'is a', 'requisition_item'),'item_name', *))" % (kwargs.get('cost_centre', ''), kwargs.get('requisition_head', ''), kwargs.get('department', '')))))
		elif kwargs.get('cost_centre') and kwargs.get('requisition_type') and kwargs.get('department'):
			print "in elifGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG"
			item_name = list(set(p.query("names(objects(subjects(subjects(subjects(subjects(subjects(*,'cost_select','%s'),'requisition_type','%s'),'department_select','%s'),'schedule_data',subjects(subjects(subjects(subjects(*,'po_status','pending'),'indent_qty','confirm'),'indent_data',subjects(subjects(*, 'indent_status', 'confirm'), 'is a', 'indent')), 'is a','schedule_qty_data')), 'is a', 'requisition_item'),'item_name', *))" % (kwargs.get('cost_centre', ''), kwargs.get('requisition_type', ''), kwargs.get('department', '')))))
		elif kwargs.get('department') == 'ALL':
			print "in el dept all HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
			item_name = list(set( p.query("names( objects(subjects(subjects(*,'schedule_data',subjects(subjects(subjects(subjects(*, 'po_status', 'pending'),'indent_qty', 'confirm'), 'is a', 'schedule_qty_data'),'indent_data',subjects(subjects(*,'indent_status', 'confirm'), 'is a', 'indent'))),'is a','requisition_item'),'item_name', *))" )))
			print "ttttttttttttttttttttttttttttttttttttttttttttttttttt", item_name		
		else:
			print "in else HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH"
			item_name = list(set( p.query("names( objects(subjects(subjects(subjects(*,'department_select', '%s'),'schedule_data',subjects(subjects(subjects(subjects(*, 'po_status', 'pending'),'indent_qty', 'confirm'), 'is a', 'schedule_qty_data'),'indent_data',subjects(subjects(*,'indent_status', 'confirm'), 'is a', 'indent'))),'is a','requisition_item'),'item_name', *))" % (kwargs.get('department')))))
			print "tttttttttttttttttttttttttttttttttttttttttttttttttttXXXXXXXXXXXXXXXXXXXXXXXX", item_name				
		# Here we can fetch the data based on Given vendor, if given
		if kwargs.get('vendor_name'):
			try:
				ven_reg_no = list(set( p.query("names( objects(subjects(subjects(subjects(*, 'vendor_approve', 'yes'), 'vendor_name', '%s'), 'is a', 'vendor_master'), 'vendor_registration_no', *) )" %(kwargs.get('vendor_name'))) ))
				vendor_item = p.query("names( objects(subjects(subjects(*, 'vend_reg', '%s'), 'is a', 'vendor_items'),'item_name', *) )" % (ven_reg_no[0]) )
				
				item_name = list( set.intersection( set(vendor_item), set(item_name) ))
			except:
				print 
				print "error coming in find_item_name for given keywords"
				print kwargs
				print
				pass
		data = []
		for item in item_name:
			data = data + [cgi.escape(item, quote=True)]
		return data
	@hermes.service()
	@iris.expose
	def find_rh_type1(self, **kwargs): 
		'''
		Finding the all requisition_head based on given department
		'''
		p = iris.findObject('poseidon')
		reqq = []
		requisition_head = []
		l=[]
		try:
			'''
			requisition_head = list(set( p.query("names(objects(subjects(subjects(subjects(subjects(*, 'is a', \
			'requisition_item'), 'item_name', '%s'), 'department_select', '%s'), 'schedule_data', subjects(subjects(*, 'is a', 'schedule_qty_data'), \
			'po_status', 'pending')), 'requisition_head', *))" %(kwargs.get('item_name'), kwargs.get('department'))) ))
			'''
			for i in dic[0]:
				print "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", i
				l.append(set(p.query("names(objects(subjects(subjects(subjects(subjects(*, 'item_name', '%s'), 'department_select', '%s'),'is a', 'requisition_item'), 'schedule_data', subjects(subjects(subjects(*, 'indent_data', subjects(subjects(*, 'indent_status','confirm'), 'is a', 'indent')), 'po_status', 'pending'), 'is a', 'schedule_qty_data')), 'requisition_head', *))" %(kwargs.get('item_name'), i))))
				#reqq = list(set( p.query("names(objects(subjects(subjects(subjects(subjects(*, 'item_name', '%s'), 'department_select', '%s'),'is a', 'requisition_item'), 'schedule_data', subjects(subjects(subjects(*, 'indent_data', subjects(subjects(*, 'indent_status','confirm'), 'is a', 'indent')), 'po_status', 'pending'), 'is a', 'schedule_qty_data')), 'requisition_head', *))" %(kwargs.get('item_name'), i))))
				print ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::",l
				#if len(reqq)>0:
					#requistion_head.insert(0,'reqq')
				for i in l:
					for j in i:
						requisition_head.append(j)
				print "requisition::::::::::::::::::", requisition_head
			#requisition_head.sort()
			print "outputOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO", requisition_head
			
		except:
			print "some error in given keywords for find_r_type"
			pass
		data = []
		for head in requisition_head:
			data = data + [cgi.escape(head, quote=True)]
		return data		
	@hermes.service()
	@iris.expose
	def find_cost_centre1(self, **kwargs): 
		'''
		Finding the all cost centre based on given department
		'''
		p = iris.findObject('poseidon')
		cost_centre = []
		try:
			# cost_centre = list(set( p.query("names(objects(objects(subjects(subjects(*, 'is a', 'department master'), \
			# 'department name', '%s'), 'cost centre details', *), 'cost centre description', *))" % (kwargs.get('department', ''))) ))
			cost_centre = list(set( p.query("names(objects(subjects(subjects(subjects(subjects(subjects(*, 'requisition_head', '%s'), 'item_name', '%s'), 'department_select', '%s'), 'schedule_data', subjects(subjects(*,'po_status', 'pending'), 'is a', 'schedule_qty_data')), 'is a','requisition_item'), 'cost_select', *))" %(kwargs.get('requisition_head'), kwargs.get('item_name'), kwargs.get('department'))) ))
			cost_centre.sort()
		except:
			pass
		data = []
		for head in cost_centre:
			data = data + [cgi.escape(head, quote=True)]
		return data


	@hermes.service()
	@iris.expose
	def pending_indent_uuid1(self, **kwargs):
		'''
		Finding the pending indent uuid for creating the new 'po'.
		parameter: kwargs['department'], kwargs['cost_centre'], kwargs['requisition_type'], 
				kwargs['vendor_name']
		return : [indent_uuid]
		'''
		p = iris.findObject('poseidon')
		find_data = []
		print "kwargs::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::",kwargs

		#if kwargs.get('refrence') == 'INDENTS' :
		temp_query = "subjects(subjects(*, 'indent_status','confirm'), 'is a', 'indent')"
		
		# Making SEARCH QUERY
		if kwargs.get('requisition_type'): # searching the data based on  requisition_type
			r = "subjects(*, 'requisition_type', '%s')" % (kwargs['requisition_type'])
			temp_query = replace(temp_query, "*", r)	
		
		if kwargs.get('requisition_head'): # searching the data based on  requisition_type
			r = "subjects(*, 'requisition_head', '%s')" % (kwargs['requisition_head'])
			print "r:::::::::::::::::::::::::::::::::::::", r
			temp_query = replace(temp_query, "*", r)	
			print "temp_query:::::::::::::::::::::::::::::::::::::::", temp_query		
		
		if kwargs.get('indent_status'):  # searching the data based on indent_status
			r = "subjects(*, 'indent_status', '%s')" % (kwargs['indent_status'])
			temp_query = replace(temp_query, "*", r)
			
		#*if kwargs.get('department'): # searching the data based on department
			#r = "subjects(*, 'department', '%s')" % (kwargs['department'])
			#temp_query = replace(temp_query, "*", r)
		# if kwargs.get('item_name'): # searching the data based on item name also
			# temp_query = "ids(objects(objects( \
										# subjects(subjects(subjects(*, 'is a', 'requisition_item'), 'cost_select', '%s'), 'item_name', '%s'), \
										# 'schedule_data', \
										# subjects(subjects(*, 'is a', 'schedule_qty_data'), 'po_status', 'pending') \
										# ), \
									# 'indent_data', \
									# %s \
								# ))" %(kwargs.get('cost_centre'), kwargs.get('item_name'), temp_query)
		# el
		if kwargs.get('vendor_name'): # with out item name			
			
			''' By default we cant show the all items, because of vendor
			# temp_query = "ids(objects(objects( \
										# subjects(subjects(subjects(*, 'is a', 'requisition_item'), 'cost_select', '%s'), 'item_name', *), \
										# 'schedule_data', \
										# subjects(subjects(*, 'is a', 'schedule_qty_data'), 'po_status', 'pending') \
										# ), \
									# 'indent_data', \
									# %s \
								# ))" %(kwargs.get('cost_centre'), temp_query)
			'''
			# Here Also Find only those item based on vendor
			ls = {}
			ls['item_name'] = kwargs['item_name']
			item_name = self.find_item_name1(ls)
			print "item_name::::::::::::::::::::::::::::::::::::::::", item_name
			q_or_condition = "''".join(item_name).replace("''", "' or '")
			print "q_or_condition::::::::::::::::::::::::::::", q_or_condition
			
			temp_query = "ids(objects(objects(subjects(subjects(*, 'item_name', '%s'), 'is a', 'requisition_item'),'schedule_data',subjects(subjects(*, 'po_status', 'pending'), 'is a', 'schedule_qty_data')),'indent_data',%s))" %(q_or_condition, temp_query)
		# End  SEARCH query
		#temp_query = "ids(" + temp_query + ")"
		try:
			print "tempCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC", temp_query
			data_uuid = list(set( p.query(temp_query) ))
			print "data_uuidDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD", data_uuid
		except:
			print "Some Error found"
			data_uuid = []
		#print 
		#print "data_uuid", data_uuid
		#print
		
		return data_uuid

	
