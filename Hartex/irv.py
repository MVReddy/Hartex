# pylint: disable-msg=W0312, C0301, C0321, C0111, C0103, R0902, R0904, R0911, R0912, R0913, R0914, W0104, W0142
'''
This module is used for creating the irv, this module is accessing by every department or other module
for creating the irv no
'''
from __future__ import division
from  string import replace, join
from  datetime import date
#from  datetime import timedelta, date
import datetime 
import time
import os , cgi

import iris, aphrodite
from plugins.CheetahPlugin import CheetahRender
import json, hermes
from idea import Idea
from apps.hartex.modules.update_scaler import update_scaler
from apps.hartex.modules.inventory import inventory
from bwquery import bwQuery
from apps.edp.modules import hartex_users
import pprint
class irv(object):
	'''
	This is class method for the irv , only one class we are defined  in irv
	'''
	path = os.path.join(os.getcwd(), 'apps', 'hartex', 'views', 'irv')
	def __init__(self):
		self.aphrodite = aphrodite.Aphrodite('hartex')

	
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
		elif len(kwargs)>0:
			if isinstance(kwargs.items()[0][1], list):
				for x in range(len(kwargs.items()[0][1])):
					return_dict = {}
					for y in kwargs.keys():
						return_dict[y] = kwargs[y][x]
					return_list.append(return_dict)
			else:
				return_list.append(kwargs)		
		return return_list
		
	@iris.expose
	def default(self):
		pass
	
	
	@iris.expose
	def index(self):
		grid_data = self.irv_grid()
		return ({'data_header':grid_data[0], 'grid_id':grid_data[1]})
	
	
	
	#Showing input field for search
	@iris.expose
	#@hartex_users.hartex_access_validate(module='storemanager',allow='storemanager_irv_grid')
	def grid_option(self, current_department=None, confirm_search=None):
		'''
		Showing the input field for searching the requsitions
		'''
		p = iris.findObject('poseidon')
		#current_department = kwargs['department']
		if current_department == 'Stores' and confirm_search== 'confirm':  #store can see tha all department data in confirm mode
			department_select = list(set( p.query("names(objects(subjects(*, 'is a', 'department master'), 'department name', *))") )) 
		else:
			department_select = [current_department]
		department_select.sort()
	
		
		return CheetahRender(data={'current_department':current_department, 'department_select':department_select, 'confirm_search':confirm_search}, \
			template = os.path.join(self.path, "search_irv.tmpl"))
	
	@iris.expose
	def irv_item(self, **kwargs):
		'''
		This is displaying the data in grid. NOt required
		'''
		def edit(id):
			'''
			for edit the irv_item
			'''
			return '''
				<a href='#'><img src='/purchasemanager/resources/images/edit.png' onclick="edit_po_no('%(id)s')" class='imgbut' style='width:20px;height:20px;'/></a>
			''' % {"id":id}
			
		def show_details_ppo_no(id):
			'''
			for showning the details of ppo
			'''
			return '''
				<a href='#'><img src='/purchasemanager/resources/images/revisionasd.png' onclick="ppo_no_details('%(id)s')" class='imgbut' style='width:20px;height:20px;'/></a>
			''' % {"id":id}
			
		p = iris.findObject('poseidon')
		req_temp_data = []
		#print " coming in grid "
		#print kwargs
		
		if kwargs.has_key('irv_uuid'):
			temp_req = p.query("ids(objects('%s', 'irv_data', *))" %(kwargs['irv_uuid']) )
		elif kwargs.has_key('irv_no'):
			temp_req = p.query("ids(subjects(subjects(*, 'is a', 'irv_item'), 'irv_no', '%s'))" % (kwargs['irv_no']))
		else:
			temp_req = p.query("ids(subjects(subjects(*, 'is a', 'temp_irv'), \
			'department_select','%s'))"%(kwargs['current_department']))
		for uid in temp_req:
			#uid=p.query("ids(subjects(subjects(subjects(*, 'is a','vendor_master'),'revision_no','%s'),'vendor_registration_no','%s'))"%(revision_no,vendor_registration_no))
			temp = update_scaler.make_scaler(bwQuery(uid).val()[0])	
			temp['check'] = "<input type='radio' name='uuid' id='uuid' style='margin-top:0.4em' value='%s'></input>" %bwQuery(uid).ids()[0]
			req_temp_data = req_temp_data + [temp]
		 
		data_header = [{'name':'check', 'display':'Check'}, {'name':'irv_type', 'display':'Req Type'}, {'name':'irv_head', 'display':'Req Head'},
		{'name':'material_type', 'display':'Material Type'}, {'name':'cost_select', 'display':'Cost center'}, 
		{'name':'section_select', 'display':'Section'}, {'name':'item_code', 'display':'Item Code'},
		{'name':'item_name', 'display':'Item Name'}, {'name':'item_uom', 'display':'UOM'}, {'name':'reqested_qty', 'display':'Requeste Qty'}]
		
		grid_id = iris.root.set_control_data(req_temp_data)
		return [data_header, grid_id]
		
	@iris.expose
	#@hartex_users.hartex_access_validate(module='storemanager',allow='storemanager_irv_grid')
	def irv_grid(self, **kwargs):
		'''
		This is displaying the data in grid.
		'''	
		p = iris.findObject('poseidon')
		req_temp_data = []
		if kwargs.has_key('department'):
			temp_req = p.query("ids(subjects(subjects(subjects(*, 'is a', 'irv'), 'department_select', '%s'), 'post_status', 'unposted'))" % (kwargs.get('department')) )
		else:
			#temp_req = p.query("ids(subjects(subjects(*, 'is a', 'irv'), 'post_status', 'unposted'))")
			temp_req = []
		print
		print temp_req
		print
		for uid in temp_req:
			#uid=p.query("ids(subjects(subjects(subjects(*, 'is a','vendor_master'),'revision_no','%s'),'vendor_registration_no','%s'))"%(revision_no,vendor_registration_no))
			temp = update_scaler.make_scaler(bwQuery(uid).val()[0])	
			temp['check'] = "<input type='checkbox' name='uuid' id='uuid' style='margin-top:0.4em' value='%s'></input>" %bwQuery(uid).ids()[0]
			req_temp_data = req_temp_data + [temp]
		pprint.pprint(req_temp_data)
		data_header = [{'name':'check', 'display':'Check'}, {'name':'irv_no', 'display':'IRV No'},
		{'name':'irv_date', 'display':'IRV Date'}, {'name':'material_type', 'display':'material type'},
		{'name':'item_name', 'display':'Item name'}, {'name':'department_select', 'display':'department'},
		{'name':'cost_select', 'display':'cost center'}, {'name':'irv_status', 'display':'Status'}]
		
		grid_id = iris.root.set_control_data(req_temp_data)
		return [data_header, grid_id]
	

	#Dispalying the irv data into the grid
	@iris.expose
	def irv_details(self, **kwargs):
		'''
		This is displaying data into the grid, calling from haretx/display
		'''
		p = iris.findObject('poseidon')
		#print kwargs
		current_department = kwargs['department']
		'''
		if current_department == 'Purchase' or current_department == 'Costing':  #purchase can see tha data of other department alse only in view mode
			department_select = list(set( p.query("names(objects(subjects(*, 'is a', 'department master'), 'department name', *))") )) 
		else:
			department_select = [current_department]
		department_select.sort()

		irv_type = list(set( p.query("names(objects(subjects(subjects(subjects(*, 'is a', 'other code master'), \
						'department name', 'Purchase'), 'master', 'irv type'), 'value', *))") ))
		irv_type.sort()
		'''
		#grid_data = self.irv_grid(**{'department':current_department})
		data_header = [{'name':'check', 'display':'Check'}, {'name':'irv_no', 'display':'IRV No'},
		{'name':'irv_date', 'display':'IRV Date'}, {'name':'material_type', 'display':'material type'},
		{'name':'item_name', 'display':'Item name'}, {'name':'department_select', 'display':'department'},
		{'name':'cost_select', 'display':'cost center'}, {'name':'irv_status', 'display':'Status'}]
		grid_id = iris.root.set_control_data([])
		#grid_id = grid_data[1]
		#irv_data = {}
		return CheetahRender(data={'current_department':current_department,  'data_header':data_header, 'grid_id':grid_id}, template = os.path.join(self.path, "irv_details.tmpl"))
	
	#For searching the irv data
	@iris.expose
	#@hartex_users.hartex_access_validate(module='storemanager',allow='storemanager_irv_grid')
	def search_irv(self):
		'''
		This is showing the search_irv.tmpl
		'''
		p = iris.findObject('poseidon')
		#current_department = kwargs['current_department']
		department_select = list(set( p.query("names(objects(subjects(*, 'is a', 'department master'), 'department name', *))") ))
		department_select.sort()
		irv_type = list(set( p.query("names(objects(subjects(subjects(subjects(*, 'is a', 'other code master'), \
						'department name', 'Purchase'), 'master', 'irv type'), 'value', *))") ))
		irv_type.sort()
		
		return CheetahRender(data={'department_select':department_select, 'irv_type':irv_type}, \
			template = os.path.join(self.path, "search_irv.tmpl"))
	
	#For creating the irv.... 
	@iris.expose
	def create_irv(self, **kwargs):
		'''
		For Creating the new irv. Taking Current_Department name, Also we are removing \
		"('is a':"temp_irv")", this data is temp. if user is Add, the irv item but not click on save
		for assign the 'irv no'
		'''
		#import pdb
		#pdb.set_trace()
		p = iris.findObject('poseidon')
		current_department = kwargs['current_department']
		if current_department == "Stores":
			hartex_users.hartex_access_validate2(module='storemanager',allow='storemanager_irv_add')
		if current_department == "Purchase":
			hartex_users.hartex_access_validate2(module='purchasemanager',allow='purchasemanager_irv_add')
		if current_department == "accounts":
			hartex_users.hartex_access_validate2(module='accounts',allow='accounts_irv_add')
		try:
			current_department_code = list(set( p.query("names(objects(subjects(subjects(*, 'is a', 'department master'), 'department name', \
				'%s'), 'department code', *))" %(current_department) ) ))[0]
		except:
			current_department_code = ""
		department_select = [current_department]
		
		#section_code = list(set( p.query("names(objects(objects(subjects(*, 'is a', 'department master'),'cost centre details', *),'section code',*))") ))
		section_select = list(set( p.query("names(objects(objects(subjects(subjects(*, 'is a', 'department master'), \
		'department name', '%s'), 'section details', *), 'section description', *))" % (current_department)) ))
		section_select.sort()	
		
		item_code = []				
		material_type = list(set(p.query("names(objects(subjects(*, 'is a', 'item master'), 'material type', *))")))
		material_type.sort()
		#grid_data = self.irv_item( **{'current_department':current_department} )
		return CheetahRender(data={'irv_data':{}, 'view_mode':'false', 'section_select':section_select, \
		'irv_no':'', 'material_type':material_type, 'item_code':item_code, \
		'current_department_code':current_department_code, 'current_department':current_department, \
		'department_select':department_select}, template = os.path.join(self.path, "create_irv"))
	
	#Saving irv 
	@iris.expose
	def save_irv(self,  **kwargs):
		'''
		Saving the irv data
		parameter: kwargs['current_department']
		'''
		p = iris.findObject('poseidon')
		#current_department = kwargs['current_department']
		
		kwargs['irv_no'] = self.max_irv_no()
		kwargs['irv_status'] = 'pending' #this is comfirm by stores
		kwargs['is a'] = 'irv'
		kwargs['post_status'] = 'unposted'
		#pprint.pprint(kwargs)
		#grid_data = self.irv_item(**{'current_department':current_department})
		p.addObject(kwargs, save=False)
		p.save()
		iris.message("IRV No %s  has been created successfully" % (kwargs['irv_no']))
		return self.create_irv(**kwargs)
	
	#Finding the max number
	@iris.expose
	def max_irv_no(self, **kwargs):
		'''
		This is return max and unique ppo_no format is HRPL/PPO/yy/00000
		'''	
		p = iris.findObject('poseidon')
		#req_data = p.query("names(objects(subjects(*, 'is a', 'irv'), 'irv_no', %s*))"%(kwargs['format']))
		if date.today().month < 4:
			year_form = str(date.today().year - 1)[2:]
			search_date = str(date.today().year - 1) + "-04-01"
		else:
			year_form = str(date.today().year)[2:]
			search_date = str(date.today().year) + "-04-01"
		today = time.strftime("%Y-%m-%d")

		irv_data = p.query("names(objects(subjects(subjects(*, 'is a', 'irv'), \
			irv_date, %s:%s), irv_no, *))" % (search_date, today) ) 
			
		max_irv = 1 + len(irv_data)
		irv_formate = "IRV/"+ year_form +"/"+  str(max_irv)
		Found_data = p.query("ids(subjects(subjects(*, 'is a', 'irv'), irv_no, '%s'))" %(irv_formate))
		i = 1
		while len(Found_data) != 0 :
			irv_formate = "IRV/"+ year_form +"/"+  str(max_irv)
			Found_data = p.query("ids(subjects(subjects(*, 'is a', 'irv'), irv_no, '%s'))" %(irv_formate))
			i = i + 1
		return irv_formate

	
	#Editing  irv using uuid
	@iris.expose
	#@hartex_users.hartex_access_validate(module='storemanager',allow='storemanager_irv_edit')
	def edit_irv(self, **kwargs):
		'''
		Description :For Editing  irv. Taking uuid
		Parameter:kwargs['uuid_checked']
		Return : data
		
		'''
		p = iris.findObject('poseidon')
		uuid = kwargs['uuid_checked']
		irv_data = update_scaler.make_scaler(bwQuery(uuid).val()[0])
		irv_data['irv_uuid'] = uuid
		current_department = kwargs['current_department']
		if current_department == "Stores":
			hartex_users.hartex_access_validate2(module='storemanager',allow='storemanager_irv_edit')
		if current_department == "Purchase":
			hartex_users.hartex_access_validate2(module='purchasemanager',allow='purchasemanager_irv_edit')
		if current_department == "accounts":
			hartex_users.hartex_access_validate2(module='accounts',allow='accounts_irv_edit')
		try:
			current_department_code = p.query("names(objects(subjects(subjects(*, 'is a', 'department master'), 'department name', \
				'%s'), 'department code', *))" % (current_department))[0]
		except:
			current_department_code = ""

		#department_code = [current_department_code]
		department_select = [irv_data.get('department_select')]
		section_select = list(set( p.query("names(objects(objects(subjects(subjects(*, 'is a', 'department master'), \
		'department name', '%s'), 'section details', *), 'section description', *))" % (current_department)) ))
		section_select.sort()
		material_type = list(set(p.query("names(objects(subjects(*, 'is a', 'item master'), 'material type', *))")))
		material_type.sort()
		item_code = list(set( p.query("names(objects(subjects(subjects(*, 'is a', 'item master'), 'material type', '%s'), 'item code', *))" % (str(irv_data['material_type']))) ))
		# irv data 
		
		pprint.pprint(irv_data)
		print "edit mode"
		irv_no	= irv_data['irv_no']
		irv_data['confirm_mode'] = kwargs.get('confirm_mode', '')
		return CheetahRender(data={'irv_data':irv_data, 'view_mode':kwargs.get('view_mode', 'true'), \
		'section_select':section_select,  'irv_no':irv_no, 'material_type':material_type, \
		'item_code':item_code, 'current_department_code':current_department_code, \
		'current_department':current_department,'department_select':department_select,}, template = os.path.join(self.path, "create_irv"))
	
		
		
	
	#Updating the irv data
	@iris.expose
	def update_irv(self, **kwargs):
		'''
		This will take the irv_uuid, and data, as kwargs
		'''
		p = iris.findObject("poseidon")
		print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
		pprint.pprint(kwargs)
		irv_uuid = kwargs['irv_uuid']
		view_mode = kwargs['view_mode']
		del kwargs['view_mode']
		del kwargs['irv_uuid']
		if kwargs.has_key('confirm_mode'):
			'''This code will run only in confirm mode by stores department.
			Also here i have to update the item master. Only if create_rc is 'no'
			'''
			confirm_mode = kwargs['confirm_mode']
			kwargs['irv_status'] = 'confirm'
			del kwargs['confirm_mode']
			if kwargs['current_department'] == 'Purchase':
				kwargs['create_rc'] = kwargs['c_rc_v']
				kwargs['create_wo'] = kwargs['c_wo']
				kwargs['irv_status'] = 'purchase confirm'
				del kwargs['c_rc_v']
				del kwargs['c_wo']
				
				
			prev_irv_data = update_scaler.make_scaler(bwQuery(irv_uuid).val()[0])
			print "my kwargsMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM", kwargs
			p.setObject(irv_uuid, kwargs, save=False)
			#print
			#print 
			#print "irv_uuid:::::::::::::::::::::::::::::::::::::::::::::::::::", irv_uuid
			#if kwargs['create_rc'] == 'no':
			item_data = p.query("select(subjects(subjects(*, 'is a', 'item master'), 'item code', '%s'))" %(kwargs['item_code']) )
			item_rec_qty = item_data[0]['_value']['total year to month receipt quantity'][0]
			grand_total_stock = item_data[0]['_value']['grand total stock'][0]
			try:
				grand_total_stock  = int(grand_total_stock) - int(item_rec_qty)
				item_rec_qty = int(item_rec_qty) + int(kwargs['irv_qty']) - int(prev_irv_data['irv_qty'])
				grand_total_stock  = int(grand_total_stock) + int(item_rec_qty)
				total_qty_data = {'grand total stock':str(grand_total_stock), 'total year to month receipt quantity':str(item_rec_qty)}
				p.setObject(item_data[0]['_id'], total_qty_data, save=False)

			except:
				#This except condition will not run in normal case...
				#grand_total_stock  = int(grand_total_stock) - int(item_rec_qty)
				#qty = int(kwargs['irv_qty']) - int(prev_irv_data['irv_qty'])
				#grand_total_stock  = int(grand_total_stock) + int(item_rec_qty)
				total_qty_data = {'grand total stock':str(kwargs['irv_qty']), 'total year to month receipt quantity':str(kwargs['irv_qty'])}
				p.setObject(item_data[0]['_id'], total_qty_data, save=False)
			#end if
			p.save()			
		else:
			confirm_mode = ''
			kwargs['irv_date'] = time.strftime("%Y-%m-%d")
			p.setObject(irv_uuid, kwargs, save=False)
			p.save()
		#print "1111"
		if confirm_mode == '' :
			iris.message("IRV No %s  has been updated successfully" % (kwargs['irv_no']))
		else:
			iris.message("IRV No %s  has been confirm successfully" % (kwargs['irv_no']))
		
		#print "2222"
		#passing the data in edit mode
		kwargs['uuid_checked'] = irv_uuid
		kwargs['view_mode'] = view_mode
		kwargs['confirm_mode'] = confirm_mode
		return self.edit_irv(**kwargs)
	
	@iris.expose
	#@hartex_users.hartex_access_validate(module='storemanager',allow='storemanager_irv_post')
	def post_irv(self, **kwargs):
		'''
		This is posting the new 'irv'. 'post_status' is 'posted'
		This is taking  id as list or unicode.Example-
		{'ids': u'!132b7014b143bbab56458b8df1d7e28d'}
		{'ids': [u'!f06df0b0e6623782ccd1850a88775aea',u'!132b7014b143bbab56458b8df1d7e28d']}
		return :----purchase_details()
		'''
		current_department = kwargs['current_department']
		if current_department == "Stores":
			hartex_users.hartex_access_validate2(module='storemanager',allow='storemanager_irv_post')
		if current_department == "Purchase":
			hartex_users.hartex_access_validate2(module='purchasemanager',allow='purchasemanager_irv_post')
		if current_department == "accounts":
			hartex_users.hartex_access_validate2(module='accounts',allow='accounts_irv_post')
		if isinstance(kwargs['ids'], list): 
			for uuid in kwargs.get('ids'):
				bwQuery(uuid).attr('post_status', 'posted').save()			
		else: # ids is list type
			bwQuery(kwargs.get('ids')).attr('post_status', 'posted').save()			
		#return self.irv_grid()
		return self.irv_details(**{"department":kwargs['current_department']})

	# For searching the data based on given data
	@iris.expose
	@hermes.service()
	def find_irv_uuid(self, **kwargs):
		'''
			Description : Searching the irv data. Based on given keywords 
			parameter : kwargs
			Return : grid
		'''
		p = iris.findObject('poseidon')
		print
		print kwargs
		print
		temp_query = "subjects(*, 'is a', 'irv')"
		if kwargs.get('irv_pending_confirm') == 'pending' or kwargs.get('irv_pending_confirm') == 'confirm':
			r = "subjects(subjects(*, 'post_status', 'posted'), 'irv_status', '%s')" % (kwargs['irv_pending_confirm'])
			temp_query = replace(temp_query, "*", r)
			if kwargs.get('department'): # searching the data based on department
				r = "subjects(*, 'department_select', '%s')" % (kwargs['department'])
				temp_query = replace(temp_query, "*", r)
		else:
			if kwargs.get('posted_or_unposted'):  # searching the data based on post_status
				if kwargs.get('current_department') == 'Purchase':
					r = "subjects(*, 'irv_status', '%s')" % (kwargs['posted_or_unposted'])
				else:
					r = "subjects(*, 'post_status', '%s')" % (kwargs['posted_or_unposted'])
				temp_query = replace(temp_query, "*", r)
			if kwargs.get('current_department'): # searching the data based on department
				r = "subjects(*, 'department_select', '%s')" % (kwargs['current_department'])
				temp_query = replace(temp_query, "*", r)
			
		if kwargs.get('irv_no'):
			r = "subjects(*, 'irv_no', '%s')" % (kwargs['irv_no'])
			temp_query = replace(temp_query, "*", r)
		else:
			if kwargs.get('from') or kwargs.get('to'): # searching the data based date
				if kwargs.get('from') and kwargs.get('to'):
					r = "subjects(*, irv_date, %s:%s)" % (kwargs['from'], kwargs['to'])
					temp_query = replace(temp_query, "*", r)	
				elif kwargs.get('from'):
					r = "subjects(*, irv_date, %s:2999-00-00)" % (kwargs['from'])
					temp_query = replace(temp_query, "*", r)			
				elif kwargs.get('to'):
					if date.today().month < 4:
						default_date  = str(date.today().year - 1) + "-04-01" #Last
					else:
						default_date  = str(date.today().year) + "-04-01" #Last
					r = "subjects(*, irv_date or irv_date, %s:%s)" % (default_date, kwargs['to'])
					temp_query = replace(temp_query, "*", r)				
			if kwargs.get('item_name'): # searching the data based on item_name
				r = "subjects(*, 'item_name', '%s')" % (kwargs['item_name'])
				temp_query = replace(temp_query, "*", r)
		# End  SEARCH query
		temp_query = "ids(" + temp_query + ")"
		
		try:
			data_uuid = p.query(temp_query)
		except:
			data_uuid = []
		search_irv_uuid = {}
		for uid in data_uuid:
			temp = update_scaler.make_scaler(bwQuery(uid).val()[0])	
			search_irv_uuid[temp.get('irv_no')] = "%s" %bwQuery(uid).ids()[0]
		#print "irv idIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", search_irv_uuid
		return {'search_irv_uuid':search_irv_uuid}
	
	@iris.expose
	def show_irv_grid(self, **kwargs):	
		'''
		Showing the grid option based on search result.
		'''
		#p = iris.findObject('poseidon')
		search_uuid = json.loads(kwargs.get('search_irv_uuid', '{}'))	
		irv_temp_data = []
		#temp_irv = p.query("ids(subjects(subjects(*, 'is a', 'irv'), 'post_status', 'unposted'))")
		for uid in search_uuid.values():
			#uid=p.query("ids(subjects(subjects(subjects(*, 'is a','vendor_master'),'revision_no','%s'),'vendor_registration_no','%s'))"%(revision_no,vendor_registration_no))
			temp = update_scaler.make_scaler(bwQuery(uid).val()[0])	
			#=if kwargs.get('post_status') == 'unposted':
			temp['check'] = "<input type='checkbox' name='uuid' id='uuid' style='margin-top:0.4em' value='%s'></input>" % bwQuery(uid).ids()[0]
			irv_temp_data = irv_temp_data + [temp]
		data_header = [{'name':'check', 'display':'Check'}, {'name':'irv_no', 'display':'IRV No'},
		{'name':'irv_date', 'display':'IRV Date'}, {'name':'material_type', 'display':'material type'},
		{'name':'item_name', 'display':'Item name'}, {'name':'department_select', 'display':'department'},
		{'name':'cost_select', 'display':'cost center'}, {'name':'irv_status', 'display':'Status'}]
		
		grid_id = iris.root.set_control_data(irv_temp_data)
		return CheetahRender(data={'data_header':data_header, 'grid_id':grid_id}, template = os.path.join(self.path, "grid.tmpl"))

	@iris.expose
	def next_prev_irv(self, **kwargs):
		'''
		Showing the next irv_no based. else first one
		'''
		#p = iris.findObject('poseidon')
		
		search_uuid = json.loads(kwargs.get('search_irv_uuid', '{}'))

		total_icode = search_uuid.keys()
		total_icode.sort()
		pos = total_icode.index(kwargs['irv_no']) # position of the given item
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
				next_item = total_icode.index(kwargs['irv_no']) + 1
				show_icode = total_icode[next_item]
		
		#This 2 line is prev one-- search_item_uuid - {'ptype_code':"uuid of that code"}
		#uuid = p.query("ids(subjects(subjects(*, 'is a', 'item master'), 'item code', '%s'))" % (show_icode))
		#kwargs['id'] = uuid[0]
		
		kwargs['uuid_checked'] = search_uuid[show_icode]
	
		# if kwargs.get('tmpl') == "revise_item_master":
			# return  self.revise_item_master(**kwargs)
		return  self.edit_irv( **kwargs)
		

	#Get cost_or_section_code
	@iris.expose
	@hermes.service()		
	def cost_equipment_section_code(self, **kwargs):
		'''
		Showing the cost_code or section_code from edp
		'''
		p = iris.findObject('poseidon')
		if kwargs.get('find_code') == 'cost_centre_code':
			# data = list(set( p.query("names(objects(subjects(objects(subjects(subjects(*, 'is a', 'department master'), \
			# 'department name', '%s'), 'cost centre details', *), 'cost centre description', '%s'), \
			# 'cost centre code', *))" % (kwargs['current_department'], kwargs['value'])) ))
			data = list(set( p.query("names(objects(subjects(subjects(*, 'is a', 'cost_centre'), 'cost_centre_description', '%s'), 'cost_centre_code', *))"  % (kwargs['value']) ) ))
		elif kwargs.get('find_code') == 'equipment':
			data = list(set(p.query("names(objects(subjects(subjects(*, 'is a', 'equipment master'), 'equipment name', '%s'), 'equipment code', *))" % ( kwargs['value']))))
		else:
			data = list(set( p.query("names(objects(subjects(objects(subjects(subjects(*, 'is a', 'department master'), \
			'department name', '%s'),'section details', *), 'section description', '%s'), \
			'section code',*))" % (kwargs['current_department'], kwargs['value'])) ))
		# if len(data) == 0:
			# data = []
		return data
	
	
	# getting department data
	@iris.expose
	@hermes.service()
	def department_data(self, **kwargs):
		'''
		Description:This will take department name and returning the releted data as a list 
		Parameter:kwargs['department_name']
		Return :{}
		'''
		p = iris.findObject('poseidon')
		data = {}
		department_name  = kwargs['department_name']
		data['current_department_code'] = list(set( p.query("names(objects(subjects(subjects(*, 'is a', \
				'department master'), 'department name', '%s'), 'department code', *))" % (department_name)) ))[0]
		return data
	
	#Get details from Item Master
	@iris.expose
	@hermes.service()		
	def get_item_data(self, **kwargs):
		"""
		This function returns 'item code' from 'Item Master' for a given 'item description'.
		"""

		p = iris.findObject("poseidon")
		#Getting Item details for a given Item Description from Item Master
		data = {}
			
		if 'item description' in kwargs.keys():
			item_key = 'item description'
			item_value = kwargs['item description']
			data['item_name'] = kwargs['item description']
			data['item_code'] = list(set( p.query("names(objects(subjects(subjects(*, 'is a', 'item master'), '%s', '%s'), 'item code', *))" % (str(item_key), str(item_value))) ))
			data['item_uom'] = list(set( p.query("names(objects(subjects(subjects(*, 'is a', 'item master'), '%s', '%s'), 'item uom', *))" % (str(item_key), str(item_value))) ))
			data['material_type'] = list(set( p.query("names(objects(subjects(subjects(*, 'is a', 'item master'), '%s', '%s'), 'material type', *))" % (str(item_key), str(item_value))) ))
			if len(data) > 0:
				return data
			else:
				return {}
		elif 'item code' in kwargs.keys():
			item_key = 'item code'
			item_value = kwargs['item code']
			data['item_code'] = kwargs['item code']
			data['item_name'] = list(set( p.query("names(objects(subjects(subjects(*, 'is a', 'item master'), '%s', '%s'), 'item description', *))" % (str(item_key), str(item_value))) ))
			data['item_uom'] = list(set( p.query("names(objects(subjects(subjects(*, 'is a', 'item master'), '%s', '%s'), 'item uom', *))" % (str(item_key), str(item_value))) ))
			data['material_type'] = list(set( p.query("names(objects(subjects(subjects(*, 'is a', 'item master'), '%s', '%s'), 'material type', *))" % (str(item_key), str(item_value))) ))
			
			if len(data) > 0:
				return data
			else:
				return {}
		elif 'material type' in kwargs.keys():
			item_key = 'material type'
			item_value = kwargs['material type']
			data = list(set( p.query("names(objects(subjects(subjects(*, 'is a', 'item master'), '%s', '%s'), 'item code', *))" % (str(item_key), str(item_value))) ))
			return data
		find = kwargs['find']
		if len(item_value)>0:
			#data = p.query("names(objects(subjects(subjects(*, 'is a', 'item master'),'%s','%s'),'%s', *))"%(str(item_key),str(item_value),str(find)))
			#data['item_code'] = p.query("names(objects(subjects(subjects(*, 'is a', 'item master'),'%s','%s'),'item code', *))"%(str(item_key),str(item_value)))
			#data['item code'] = p.query("names(objects(subjects(*, 'is a', 'item master'),'%s', *))"%str(find))
			
			data['item_uom'] = list(set( p.query("names(objects(subjects(subjects(*, 'is a', 'item master'), '%s', '%s'), 'item uom', *))" % (str(item_key), str(item_value))) ))
			data['item_code'] = list(set( p.query("names(objects(subjects(*, 'is a', 'item master'),'%s', *))" % str(find)) ))
			if len(data)>0:
				return data
			else:
				data['item_code'] = list(set( p.query("names(objects(subjects(*, 'is a', 'item master'),'%s', *))" % str(find)) ))
				data['item_uom'] = list(set( p.query("names(objects(subjects(*, 'is a', 'item master'), '%s', *))" % str(find)) ))
				data = list(set( p.query("names(objects(subjects(*, 'is a', 'item master'), '%s', *))" % str(find)) ))
				if len(data)>0:
					data.sort()
					return data
				else:
					data = {}
					return data		
		else:
			data = {}
			data['item_code'] = ""
			data['item_name'] = ""
			data['item_uom'] = ""
			return data
	
	@iris.expose
	def find(self, **kwargs):
		
		p = iris.findObject("poseidon")
		if len(kwargs) == 0:
			return []
		else:
			if len(kwargs['q'])>2:
				if "is a" in kwargs.keys():
					query = "subjects(*, 'is a', '%s')" % str(kwargs['is a'])
					del kwargs['is a']
				else:
					query = '*'
				
				for x in kwargs:
					if x != 'keyname' and x != 'q':
						query = "subjects(%s, %r, %s)" % (query, str(x), repr(str(kwargs[x])))
			
				query = "names(objects(%s, %s, %s*))" % (query, repr(str(kwargs['keyname'])), str(kwargs['q']).lower())
			
				data = sorted( p.query(query))
			
				if len(data)>0:
					data = sorted( list(set( p.query(query) )) )
					return '\n'.join(data)
				else:
					return ""	
			else:
				return []
	
	@iris.expose
	@hartex_users.hartex_access_validate(module='storemanager',allow='storemanager_confirm_irv_confirm')
	def confirm_irv_details(self, **kwargs):
		'''
		This page will display the data for confirming the data. This data is confimed by only stores
		'''
		data_header = [{'name':'check', 'display':'Check'}, {'name':'irv_no', 'display':'IRV No'},
		{'name':'irv_date', 'display':'IRV Date'}, {'name':'material_type', 'display':'material type'},
		{'name':'item_name', 'display':'Item name'}, {'name':'department_select', 'display':'department'},
		{'name':'cost_select', 'display':'cost center'}, {'name':'irv_status', 'display':'Status'}]
		grid_id = iris.root.set_control_data([])
		#grid_id = grid_data[1]
		#irv_data = {}
		current_department = "Stores"
		return CheetahRender(data={'current_department':current_department,  'data_header':data_header, 'grid_id':grid_id}, template = os.path.join(self.path, "confirm_irv_details.tmpl"))
	
	@iris.expose
	def import_irv(self, **kwargs):
		'''
		'''
		p = iris.findObject("poseidon")

		irv_hdr = p.query("select_one(subjects(*, 'is a', 'irvhdr'))")
		for irv in irv_hdr:
			i = 0
			irvhdr = irv['_value']
			irv_data = {u'cost_code': '',
			'cost_select': '',
			'create_rc':'no',
			'current_department': '',
			'department_code': '',
			'department_select': '',
			'irv_date': '',
			'irv_make': '',
			'irv_no': '',
			'irv_qty': '',
			'irv_specifications': '',
			'irv_status': 'pending',
			'is a': 'irv',
			'item_code': '',
			'item_name': '',
			'item_uom': '',
			'material_type': '',
			'post_status': 'posted',
			'remarks': 'This is imported data',
			'return_class': '',
			'section_code': '',
			'section_select': '',
			}
			irv_data['imported_irv'] = 'true'
			irv_data['irv_no'] = irvhdr['IRHRETUR']
			irv_data['irv_date'] = str(irvhdr['IRHRETURN'][0]).replace('/', '-')
			irv_data['cost_code'] = irvhdr['IRHC']
			irv_data['cost_select'] = p.query("names(objects(subjects(subjects(*, 'is a', 'cost_centre'), 'cost_centre_code', '%s'), 'cost_centre_description', *))" %(str(irvhdr['IRHC'][0])))[0]
			irv_data['IRHD'] = irvhdr['IRHD']
			irv_data['created_by'] = irvhdr['IRHCRT']
			irv_dtl = p.query("select(subjects(subjects(*, 'is a', 'irvdtl'), 'IRDRETUR', '%s'))" %(str(irvhdr['IRHRETUR'][0])) )
			print len(irv_dtl)
			#print "select(subjects(subjects(*, 'is a', 'irvdtl'), 'irv', '%s'))" %(str(irvhdr['IRHRETUR'][0])) 
			for irv_items in irv_dtl:
				irv_items = irv_items['_value']
				irv_data['item_code'] = irv_items['IRDITE']
				#print irv_items['IRDITE']
				item_data = p.query("select(subjects(subjects(*, 'is a', 'item master'), 'item code', '%s'))" %(str(irv_items['IRDITE'][0])) )
				item_data = item_data[0]['_value']
				irv_data['item_code'] = item_data['item description'][0]
				irv_data['item_uom'] = item_data['item uom'][0]
				irv_data['material_type'] = item_data['material type'][0]
				i = i + 1
				p.addObject(irv_data, save=False)
			#print i	
		p.commit()
		bwQuery.select(where={'is a':'irvhdr'}).remove()
		bwQuery.select(where={'is a':'irvdtl'}).remove()
		return "Irv is done"

	#Dispalying the irv data into the grid in purchase
	@iris.expose
	def irv_details_confirm(self, **kwargs):
		'''
		This is displaying data into the grid, calling from haretx/display
		'''
		p = iris.findObject('poseidon')
		#print kwargs
		current_department = kwargs['department']
		'''
		if current_department == 'Purchase' or current_department == 'Costing':  #purchase can see tha data of other department alse only in view mode
			department_select = list(set( p.query("names(objects(subjects(*, 'is a', 'department master'), 'department name', *))") )) 
		else:
			department_select = [current_department]
		department_select.sort()

		irv_type = list(set( p.query("names(objects(subjects(subjects(subjects(*, 'is a', 'other code master'), \
						'department name', 'Purchase'), 'master', 'irv type'), 'value', *))") ))
		irv_type.sort()
		'''
		#grid_data = self.irv_grid(**{'department':current_department})
		data_header = [{'name':'check', 'display':'Check'}, {'name':'irv_no', 'display':'IRV No'},
		{'name':'irv_date', 'display':'IRV Date'}, {'name':'material_type', 'display':'material type'},
		{'name':'item_name', 'display':'Item name'}, {'name':'department_select', 'display':'department'},
		{'name':'cost_select', 'display':'cost center'}, {'name':'irv_status', 'display':'Status'}]
		grid_id = iris.root.set_control_data([])
		#grid_id = grid_data[1]
		#irv_data = {}
		return CheetahRender(data={'current_department':current_department,  'data_header':data_header, 'grid_id':grid_id}, template = os.path.join(self.path, "irv_details.tmpl"))
	
	@iris.expose
	@hartex_users.hartex_access_validate(module='storemanager',allow='storemanager_confirm_irv_confirm')
	def confirm_irv_purchase(self, **kwargs):
		'''
		This page will display the data for confirming the data. This data is confimed by only stores
		'''
		data_header = [{'name':'check', 'display':'Check'}, {'name':'irv_no', 'display':'IRV No'},
		{'name':'irv_date', 'display':'IRV Date'}, {'name':'material_type', 'display':'material type'},
		{'name':'item_name', 'display':'Item name'}, {'name':'department_select', 'display':'department'},
		{'name':'cost_select', 'display':'cost center'}, {'name':'irv_status', 'display':'Status'}]
		grid_id = iris.root.set_control_data([])
		#grid_id = grid_data[1]
		#irv_data = {}
		current_department = "Purchase"
		return CheetahRender(data={'current_department':current_department,  'data_header':data_header, 'grid_id':grid_id}, template = os.path.join(self.path, "confirm_irv_details.tmpl"))	




	#Get details from Item Master
	@iris.expose
	@hermes.service()		
	def get_item_data_1(self, **kwargs):
		"""
		This function returns 'item code' from 'Item Master' for a given 'item description'.
		"""

		p = iris.findObject("poseidon")
		#Getting Item details for a given Item Description from Item Master
		data = {}
		
		print kwargs	
		
		if 'item description' in kwargs.keys():
			
			item_key = 'item description'
			item_value = kwargs['item description']
			data['item_name'] = kwargs['item description']
			item_id =  p.query("ids(subjects(subjects(*, 'is a', 'item master'), 'item description', '%s'))"%str(kwargs['item description']))
			#print "item_id:::::::::::::::::::::::::::::::::::::::", item_id
 			#print "itemid[0]***********************************************", item_id[0]
			data['item_code'] = list(set( p.query("names(objects('%s', 'item code', *))" % (item_id[0])) ))
			
			data['item_uom'] = list(set( p.query("names(objects('%s', 'item uom', *))" % (item_id[0])) ))
			
			data['material_type'] = list(set( p.query("names(objects('%s', 'material type', *))" % (item_id[0])) ))
			
			if len(data) > 0:
				print "data******:::::::::::::::::::::::::::::", data
				return data
			else:
				return {}
		elif 'item code' in kwargs.keys():
			item_key = 'item code'
			item_value = kwargs['item code']
			data['item_code'] = kwargs['item code']
			item_id =  p.query("ids(subjects(subjects(*, 'is a', 'item master'), 'item code', '%s'))"%str(kwargs['item code']))
 			
			data['item_name'] = list(set( p.query("names(objects('%s', 'item description', *))" % (item_id[0])) ))
			data['item_uom'] = list(set( p.query("names(objects('%s', 'item uom', *))" % (item_id[0])) ))
			data['material_type'] = list(set( p.query("names(objects('%s', 'material type', *))" % (item_id[0])) ))
			
			if len(data) > 0:
				return data
			else:
				return {}
		elif 'material type' in kwargs.keys():
			item_key = 'material type'
			item_value = kwargs['material type']
			item_id =  p.query("ids(subjects(subjects(*, 'is a', 'item master'), 'material type', '%s'))"%str(kwargs['material type']))
			#print "item_id:::::::::::::::::::::::::::::::::::::::", item_id
			data = list(set( p.query("names(objects('%s', 'item code', *))" % (item_id[0])) ))
			return data
		find = kwargs['find']
		
		if len(item_value)>0:
			#data = p.query("names(objects(subjects(subjects(*, 'is a', 'item master'),'%s','%s'),'%s', *))"%(str(item_key),str(item_value),str(find)))
			#data['item_code'] = p.query("names(objects(subjects(subjects(*, 'is a', 'item master'),'%s','%s'),'item code', *))"%(str(item_key),str(item_value)))
			#data['item code'] = p.query("names(objects(subjects(*, 'is a', 'item master'),'%s', *))"%str(find))

			data['item_uom'] = list(set( p.query("names(objects(subjects(subjects(*, '%s', '%s'), 'is a', 'item master'), 'item uom', *))" % (str(item_key), str(item_value))) ))
			data['item_code'] = list(set( p.query("names(objects(subjects(*, 'is a', 'item master'),'%s', *))" % str(find)) ))
			#data['po_rate'] = list(set( p.query("names(objects(subjects(subjects(*, '%s', '%s'), 'is a', 'item master'), 'last po rate', *))" % (str(item_key), str(item_value))) ))
			
			if len(data)>0:
				print "data:::::::::::::::::::::::::::::::::", data['po_rate']
				return data
			else:
				data['item_code'] = list(set( p.query("names(objects(subjects(*, 'is a', 'item master'),'%s', *))" % str(find)) ))
				data['item_uom'] = list(set( p.query("names(objects(subjects(*, 'is a', 'item master'), '%s', *))" % str(find)) ))
				
				data = list(set( p.query("names(objects('%s', '%s', *))" %(item_id[0], str(find))) ))
				if len(data)>0:
					data.sort()
					return data
				else:
					data = {}
					return data		
		else:
			data = {}
			data['item_code'] = ""
			data['item_name'] = ""
			data['item_uom'] = ""
			data['po_rate']  = ""
			return data
	
