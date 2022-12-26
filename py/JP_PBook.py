from database import sqlQuery, sqlExec, InsertValues


def findKey(d, s):
    for k, v in d.items():
        if v == s:
            return k


def getPosts(filt):
    # filt = 'USDBRL'
    tags = sqlQuery("SELECT * FROM PBTags ORDER BY Texto")
    tbTags = {}
    for l in tags:
        tbTags[l['id']] = l['Texto']

    tb_rel = sqlQuery("SELECT * FROM PBPostsTags")
    rel = {}
    for l in tb_rel:
        if l['id_post'] not in rel:
            rel[l['id_post']] = []
        rel[l['id_post']].append(l['id_tag'])

    afilt = filt.split(",")
    sfilt = set(list(filter(None, afilt)))
    afilt = list(sfilt)
    print(afilt)

    tb = sqlQuery("SELECT * FROM PBPosts ORDER BY datahora desc")
    res = []
    for l in tb:
        r = {}
        r['id'] = l['id']
        r['datahora'] = l['datahora']
        r['texto'] = l['Texto']
        if len(afilt) == 0:
            res.append(r)
        elif l['id'] not in rel:
            pass
        else:
            # Verifica se a tag esta no filtro
            incl = False
            for f in afilt:
                kid = findKey(tbTags, f)
                if kid in rel[l['id']]:
                    incl = True
            if incl:
                res.append(r)

    return {'Posts': res, 'Tags': tags, 'Rel': rel, 'tbTags': tbTags}
