import config


def resolve_lookups_in_description(s):
    if not s:
        return s
    db = config.get_database()
    donethat = {}
    while True:
        b = s.find('{{')
        if b < 0:
            break
        e = s.find('}}')
        if e < 0:
            break
        lookup = s[b+2:e]
        # print(lookup)
        parts = lookup.split('.')
        if parts[0] == 'DataDictionary':
            dic_key = parts[1] + '.' + parts[2]
            if dic_key in donethat:
                s = s.replace('{{' + lookup + '}}', '?? ***' + dic_key + ' has been done already ***  ??')
                break
            donethat[dic_key] = "Done"
            # print(donethat)
            try:
                datadic = db.select1('DataDictionary', TableName=parts[1], Attribute=parts[2])
                s = s.replace('{{' + lookup + '}}', datadic.Documentation)
            except:
                s = s.replace('{{' + lookup + '}}', '??' + parts[1] + '.' + parts[2] +
                              ' *** Not Found in DataDictionary *** ??')
        else:
            s = s.replace('{{' + lookup + '}}', '--' + parts[1] + '.' + parts[2] +
                          ' *** Code needed to add link. *** --')
    return s
