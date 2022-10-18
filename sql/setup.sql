DROP TABLE IF EXISTS Contas;

CREATE TABLE Contas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  Conta TEXT NOT NULL,     /* Nome da Conta */
  RecDes INTEGER, /* 0: RECEITA - 1: DESPESA */
  FixVar INTEGER /* 0: Fixa - 1: Variavel */
  );

INSERT INTO Contas (Conta,RecDes,FixVar) VALUES ("Salario -> Fixo", 0, 0);
INSERT INTO Contas (Conta,RecDes,FixVar) VALUES ("Salario -> Variavel", 0, 1); 
