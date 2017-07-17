# from enum import Enum
import requests
from flask import request
from nio.block.base import Block
from nio.properties import VersionProperty, ListProperty, PropertyHolder, \
        Property, SelectProperty, IntProperty
from nio.util.threading.spawn import spawn
import dash
import dash_core_components as dcc
import dash_html_components as html


# class ElementTypes(Enum):
    # Graph = 'Graph'

class Series(PropertyHolder):
    kwargs = Property(title='Keyword Args', default='{{ {} }}')
    # type = ListProperty(ElementTypes,
                        # title='Element Type',
                        # default=ElementTypes.Graph)

class Graphs(PropertyHolder):

    id = Property(title='Graph Title', default = '')
    series = ListProperty(Series, title='Series', default=[])

class PlotlyDash(Block):

    version = VersionProperty('0.1.0')
    port = IntProperty(title='Server Port', default=8050)
    graph_layout = ListProperty(Graphs, title='Graphs', default=[])
    app = dash.Dash()

    def __init__(self):
        self._server_thread = None
        super().__init__()

    def start(self):
        self._server_thread = spawn(self._server)
        self.logger.debug('server started on localhost:{}'.format(self.port()))
        super().start()

    def stop(self):
        # http://flask.pocoo.org/snippets/67/
        try:
            r = requests.get('http://localhost:{}/shutdown'.format(
                self.port()))
            self.logger.debug('shutting down server ...')
        except:
            self.logger.warning('shutdown_server callback failed')
        try:
            self._server_thread.join()
            self.logger.debug('_server_thread joined')
        except:
            self.logger.warning('_server_thread exited before join() call')
        if self._server_thread.is_alive():
            self.logger.warning('_server_thread did not exit')
        super().stop()

    def process_signals(self, signals):
        for signal in signals:
            self.app.layout = html.Div([dcc.Graph(id=g.id(signal), figure={'data': [d.kwargs(signal) for d in g.series(signal)], 'layout': {'title': g.id(signal)}}) for g in self.graph_layout()])

    def _server(self):
        self.app.layout = html.Div()
        # if debug isn't passed the server breaks silently
        self.app.run_server(debug=False, port=self.port())

    def shutdown_server():
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            self.logger.warning('Not running with the Werkzeug Server')
        func()

    @app.server.route('/shutdown', methods=['GET'])
    def shutdown():
        PlotlyDash.shutdown_server()
        return 'OK'
