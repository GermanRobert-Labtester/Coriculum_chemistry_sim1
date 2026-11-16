# -*- coding: utf-8 -*-
"""Task-block renderer: one consistent six-line route for every task."""
from routes import mini, ROUTES
import error_cases

TASKS = {}


def T(tid, src, title, dots, find, route, rkey, calc, answer, check, why,
      note=None, wrong=None, kind='avotā', extra='', assumption=None,
      k=None, mechanism=None, first_error=None, why_parts=None):
    if why_parts:
        if isinstance(why_parts, (list, tuple)) and len(why_parts) == 3:
            why = f'{why_parts[0]} {why_parts[1]} {why_parts[2]}'
            if mechanism is None:
                mechanism = why_parts[0]
        elif isinstance(why_parts, dict):
            why = f"{why_parts.get('route', '')} {why_parts.get('trap', '')} {why_parts.get('boundary', '')}".strip()
            if mechanism is None:
                mechanism = why_parts.get('route')

    mech = mechanism if mechanism is not None else why
    err = first_error if first_error is not None else wrong

    TASKS[tid] = dict(tid=tid, src=src, title=title, dots=dots, find=find,
                      route=route, rkey=rkey, calc=calc, answer=answer,
                      check=check, why=why, note=note, wrong=err,
                      kind=kind, extra=extra, assumption=assumption,
                      k=k, mechanism=mech, first_error=err, why_parts=why_parts)


def render(ids):
    out = []
    for tid in ids:
        t = TASKS[tid]
        anchor = 't-' + tid.lower().replace(' ', '').replace('.', '-').replace('/', '-').replace('*', 's')
        src = t['src']
        k_attr = f' data-k="{t["k"]}"' if t.get('k') else ''
        k_link = f' · <a class="k-link" href="#k-{t["k"].lower()}" title="Skatīt reģistra ierakstu {t["k"]}">Skatīt {t["k"]}</a>' if t.get('k') else ''
        rinfo = ROUTES.get(t['rkey'])
        unit_meta = ''
        if rinfo and rinfo.get('unit_chain'):
            unit_meta = f' <span class="route-unit-note">· Vienību analīze: <span class="route-units">{rinfo["unit_chain"]}</span></span>'

        p = [f'<article class="task" id="{anchor}" data-route="{t["rkey"]}"{k_attr}>',
             '<div class="task-head"><div>',
             f'<p class="task-src"><span class="task-id">{src}</span> · <span class="provenance">{t["kind"]}</span>{k_link}</p>',
             f'<h3>{t["title"]}</h3></div>',
             mini(t['rkey']), '</div>',
             '<dl class="route">',
             f'<div><dt>Dots</dt><dd>{t["dots"]}</dd></div>',
             f'<div><dt>Meklējams</dt><dd>{t["find"]}</dd></div>',
             f'<div><dt>Maršruts</dt><dd>{t["route"]}{unit_meta}</dd></div>',
             *([f'<div><dt>Pieņēmums</dt><dd>{t["assumption"]}</dd></div>'] if t['assumption'] else []),
             f'<div><dt>Aprēķins</dt><dd>{t["calc"]}</dd></div>',
             '</dl>',
             '<div class="role role-verified" data-role="answer"><p class="role-label">Atbilde · pārbaudīta ar programmu</p>',
             f'<p>{t["answer"]}</p></div>',
             f'<p class="answer-check"><strong>Pārbaude.</strong> <sup class="sig-link"><a href="#n16g" title="Zīmīgo ciparu un noapaļošanas līgums">§16.g</a></sup> {t["check"]}</p>',
             f'<p class="why"><strong>Kāpēc šādi.</strong> {t["why"]}</p>']
        if t['extra']:
            p.append(t['extra'])
        if t['note']:
            lab, txt = t['note']
            p.append(f'<div class="source-note" data-role="source"><p class="source-note-label">Piezīme avotam</p><p>{txt}</p></div>')
        if t['wrong']:
            p.append('<div class="role role-mistake" data-role="mistake"><p class="role-label">Biežākā kļūda</p>' + t['wrong'] + '</div>')
        if t['tid'] in error_cases.CASES:
            p.append(error_cases.render(t['tid']))
        p.append('</article>')
        out.append('\n'.join(p))
    return '\n'.join(out)


def render_ids(ids):
    return render(ids)
