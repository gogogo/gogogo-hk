from ragendja.template import render_to_response

def server_error(request, *args, **kwargs):
    return render_to_response(request, '500.html')
