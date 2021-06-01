from django.shortcuts import render
from django.http import HttpResponse

import grpc
import pika
import threading
import concurrent.futures

from .grpcprotos import miniproject3_pb2 as mppb2
from .grpcprotos import miniproject3_pb2_grpc as mpgrpc

def index(request):
    if request.method == 'POST':
        
        print(request.POST["url_text"])
        url_text = request.POST["url_text"]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(processdownload, url_text)
            uniq_id = future.result()
            return HttpResponse(uniq_id)
        
        return HttpResponse(response.uniq_id)
    return render(request, "index.html")

def processdownload(url_text):
    channel = grpc.insecure_channel('localhost:50051')
    stub = mpgrpc.MiniProjectServiceStub(channel)
    response = stub.Download(mppb2.DownloadRequest(url=url_text))
    print("Response Process Download: " + response.uniq_id)
    return response.uniq_id

