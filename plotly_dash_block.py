# from enum import Enum
from nio.block.base import Block
from nio.properties import VersionProperty, ListProperty, PropertyHolder, \
        Property, SelectProperty
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

    id = Property(title='Graph ID', default = '')
    series = ListProperty(Series, title='Series', default=[])

class PlotlyDash(Block):

    version = VersionProperty('0.1.0')
    graph_layout = ListProperty(Graphs, title='Graphs', default=[])

    def __init__(self):
        self._server_thread = None
        self.app = dash.Dash()
        super().__init__()

    def start(self):
        self._server_thread = spawn(self._server)
        self.logger.debug('server started on localhost:8050')
        super().start()

    def stop(self):
        try:
            self._server_thread.join()
            self.logger.debug('server stopped')
        except:
            self.logger.warning('main thread exited before join()')
        super().stop()

    def process_signals(self, signals):
        for signal in signals:
            self.app.layout = html.Div([dcc.Graph(id=g.id(signal), figure={'data': [d.kwargs(signal) for d in g.series(signal)], 'layout': {'title': g.id(signal)}}) for g in self.graph_layout()])

    def _server(self):
        self.app.run_server(debug=False)
