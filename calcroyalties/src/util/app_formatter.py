#!/bin/env python3
#'mprod,250,.02,300,.03,400,.04,500,.05,0,.06')
import locale

def format_gorr(gorr):
    locale.setlocale( locale.LC_ALL, '' )
    if not gorr:
        return ''
    words = gorr.split(",")
    start_vol = '0.0'
    i = 0
    msg = 'Based On: '
    for w in words:
        i += 1
        if i == 1:
            if w == 'dprod':
                msg += 'Daily Prod;'
            elif w == 'mprod':
                msg += 'Monthly Prod;'
            elif w == 'rev':
                msg += 'Revenue;'
            elif w[:2] == '=(':
                msg += w + ";"
            else:
                msg += 'GORR:"' + w + '" not known;'
        elif i % 2 == 0:
            if w == '0':
                w = 'max'
                msg += ' (>' + start_vol
            else:
                msg += ' (<=' + w
                # msg += ' (' + start_vol + '-' + w
            start_vol = w
        else:
            if w[1:2] is not '=':
                if w[:1] == '%':
                    v = '{:.1%}'.format(float(w[1:]))
                elif w[:1] == '$':
                    v = locale.currency(float(w[1:]), grouping=True)
                    # v = '${:,.{2}f}'.format(float(w[1:]))
                else:
                    v = w
                msg += ': ' + v + ');'
            else:
                msg += ': ' + w + ');'
            # msg += ': ' + '{:.1%}'.format(float(w)) + ')'
            # msg += ':' + w + '%)'


    return msg
