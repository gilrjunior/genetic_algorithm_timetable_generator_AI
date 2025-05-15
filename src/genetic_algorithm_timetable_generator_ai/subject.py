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
        self.is_empty_slot = False

    @classmethod
    def create_empty_slot(cls, period):
        """
        Cria uma disciplina especial para representar horários vagos.
        """
        empty = cls(0, "VAGO", "N/A", 1, period)
        empty.is_empty_slot = True
        return empty

    def __str__(self):
        if self.is_empty_slot:
            return "VAGO"
        return f"{self.name} (Prof. {self.teacher}) - Período {self.period}"

    def __repr__(self):
        return self.__str__() 