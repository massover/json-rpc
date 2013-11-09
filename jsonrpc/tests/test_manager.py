import unittest

from ..manager import JSONRPCResponseManager
from ..jsonrpc2 import (
    JSONRPC20BatchRequest,
    JSONRPC20BatchResponse,
    JSONRPC20Request,
    JSONRPC20Response,
)
from ..jsonrpc1 import JSONRPC10Request, JSONRPC10Response


class TestJSONRPCResponseManager(unittest.TestCase):
    def setUp(self):
        def raise_(e):
            raise e

        self.dispatcher = {
            "add": sum,
            "list_len": len,
            "101_base": lambda **kwargs: int("101", **kwargs),
            "error": lambda: raise_(KeyError("error_explanation"))
        }

    def test_returned_type_response(self):
        request = JSONRPC20Request("add", [[]], _id=0)
        response = JSONRPCResponseManager.handle(request.json, self.dispatcher)
        self.assertTrue(isinstance(response, JSONRPC20Response))

    def test_returned_type_butch_response(self):
        request = JSONRPC20BatchRequest(
            JSONRPC20Request("add", [[]], _id=0))
        response = JSONRPCResponseManager.handle(request.json, self.dispatcher)
        self.assertTrue(isinstance(response, JSONRPC20BatchResponse))

    def test_returned_type_response_rpc10(self):
        request = JSONRPC10Request("add", [[]], _id=0)
        response = JSONRPCResponseManager.handle(request.json, self.dispatcher)
        self.assertTrue(isinstance(response, JSONRPC10Response))

    def test_parse_error(self):
        req = '{"jsonrpc": "2.0", "method": "foobar, "params": "bar", "baz]'
        response = JSONRPCResponseManager.handle(req, self.dispatcher)
        self.assertTrue(isinstance(response, JSONRPC20Response))
        self.assertEqual(response.error["message"], "Parse error")
        self.assertEqual(response.error["code"], -32700)

    def test_invalid_request(self):
        req = '{"jsonrpc": "2.0", "method": 1, "params": "bar"}'
        response = JSONRPCResponseManager.handle(req, self.dispatcher)
        self.assertTrue(isinstance(response, JSONRPC20Response))
        self.assertEqual(response.error["message"], "Invalid Request")
        self.assertEqual(response.error["code"], -32600)

    def test_method_not_found(self):
        request = JSONRPC20Request("does_not_exist", [[]], _id=0)
        response = JSONRPCResponseManager.handle(request.json, self.dispatcher)
        self.assertTrue(isinstance(response, JSONRPC20Response))
        self.assertEqual(response.error["message"], "Method not found")
        self.assertEqual(response.error["code"], -32601)

    def test_invalid_params(self):
        request = JSONRPC20Request("add", {"a": 0}, _id=0)
        response = JSONRPCResponseManager.handle(request.json, self.dispatcher)
        self.assertTrue(isinstance(response, JSONRPC20Response))
        self.assertEqual(response.error["message"], "Invalid params")
        self.assertEqual(response.error["code"], -32602)

    def test_server_error(self):
        request = JSONRPC20Request("error", _id=0)
        response = JSONRPCResponseManager.handle(request.json, self.dispatcher)
        self.assertTrue(isinstance(response, JSONRPC20Response))
        self.assertEqual(response.error["message"], "Server error")
        self.assertEqual(response.error["code"], -32000)
        self.assertEqual(response.error["data"], {
            "type": "KeyError",
            "args": ('error_explanation',),
            "message": "'error_explanation'",
        })