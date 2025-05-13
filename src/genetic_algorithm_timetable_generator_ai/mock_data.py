from .subject import Subject

# Lista de disciplinas mockadas
subjects = [
    # Período 1
    Subject(1, "Algoritmos", "Ernani Borges", 8, 1),
    Subject(2, "F. WEB Design", "Marco Maciel", 2, 1),
    Subject(3, "Matemática", "Jorge", 6, 1),
    Subject(4, "Extensão 1", "Aline", 1, 1),
    Subject(5, "Arquitetura", "Rogélio", 3, 1),
    
    # Período 2
    Subject(6, "Lógica", "Marcelo Barreiro", 3, 2),
    Subject(7, "E.D.", "Alexandre", 6, 2),
    Subject(8, "Mod. B.D.", "Camilo", 2, 2),
    Subject(9, "S.O.", "Gustavo Bota", 4, 2),
    Subject(10, "Extensão 2", "Rogélio", 1, 2),
    Subject(11, "Script Web", "Aline", 2, 2),
    
    # Período 3
    Subject(12, "P.O.O.", "Eduardo Silvestre", 6, 3),
    Subject(13, "Extensão 3", "Camilo", 1, 3),
    Subject(14, "P.O.", "Hugo", 5, 3),
    Subject(15, "B.D.", "Rogério Costa", 6, 3),
    Subject(16, "Interface", "Lídia", 2, 3),
    
    # Período 4
    Subject(17, "P.D.M.", "Jefferson", 8, 4),
    Subject(18, "D.A.W. 1", "Rafael Godoy", 4, 4),
    Subject(19, "ESOF", "Rogério", 4, 4),
    Subject(20, "Redes", "Frederico", 4, 4),
    
    # Período 5
    Subject(21, "LabESOF", "Mauro", 6, 5),
    Subject(22, "P.P.", "Marco Maciel", 2, 5),
    Subject(23, "DAW 2", "Lídia", 4, 5),
    Subject(24, "Probabilidade", "Alef", 2, 5),
    Subject(25, "Ética", "Ana Lúcia", 2, 5),
    Subject(26, "Implant Servidores", "Gustavo Bota", 4, 5),
    
    # Período 6
    Subject(27, "GeProj", "Marco Maciel", 4, 6),
    Subject(28, "Seg. Info", "Elson", 4, 6),
    Subject(29, "Extensão 6", "Ademir", 2, 6),
    Subject(30, "Empreend.", "Ana Lúcia", 2, 6),
    Subject(31, "Ciência de Dados", "Marcelo Barreiro", 4, 6),
    Subject(32, "Intel. Comput.", "José Ricardo", 4, 6),
]

# Mapeamento de períodos para disciplinas
period_subjects = {
    1: [subject.id for subject in subjects if subject.period == 1],
    2: [subject.id for subject in subjects if subject.period == 2],
    3: [subject.id for subject in subjects if subject.period == 3],
    4: [subject.id for subject in subjects if subject.period == 4],
    5: [subject.id for subject in subjects if subject.period == 5],
    6: [subject.id for subject in subjects if subject.period == 6],
} 


if __name__ == "__main__":
    print(period_subjects)
