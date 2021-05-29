
from concurrent import futures
from grpcprotos import miniproject3_pb2 as mppb2
from grpcprotos import miniproject3_pb2_grpc as mpgrpc
import logging
import grpc
import random
import pika
import io, urllib.request
import os
import posixpath
import json
import threading
try:
    from urlparse import urlsplit
    from urllib import unquote
except ImportError: # Python 3
    from urllib.parse import urlsplit, unquote

class MiniProjectService(mpgrpc.MiniProjectServiceServicer):

    def Download(self, request, context):
        unique_id = str(random.randint(0,999999))
        url = request.url
        download_thread = threading.Thread(
            target=download, 
            args=(url, unique_id))
        download_thread.start()

        return mppb2.DownloadResponse(url=url,uniq_id=unique_id)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mpgrpc.add_MiniProjectServiceServicer_to_server(MiniProjectService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

def getfilename(url):
    urlpath = urlsplit(url).path
    basename = posixpath.basename(unquote(urlpath))
    if (os.path.basename(basename) != basename or
        unquote(posixpath.basename(urlpath)) != basename):
        raise ValueError  # reject '%2f' or 'dir%5Cbasename.ext' on Windows
    return basename

def download(Url, unique_id):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    exchangemq = "1706024513"
    routing_key = str(unique_id)
    print("Routing key: " + routing_key)
    channel.exchange_declare(exchange=exchangemq, exchange_type='direct', durable=True)

    with urllib.request.urlopen(Url) as Response:
        Length = Response.getheader('content-length')
        BlockSize = 1000000  # default value
        name = getfilename(Url)

        if Length:
            Length = int(Length)
            BlockSize = max(4096, Length // 20)

        print("UrlLib len, blocksize: ", Length, BlockSize)

        BufferAll = io.BytesIO()
        Size = 0

        with open("media/" +name, "wb") as filewritten:
            while True:
                BufferNow = Response.read(BlockSize)
                if not BufferNow:
                    break
                BufferAll.write(BufferNow)
                filewritten.write(BufferNow)
                Size += len(BufferNow)
                
                if Length:
                    Percent = int((Size / Length)*100)
                    message = {
                        "percent" : Percent,
                        "size_progress" : Size,
                        "total_size" : Length
                    }

                    channel.basic_publish(exchange=exchangemq,
                                        routing_key=routing_key,
                                        body=json.dumps(message))
                    # print(f"download: {Percent}% {Url}")
        message["urldownload"] = "http://localhost:5001/media/" + name 


        channel.basic_publish(exchange=exchangemq,
                            routing_key=routing_key,
                            body=json.dumps(message))

        print("Buffer All len:", len(BufferAll.getvalue()))

if __name__ == '__main__':
    logging.basicConfig()
    serve()