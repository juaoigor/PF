from datetime import datetime

def despProcessarTexto(s):
  r = []
  i = 1
  for l in s.split("$"):
    a = l.split("#")
    if len(a) == 3:
      r.append({'Data': a[0], 'Texto': a[1], 'Valor': a[2], 'ID': i })
      i = i + 1
  return r


def str2date(s, fmt):
  return datetime.strptime(s, fmt)

def date2str(d, fmt):
  return d.strftime(fmt)



def MontaTabelaResumo(mes,ano):

  from database import sqlQuery

  r = sqlQuery("SELECT t1.datahora, t1.texto, t1.valor, t2.conta FROM Despesas t1, Contas t2 where t1.id_conta = t2.id and cast(strftime('%Y', t1.datahora) as integer) = {} and cast(strftime('%m', t1.datahora) as integer) = {} order by t1.datahora, t2.conta".format(ano,mes))
  t = 0
  i = 0
  for l in r:
    t = t + l['valor']
    r[i]['total'] = t
    i = i + 1


  res = {}
  res['detalhe'] = r

  return res
