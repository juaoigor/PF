DROP TABLE IF EXISTS Contas;
CREATE TABLE Contas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  Conta TEXT NOT NULL,     /* Nome da Conta */
  RecDes INTEGER, /* 0: RECEITA - 1: DESPESA */
  FixVar INTEGER /* 0: Fixa - 1: Variavel */
  );

INSERT INTO Contas (Conta,RecDes,FixVar) VALUES ("Salario -> Fixo", 0, 0);
INSERT INTO Contas (Conta,RecDes,FixVar) VALUES ("Salario -> Variavel", 0, 1); 

DROP TABLE IF EXISTS Pessoas;
CREATE TABLE Pessoas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  Nome TEXT NOT NULL
  );
INSERT INTO Pessoas (Nome) VALUES ("Juão");
INSERT INTO Pessoas (Nome) VALUES ("Simone");
INSERT INTO Pessoas (Nome) VALUES ("Vicente");

DROP TABLE IF EXISTS Bens;
CREATE TABLE Bens (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  Nome TEXT NOT NULL
  );
INSERT INTO Bens (Nome) VALUES ("Ap GP");
INSERT INTO Bens (Nome) VALUES ("Corolla");
INSERT INTO Bens (Nome) VALUES ("SH150");

DROP TABLE IF EXISTS Despesas;
CREATE TABLE Despesas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  id_conta INTEGER,
  id_cartao INTEGER,
  id_bem INTEGER,
  id_pessoa INTEGER,
  datahora TEXT,
  valor DOUBLE
);