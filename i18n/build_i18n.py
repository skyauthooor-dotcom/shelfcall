# -*- coding: utf-8 -*-
"""Write the Russian dictionary in i18n/ru.py into the master.

    python3 i18n/build_i18n.py

Replaces ONLY the contents of the two tables inside
prototype/shelfcall-all-roles.html:

    var RU_X = { ... };          <- EXACT
    var RU_P = [ ... ].map(...)  <- PATTERNS

Everything around them (RU_SUB, the plural rule, the text-node walker, the
Armenian table) is code and stays as written in the master. An earlier version
of this script regenerated the whole i18n block from a template, which would
now delete RU_SUB and everything added to the block since.

Idempotent: run it as often as you like. Then run build/build.py to rebuild
the site.
"""
import importlib.util, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MASTER = os.path.join(ROOT, 'prototype', 'shelfcall-all-roles.html')

spec = importlib.util.spec_from_file_location('ru', os.path.join(HERE, 'ru.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def js(s):
    return json.dumps(s, ensure_ascii=False)


exact = '\n' + ',\n'.join('      %s:%s' % (js(k), js(v)) for k, v in m.EXACT.items())
pats = '\n' + ',\n'.join('      [%s,%s]' % (js(rx), js(rep)) for rx, rep in m.PATTERNS)

with open(MASTER, encoding='utf-8') as f:
    src = f.read()


def splice(src, start, end, body, label):
    i = src.find(start)
    if i < 0:
        sys.exit('build_i18n.py: could not find %r in the master' % start)
    i += len(start)
    j = src.find(end, i)
    if j < 0:
        sys.exit('build_i18n.py: could not find the end of the %s table' % label)
    return src[:i] + body + src[j:]


src = splice(src, '  var RU_X = {', '\n  };', exact, 'RU_X')
src = splice(src, '  var RU_P = [', '\n  ].map(', pats, 'RU_P')

with open(MASTER, 'w', encoding='utf-8', newline='\n') as f:
    f.write(src)
print('spliced: %d exact, %d patterns' % (len(m.EXACT), len(m.PATTERNS)))
