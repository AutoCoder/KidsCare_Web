from django.http import HttpResponse
from datetime import datetime
import os

def hello(request):
    return HttpResponse("Hello world")

def rtthreadaudio(request):
	filename = 'winlogoff.wav'
	f = open(filename)
	data = f.read()
	f.close()
	return HttpResponse(data, content_type='audio/x-wav')
	#response = HttpResponse(content_type='audio/x-wav')
	#response['Content-Disposition'] = 'attachment; filename=winlogoff.wav'  
	#return response

def rtthreadaudiostream(request):
	filename = os.path.join(os.path.dirname(__file__),'winlogoff.wav')
	f = open(filename)
	data = f.read()
	f.close()
	return HttpResponse(data, content_type='audio/x-wav')#application/octet-stream')

def rtthreadaudioattachment(request):
	response = HttpResponse(content_type='audio/x-wav')
	response['Content-Disposition'] = 'attachment; filename=winlogoff.wav' 
	return response

def rtthreadtext(request):  
	ret_msg = {}
	ret_msg['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	return HttpResponse(str(ret_msg), content_type='application/json')