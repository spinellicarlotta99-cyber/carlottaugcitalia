#!/usr/bin/env python3
"""Server locale per provare /corso con un finto portale.

Serve la cartella docs/ e risponde al form come farebbe il portale
(POST /public/landing-lead), stampando nel terminale i dati ricevuti.

    python3 scripts/dev-corso.py                 # risposta ok
    python3 scripts/dev-corso.py --mode 400email # email rifiutata dal portale
    python3 scripts/dev-corso.py --mode down     # portale che non risponde

Solo libreria standard: basta Python 3.8+.
"""
import argparse
import functools
import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

DOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")
API = "/public/landing-lead"
MODES = {
    "ok": None,
    "400email": (400, {"statusCode": 400, "message": ["email must be an email"]}),
    "400phone": (400, {"statusCode": 400, "message": ["phone must match regular expression"]}),
    "429": (429, {"statusCode": 429, "message": "Too Many Requests"}),
    "500": (500, {"statusCode": 500, "message": "Internal server error"}),
    "down": None,
}


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # niente cache: ogni ricarica prende l'ultima versione dei file
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        # nel terminale solo i lead e gli errori, non ogni file servito
        if self.command == "POST" or (len(args) > 1 and str(args[1])[:1] in "45"):
            super().log_message(fmt, *args)

    def send_json(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path.split("?")[0] != API:
            return self.send_error(404)
        raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        try:
            body = json.loads(raw or b"{}")
        except ValueError:
            body = {"(non JSON)": raw.decode(errors="replace")}
        mode = self.server.mode
        print("\n=== lead ricevuto (modalità %s) ===\n%s" % (mode, json.dumps(body, indent=2, ensure_ascii=False)), flush=True)
        if mode == "down":
            # chiude la connessione senza rispondere, come un portale irraggiungibile
            self.close_connection = True
            return
        if MODES[mode]:
            return self.send_json(*MODES[mode])
        self.send_json(200, {"slot": 1, "setter": self.server.setter, "whatsapp": self.server.wa})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--mode", choices=sorted(MODES), default="ok", help="come risponde il finto portale")
    ap.add_argument("--setter", default="Setter di prova", help="nome della setter nella risposta")
    ap.add_argument("--wa", default=None, help="WhatsApp della setter (es. 393331234567); vuoto = numero di riserva della pagina")
    a = ap.parse_args()

    srv = ThreadingHTTPServer(("127.0.0.1", a.port), functools.partial(Handler, directory=os.path.normpath(DOCS)))
    srv.mode, srv.setter, srv.wa = a.mode, a.setter, a.wa
    base = "http://localhost:%d/corso/" % a.port
    print("Finto portale in modalità '%s'. Apri:\n" % a.mode)
    print("  flusso veloce   %s?videoID=1&src=adv&api=mock&pct=0.03&end=9999&reset=1" % base)
    print("  flusso reale    %s?videoID=1&src=adv&api=mock&reset=1" % base)
    print("\nI dati del form compaiono qui sotto. Ctrl+C per fermare.", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
