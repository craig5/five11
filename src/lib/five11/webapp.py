# vim: set expandtab tabstop=4 shiftwidth=4 autoindent smartindent:
#
import logging
import os
import flask
import jinja2
import five11.data
import five11.constants

_BASE_DIR = five11.constants._BASE_DIR
_TEMPLATE_DIR = five11.constants._TEMPLATE_DIR
_STATIC_DIR = five11.constants._STATIC_DIR
_DATA_DIR = five11.constants._DATA_DIR
app = flask.Flask(__name__, template_folder=_TEMPLATE_DIR,
        static_folder=_STATIC_DIR)
# XXX include config stuff
##app.config.from_object(__name__)
#print _TEMPLATE_DIR

datamgr = five11.data.DataManager()
trains_data = datamgr.read_train_data()
app.logger.debug("Train data read...")

_PAGE_TITLE = 'LI Five11'
page_data = dict()
page_data['title'] = _PAGE_TITLE

@app.route('/')
def home():
  return flask.render_template('home.html', page_data=page_data)

@app.route('/office/mv')
def show_mv_office():
  return flask.render_template('station.html', page_data=page_data)

@app.route('/office/svale')
def show_svale_office():
  return flask.render_template('station.html', page_data=page_data)

@app.route('/about')
def about():
  return flask.render_template('about.html', page_data=page_data)

@app.errorhandler(404)
def page_not_found(error):
  return flask.render_template('404.html', page_data=page_data), 404


# End of file.
