# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from backend import server_pb2 as backend_dot_server__pb2


class PIServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.getNonce = channel.unary_unary(
                '/PIService/getNonce',
                request_serializer=backend_dot_server__pb2.UserToken.SerializeToString,
                response_deserializer=backend_dot_server__pb2.Nonce.FromString,
                )
        self.requestURL = channel.unary_unary(
                '/PIService/requestURL',
                request_serializer=backend_dot_server__pb2.PaymentInfo.SerializeToString,
                response_deserializer=backend_dot_server__pb2.URL.FromString,
                )
        self.requestConfirmation = channel.unary_unary(
                '/PIService/requestConfirmation',
                request_serializer=backend_dot_server__pb2.UserToken.SerializeToString,
                response_deserializer=backend_dot_server__pb2.Confirmation.FromString,
                )


class PIServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def getNonce(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def requestURL(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def requestConfirmation(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_PIServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'getNonce': grpc.unary_unary_rpc_method_handler(
                    servicer.getNonce,
                    request_deserializer=backend_dot_server__pb2.UserToken.FromString,
                    response_serializer=backend_dot_server__pb2.Nonce.SerializeToString,
            ),
            'requestURL': grpc.unary_unary_rpc_method_handler(
                    servicer.requestURL,
                    request_deserializer=backend_dot_server__pb2.PaymentInfo.FromString,
                    response_serializer=backend_dot_server__pb2.URL.SerializeToString,
            ),
            'requestConfirmation': grpc.unary_unary_rpc_method_handler(
                    servicer.requestConfirmation,
                    request_deserializer=backend_dot_server__pb2.UserToken.FromString,
                    response_serializer=backend_dot_server__pb2.Confirmation.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'PIService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class PIService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def getNonce(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/PIService/getNonce',
            backend_dot_server__pb2.UserToken.SerializeToString,
            backend_dot_server__pb2.Nonce.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def requestURL(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/PIService/requestURL',
            backend_dot_server__pb2.PaymentInfo.SerializeToString,
            backend_dot_server__pb2.URL.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def requestConfirmation(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/PIService/requestConfirmation',
            backend_dot_server__pb2.UserToken.SerializeToString,
            backend_dot_server__pb2.Confirmation.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
