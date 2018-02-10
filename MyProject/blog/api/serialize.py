import json
from taggit.models import Tag


def serialize(obj, parameters, msg):
    # 成功时的序列化
    data = {}
    for p in parameters:
        if p == 'cute_name':
            data[p] = obj.profile.cute_name
        elif p == 'tags':
            tags = obj.tags.all()
            t = []
            for tag in tags:
                t.append(str(tag))
            data[p] = t
        else:
            data[p] = str(obj.__dict__[p])
    d = {
        'status': 0,
        'msg': msg,
        'data': data
    }
    return d


def error_handle(msg):
    # 错误时的返回信息
    return {'status': 1, 'msg': msg}
