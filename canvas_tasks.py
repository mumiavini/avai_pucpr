#!/usr/bin/env python3
"""Lista tarefas e prazos do Canvas (Instructure) via API.

Uso:
    export CANVAS_TOKEN="seu_token"
    export CANVAS_URL="https://SUA-INSTITUICAO.instructure.com"
    python canvas_tasks.py              # tarefas pendentes, ordenadas por prazo
    python canvas_tasks.py --all        # inclui tarefas já entregues
    python canvas_tasks.py --csv out.csv

No Windows (PowerShell):
    $env:CANVAS_TOKEN="seu_token"
    $env:CANVAS_URL="https://SUA-INSTITUICAO.instructure.com"

Requer: pip install requests
"""

import argparse
import csv
import os
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests

try:  # usa o repositório de certificados do Windows (proxy corporativo)
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

TZ = ZoneInfo("America/Sao_Paulo")


def load_env(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")):
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def get_session():
    load_env()
    token = os.environ.get("CANVAS_TOKEN")
    base = os.environ.get("CANVAS_URL", "https://pucpr.instructure.com").rstrip("/")
    if not token or not base:
        sys.exit("Defina as variáveis de ambiente CANVAS_TOKEN e CANVAS_URL.")
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {token}"
    return s, base


def get_all(session, url, params=None):
    """Percorre todas as páginas da API (paginação via header Link)."""
    params = dict(params or {})
    params.setdefault("per_page", 100)
    results = []
    while url:
        r = session.get(url, params=params, timeout=30)
        if r.status_code == 401:
            sys.exit("Token inválido, expirado ou revogado (401).")
        r.raise_for_status()
        data = r.json()
        results.extend(data if isinstance(data, list) else [data])
        url = r.links.get("next", {}).get("url")
        params = None  # a URL "next" já carrega os parâmetros
    return results


def parse_dt(value):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(TZ)


def fmt_dt(dt):
    return dt.strftime("%d/%m/%Y %H:%M") if dt else "sem prazo"


def collect(session, base, include_submitted):
    courses = get_all(
        session,
        f"{base}/api/v1/courses",
        {"enrollment_state": "active", "state[]": "available"},
    )
    rows = []
    for c in courses:
        if "name" not in c:  # cursos sem acesso retornam objeto incompleto
            continue
        assignments = get_all(
            session,
            f"{base}/api/v1/courses/{c['id']}/assignments",
            {"include[]": "submission", "order_by": "due_at"},
        )
        for a in assignments:
            sub = a.get("submission") or {}
            submitted = sub.get("workflow_state") in ("submitted", "graded", "pending_review")
            if submitted and not include_submitted:
                continue
            rows.append(
                {
                    "disciplina": c["name"],
                    "tarefa": a["name"],
                    "prazo": parse_dt(a.get("due_at")),
                    "pontos": a.get("points_possible"),
                    "entregue": submitted,
                    "nota": sub.get("score"),
                    "link": a.get("html_url"),
                }
            )
    # prazos mais próximos primeiro; sem prazo vão para o fim
    far = datetime.max.replace(tzinfo=timezone.utc).astimezone(TZ)
    rows.sort(key=lambda r: r["prazo"] or far)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="incluir tarefas já entregues")
    ap.add_argument("--csv", metavar="ARQUIVO", help="exportar para CSV")
    args = ap.parse_args()

    session, base = get_session()
    rows = collect(session, base, args.all)
    now = datetime.now(TZ)

    for r in rows:
        atraso = " [ATRASADA]" if r["prazo"] and r["prazo"] < now and not r["entregue"] else ""
        status = "entregue" if r["entregue"] else "pendente"
        print(f"{fmt_dt(r['prazo'])} | {r['disciplina']} | {r['tarefa']} | {status}{atraso}")

    print(f"\n{len(rows)} tarefa(s).")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["disciplina", "tarefa", "prazo", "pontos", "entregue", "nota", "link"])
            for r in rows:
                w.writerow(
                    [r["disciplina"], r["tarefa"], fmt_dt(r["prazo"]), r["pontos"],
                     r["entregue"], r["nota"], r["link"]]
                )
        print(f"CSV salvo em {args.csv}")


if __name__ == "__main__":
    main()
