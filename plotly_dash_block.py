from nio.block.base import Block
from nio.properties import VersionProperty
from nio.util.threading.spawn import spawn
import dash
import dash_core_components as dcc
import dash_html_components as html


class PlotlyDash(Block):

    version = VersionProperty('0.1.0')

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
        graphs = []
        for signal in signals:
            figure = {'data': signal.data, 'layout': {'title': signal.title}}
            graphs.append(dcc.Graph(id=signal.title, figure=figure))
        self.app.layout = html.Div(graphs)
        self.logger.debug('displaying {} graphs '.format(len(graphs)))

    def _server(self):
        self.app.layout = html.Div()
        self.app.run_server(debug=False)
