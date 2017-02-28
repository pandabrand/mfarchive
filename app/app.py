from flask import Flask, render_template, make_response
from flask import request, jsonify
from model import db
from database import *
from model import app as application
import simplejson as json
from sqlalchemy.exc import IntegrityError
import os
import logging, sys
from sqlalchemy import or_, extract
import logging, sys
import time

from xhtml2pdf import pisa
from StringIO import StringIO

# initate flask app
app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.config['SERVER_NAME'] = 'localhost:8082'
app.config['STATIC_URL'] = '/static/'
app.config['STATIC_ROOT'] = '/Volumes/Rosetta/Clients/MarketForward/flask-archive/Docker-Compose/Flask-MySQL/app/'
app.config['MEDIA_URL'] = '/static/'
app.config['MEDIA_ROOT'] = '/Volumes/Rosetta/Clients/MarketForward/flask-archive/Docker-Compose/Flask-MySQL/app/'
PER_PAGE = 30
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

current_milli_time = lambda: int(round(time.time() * 1000))

sep = ';'

NUM_OF_ORDERS = 0
NUM_OF_ORDERS_FILES = 0
NUM_OF_DIVISIONS = 0
NUM_OF_DISTRICTS = 0
NUM_OF_COMPLEXES = 0
NUM_OF_BRANCHES = 0

def get_counts():
    logging.debug('updating orders')
    orders_q = Order.query
    orders_q = orders_q.filter(Order.fk_order_status_id == OrderStatus.pk_id).filter(or_(OrderStatus.name_for_display == 'Completed', OrderStatus.name_for_display == 'Ready for Download'))
    orders_q = orders_q.filter(extract('year', Order.date_created) >= 2010)
    orders = orders_q.all()
    global NUM_OF_ORDERS, NUM_OF_ORDERS_FILES, NUM_OF_DIVISIONS, NUM_OF_DISTRICTS, NUM_OF_COMPLEXES, NUM_OF_BRANCHES
    NUM_OF_ORDERS = len(orders)
    for order in orders:
        NUM_OF_ORDERS_FILES += 1 if order.hi_res_path else 0
    logging.debug(NUM_OF_ORDERS_FILES)
    divisions = Division.query.filter(Division.is_active == 'Y').all()
    NUM_OF_DIVISIONS = len(divisions)
    logging.debug(NUM_OF_DIVISIONS)
    districts = District.query.filter(District.is_active == 'Y').all()
    NUM_OF_DISTRICTS = len(districts)
    complexes = Complex.query.filter(Complex.is_active == 'Y').all()
    NUM_OF_COMPLEXES = len(complexes)
    branches = Branch.query.filter(Branch.is_active == 'Y').all()
    NUM_OF_BRANCHES = len(branches)

# def filter_query(self, query):
# 	# model_class = self._get_model_class(query) # returns the query's Model
# 	raw_filters = request.args.getlist('filter')
# 	for raw in raw_filters:
# 	  try:
# 	    key, op, value = raw.split(self.sep, 3)
# 	  except ValueError:
# 	    raise APIError(400, 'Invalid filter: %s' % raw)
# 	  column = getattr(Order, key, None)
# 	  if not column:
# 	    raise APIError(400, 'Invalid filter column: %s' % key)
# 	  if op == 'in':
# 	    filt = column.in_(value.split(','))
# 	  else:
# 	    try:
# 	      attr = filter(
# 	        lambda e: hasattr(column, e % op),
# 	        ['%s', '%s_', '__%s__']
# 	      )[0] % op
# 	    except IndexError:
# 	      raise APIError(400, 'Invalid filter operator: %s' % op)
# 	    if value == 'null':
# 	      value = None
# 	    filt = getattr(column, attr)(value)
# 		query = query.filter(filt)
# 	return query

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    # use short variable names
    sUrl = '/static/'#app.config.STATIC_URL      # Typically /static/
    sRoot = '/Volumes/Rosetta/Clients/MarketForward/flask-archive/Docker-Compose/Flask-MySQL/app/static/'#app.config.STATIC_ROOT    # Typically /home/userX/project_static/
    mUrl = '/static/'#app.config.MEDIA_URL       # Typically /static/media/
    mRoot = '/Volumes/Rosetta/Clients/MarketForward/flask-archive/Docker-Compose/Flask-MySQL/app/static/'#app.config.MEDIA_ROOT     # Typically /home/userX/project_static/media/

    # convert URIs to absolute system paths
    # if uri.startswith(sUrl):
    path = os.path.join(sRoot, uri.replace(sUrl, ""))
    # elif uri.startswith(mUrl):
    #     path = os.path.join(mRoot, uri.replace(mUrl, ""))
    # else:
    #     return uri  # handle absolute uri (ie: http://some.tld/foo.png)

    # make sure that file exists
    if not os.path.isfile(path):
            raise Exception(
                '%s media URI must start with %s or %s' % (path, sUrl, mUrl)
            )
    return path

# @app.route('/')
@app.route('/order/', defaults={'page': 1})
@app.route('/order/<int:page>')
def index(page):
	# orders_q = Order.query.filter(Order.fk_order_status_id == OrderStatus.pk_id).filter(or_(OrderStatus.name_for_display == 'Completed', OrderStatus.name_for_display == 'Ready for Download'))
	# orders = orders_q.paginate(page, PER_PAGE, False)
	return render_template('index.html')

@app.route('/')
def dashboard():
    return render_template('order_dashboard.html')

@app.route('/division/', defaults={'page': 1})
@app.route('/division/<int:page>')
def division(page):
	# orders_q = Order.query.filter(Order.fk_order_status_id == OrderStatus.pk_id).filter(or_(OrderStatus.name_for_display == 'Completed', OrderStatus.name_for_display == 'Ready for Download'))
	# orders = orders_q.paginate(page, PER_PAGE, False)
	return render_template('division.html')

@app.route('/district/', defaults={'page': 1})
@app.route('/district/<int:page>')
def district(page):
	# orders_q = Order.query.filter(Order.fk_order_status_id == OrderStatus.pk_id).filter(or_(OrderStatus.name_for_display == 'Completed', OrderStatus.name_for_display == 'Ready for Download'))
	# orders = orders_q.paginate(page, PER_PAGE, False)
	return render_template('district.html')


@app.route('/complex/', defaults={'page': 1})
@app.route('/complex/<int:page>')
def complex(page):
	# orders_q = Order.query.filter(Order.fk_order_status_id == OrderStatus.pk_id).filter(or_(OrderStatus.name_for_display == 'Completed', OrderStatus.name_for_display == 'Ready for Download'))
	# orders = orders_q.paginate(page, PER_PAGE, False)
	return render_template('complex.html')


@app.route('/branch/', defaults={'page': 1})
@app.route('/branch/<int:page>')
def branch(page):
	# orders_q = Order.query.filter(Order.fk_order_status_id == OrderStatus.pk_id).filter(or_(OrderStatus.name_for_display == 'Completed', OrderStatus.name_for_display == 'Ready for Download'))
	# orders = orders_q.paginate(page, PER_PAGE, False)
	return render_template('branch.html')

@app.route('/api/order_and_file_count')
def order_file_json():
    if(NUM_OF_ORDERS < 1):
        get_counts()
    return jsonify({'num_orders':NUM_OF_ORDERS,'num_files':NUM_OF_ORDERS_FILES,'division_count':NUM_OF_DIVISIONS,'district_count':NUM_OF_DISTRICTS,'complex_count':NUM_OF_COMPLEXES,'branch_count':NUM_OF_BRANCHES})

@app.route('/api/order/', defaults={'page': 1})
@app.route('/api/order/<int:page>')
def index_json(page):
	sort = request.args.get('sort') if request.args.get('sort') is not None else 'Order'
	sort_direction = request.args.get('direction') if request.args.get('direction') is not None else 'asc'
	sort_col = request.args.get('col') if request.args.get('col') is not None else 'pk_id'
	sort_model = getattr(sys.modules[__name__], sort)
	sort_col = getattr(sort_model, sort_col)
	search_req = request.args.get('search') if request.args.get('search') is not None else ''
	order_id = request.args.get('order_id') if request.args.get('order_id') is not None else ''

	orders_q = Order.query
	orders_q = orders_q.filter(Order.fk_order_status_id == OrderStatus.pk_id).filter(or_(OrderStatus.name_for_display == 'Completed', OrderStatus.name_for_display == 'Ready for Download'))

	if search_req == 'true':
		orders_q = orders_q.filter(Order.pk_id == order_id)

	if sort_direction == 'desc':
		orders_q = orders_q.order_by(sort_col.desc())
	else:
		orders_q = orders_q.order_by(sort_col)

	# logging.debug(orders_q)
	order_schema = OrderSchema(many=True)
	orders = orders_q.paginate(page, PER_PAGE, False)
	items = orders.items
	json_orders = order_schema.dump(items).data
	return jsonify({'orders':json_orders, 'paginate':{'has_next':orders.has_next, 'has_prev':orders.has_prev, 'next_num':orders.next_num, 'prev_num':orders.prev_num, 'page':orders.page, 'pages':orders.pages, 'per_page':orders.per_page}})

@app.route('/api/division/', defaults={'page': 1})
@app.route('/api/division/<int:page>')
def division_json(page):
	sort = request.args.get('sort') if request.args.get('sort') is not None else 'Division'
	sort_direction = request.args.get('direction') if request.args.get('direction') is not None else 'asc'
	sort_col = request.args.get('col') if request.args.get('col') is not None else 'region_id'
	sort_model = getattr(sys.modules[__name__], sort)
	sort_col = getattr(sort_model, sort_col)
	# search_req = request.args.get('search') if request.args.get('search') is not None else ''
	# order_id = request.args.get('order_id') if request.args.get('order_id') is not None else ''

	divisions_q = Division.query
	divisions_q = divisions_q.filter(Division.is_active == 'Y')

	if sort_direction == 'desc':
		divisions_q = divisions_q.order_by(sort_col.desc())
	else:
		divisions_q = divisions_q.order_by(sort_col)

	division_schema = DivisionSchema(many=True)
	divisions = divisions_q.paginate(page, PER_PAGE, False)
	items = divisions.items
	json_divisions = division_schema.dump(items).data
	return jsonify({'divisions':json_divisions, 'paginate':{'has_next':divisions.has_next, 'has_prev':divisions.has_prev, 'next_num':divisions.next_num, 'prev_num':divisions.prev_num, 'page':divisions.page, 'pages':divisions.pages, 'per_page':divisions.per_page}})


@app.route('/api/district/', defaults={'page': 1})
@app.route('/api/district/<int:page>')
def district_json(page):
	sort = request.args.get('sort') if request.args.get('sort') is not None else 'District'
	sort_direction = request.args.get('direction') if request.args.get('direction') is not None else 'asc'
	sort_col = request.args.get('col') if request.args.get('col') is not None else 'area_number'
	sort_model = getattr(sys.modules[__name__], sort)
	sort_col = getattr(sort_model, sort_col)
	# search_req = request.args.get('search') if request.args.get('search') is not None else ''
	# order_id = request.args.get('order_id') if request.args.get('order_id') is not None else ''

	districts_q = District.query
	districts_q = districts_q.filter(District.is_active == 'Y')

	if sort_direction == 'desc':
		districts_q = districts_q.order_by(sort_col.desc())
	else:
		districts_q = districts_q.order_by(sort_col)

	district_schema = DistrictSchema(many=True)
	districts = districts_q.paginate(page, PER_PAGE, False)
	items = districts.items
	json_districts = district_schema.dump(items).data
	return jsonify({'districts':json_districts, 'paginate':{'has_next':districts.has_next, 'has_prev':districts.has_prev, 'next_num':districts.next_num, 'prev_num':districts.prev_num, 'page':districts.page, 'pages':districts.pages, 'per_page':districts.per_page}})

@app.route('/api/complex/', defaults={'page': 1})
@app.route('/api/complex/<int:page>')
def complex_json(page):
	sort = request.args.get('sort') if request.args.get('sort') is not None else 'Complex'
	sort_direction = request.args.get('direction') if request.args.get('direction') is not None else 'asc'
	sort_col = request.args.get('col') if request.args.get('col') is not None else 'complex_id'
	sort_model = getattr(sys.modules[__name__], sort)
	sort_col = getattr(sort_model, sort_col)
	# search_req = request.args.get('search') if request.args.get('search') is not None else ''
	# order_id = request.args.get('order_id') if request.args.get('order_id') is not None else ''

	complexes_q = Complex.query
	complexes_q = complexes_q.filter(Complex.is_active == 'Y')

	if sort_direction == 'desc':
		complexes_q = complexes_q.order_by(sort_col.desc())
	else:
		complexes_q = complexes_q.order_by(sort_col)

	complex_schema = ComplexSchema(many=True)
	complexes = complexes_q.paginate(page, PER_PAGE, False)
	items = complexes.items
	json_complexes = complex_schema.dump(items).data
	return jsonify({'complexes':json_complexes, 'paginate':{'has_next':complexes.has_next, 'has_prev':complexes.has_prev, 'next_num':complexes.next_num, 'prev_num':complexes.prev_num, 'page':complexes.page, 'pages':complexes.pages, 'per_page':complexes.per_page}})

@app.route('/api/branch/', defaults={'page': 1})
@app.route('/api/branch/<int:page>')
def branch_json(page):
	sort = request.args.get('sort') if request.args.get('sort') is not None else 'Branch'
	sort_direction = request.args.get('direction') if request.args.get('direction') is not None else 'asc'
	sort_col = request.args.get('col') if request.args.get('col') is not None else 'branch_id'
	sort_model = getattr(sys.modules[__name__], sort)
	sort_col = getattr(sort_model, sort_col)
	# search_req = request.args.get('search') if request.args.get('search') is not None else ''
	# order_id = request.args.get('order_id') if request.args.get('order_id') is not None else ''

	branches_q = Branch.query
	branches_q = branches_q.filter(Branch.is_active == 'Y').filter(Branch.branch_id != '000000')

	if sort_direction == 'desc':
		branches_q = branches_q.order_by(sort_col.desc())
	else:
		branches_q = branches_q.order_by(sort_col)

	branch_schema = BranchSchema(many=True)
	branches = branches_q.paginate(page, PER_PAGE, False)
	items = branches.items
	json_branches = branch_schema.dump(items).data
	return jsonify({'branches':json_branches, 'paginate':{'has_next':branches.has_next, 'has_prev':branches.has_prev, 'next_num':branches.next_num, 'prev_num':branches.prev_num, 'page':branches.page, 'pages':branches.pages, 'per_page':branches.per_page}})

@app.route('/arf/<int:orderId>')
def arf(orderId):
	order = Order.query.get(orderId)
   	data = render_template('arf.html', order=order)
	pdf = generatePdf(data)
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = 'inline; filename={0}-arf.pdf'.format(orderId)
	return response

def generatePdf(pdf_data):
	pdf = StringIO()
	pisa.CreatePDF(StringIO(pdf_data), pdf)#, link_callback=link_callback)
	rendered = pdf.getvalue()
	pdf.close()
	return rendered

@app.route('/info')
def app_status():
	return json.dumps({'server_info':application.config['SQLALCHEMY_DATABASE_URI']})

# run app service
if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8082, debug=True)
	get_counts()
