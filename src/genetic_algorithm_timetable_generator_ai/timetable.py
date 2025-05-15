import numpy as np
from .subject import Subject

class Timetable:
    def __init__(self, num_periods=6, num_days=5, num_slots=4):
        """
        Inicializa uma grade horária vazia.
        
        :param num_periods: Número de períodos
        :param num_days: Número de dias na semana
        :param num_slots: Número de aulas por dia
        """
        self.num_periods = num_periods
        self.num_days = num_days
        self.num_slots = num_slots
        self.total_slots = num_days * num_slots
        self.schedule = np.zeros((num_periods, self.total_slots), dtype=int)
        
    def get_subject_at(self, period, day, slot):
        """
        Retorna a disciplina em um determinado horário.
        """
        slot_index = self._get_slot_index(day, slot)
        return self.schedule[period, slot_index]
    
    def set_subject_at(self, period, day, slot, subject_id):
        """
        Define uma disciplina em um determinado horário.
        """
        slot_index = self._get_slot_index(day, slot)
        self.schedule[period, slot_index] = subject_id
    
    def _get_slot_index(self, day, slot):
        """
        Converte dia e horário em índice de slot.
        """
        return day * self.num_slots + slot
    
    def _get_day_and_slot(self, slot_index):
        """
        Converte índice de slot em dia e horário.
        """
        day = slot_index // self.num_slots
        slot = slot_index % self.num_slots
        return day, slot
    
    def get_period_schedule(self, period):
        """
        Retorna a grade horária de um período específico.
        """
        return self.schedule[period]
    
    def is_slot_empty(self, period, day, slot):
        """
        Verifica se um horário está vago.
        """
        return self.get_subject_at(period, day, slot) == 0
    
    def count_empty_slots(self, period):
        """
        Conta quantos horários vazios existem em um período.
        """
        return np.sum(self.schedule[period] == 0)
    
    def __str__(self):
        """
        Retorna uma representação em string da grade horária.
        """
        days = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
        slots = ["1º", "2º", "3º", "4º"]
        
        result = []
        for period in range(self.num_periods):
            result.append(f"\nPeríodo {period + 1}:")
            result.append("Horário | " + " | ".join(days))
            result.append("-" * 50)
            
            for slot in range(self.num_slots):
                row = [f"{slots[slot]}"]
                for day in range(self.num_days):
                    subject_id = self.get_subject_at(period, day, slot)
                    row.append(f"{subject_id:^8}")
                result.append(" | ".join(row))
        
        return "\n".join(result) 