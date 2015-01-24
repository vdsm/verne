from verne.web import comment


def application(env, start_response):
    path = env['PATH_INFO'].rstrip('/')
    if path == '/cgi-bin/comment':
        return comment.wsgi(env, start_response)
    start_response('404 not found', [('Content-Type','text/html')])
    return ["Not found"]

