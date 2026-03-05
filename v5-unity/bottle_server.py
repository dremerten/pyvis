# Lightweight OPT server that works on both Python 2 and 3

# NOTE that this is meant only for testing and not deployment, since
# there is no sandboxing

# to invoke, run 'python bottle_server.py'
# and visit http://localhost:8080/index.html
#
# external dependencies: bottle
#
# easy_install pip
# pip install bottle

# Python 3.14 compatibility shims for legacy Bottle
import inspect
import collections
import collections.abc
from collections import namedtuple
if not hasattr(inspect, 'getargspec'):
    def _getargspec(func):
        sig = inspect.signature(func)
        args = [p.name for p in sig.parameters.values()
                if p.kind in (inspect.Parameter.POSITIONAL_ONLY,
                              inspect.Parameter.POSITIONAL_OR_KEYWORD)]
        varargs = next((p.name for p in sig.parameters.values()
                        if p.kind == inspect.Parameter.VAR_POSITIONAL), None)
        varkw = next((p.name for p in sig.parameters.values()
                      if p.kind == inspect.Parameter.VAR_KEYWORD), None)
        defaults_list = [p.default for p in sig.parameters.values()
                         if p.kind in (inspect.Parameter.POSITIONAL_ONLY,
                                       inspect.Parameter.POSITIONAL_OR_KEYWORD)
                         and p.default is not inspect._empty]
        defaults = tuple(defaults_list) if defaults_list else None
        return namedtuple('ArgSpec', 'args varargs keywords defaults')(args, varargs, varkw, defaults)
    inspect.getargspec = _getargspec

# collections ABCs moved to collections.abc in modern Python
for _name in ("MutableMapping", "Mapping", "MutableSet", "MutableSequence", "Iterable"):
    if not hasattr(collections, _name):
        setattr(collections, _name, getattr(collections.abc, _name))

from bottle import route, get, request, run, template, static_file
try:
    import StringIO # NB: don't use cStringIO since it doesn't support unicode!!!
except:
    import io as StringIO # py3
import json
import pg_logger
import os


@route('/web_exec_<name:re:.+>.py')
@route('/LIVE_exec_<name:re:.+>.py')
@route('/viz_interaction.py')
@route('/syntax_err_survey.py')
@route('/runtime_err_survey.py')
@route('/eureka_survey.py')
@route('/error_log.py')
@route('/v5-unity/web_exec_<name:re:.+>.py')
@route('/v5-unity/LIVE_exec_<name:re:.+>.py')
@route('/v5-unity/viz_interaction.py')
@route('/v5-unity/syntax_err_survey.py')
@route('/v5-unity/runtime_err_survey.py')
@route('/v5-unity/eureka_survey.py')
@route('/v5-unity/error_log.py')
def dummy_ok(name=None):
    return 'OK'

@route('/<filepath:path>')
def index(filepath):
    return static_file(filepath, root='.')

@route('/v5-unity/<filepath:path>')
def index_prefixed(filepath):
    return static_file(filepath, root='./v5-unity')


# Note that this will run either Python 2 or 3, depending on which
# version of Python you used to start the server, REGARDLESS of which
# route was taken:
@route('/web_exec_py2.py')
@route('/web_exec_py3.py')
@route('/LIVE_exec_py2.py')
@route('/LIVE_exec_py3.py')
@route('/v5-unity/web_exec_py2.py')
@route('/v5-unity/web_exec_py3.py')
@route('/v5-unity/LIVE_exec_py2.py')
@route('/v5-unity/LIVE_exec_py3.py')
def get_py_exec():
  out_s = StringIO.StringIO()

  def json_finalizer(input_code, output_trace):
    ret = dict(code=input_code, trace=output_trace)
    json_output = json.dumps(ret, indent=None)
    out_s.write(json_output)

  options = json.loads(request.query.options_json)

  pg_logger.exec_script_str_local(request.query.user_script,
                                  request.query.raw_input_json,
                                  options['cumulative_mode'],
                                  options['heap_primitives'],
                                  json_finalizer)

  return out_s.getvalue()


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    run(host=host, port=port, reloader=True)
