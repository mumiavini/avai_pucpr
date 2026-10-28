"""Gera um .ics com o cronograma (schedule_data.py) e os prazos do Canvas."""
import hashlib
import re
import sys
from datetime import date, datetime, timedelta, timezone

sys.stdout.reconfigure(encoding="utf-8")
import canvas_tasks as ct

try:
    from schedule_data import CAL_NAME, EV, Y, class_time, utc
except ImportError:
    sys.exit("Crie schedule_data.py a partir de schedule_data.example.py.")

OUT = "faculdade.ics"


def esc(t):
    return t.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def fold(line):
    b = line.encode("utf-8")
    out, first = [], True
    while len(b) > 73:
        cut = 73 if first else 72
        while (b[cut] & 0xC0) == 0x80:
            cut -= 1
        out.append(b[:cut].decode("utf-8"))
        b, first = b[cut:], False
    out.append(b.decode("utf-8"))
    return "\r\n ".join(out)


def uid(*a):
    return hashlib.md5("|".join(map(str, a)).encode()).hexdigest() + "@canvas"


def alarm(txt, days):
    return ["BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{esc(txt)}", f"TRIGGER:-P{days}D", "END:VALARM"]


s, base = ct.get_session()
DL = []
for r in ct.collect(s, base, True):
    p = r["prazo"]
    if not p or p.date() < date(Y, 7, 20):
        continue
    disc = re.split(r" \(Turma| - Engenharia| \| ", r["disciplina"])[0].strip()
    DL.append((p, disc, r["tarefa"].strip(), r["entregue"], r["link"]))

PFX = {"aula": "", "prova": "PROVA: ", "entrega": "ENTREGA: ", "aviso": ""}
now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
L = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Canvas//PT-BR//", "CALSCALE:GREGORIAN",
     f"X-WR-CALNAME:{CAL_NAME}", "X-WR-TIMEZONE:America/Sao_Paulo"]

for dt, disc, txt, kind, note in sorted(EV, key=lambda e: e[0]):
    tm = class_time(dt, disc, txt) if kind in ("aula", "prova") else None
    if tm:
        ds_ = [f"DTSTART:{utc(dt, tm[0])}", f"DTEND:{utc(dt, tm[1])}"]
    else:
        ds_ = [f"DTSTART;VALUE=DATE:{dt:%Y%m%d}", f"DTEND;VALUE=DATE:{dt + timedelta(days=1):%Y%m%d}"]
    L += ["BEGIN:VEVENT", f"UID:{uid('pe', dt, disc, txt)}", f"DTSTAMP:{now}", *ds_,
          f"SUMMARY:{esc(PFX[kind] + '[' + disc + '] ' + txt)}", f"DESCRIPTION:{esc(note)}"]
    if kind in ("prova", "entrega"):
        L += alarm(f"{disc}: {txt}", 1)
    L.append("END:VEVENT")

for p, disc, t, done, link in DL:
    u = p.astimezone(timezone.utc)
    st = u - timedelta(minutes=30)
    L += ["BEGIN:VEVENT", f"UID:{uid('cv', disc, t, p)}", f"DTSTAMP:{now}",
          f"DTSTART:{st:%Y%m%dT%H%M%SZ}", f"DTEND:{u:%Y%m%dT%H%M%SZ}",
          f"SUMMARY:{esc('PRAZO' + (' (entregue)' if done else '') + ': [' + disc + '] ' + t)}",
          f"DESCRIPTION:{esc('Prazo no Canvas. ' + (link or ''))}"]
    if not done:
        L += alarm(f"Prazo: {t}", 1)
    L.append("END:VEVENT")

L.append("END:VCALENDAR")
open(OUT, "w", encoding="utf-8", newline="").write("\r\n".join(fold(x) for x in L) + "\r\n")
print(len(EV), "eventos do cronograma;", len(DL), "prazos do Canvas ->", OUT)
