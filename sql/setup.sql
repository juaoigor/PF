DROP TABLE IF EXISTS Contas;
CREATE TABLE Contas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  Conta TEXT NOT NULL,     /* Nome da Conta */
  RecDes INTEGER DEFAULT 0, /* 0: RECEITA - 1: DESPESA */
  FixVar INTEGER DEFAULT 0, /* 0: Fixa - 1: Variavel */
  Inv INTEGER DEFAULT 0, /* 0: Nao - 1: Sim */
  Saldo INTEGER DEFAULT 0 /* 0: Nao - 1: Sim */
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
  id_transfer INTEGER,
  datahora TEXT,
  texto TEXT,
  valor DOUBLE
);

DROP TABLE IF EXISTS Saldos;
CREATE TABLE Saldos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  id_conta INTEGER,
  datahora TEXT,
  valor DOUBLE
);

DROP TABLE IF EXISTS AutoUpdate;
CREATE TABLE AutoUpdate (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  id_conta INTEGER,
  texto TEXT
);

DROP TABLE IF EXISTS Transfers;
CREATE TABLE Transfers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  id_conta_de INTEGER,
  id_conta_para INTEGER,
  dia INTEGER,
  texto TEXT
);


