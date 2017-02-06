from flask import Flask, render_template, make_response
from flask import request, jsonify
from model import db
from database import *
from model import app as application
import simplejson as json
from sqlalchemy.exc import IntegrityError
import os
import logging, sys
from sqlalchemy import or_
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
@app.route('/', defaults={'page': 1})
@app.route('/<int:page>')
def index(page):
	# orders_q = Order.query.filter(Order.fk_order_status_id == OrderStatus.pk_id).filter(or_(OrderStatus.name_for_display == 'Completed', OrderStatus.name_for_display == 'Ready for Download'))
	# orders = orders_q.paginate(page, PER_PAGE, False)
	return render_template('index.html')

@app.route('/api', defaults={'page': 1})
@app.route('/api/<int:page>')
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
# @app.route('/user')
# def show_user():
# 	#return json.dumps({'username':request.args['username']})
# 	try:
# 		user = User.query.filter_by(username=request.args['username']).first_or_404()
# 		return json.dumps({user.username:{ 'email': user.email, 'phone': user.phone,'fax':user.fax}})
# 	except IntegrityError:
# 		return json.dumps({})

# http://localhost/
# @app.route('/insert')
# def insert_user():
# 	try:
# 		user = User(request.args['username'],
# 				request.args['email'],
# 				request.args['phone'],
# 				request.args['fax'])
# 		db.session.add(user)
# 		db.session.commit()
# 		return json.dumps({'status':True})
# 	except IntegrityError:
# 		return json.dumps({'status':False})

# @app.route('/createtbl')
# def createUserTable():
# 	try:
# 		db.create_all()
# 		return json.dumps({'status':True})
# 	except IntegrityError:
# 		return json.dumps({'status':False})

@app.route('/users')
def users():
	try:
		users = User.query.all()
		users_dict = {}
		for user in users:
			users_dict[user.username] = {
							'new login': user.new_login,
						    }

		return json.dumps(users_dict)
	except IntegrityError:
		return json.dumps({})
#
# @app.route('/createdb')
# def createDatabase():
# 	HOSTNAME = 'localhost'
# 	try:
# 		HOSTNAME = request.args['hostname']
# 	except:
# 		pass
# 	database = CreateDB(hostname = HOSTNAME)
# 	return json.dumps({'status':True})

@app.route('/info')
def app_status():
	return json.dumps({'server_info':application.config['SQLALCHEMY_DATABASE_URI']})

# run app service
if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8082, debug=True)
