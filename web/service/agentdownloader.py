
from concurrent import futures
from grpcprotos import miniproject3_pb2 as mppb2
from grpcprotos import miniproject3_pb2_grpc as mpgrpc
import logging
import traceback
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

import requests

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


    try:
        r = requests.get(Url, stream=True)
        name = getfilename(Url)
        path = 'media/' + name
        with open(path, 'wb') as f:
            total_length = int(r.headers.get('content-length'))
            print ("Total length: " + str(total_length))
            size_progress = 0
            print ("Progress: " + str(size_progress))
            chunk_size = 2048
            for chunk in r.iter_content(chunk_size=chunk_size): 
                if chunk:
                    size_progress += chunk_size
                    Percent = int((size_progress / total_length)*100)
                    message = {
                        "percent" : Percent,
                        "size_progress" : size_progress,
                        "total_size" : total_length
                    }

                    channel.basic_publish(exchange=exchangemq,
                                        routing_key=routing_key,
                                        body=json.dumps(message))
                    f.write(chunk)
                    f.flush()
            
            message["endpointdownload"] = "/media/" + name 
            channel.basic_publish(exchange=exchangemq,
                                routing_key=routing_key,
                                body=json.dumps(message))

    except Exception as e:
        message = {}
        message["error"] =  traceback.format_exc()
        print("Error: ")
        print(message["error"])

        channel.basic_publish(exchange=exchangemq,
                            routing_key=routing_key,
                            body=json.dumps(message))

if __name__ == '__main__':
    logging.basicConfig()
    serve()