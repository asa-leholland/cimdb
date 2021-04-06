# webapp.py
from flask import Flask, render_template, flash
from flask import request, redirect

# add json to handle db connection
from flask import json

# import these to handle user accounts
from flask import url_for, session
import flask_login
from flask_login import login_user, current_user, logout_user, login_required

# import a local python script to generate new passwords
import cim.static.py.password_generator as pw_gen

# perform a local import to load the dummy data
from cim.dummy_data import DummyData

# connect to databse
import cim.database.db_connector as db

# import basic queries that are used in multiple routes
import cim.database.db_queries as dbq

# import INSERT queries as dbiq
import cim.database.db_insert_queries as dbiq

# import UPDATE queries as dbiq
import cim.database.db_update_queries as dbuq

# import DELETE queries as dbdq
import cim.database.db_delete_queries as dbdq

# import filter (SELECT) queries as dbfq
import cim.database.db_filter_queries as dbfq

# resolve CORS issues for local development
from flask_cors import CORS, cross_origin

# for backend processes
import random

#to handel json files for return statment
from flask import jsonify

#create the web application
webapp = Flask(__name__)
CORS(webapp)

# added a 'secret' key for user management
webapp.secret_key = 'Team CS Cats'


# Set up login manager to handle basic user authentication
login_manager = flask_login.LoginManager()
login_manager.init_app(webapp)




# Load dummy data for the webpages to reference
data = DummyData()


#global_site_id for inventory_id lookup processes all CRUD processes will assign to shelf 1 of one of the rooms below:
# Room 1: Receiving Department
# Room 2: Warehouse  
# Room 3: Assembly Department
# Room 4: QC Department
# Room 5: Shipping Department
#TODO: implement site id retrived from session data
# the site id is set for Reno site
global_site_id='16'


# Set up a mock set of user ids to use for our logins (this can be moved/replaced later)
users = {}

for employee in data.get_emp():
	emp_email = employee["employee_email"]
	emp_pass = employee["employee_password"]
	users[emp_email] = {'password': emp_pass}


# Create a basic user class
class User(flask_login.UserMixin):
	pass


# Associate the login manager with the users provided, unless the user provided isn't on the allowed dictionary
@login_manager.user_loader
def user_loader(email):

	# if the email provided is not in the prepopulated user database, return nothing
	if email not in users:
		return

	# otherwise, initiate a new user based on the provided email and return it
	user = User()
	user.id = email
	return user

# Associate a logged in user with the current session
@login_manager.request_loader
def request_loader(request):

	# obtain the current email
	email = request.form.get('email')

	# if the current email isn't on the list of allowed users, return nothing
	if email not in users:
		return

	# if the user email is allowed, set it as the id of the current user
	user = User()
	user.id = email
	user.is_authenticated = request.form['password'] == users[email]['password']
	return user

# Add an association for any unauthorized session logins.
@login_manager.unauthorized_handler
def unauthorized_handler():
	return redirect(url_for('index'))




#provide a route for the index of the webpage requests on the web application can be addressed
@webapp.route('/', methods=['GET', 'POST'])
def index():
	"""The webapp's landing page."""

	# if the user attempts to login, but provides no info, refresh the page
	if request.method == 'GET':
		return render_template("index.html")

	# if the user attempts to login with info, check to see if their info is valid
	email = request.form['email']
	if request.form['password'] == users[email]['password']:

		# If valid credentials, sign the user into the Work Orders page
		user = User()
		user.id = email
		flask_login.login_user(user)
		return redirect(url_for('workorders'))

	# If the user provided bad credentials, return them to the index page (TODO: flash error)
	return render_template("index.html")


# Provide a route to redirect a logged in user to the orders page web app
@webapp.route('/login', methods=['GET', 'POST'])
def login():

	
	# if the user attempts to login, but provides no info, refresh the page
	if request.method == 'GET':
		return render_template("index.html")

	# if the user attempts to login with info, check to see if their info is valid
	email = request.form['email']

	if email not in users:
		return redirect(url_for('index'))

	if request.form['password'] == users[email]['password']:

		# If valid credentials, sign the user into the Work Orders page
		user = User()
		user.id = email

		# determine the employee ID of the user email provided
		employee_details = None
		for employee_info in data.get_emp():
			if employee_info['employee_email'] == email:
				user.employee_details = employee_info

				print('HERE', type(user.employee_details))
				break

		# if we couldn't find the details, redirect to the index
		if user.employee_details is None:
			return redirect(url_for('index'))

		# otherwise use the id to save the employee details and render the landing page
		user_first_name = user.employee_details['employee_first_name']
		user_last_name = user.employee_details['employee_last_name']
		user_email = user.employee_details['employee_email']
		user_id = user.employee_details['employee_id']
		user_site_id = user.employee_details['employee_site_id']
		user_group = user.employee_details['employee_group'].capitalize()
		flask_login.login_user(user)

		# Commented out since we have not implemented sessions
		# session['user_first_name'] = user_first_name
		# return redirect(url_for('landing', 
		# 	user_first_name=user_first_name, 
		# 	user_last_name=user_last_name, 
		# 	user_email=user_email, 
		# 	user_id=user_id, 
		# 	user_site_id=user_site_id,
		# 	user_group=user_group
		# 	))

		# otherwise, render the landing page
		return redirect(url_for('landing'))

	# If the user provided bad credentials, return them to the index page (TODO: flash error)
	return render_template("index.html")


# Provide a route to log out the web app
@webapp.route('/logout', methods=['GET', 'POST'])
def logout():

	flask_login.logout_user()
	return redirect(url_for("index"))


@webapp.route('/workorders', methods=['GET', 'POST','PUT','DELETE'])
@login_required
def workorders():
	"""The webapp's page for work orders, which allows reviewing and adding work orders."""

	# if the current user is not authenticated, redirect the user to the logged out index page
	if not current_user.is_authenticated:
		error = 'You are not logged in. Please log in to view this page.'
		return redirect(url_for("cim.templates.index", error))

	# otherwise, prcocess the request
	if request.method=="GET":

		# get information from DB
		workorder_results=dbq.get_db_work_orders()
		employee_results=dbq.get_db_employees()
			
		# get work orders status
		workorder_status=data.get_wo_status()
		
		return render_template("workorders.html",
								employees=employee_results ,
								workorders=workorder_results,
								workorder_status=workorder_status
								)

	if request.method=="POST":
		
		#if filter request
		if request.json["req"]=="filter":
			filter_key=request.json["filter_key"]
			filter_value=request.json["filter_value"]

			print(f'Post request for filter: key is: {filter_key} and value is:{filter_value}')

			# Get filtered information from DB
			workorder_results=dbfq.filter_work_order(filter_key,filter_value)

			# Get information from DB
			employee_results=dbq.get_db_employees()
			
			# get work orders status
			workorder_status=data.get_wo_status()
			
			# return jsonify(workorder_results)
			return render_template("workorders.html",
									employees=employee_results ,
									workorders=workorder_results,
									workorder_status=workorder_status
									)


		id=request.json["id"]
		date=request.json["date"]
		reference=request.json["reference"]
		dbiq.insert_work_order(date,None,"assembly_pending",int(reference),id)
		print(f'post request: id is: {id} and date is: {date} and reference is{reference}')
		return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

	if request.method=='PUT':

		# extract information form request body
		wo_id=request.json["wo_id"]
		wo_open_date=request.json["wo_open_date"]
		wo_close_date=request.json["wo_close_date"]
		wo_status=request.json["wo_status"]
		wo_reference_number=request.json["wo_reference_number"]
		wo_employee_name=request.json["wo_employee_name"]

		# retrive employee ID using it's name:

		employee_first_name,employee_last_name=wo_employee_name.split()
		wo_employee_id=dbq.get_db_get_employee_id(employee_first_name,employee_last_name)['employee_id']
		# print(f'first is {employee_first_name} and lst is {employee_last_name} and id is {wo_employee_id}')

		# add quotations to dates and status
		# TODO a more smart way
		wo_open_date="'"+wo_open_date+"'"

		if wo_close_date=="":
			wo_close_date= "NULL"
		else:
			wo_close_date="'"+wo_close_date+"'"

		wo_status = "'"+wo_status+"'"


		# update DB

		dbuq.update_work_order(wo_id,wo_open_date,wo_close_date,wo_status,wo_reference_number,wo_employee_id)

		# return response
		# TODO error respose

		print(f'got a PUT request! id is: {wo_id} and wo_employee_name is {wo_employee_name}')
		return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
	
	if request.method=='DELETE':
		# extract information form request body
		wo_id=request.json["wo_id"]

		# retrive products SN
		product_results=dbq.get_db_products_in_a_workorder(wo_id)
		products_in_wo=[]
		for product in product_results:
			products_in_wo.append(product["wop_product_sn"])
		

		# get product components
		
		regular_components=[]
		for sn in products_in_wo:
			regular_components.append(dbq.get_db_product_components(sn))

				
		# retrive SC SN
		sc_sn=[]

		for sn in products_in_wo:
			sc_sn.append(dbq.get_db_product_details(sn)['product_sc_sn'])

		

		# retrive the total number of RC
		regular_products_to_restore={}
		
		for components in regular_components: #for each product in WO
			for component in components:	# for each component in product
				# if products does not exists in the dictionary add it with it's quantity
				if component['prc_rc_pn'] not in regular_products_to_restore.keys():
					regular_products_to_restore[component['prc_rc_pn']]=component['prc_quantity_needed']
				
				# otherwise add the quantity to curretn quantitiy
				else:
					regular_products_to_restore[component['prc_rc_pn']]=regular_products_to_restore[component['prc_rc_pn']]+component['prc_quantity_needed']
		
		# NO GC should be removed as its not a real RC
		regular_products_to_restore.pop('200', None)

				
		# update DB
		#  All free SC and RC will be added to the warehouse room 2 shelf 1 of the site location 
		#  for now the location is: RENO ID 57
		#TODO : retrive site id from session data 
		# get location id
		location_id=str(dbq.get_location_id(global_site_id,'2','1'))

		# remove all products
		# as product_sn is a FK in 2 tables, first it has to be deleted from those tables
		# the product itself can be deleted

		# remove wo (and its products) from WorkorderProducts
		dbdq.delete_work_order_products_by_wo_id(wo_id)

		# remove product from ProductsRegularComps and Products 
		for sn in products_in_wo:
			dbdq.delete_products_regular_comps(str(sn))
			dbdq.delete_product(str(sn))
		
		
		# set SC to free and update location
		
		for sn in sc_sn:
			dbuq.set_sc_free(sn)
			dbuq.set_sc_location(str(sn),location_id) 

		# add RC to inventory -- get current quant and update it

		for rc_pn,quantity in regular_products_to_restore.items():
			current_quantity=dbq.get_rc_quantity_in_a_location(str(rc_pn),location_id)
			
			if current_quantity==-1: # does not exists should be added a new entry
				dbiq.ali_insert_location_regular_comps(str(rc_pn),location_id,str(quantity))
			
			else: # exists should be updated
				new_quant=current_quantity+quantity
				dbuq.set_rc_quantity_in_a_location(str(rc_pn),location_id,str(new_quant))
		

		# Remove workorder
		dbdq.delete_work_order(wo_id)

		# return response
		# TODO error respose

		print(f'got a Delete request! id is: {wo_id}')
		return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 


@webapp.route('/landing', methods=['GET', 'POST'])
@login_required
def landing():
	"""The webapp's logged in landing page, which allows an employee to access the internal links."""

	# otherwise, return the landing page and pass it the employee ID which can be used as a key
	if request.method=="GET":

		# determine the number of work orders currently assigned to the current employee
		wo_count = 0
		for work_order in data.get_wo():
			if work_order['wo_employee_id'] == request.args.get('user_id'):
				wo_count += 1


		return render_template("landing.html", 
			user_first_name=request.args.get('user_first_name'),
			user_last_name=request.args.get('user_last_name'),
			user_email=request.args.get('user_email'),
			user_id=request.args.get('user_id'),
			user_site_id=request.args.get('user_site_id'),
			user_group=request.args.get('user_group'),
			sites = data.get_sites(),
			work_order_count = wo_count
			)

@webapp.route('/products', methods=['GET', 'POST'])
@login_required
def products():
	"""The webapp's page for viewing an employee's currently assigned products to assemble and QC."""

	# if the current user is not authenticated, redirect the user to the logged out index page
	if not current_user.is_authenticated:
		return redirect(url_for("cim.templates.index"))

	if request.method=="GET":
		return render_template("products.html")


@webapp.route('/inventory-spec', methods=['GET', 'POST'])
@login_required
def inventory_special_components():
	"""The webapp's page for viewing the inventory.
	This allows the employee to review existing stock and order new stock of standard and special components."""

	# if the current user is not authenticated, redirect the user to the logged out index page
	if not current_user.is_authenticated:
		return redirect(url_for("cim.templates.index"))

	if request.method=="GET":
		return render_template("inventory_special_comps.html", 
			special_components=dbq.get_db_special_components(), 
			sites=dbq.get_db_sites(),
			special_components_catalog=data.get_sp_catalog(),
			locations=dbq.get_db_locations()
			)

	# handle POST requests from Order New and Edit
	if request.method=="POST":

		# Handle Order New Special Component (INSERT)
		if "btnAddSpecComp" in request.form:

			provided_new_sc_pn = request.form['new_spec_comp_part_number']
			provided_new_sc_site = int(request.form['new_spec_comp_site'])
			provided_new_sc_quantity = int(request.form['new_spec_comp_quantity'])

			# perform the insertion
			for insertion in range(provided_new_sc_quantity):
				dbiq.insert_special_component(
					new_sc_pn=provided_new_sc_pn, 
					new_sc_location_id=provided_new_sc_site)
			
			return render_template("inventory_special_comps.html", 
				special_components=dbq.get_db_special_components(), 
				sites=dbq.get_db_sites(),
				special_components_catalog=data.get_sp_catalog(),
				locations=dbq.get_db_locations()
				)

		# Handle Edit Existing Special Component (UPDATE)
		if "btnSpecCompUpdate" in request.form:

			# obtain data from new special component form
			updated_spec_comp_part_number = request.form['spec-comp-edit-part-number']
			updated_spec_comp_location = int(request.form['spec-comp-edit-location'])

			# for the 'Is Free' checkbox, we first assume it is False (not checked). Then, if it is found to be checked, we update.
			updated_spec_comp_is_free = 0
			if request.form.get('spec-comp-edit-is-free'):
				updated_spec_comp_is_free = 1
			
			sc_id_to_update = request.form['spec-comp-serial-number']

			# perform the update
			dbuq.update_special_component(updated_spec_comp_part_number=updated_spec_comp_part_number, 
				updated_spec_comp_location=updated_spec_comp_location,
				updated_spec_comp_is_free=updated_spec_comp_is_free,
				sc_id_to_update=sc_id_to_update)


		# Check if the user submitted a form to filter existing special components
		if "btnFilterSpecComps" in request.form:

			# Obtain data from the filter existing special components form			
			provided_filter_spec_comps_paramaters = request.form.get('filterSpecCompsSearch')

			# Perform the filter
			filtered_spec_comps_results = dbfq.filter_special_components(filter_spec_comps_parameter=provided_filter_spec_comps_paramaters)

			# render the page using the filtered results
			return render_template("inventory_special_comps.html", 
				special_components=filtered_spec_comps_results, 
				sites=dbq.get_db_sites(),
				special_components_catalog=data.get_sp_catalog(),
				locations=dbq.get_db_locations()
				)



		# Check if the user submitted a form to clear all filters of existing special components
		if "btnClearFilterSpecComps" in request.form:

			# Refresh the selection query before reloading the page
			employee_results = dbq.get_db_employees()

		# Handle Delete Existing Special Component (DELETE)
		if "btnSpecCompDelete" in request.form:

			# obtain data from new special component form
			sc_id_to_delete = request.form['spec-comp-delete-serial-number']

			# perform the update
			dbdq.delete_special_component(spec_comp_sn_to_delete=sc_id_to_delete)



		# regardless, refresh the page with any changes to the data
		return render_template("inventory_special_comps.html", 
			special_components=dbq.get_db_special_components(), 
			sites=dbq.get_db_sites(),
			special_components_catalog=data.get_sp_catalog(),
			locations=dbq.get_db_locations()
			)

@webapp.route('/inventory-reg', methods=['GET', 'POST'])
@login_required
def inventory_regular_components():
	"""The webapp's page for viewing the inventory.
	This allows the employee to review existing stock and order new stock of standard and special components."""

	# if the current user is not authenticated, redirect the user to the logged out index page
	if not current_user.is_authenticated:
		return redirect(url_for("cim.templates.index"))

	# Load location results from the database (or the dummy data if the database doesn't work)
	regular_component_results = dbq.get_db_regular_components()

	# regular comps by location 
	reg_comp_location_details = dbq.get_db_regular_components_by_location()

	# Load site results from the database (or the dummy data if the database doesn't work)
	site_results = dbq.get_db_sites()

	if request.method=="GET":
		return render_template("inventory_regular_comps.html", 
			regular_components=regular_component_results, 
			reg_comp_locations=reg_comp_location_details, 
			sites=site_results)


	if request.method=="POST":

		# Handle Order New Regular Component (INSERT)
		if "btnAddRegComp" in request.form:
			
			# First, load in the reg comp details from the web page
			provided_part_description = request.form['new_reg_comp_part_description']
			provided_part_category = request.form['new_reg_comp_part_category']
			provided_site_id = int(request.form['new_reg_comp_part_site_id'])
			provided_quantity = int(request.form['new_reg_comp_part_quantity'])

			print(provided_part_description, provided_part_category, provided_site_id, provided_quantity)

			# We need to insert the new regular component using the part number description and regular component category
			dbiq.insert_regular_component(new_rc_pn_desc=provided_part_description, new_rc_category=provided_part_category)

			# This returns the newest regular component part number that has been generated (which will be the one we just inserted) 
			new_regular_component_part_number = dbq.get_newest_regular_component_part_number()

			print('new_regular_component_part_number', new_regular_component_part_number)

			# Then we need to obtain the location ID where the regular components will be placed.
			# We do this by selecting the location ID where the provided site has a receiving department (room 1)
			receiving_location_id = dbiq.get_receiving_id(site_id=provided_site_id)

			print('receiving_location_id', receiving_location_id)

			# Then insert into the LocationsRegularComps table using the location ID, reg comp ID, and quantity ordered
			dbiq.insert_location_regular_comps(
				new_regular_component_quantity=provided_quantity, 
				location_id_from_dropdown_Input=receiving_location_id, 
				regular_component_id_from_dropdown_Input=new_regular_component_part_number
				)

			

		# Handle Edit Existing Regular Component (UPDATE)
		if "btnRegCompQuantityUpdate" in request.form:

			# obtain data from new special component form
			updated_reg_comp_id = request.form['reg-comp-id-to-edit']
			updated_location_id = request.form['location-id-to-edit']
			updated_quantity = request.form['reg-comp-edit-quantity']

			print('the post is', updated_reg_comp_id, updated_location_id, updated_quantity)

			# perform the update
			dbuq.update_reg_comp_location_quantity(rc_id=updated_reg_comp_id, loc_id=updated_location_id, qty=updated_quantity)

		# # Handle Delete Existing Special Component (DELETE)
		# if "btnSpecCompDelete" in request.form:

		# 	# obtain data from new special component form
		# 	sc_id_to_delete = request.form['spec-comp-delete-serial-number']

		# 	# perform the update
		# 	dbdq.delete_special_component(spec_comp_sn_to_delete=sc_id_to_delete)



		# regardless, refresh the page with any changes to the data
		return render_template("inventory_regular_comps.html", 
			regular_components=dbq.get_db_regular_components(), 
			reg_comp_locations=dbq.get_db_regular_components_by_location(), 
			sites=dbq.get_db_sites())

@webapp.route('/shipping', methods=['GET', 'POST'])
@login_required
def shipping():
	"""The webapp's page for viewing the shipping status of work orders.
	This allows the employee to review existing work orders and see if they are ready to ship or not."""

	# if the current user is not authenticated, redirect the user to the logged out index page
	if not current_user.is_authenticated:
		return redirect(url_for("cim.templates.index"))

	# When first loaded, load in work orders and employee data from DB
	if request.method=="GET":
		return render_template("shipping.html", work_orders=dbq.get_db_work_orders(), employees=dbq.get_db_employees())

	# If a POST request is submitted, update the Status for the provided work order to Shipped
	if request.method=="POST":

		# obtain the details of the work order to update
		shipped_work_order = str(request.form['work-order-id-to-ship'])

		# Update the status of the work order to completed
		dbuq.set_workorder_status(wo_id=shipped_work_order, wo_status="'completed'")

		# reload with updated information
		return render_template("shipping.html", work_orders=dbq.get_db_work_orders(), employees=dbq.get_db_employees())

@webapp.route('/locations', methods=['GET', 'POST'])
@login_required
def locations():
	"""The webapp's page for viewing the locations at the various sites, 
	as well as which regular components, special components, and products are placed in which locations."""

	# if the current user is not authenticated, redirect the user to the logged out index page
	if not current_user.is_authenticated:
		return redirect(url_for("cim.templates.index"))

	# Load location results from the database (or the dummy data if the database doesn't work)
	location_results = dbq.get_db_locations()

	# Load site results from the database (or the dummy data if the database doesn't work)
	site_results = dbq.get_db_sites()

	if request.method=="GET":
		return render_template("locations.html", 
		locations=location_results, products=data.get_products(), regular_components=data.get_rc(), special_components=data.get_sc(), sites=site_results)

	# if post request perform insertion of new location
	if request.method=="POST":

		# First check for a new insertion
		if "addNewLocationBtn" in request.form:

			# obtain data from new location form
			provided_add_new_location_site = request.form['add_new_location_site']
			provided_add_location_room_number = request.form['add_location_room_number']
			provided_add_location_shelf_number = request.form['add_location_shelf_number']	

			# perform the insertion
			dbiq.insert_location(
				new_location_room_number=provided_add_location_room_number, 
				new_location_shelf_number=provided_add_location_shelf_number, 
				new_location_site_id=provided_add_new_location_site)


		# Then, check to handle Edit (UPDATE) an exisitng location
		if "editExistingLocationBtn" in request.form:

			# obtain data from the Edit Employee Details Modal
			provided_edit_location_site = request.form['location-site']
			provided_edit_location_room_number = request.form['room-number']
			provided_edit_location_shelf_number = request.form['shelf-number']
			provided_edit_location_site_id = request.form['location-id-to-edit']	

			# Perform the update
			dbuq.update_location(location_room_number_input=provided_edit_location_room_number, 
				location_shelf_number_input=provided_edit_location_shelf_number, 
				location_site_id_dropdown_input=provided_edit_location_site, 
				location_id_from_update_button=provided_edit_location_site_id)

		# Lastly, check if the POST was a DELETE for a location
		if "btnLocationDelete" in request.form:

			# obtain data from the Delete Location Modal
			location_id_to_delete = request.form['location-id-to-delete']

			# Perform the deletion
			dbdq.delete_location(location_id_to_delete=location_id_to_delete)

		# Update the location results since they have changed
		location_results = dbq.get_db_locations()
		
		return render_template("locations.html", 
		locations=location_results, products=data.get_products(), regular_components=data.get_rc(), special_components=data.get_sc(), sites=site_results)

@webapp.route('/employee-mgmt', methods=['GET', 'POST'])
@login_required
def employee_management():
	"""The webapp's page for managing current sites. This allows a manager to update information about current sites."""

	# if the current user is not authenticated, redirect the user to the logged out index page
	if not current_user.is_authenticated:
		return redirect(url_for("cim.templates.index"))

	# Load site results from the database (or the dummy data if the database doesn't work)
	site_results = dbq.get_db_sites()

	# Load employee results from the database (or the dummy data if the database doesn't work)
	employee_results = dbq.get_db_employees()

	if request.method=="GET":
		return render_template("employee_mgmt.html", sites=site_results, employees=employee_results)

	if request.method=="POST":

		# first, handle a POST from the Add New Employee INSERT
		if "addNewEmployeeBtn" in request.form:

			# obtain data from new site form
			provided_employee_fname = request.form['new_employee_fname']
			provided_employee_lname = request.form['new_employee_lname']
			provided_employee_email = request.form['new_employee_email']
			provided_employee_group = request.form['new_employee_group']
			provided_employee_site_id = request.form['new_employee_site']	

			# generate a password
			generated_password = pw_gen.new_password(size=8)

			# perform the insertion
			dbiq.insert_employee(new_employee_first_name=provided_employee_fname, 
				new_employee_last_name=provided_employee_lname, 
				new_employee_email=provided_employee_email, 
				new_employee_group=provided_employee_group, 
				new_employee_password=generated_password,
				new_employee_site_id=provided_employee_site_id)

		# Then, check to handle Edit exisitng employee UPDATE
		if "editExistingEmployeeBtn" in request.form:

			# obtain data from the Edit Employee Details Modal
			updated_employee_fname = request.form['edit-employee-first-name']
			updated_employee_lname = request.form['edit-employee-last-name']
			updated_employee_group = request.form['edit-employee-group']
			updated_employee_site_id = request.form['edit-employee-site']
			updated_employee_email = request.form['edit-employee-email']
			employee_id_to_update = request.form['employee-id-to-update']

			# Perform the update
			dbuq.update_employee(employee_group_input=updated_employee_group, employee_first_name_input=updated_employee_fname, 
				employee_last_name_input=updated_employee_lname, employee_email_input=updated_employee_email, 
				employee_site_id_dropdown_input=updated_employee_site_id, employee_id_from_update_button=employee_id_to_update)

		# Check if the user submitted a form to filter existing employees
		if "btnFilterEmployees" in request.form:

			# Obtain data from the filter existing sites form			
			provided_filter_employee_paramaters = request.form.get('filterEmployeeSearch')

			# Perform the filter
			filtered_employee_results = dbfq.filter_employees(filter_employees_parameter=provided_filter_employee_paramaters)

			# Reload the site results, since the original connection to the database has expired
			site_results = dbq.get_db_sites()
			return render_template("employee_mgmt.html", sites=site_results, employees=filtered_employee_results)


		# Check if the user submitted a form to clear all filters of existing employees
		if "btnClearFilterEmployees" in request.form:

			# Refresh the selection query before reloading the page
			employee_results = dbq.get_db_employees()


		# Lastly, check if the POST was a DELETE for an employee
		if "deleteExistingEmployeeBtn" in request.form:

			# obtain data from the Delete Employee Modal
			employee_id_to_delete = request.form['employee-id-to-delete']

			# Perform the deletion
			dbdq.delete_employee(employee_id_to_delete=employee_id_to_delete)


		# Reload the employee details since they have been updated
		employee_results = dbq.get_db_employees()
		site_results = dbq.get_db_sites()
		return render_template("employee_mgmt.html", sites=site_results, employees=employee_results)



@webapp.route('/site-mgmt', methods=['GET', 'POST'])
@login_required
def site_management():
	"""The webapp's page for managing current sites. This allows a manager to update information about current sites."""

	# if the current user is not authenticated, redirect the user to the logged out index page
	if not current_user.is_authenticated:
		return redirect(url_for("cim.templates.index"))

	# Load site results from the database (or the dummy data if the database doesn't work)
	site_results = dbq.get_db_sites()

	print(site_results)
	
	if request.method=="GET":
		return render_template("site_mgmt.html", sites=site_results, states=data.get_states())

	if request.method=="POST":

		# Check if the user submitted a form to add a new site
		if "addNewSiteBtn" in request.form:

			# obtain data from new site form
			provided_site_address_1 = request.form['new_site_address_1']
			provided_site_address_2 = request.form['new_site_address_2']
			provided_site_city = request.form['new_site_city']
			provided_site_state = request.form['new_site_state']
			provided_site_zip = request.form['new_site_zip']

			print('provided_site_address_2 is', provided_site_address_2)

			# perform the insertion
			dbiq.insert_site(new_site_address_1=provided_site_address_1, 
				new_site_address_2=provided_site_address_2, 
				new_site_city=provided_site_city, 
				new_site_state=provided_site_state, 
				new_site_zip=provided_site_zip)

		# Check if the user submitted a form to update an existing site
		if "btnUpdate" in request.form:

			# obtain data from new site form
			update_site_address_1 = request.form['site-edit-address-1']
			update_site_address_2 = request.form['site-edit-address-2']
			update_site_city = request.form['site-edit-city']
			update_site_state = request.form['site-edit-state']
			update_site_zip = request.form['site-edit-zip']
			site_id_to_update = request.form['site-id-to-edit']

			# perform the update
			dbuq.update_site(update_site_address_1=update_site_address_1, 
				update_site_address_2=update_site_address_2, 
				update_site_city=update_site_city, 
				update_site_state=update_site_state, 
				update_site_zip=update_site_zip,
				site_id_to_update=site_id_to_update)

		# Check if the user submitted a form to filter existing sites
		if "btnFilterSites" in request.form:

			# Obtain data from the filter existing sites form			
			provided_filter_site_paramaters = request.form.get('filterSiteSearch')

			# Perform the filter
			site_results = dbfq.filter_site(filter_site_paramater=provided_filter_site_paramaters)
			return render_template("site_mgmt.html", sites=site_results, states=data.get_states())


		# Check if the user submitted a form to clear all filters of existing sites
		if "btnClearFilterSites" in request.form:

			# Refresh the selection query before reloading the page
			site_results = dbq.get_db_sites()
		
		# Lastly, check if the POST was a DELETE for a site
		if "btnSiteDelete" in request.form:

			# obtain data from the Delete Site Modal
			site_id_to_delete = request.form['site-id-to-delete']

			# Perform the deletion
			dbdq.delete_site(site_id_to_delete=site_id_to_delete)

		# Reload the site results, and refresh the page
		site_results = dbq.get_db_sites()
		return render_template("site_mgmt.html", sites=site_results, states=data.get_states())




# workorder details. it takes the wo_id as argument to retrive the the information from DB
@webapp.route('/wo-details', methods=['GET', 'POST','PUT','DELETE'])
@login_required
def wo_details(wo_id=""):
	"""The webapp's page takes wo_id and retrieve  the inforamtion from DB."""

	# if the current user is not authenticated, redirect the user to the logged out index page
	if not current_user.is_authenticated:
		return redirect(url_for("cim.templates.index"))

	if request.method=="GET":

		if request.args.get("wo_id"):
			wo_id=request.args.get("wo_id")
				
		
		#get products catalog
		products_catalog=data.get_products_catalog()
		
		#get locations
		location_results = dbq.get_db_locations()

		
		if wo_id !="":
			products=dbq.get_db_workorder_details(str(wo_id))
			workorder_information=dbq.get_a_work_order(wo_id)
		
		else:
			products={}
			workorder_information={}

		# render wo detail page
		return render_template("wo-details.html",
								wo_id=wo_id,
								products_catalog=products_catalog ,
								products=products,
								workorder_information=workorder_information,
								locations=location_results
								)

	if request.method=="POST":
		
		print(f'post request: request.json is: {request.json}')
				
		# make a new product with the first avaible sc_pn and assign it to this work order
		

		#TODO : retrive site id from session data 
		# get location id
		location_id=str(dbq.get_location_id(global_site_id,'2','1'))

		free_sc=dbq.get_free_sc_sn(request.json["sc_pn"],location_id)
		# no avilable free SC
		if free_sc==-1:
			print("EROOR in FREE SC!!!")
			# TODO: error to front end
			return error
					
		else:
			product_sc_sn=free_sc[0]["sc_sn"]
				
		product_pn=request.json["product_pn"]
		product_family=request.json["product_family"]
		employee_id=request.json["employee_id"]
		# product_location=10
		product_location=str(dbq.get_location_id(global_site_id,'3','1'))

		
		# dates are set to None
		product_assmebly_date=None
		product_qc_date=None
		product_warranty_date=None

		# insert product
		dbiq.insert_product(product_pn,product_family,product_assmebly_date,product_qc_date,
		product_warranty_date,employee_id,product_location,product_sc_sn)

		# update is_free attr
		dbuq.set_sc_not_free(product_sc_sn)
						

		# get product_sn using its SC_sn
		product_sn=dbq.get_product_sn(product_sc_sn)

		if product_sn==-1:
			# TODO: return error
			pass

		else:
			# add to work order
			wo_id=request.json["wo_id"]
			dbiq.insert_work_order_products(wo_id,product_sn)

		return json.dumps({'success':'A new product is added'}), 200, {'ContentType':'application/json'} 



	if request.method=='PUT':

		# extract information form request body
		product_sn=request.json["product_sn"]
		product_pn=request.json["product_pn"]
		product_family=request.json["product_family"]
		product_date_assembly=request.json["product_date_assembly"]
		product_qc_date=request.json["product_qc_date"]
		product_warranty_expiration_date=request.json["product_warranty_expiration_date"]
		product_location_id=request.json["product_location_id"]

				
		# add quotations to dates and family and pn
		# TODO a more smart way
		product_pn="'"+product_pn+"'"

		product_family="'"+product_family+"'"


		if product_date_assembly=="":
			product_date_assembly= "NULL"
		else:
			product_date_assembly="'"+product_date_assembly+"'"

		if product_qc_date=="":
			product_qc_date= "NULL"
		else:
			product_qc_date="'"+product_qc_date+"'"

		if product_warranty_expiration_date=="":
			product_warranty_expiration_date= "NULL"
		else:
			product_warranty_expiration_date="'"+product_warranty_expiration_date+"'"

		#  update DB
		dbuq.update_product(str(product_pn),product_family,product_date_assembly,product_qc_date,product_warranty_expiration_date,product_location_id,product_sn)

		# return response
		# TODO error respose

		print(f'got a PUT request! id is: {product_sn} and product_location_id is {product_location_id}')
		return json.dumps({'success':"Product is updated"}), 200, {'ContentType':'application/json'} 


	if request.method=='DELETE':
		# extract information form request body
		product_sn=request.json["product_sn"]

	
		# get product components
		regular_components=dbq.get_db_product_components(product_sn)
		print("products details in wo are: ", regular_components)
		
		# retrive SC SN
		sc_sn=dbq.get_db_product_details(product_sn)['product_sc_sn']
		print("sc_sn in wo are: ", sc_sn)

		# retrive the total number of RC
		regular_products_to_restore={}
		
		for component in regular_components: #for each component in product
			
			# if products does not exists in the dictionary add it with it's quantity
			if component['prc_rc_pn'] not in regular_products_to_restore.keys():
				regular_products_to_restore[component['prc_rc_pn']]=component['prc_quantity_needed']
			
			# otherwise add the quantity to curretn quantitiy
			else:
				regular_products_to_restore[component['prc_rc_pn']]=regular_products_to_restore[component['prc_rc_pn']]+component['prc_quantity_needed']
		
		# NO GC should be removed as its not a real RC
		regular_products_to_restore.pop('200', None)

		print("regular_products_to_restore in wo are: ", regular_products_to_restore)



		# update DB
		#  All free SC and RC will be added to the warehouse room 2 shelf 1 of the site location 
		#  for now the location is: RENO ID 57
		#TODO : retrive site ID from data session
		# get location id
		location_id=str(dbq.get_location_id(global_site_id,'2','1'))

		
		# as product_sn is a FK in 2 tables, first it has to be deleted from those tables
		# the product itself can be deleted

		# remove product from WorkorderProducts
		dbdq.delete_work_order_products_by_product_sn(str(product_sn))
		

		# remove product from ProductsRegularComps and Products 
		dbdq.delete_products_regular_comps(str(product_sn))
		dbdq.delete_product(str(product_sn))
		
		
		# set SC to free and update location
		dbuq.set_sc_free(sc_sn)
		dbuq.set_sc_location(str(sc_sn),location_id) 

		# add RC to inventory -- get current quant and update it

		for rc_pn,quantity in regular_products_to_restore.items():
			current_quantity=dbq.get_rc_quantity_in_a_location(str(rc_pn),location_id)

			if current_quantity==-1: # does not exists should be added a new entry
				dbiq.ali_insert_location_regular_comps(str(rc_pn),location_id,str(quantity))
			
			else: # exists should be updated
				new_quant=current_quantity+quantity
				dbuq.set_rc_quantity_in_a_location(str(rc_pn),location_id,str(new_quant))
		
	
		# return response
		# TODO error respose

		print(f'got a Delete request! id is: {product_sn}')
		return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 


# products details. it takes the product_sn as argument to retrive the the information from DB
@webapp.route('/product-details', methods=['GET', 'POST','PUT'])
@login_required
def product_details(product_sn=""):
	"""The webapp's page takes product_sn and retrieve  the inforamtion from DB."""

	# if the current user is not authenticated, redirect the user to the logged out index page
	if not current_user.is_authenticated:
		return redirect(url_for("cim.templates.index"))

	if request.method=="GET":

		if request.args.get("product_sn"):
			product_sn=request.args.get("product_sn")
		

		# get product information:
		if product_sn != "":
			product=dbq.get_db_product_details(product_sn)
											
		else:
			product={}
		
		
		# get components information:
		if product_sn != "":
			components_from_db=dbq.get_db_product_components(product_sn)

			# make a custom object from query result
			components={}
			for item in components_from_db:
				# print(f'item is: {item}')
				components[item["rc_category"]]=item["rc_pn_desc"]
				components[item["rc_category"]+"_quant"]=item["prc_quantity_needed"]

			print(f'temp is {components}')
								
		else:
			components={}
		
					
		#get reqular components catalog
		regular_components_catalog=data.get_rc_catalog()

		#get special components catalog
		special_components_catalog=data.get_sp_catalog()
		
	
		# render the detail page
		return render_template("product-details.html",
								product=product,
								components=components,
								special_components_catalog=special_components_catalog,
								regular_components_catalog=regular_components_catalog)

	if request.method=="POST":

		# dbiq.insert_products_regular_comps(10,2000,500)

		print(f'got a post request! and request.json is: {request.json}')

		# create correct object using post data
		product_sn=request.json['product_sn']
		regular_components=[
			{'rc_pn':dbq.get_db_regular_component_pn(request.json['MB'])[0]['rc_pn'],'quant':1}, # MB Data
			{'rc_pn':dbq.get_db_regular_component_pn(request.json['Case'])[0]['rc_pn'],'quant':1}, # Case Data
			{'rc_pn':dbq.get_db_regular_component_pn(request.json['GC'])[0]['rc_pn'],'quant':1}, # GC Data
			{'rc_pn':dbq.get_db_regular_component_pn(request.json['RAM'])[0]['rc_pn'],'quant':request.json['RAM_quant']}, # RAM Data
			{'rc_pn':dbq.get_db_regular_component_pn(request.json['HDD'])[0]['rc_pn'],'quant':request.json['HDD_quant']}, # HDD Data
		]

		# adjust RC quantity in inventory

		#TODO : retrive  site id from session data 
		# get location id
		location_id=str(dbq.get_location_id(global_site_id,'2','1'))

		# Check inventory
		for rc in regular_components:
			rc_pn=rc['rc_pn']
			quantity=int(rc['quant'])
	
			current_quantity=dbq.get_rc_quantity_in_a_location(str(rc_pn),location_id)

			if current_quantity<quantity and rc_pn!=200 : # not enough in inventory
				pn_desc=dbq.get_db_regular_component_desc(rc_pn)[0]['rc_pn_desc']
				
				return json.dumps({'Error':'Not enough','pn':pn_desc}), 400, {'ContentType':'application/json'}


		# if  all rcs are in inventory then update the product and inventory
		
		for rc in regular_components:
			rc_pn=rc['rc_pn']

			if rc_pn==200:
				# add components into product
				dbiq.insert_products_regular_comps(product_sn,rc_pn,quantity)
			

			else:
				quantity=int(rc['quant'])

				# add components into product
				dbiq.insert_products_regular_comps(product_sn,rc_pn,quantity)
		
				# update rc inventory		
				current_quantity=int(dbq.get_rc_quantity_in_a_location(str(rc_pn),location_id))
				updated_quantity=current_quantity-quantity

				print(f'pn is {rc_pn} , current quantity is {current_quantity} updated quantity is {updated_quantity}')

				dbuq.set_rc_quantity_in_a_location(str(rc_pn),location_id,str(updated_quantity))	
		
		

		return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

	if request.method=='PUT':

		#  for SC and RC it first delete all previous components and adds them into inventory
		# then take new itmes from inventory and assign into to the product

		
		print(f'got a PUT request! and request.json is: {request.json}')

		# create correct object using post data
		product_sn=request.json['product_sn']
		updated_regular_components=[
			{'rc_pn':dbq.get_db_regular_component_pn(request.json['MB'])[0]['rc_pn'],'quant':1}, # MB Data
			{'rc_pn':dbq.get_db_regular_component_pn(request.json['Case'])[0]['rc_pn'],'quant':1}, # Case Data
			{'rc_pn':dbq.get_db_regular_component_pn(request.json['GC'])[0]['rc_pn'],'quant':1}, # GC Data
			{'rc_pn':dbq.get_db_regular_component_pn(request.json['RAM'])[0]['rc_pn'],'quant':request.json['RAM_quant']}, # RAM Data
			{'rc_pn':dbq.get_db_regular_component_pn(request.json['HDD'])[0]['rc_pn'],'quant':request.json['HDD_quant']}, # HDD Data
		]
		updated_sc_sn=request.json['sc_sn']

		#TODO : retrive site ID from data session
		# get location id
		location_id=str(dbq.get_location_id(global_site_id,'2','1'))

		# Check inventory
		for rc in updated_regular_components:
			rc_pn=rc['rc_pn']
			quantity=int(rc['quant'])
	
			current_quantity=dbq.get_rc_quantity_in_a_location(str(rc_pn),location_id)

			if current_quantity<quantity and rc_pn!=200 : # not enough in inventory
				pn_desc=dbq.get_db_regular_component_desc(rc_pn)[0]['rc_pn_desc']
				
				return json.dumps({'Error':'Not enough','pn':pn_desc}), 400, {'ContentType':'application/json'}


		# get product components
		regular_components=dbq.get_db_product_components(product_sn)
		print("products details are: ", regular_components)
		
		# retrive SC SN
		sc_sn=dbq.get_db_product_details(product_sn)['product_sc_sn']
		print("sc_sn is: ", sc_sn)

		# retrive the total number of RC
		regular_products_to_restore={}
		
		for component in regular_components: #for each component in product
			
			# if products does not exists in the dictionary add it with it's quantity
			if component['prc_rc_pn'] not in regular_products_to_restore.keys():
				regular_products_to_restore[component['prc_rc_pn']]=component['prc_quantity_needed']
			
			# otherwise add the quantity to curretn quantitiy
			else:
				regular_products_to_restore[component['prc_rc_pn']]=regular_products_to_restore[component['prc_rc_pn']]+component['prc_quantity_needed']

		# NO GC should be removed as its not a real RC
		regular_products_to_restore.pop('200', None)


		# remove current components
		# remove product from ProductsRegularComps and Products 
		dbdq.delete_products_regular_comps(str(product_sn))
		
		# set SC to free and update location
		dbuq.set_sc_free(sc_sn)
		dbuq.set_sc_location(str(sc_sn),location_id) 

		# add RC to inventory -- get current quant and update it

		for rc_pn,quantity in regular_products_to_restore.items():
			if rc_pn!=200:
				current_quantity=dbq.get_rc_quantity_in_a_location(str(rc_pn),location_id)

				if current_quantity==-1: # does not exists should be added a new entry
					dbiq.ali_insert_location_regular_comps(str(rc_pn),location_id,str(quantity))
				
				else: # exists should be updated
					new_quant=current_quantity+quantity
					dbuq.set_rc_quantity_in_a_location(str(rc_pn),location_id,str(new_quant))

			
		# update special_component
		dbuq.set_sc_not_free(str(updated_sc_sn))

		dbuq.set_sc_sn_of_a_product(str(updated_sc_sn),str(product_sn))

		# add new RCs and adjust RC quantity

		for rc in updated_regular_components:
			rc_pn=rc['rc_pn']

			if rc_pn==200:
				# add components into product
				dbiq.insert_products_regular_comps(product_sn,rc_pn,quantity)
			

			else:
				quantity=int(rc['quant'])

				# add components into product
				dbiq.insert_products_regular_comps(product_sn,rc_pn,quantity)
		
				# update rc inventory		
				current_quantity=int(dbq.get_rc_quantity_in_a_location(str(rc_pn),location_id))
				updated_quantity=current_quantity-quantity

				print(f'pn is {rc_pn} , current quantity is {current_quantity} updated quantity is {updated_quantity}')

				dbuq.set_rc_quantity_in_a_location(str(rc_pn),location_id,str(updated_quantity))
	
		# return response
		# TODO error respose

		print(f'got a PUT request! id is: {product_sn}')
		return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
				

		
# Assembly page. The page lists are assigned products ready for assembly 
@webapp.route('/assembly', methods=['GET', 'POST','PUT'])
@login_required
def assembly():
	"""The webapp's page retrieve  the inforamtion from DB for the Assembly process."""

	# if the current user is not authenticated, redirect the user to the logged out index page
	if not current_user.is_authenticated:
		return redirect(url_for("cim.templates.index"))

	if request.method=="GET":

		# get employee ID

		employee_id=None

		# assembly_list=data.get_assembly()

		assembly_list=dbq.get_assembly_list(employee_id)

		print(f'assembly is: {assembly_list}')

		products_catalog=data.get_products_catalog()
		
		
		# render the assembly page
		return render_template("assembly.html",assembly_list=assembly_list,products_catalog=products_catalog)

	if request.method=="PUT":
		print(f'got a PUT request! and request.json is: {request.json}')

		product_sn=request.json['product_sn']
		product_date_assembly="'"+request.json['product_date_assembly']+"'"

		print(f'sn is: {product_sn} and product_date_assembly is : {product_date_assembly}')

		# get location id 
		# Assembled prodcuts will be in QC department room 4 shelf 1
		#TODO: retrive site id from session
		location_id=str(dbq.get_location_id(global_site_id,'4','1'))
		
		# update database
		dbuq.set_product_date_assembly(product_sn,product_date_assembly)

		# update product location
		dbuq.set_product_location(product_sn,location_id)

		# update sc location
		sc_sn=dbq.get_db_product_details(product_sn)['product_sc_sn']
		dbuq.set_sc_location(sc_sn,location_id)

		# update wo status if needed
		wo_id=dbq.get_wo_of_a_product(str(product_sn))['wop_wo_id']
		update_workorder_status(str(wo_id))

		# return response
		# TODO error respose
		
		return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

		

# QC page. The page lists are assigned products ready for assembly 
@webapp.route('/qc', methods=['GET', 'POST','PUT'])
@login_required
def QC():
	"""The webapp's page retrieve  the inforamtion from DB for the Assembly process."""

	# if the current user is not authenticated, redirect the user to the logged out index page
	if not current_user.is_authenticated:
		return redirect(url_for("cim.templates.index"))

	if request.method=="GET":
		# get employee ID

		employee_id=None

		# assembly_list=data.get_assembly()

		qc_list=dbq.get_qc_list(employee_id)

		print(f'qc is: {qc_list}')

		products_catalog=data.get_products_catalog()
		
		# render the assembly page
		return render_template("qc.html",qc_list=qc_list,products_catalog=products_catalog)

	if request.method=="PUT":
		print(f'got a PUT request! and request.json is: {request.json}')

		product_sn=request.json['product_sn']
		product_qc_date="'"+request.json['product_qc_date']+"'"

		print(f'sn is: {product_sn} and qc_date is : {product_qc_date}')

		# get location id 
		# QC'ed prodcuts will be in shipping department room5 shelf 1
		#TODO: retrive site id from session
		location_id=str(dbq.get_location_id(global_site_id,'5','1'))


		# update database
		# update date
		dbuq.set_product_qc_date(product_sn,product_qc_date)

		# update product location
		dbuq.set_product_location(product_sn,location_id)

		# update sc location
		sc_sn=dbq.get_db_product_details(product_sn)['product_sc_sn']
		dbuq.set_sc_location(sc_sn,location_id)

		# update wo status if needed
		wo_id=dbq.get_wo_of_a_product(str(product_sn))['wop_wo_id']
		update_workorder_status(str(wo_id))

		# return response
		# TODO error respose
		
		return json.dumps({'success':True}), 200, {'ContentType':'application/json'}




@webapp.route('/data/product_catalog', methods=['GET', 'POST'])
@login_required
def get_products_catalog_r():
	# returns products catalog
	if request.method=="GET":
		print(data.get_products_catalog())
		return data.get_products_catalog()


@webapp.route('/data/free_sn', methods=['GET', 'POST'])
@login_required
def get_free_sc_sn():
	# Returns a valid free SC_SN based on the given PN and Method

	if request.method=="POST":
		
		print(f'got a post request! and request.json is: {request.json}')

		#TODO : retrive site id from session data 
		# get location id
		location_id=str(dbq.get_location_id(global_site_id,'2','1'))
		
		method=request.json["method"]
		part_number=request.json["product_pn"]
		free_sc_sn=[]
		for sn in dbq.get_free_sc_sn(part_number,location_id):
			free_sc_sn.append(sn["sc_sn"])
			
		if method=="FIFO":
			result=free_sc_sn[-1]

		if method=="LIFO":
			result=free_sc_sn[0]

		if method=="random":
			result=random.choice(free_sc_sn)


		print(f'free sc are: {free_sc_sn}')
		print(f'result is: {result}')
		return json.dumps({'sn':result}), 200, {'ContentType':'application/json'}


@webapp.route('/data/product_components_exist', methods=['GET', 'POST'])
@login_required
def get_product_components():
	# returns True if a product has Regular components otherwise returns False

	if request.method=="POST":
		
		print(f'got a post request! and request.json is: {request.json}')
		
		product_components=dbq.get_db_product_components(request.json["product_sn"])

		if len(product_components)==0:
			return json.dumps({'result':False}), 200, {'ContentType':'application/json'}

		else:
			return json.dumps({'result':True}), 200, {'ContentType':'application/json'}




@webapp.route('/data/wo_status_cataloge', methods=['GET'])
@login_required
def wo_status_cataloge():

	return jsonify(data.get_wo_status())


@webapp.route('/data/list_of_employees', methods=['GET'])
@login_required
def employees():

	employees=dbq.get_db_employees()
	result=[]
	for employee in employees:
		result.append(employee["employee_first_name"]+" "+employee["employee_last_name"])
	return jsonify(result)



def update_workorder_status(wo_id):
	# function to update work order status after qc, assembly 

	wo_status=dbq.get_a_work_order(wo_id)['wo_status']
	products_sn=[]
	for product in dbq.get_db_products_in_a_workorder(wo_id):
		products_sn.append(product['wop_product_sn'])

	# print(f'wo_id is {wo_id} and wo status is {wo_status}')
	# print(f'products are {products_sn}')

	#check if all products are assembled
	if wo_status=='assembly_pending':
		for sn in products_sn:
			product=dbq.get_db_product_details(str(sn))
			if product['product_date_assembly']==None:
				return
		dbuq.set_workorder_status(wo_id,"'qc_pending'")

	#check if all products are QC'ed
	if wo_status=='qc_pending':
		for sn in products_sn:
			product=dbq.get_db_product_details(str(sn))
			if product['product_qc_date']==None:
				return
		dbuq.set_workorder_status(wo_id,"'shipping_pending'")