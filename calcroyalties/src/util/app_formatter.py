#!/bin/env python3
#'mprod,250,.02,300,.03,400,.04,500,.05,0,.06')

def format_gorr(gorr):
    if not gorr:
        return ''
    words = gorr.split(",")
    start_vol = '0.0'
    i = 0
    for w in words:
        i += 1
        if i == 1:
            if w == 'dprod':
                msg = 'Daily Prod:'
            elif w == 'mprod':
                msg = 'Monthly Prod:'
            elif w == 'rev':
                msg = 'Revenue:'
            elif w[:2] == '=(':
                msg = w + ":"
            else:
                msg = 'GORR:"' + w + '" not known'
        elif i % 2 == 0:
            if w == '0':
                w = 'max'
                msg += '(>' + start_vol
            else:
                msg += ' (<=' + w
                # msg += ' (' + start_vol + '-' + w
            start_vol = w
        else:
            msg += ': ' + '{:.1%}'.format(float(w)) + ')'
            # msg += ':' + w + '%)'


    return msg
