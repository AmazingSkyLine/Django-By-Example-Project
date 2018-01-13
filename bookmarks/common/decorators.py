from django.http import HttpResponseBadRequest


def ajax_required(f):
    # *args表示任何多个无名参数，它是一个tuple；**kwargs表示关键字参数，它是一个dict
    # 并且同时使用*args和**kwargs时，必须*args参数列要在**kwargs前
    def wrap(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()
        return f(request, *args, **kwargs)
    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap