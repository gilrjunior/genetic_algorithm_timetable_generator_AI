class Subject:
    def __init__(self, id, name, teacher, workload, period):
        """
        Inicializa uma disciplina.

        :param id: Identificador único da disciplina
        :param name: Nome da disciplina
        :param teacher: Professor responsável pela disciplina
        :param workload: Carga horária semanal da disciplina em horas
        :param period: Período ao qual a disciplina pertence
        """
        self.id = id
        self.name = name
        self.teacher = teacher
        self.workload = workload
        self.period = period

    def __str__(self):
        return f"{self.name} (Prof. {self.teacher}) - Período {self.period}"

    def __repr__(self):
        return self.__str__() 