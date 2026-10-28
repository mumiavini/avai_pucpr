"""Modelo de schedule_data.py. Copie para schedule_data.py (ignorado pelo git) e preencha."""
from datetime import date, datetime, timedelta

Y = 2026
CAL_NAME = "Faculdade 2026/2"
# (data, disciplina, descrição, tipo, nota); tipo: aula | prova | entrega | aviso
EV = []


def d(s):  # "dia/mês" -> date
    day, mon = s.split("/")
    return date(Y, int(mon), int(day))


def add(ds, disc, txt, kind="aula", note="Fonte: Plano de Ensino"):
    EV.append((d(ds), disc, txt, kind, note))


EX = "Disciplina Exemplo"
add("3/8", EX, "Apresentação do plano de ensino")
add("28/9", EX, "Avaliação 1", "prova")
add("16/10", EX, "TDE 1 (prazo)", "entrega")

# horários de aula (início, fim) em BRT; disciplinas sem horário viram eventos de dia inteiro
TIMES = {EX: ((18, 15), (19, 45))}


def class_time(dt, disc, txt):
    return TIMES.get(disc)


def utc(dt, hm):  # BRT (UTC-3) -> UTC
    return (datetime(dt.year, dt.month, dt.day, *hm) + timedelta(hours=3)).strftime("%Y%m%dT%H%M%SZ")
