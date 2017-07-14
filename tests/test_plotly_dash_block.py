from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from ..plotly_dash_block import PlotlyDash
from unittest.mock import patch, MagicMock


class TestExample(NIOBlockTestCase):

    def test_server_start(self):
        with patch('dash.Dash') as mock_dash:
            blk = PlotlyDash()
            self.configure_block(blk, {})
            blk.start()
            blk.stop()
            self.assertEqual(mock_dash.call_count, 1)
            self.assertEqual(mock_dash.return_value.run_server.call_count, 1)

    def test_page_layout(self):
        input_signals = [Signal({'a': {'name': 'a', 'y': [0,1,2]},
                                 'b': {'name': 'b', 'y': [2,1,0]},
                                 'c': {'name': 'c', 'x': [0,1,2], 'y': [1,1,1]}})]
        config = {'graph_layout': [{'id': '0',
                                   'series': [{'kwargs': "{{ {'name': $a['name'], 'y': $a['y']} }}"},
                                              {'kwargs': "{{ {'name': $b['name'], 'y': $b['y']} }}"}]},
                                  {'id': '1',
                                   'series': [{'kwargs': "{{ {'name': $c['name'], 'x': $c['x'], 'y': $c['y']} }}"}]}]}
        with patch('dash.Dash') as mock_dash, \
                patch('dash_html_components.Div') as mock_div, \
                patch('dash_core_components.Graph') as mock_graph:
            graphs = [MagicMock(), MagicMock()]
            mock_graph.side_effect = graphs
            blk = PlotlyDash()
            self.configure_block(blk, config)
            blk.start()
            blk.process_signals(input_signals)
            blk.stop()
            mock_div.assert_called_once_with(graphs)
            i = input_signals[0].to_dict()
            # todo: make this work for an arbitrary number of graph configs
            mock_graph.assert_any_call(id='0', figure={'layout': {'title': '0'}, 'data': [i['a'], i['b']]})
            mock_graph.assert_any_call(id='1', figure={'layout': {'title': '1'}, 'data': [i['c']]})
            self.assertEqual(mock_graph.call_count, len(config['graph_layout']))
