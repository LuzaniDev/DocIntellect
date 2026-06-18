#!/usr/bin/env python3
"""Runner do DocIntellect RPA: sobe API + UI com um comando."""

import argparse
import os
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser(description="DocIntellect RPA")
    parser.add_argument("--api-host", default="127.0.0.1", help="Host da API (default: 127.0.0.1)")
    parser.add_argument("--api-port", type=int, default=8000, help="Porta da API (default: 8000)")
    parser.add_argument("--ui-port", type=int, default=8501, help="Porta da UI (default: 8501)")
    parser.add_argument("--reload", action="store_true", help="Auto-reload da API")
    parser.add_argument("--no-ui", action="store_true", help="Nao inicia a interface grafica")
    parser.add_argument("--no-api", action="store_true", help="Nao inicia a API")
    args = parser.parse_args()

    os.environ.setdefault("APP_NAME", "docintellect-rpa")
    os.environ["API_URL"] = f"http://{args.api_host}:{args.api_port}"

    procs = []

    if not args.no_api:
        print(f"  Iniciando API em http://{args.api_host}:{args.api_port}")
        api_cmd = [sys.executable, "-m", "uvicorn", "app.api.main:app",
                   "--host", str(args.api_host), "--port", str(args.api_port),
                   "--log-level", "info"]
        if args.reload:
            api_cmd.append("--reload")
        procs.append(subprocess.Popen(api_cmd))

    if not args.no_ui:
        print(f"  Iniciando UI em http://127.0.0.1:{args.ui_port}")
        ui_cmd = [sys.executable, "-m", "streamlit", "run", "app/ui/app.py",
                  "--server.port", str(args.ui_port),
                  "--server.headless", "true",
                  "--server.runOnSave", "false"]
        procs.append(subprocess.Popen(ui_cmd))

    if not procs:
        print("  Nada a iniciar. Use --no-api e/ou --no-ui para desligar componentes.")
        return

    time.sleep(2)
    print()
    print(f"  API: http://{args.api_host}:{args.api_port}  |  Swagger: http://{args.api_host}:{args.api_port}/docs")
    if not args.no_ui:
        print(f"  UI:  http://127.0.0.1:{args.ui_port}")
    print()
    print("  Pressione Ctrl+C para parar tudo.")

    try:
        for p in procs:
            p.wait()
    except KeyboardInterrupt:
        print("\n  Parando...")
        for p in procs:
            p.terminate()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
        print("  Finalizado.")


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
