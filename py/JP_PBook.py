from database import sqlQuery, sqlExec, InsertValues


def getPosts():
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

    tb = sqlQuery("SELECT * FROM PBPosts ORDER BY datahora desc")
    res = []
    for l in tb:
        r = {}
        r['id'] = l['id']
        r['datahora'] = l['datahora']
        r['texto'] = l['Texto']

        res.append(r)

    return {'Posts': res, 'Tags': tags, 'Rel': rel, 'tbTags': tbTags}
