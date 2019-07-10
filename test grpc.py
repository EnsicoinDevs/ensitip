#! /usr/bin/python
import grpc
import node_pb2_grpc as npg
import node_pb2 as np

channel = grpc.insecure_channel("localhost:4225")
stub = npg.NodeStub(channel)

addr = np.Address(ip = "78.248.188.120", port= 4224)
pair = np.Peer(address = addr)

stub.ConnectPeer(np.ConnectPeerRequest(peer = pair))
stub.GetBestBlocks(np.GetBestBlocksRequest())

a = stub.GetInfo(np.GetInfoRequest())
print(a)
#tx = stub.GetTxByHash(np.GetTxByHashRequest())
genesis = a.best_block_hash

print(stub.GetBlockByHash(np.GetBlockByHashRequest(hash=genesis)))
