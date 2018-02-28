from django.http import HttpResponseBadRequest


def ajax_required(f):
    def wrap(request):
        if not request.is_ajax():
            return HttpResponseBadRequest
        return f()

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap
