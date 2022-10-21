DROP TABLE IF EXISTS Contas;
CREATE TABLE Contas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  Conta TEXT NOT NULL,     /* Nome da Conta */
  RecDes INTEGER DEFAULT 0, /* 0: RECEITA - 1: DESPESA */
  FixVar INTEGER DEFAULT 0, /* 0: Fixa - 1: Variavel */
  Inv INTEGER DEFAULT 0 /* 0: Nao - 1: Sim */
);

INSERT INTO Contas (Conta,RecDes,FixVar, Inv) VALUES ('Receitas -> Salario -> Fixo', 0, 0, 0);
INSERT INTO Contas (Conta,RecDes,FixVar, Inv) VALUES ('Receitas -> Salario -> Variavel', 0, 1, 0);
INSERT INTO Contas (Conta,RecDes,FixVar, Inv) VALUES ('Investimentos -> Renda -> Investimentos', 0, 0, 1);


DROP TABLE IF EXISTS Pessoas;
CREATE TABLE Pessoas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  Nome TEXT NOT NULL
);
INSERT INTO Pessoas (Nome) VALUES ('#N/A');
INSERT INTO Pessoas (Nome) VALUES ('Juao');
INSERT INTO Pessoas (Nome) VALUES ('Simone');
INSERT INTO Pessoas (Nome) VALUES ('Vicente');

DROP TABLE IF EXISTS Bens;
CREATE TABLE Bens (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  Nome TEXT NOT NULL
);
INSERT INTO Bens (Nome) VALUES ('#N/A');
INSERT INTO Bens (Nome) VALUES ('Ap GP');
INSERT INTO Bens (Nome) VALUES ('Corolla');
INSERT INTO Bens (Nome) VALUES ('SH150');

DROP TABLE IF EXISTS Despesas;
CREATE TABLE Despesas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  id_conta INTEGER,
  id_cartao INTEGER,
  id_bem INTEGER,
  id_pessoa INTEGER,
  datahora TEXT,
  texto TEXT,
  valor DOUBLE
);

DROP TABLE IF EXISTS AutoUpdate;
CREATE TABLE Despesas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  id_conta INTEGER,
  texto TEXT
);

INSERT INTO AutoUpdate (id_conta, texto) value (5,'%IFOOD%DDU%');
INSERT INTO AutoUpdate (id_conta, texto) value (5,'%SODEXO%DDU%');
INSERT INTO AutoUpdate (id_conta, texto) value (5,'%NUTRICAR%DDU%');
INSERT INTO AutoUpdate (id_conta, texto) value (5,'%OLGA RI%');
INSERT INTO AutoUpdate (id_conta, texto) value (5,'%LUGAR 166%');
INSERT INTO AutoUpdate (id_conta, texto) value (9,'%RASCAL%DDF%');
INSERT INTO AutoUpdate (id_conta, texto) value (9,'%SL CAFES DO%');
INSERT INTO AutoUpdate (id_conta, texto) value (9,'%IFOOD%DDF%');
INSERT INTO AutoUpdate (id_conta, texto) value (9,'%OFNER%');
INSERT INTO AutoUpdate (id_conta, texto) value (9,'%TEMPERO DAS GERAIS%');
INSERT INTO AutoUpdate (id_conta, texto) value (9,'%JOAKINS%');
INSERT INTO AutoUpdate (id_conta, texto) value (9,'%BACIO DI LATTE%DDF%');
INSERT INTO AutoUpdate (id_conta, texto) value (9,'%PASTEL%DDF%');
INSERT INTO AutoUpdate (id_conta, texto) value (9,'%PASTEL%DDU%');
INSERT INTO AutoUpdate (id_conta, texto) value (9,'%CUCINA%PIZZARIA%');
INSERT INTO AutoUpdate (id_conta, texto) value (9,'%RASCAL%DDU%');
INSERT INTO AutoUpdate (id_conta, texto) value (9,'%OURO CHOPP DDU%');
INSERT INTO AutoUpdate (id_conta, texto) value (9,'%PAGALECRISBEBIDAS%');
INSERT INTO AutoUpdate (id_conta, texto) value (11,'%SAMS%');
INSERT INTO AutoUpdate (id_conta, texto) value (11,'%PAO DE ACUCAR%');
INSERT INTO AutoUpdate (id_conta, texto) value (11,'%ST%MARCHE%');
INSERT INTO AutoUpdate (id_conta, texto) value (11,'%CARNES%DAYT%');
INSERT INTO AutoUpdate (id_conta, texto) value (11,'%COMPANHIA BRASILEIRA%');
INSERT INTO AutoUpdate (id_conta, texto) value (5,'%NUTRICAR%DDF%');
INSERT INTO AutoUpdate (id_conta, texto) value (5,'%CARREFOUR%');
INSERT INTO AutoUpdate (id_conta, texto) value (5,'%MINUTO PA%');
INSERT INTO AutoUpdate (id_conta, texto) value (7,'%NETFLIX%');
INSERT INTO AutoUpdate (id_conta, texto) value (7,'%APPLE%BILL%');
INSERT INTO AutoUpdate (id_conta, texto) value (7,'%AMAZON%PRIME%');
INSERT INTO AutoUpdate (id_conta, texto) value (7,'%AMAZON%DIGITAL%');
INSERT INTO AutoUpdate (id_conta, texto) value (7,'%NETSERVICOS%');
INSERT INTO AutoUpdate (id_conta, texto) value (7,'%CLAROMVEL%');
INSERT INTO AutoUpdate (id_conta, texto) value (7,'%ENELSPELETROP%');
INSERT INTO AutoUpdate (id_conta, texto) value (7,'%ANUIDADE DIFERENCIAD%');
INSERT INTO AutoUpdate (id_conta, texto) value (7,'%SEGURO CARTAO%');
INSERT INTO AutoUpdate (id_conta, texto) value (16,'%PBKIDS%');
INSERT INTO AutoUpdate (id_conta, texto) value (16,'%RI HAPPY%');
INSERT INTO AutoUpdate (id_conta, texto) value (15,'%FARMA%');
INSERT INTO AutoUpdate (id_conta, texto) value (15,'%DROGA%');
INSERT INTO AutoUpdate (id_conta, texto) value (15,'%DROG%PAULO%');
INSERT INTO AutoUpdate (id_conta, texto) value (12,'%SODIMAC%');
INSERT INTO AutoUpdate (id_conta, texto) value (12,'%WESTWING%');
INSERT INTO AutoUpdate (id_conta, texto) value (12,'%LEROY%');
INSERT INTO AutoUpdate (id_conta, texto) value (12,'%FAST SHOP%');
INSERT INTO AutoUpdate (id_conta, texto) value (12,'%GALERIA9%');
INSERT INTO AutoUpdate (id_conta, texto) value (12,'%LEO MADEIRAS%');
INSERT INTO AutoUpdate (id_conta, texto) value (12,'%WW NOW%');
INSERT INTO AutoUpdate (id_conta, texto) value (12,'%LA CASA DI M%');
INSERT INTO AutoUpdate (id_conta, texto) value (12,'%ELO7%');
INSERT INTO AutoUpdate (id_conta, texto) value (12,'%MOBLY%');
INSERT INTO AutoUpdate (id_conta, texto) value (12,'%HOME DEC%');
INSERT INTO AutoUpdate (id_conta, texto) value (12,'%RCHLO LOJA%');
INSERT INTO AutoUpdate (id_conta, texto) value (12,'%BRASTEMP%');
INSERT INTO AutoUpdate (id_conta, texto) value (12,'%MMARTAN%');
INSERT INTO AutoUpdate (id_conta, texto) value (4,'%UBER%');
INSERT INTO AutoUpdate (id_conta, texto) value (4,'%ESTACIONAMENTO%');
INSERT INTO AutoUpdate (id_conta, texto) value (4,'%ESTAPAR%');
INSERT INTO AutoUpdate (id_conta, texto) value (4,'%AUTO POSTO%');
INSERT INTO AutoUpdate (id_conta, texto) value (10,'%GOL%AEREAS%');
INSERT INTO AutoUpdate (id_conta, texto) value (10,'%TRAVEL PARTNER%');
INSERT INTO AutoUpdate (id_conta, texto) value (10,'%PATACHOCAS%');
INSERT INTO AutoUpdate (id_conta, texto) value (10,'%WINDSOR%');
INSERT INTO AutoUpdate (id_conta, texto) value (10,'%AEROLINEAS%');
INSERT INTO AutoUpdate (id_conta, texto) value (10,'%AG DE TURISMO%');
INSERT INTO AutoUpdate (id_conta, texto) value (10,'%BRITISH AIRWAYS%');
INSERT INTO AutoUpdate (id_conta, texto) value (10,'%PALACIO TANGARA%');
INSERT INTO AutoUpdate (id_conta, texto) value (10,'%BOOKING%');
INSERT INTO AutoUpdate (id_conta, texto) value (9999,'%DEBITO%FATURA%CARTAO%');
INSERT INTO AutoUpdate (id_conta, texto) value (9999,'%DEB%FATURA%EM%');