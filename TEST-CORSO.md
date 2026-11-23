# Provare /corso in locale

La pagina `docs/corso/` mostra la VSL da Bunny in base a `?videoID=`. A metà video la ferma e chiede email, nome e telefono per mandare un regalo. Poi invia il lead al portale e sblocca WhatsApp con il numero della setter. Il form completo, con le 4 domande, si apre da "Richiedi la call gratuita".

Guida passo passo per chi non programma (VS Code + Claude Code): https://carlottaugcitalia.com/prova-corso/

Per provare tutto senza toccare il portale vero c'è `scripts/dev-corso.py`. Lo script serve il sito e fa finta di essere il portale: risponde al form e stampa nel terminale i dati ricevuti. Serve solo Python 3.8+, senza `npm install` e senza backend.

## Avvio

```bash
python3 scripts/dev-corso.py
```

Poi apri il link "flusso veloce" che compare nel terminale:

```
http://localhost:8080/corso/?videoID=1&src=adv&api=mock&pct=0.03&end=9999&reset=1
```

## Parametri dell'URL (valgono solo su localhost)

| Parametro | Cosa fa |
|---|---|
| `videoID=1` / `2` / `3` | quale VSL di Bunny mostrare (come dagli annunci) |
| `src=adv` | provenienza, arriva nel lead |
| `api=mock` | manda il form al finto portale dello script. Senza questo parametro va al portale **vero** e crea lead reali |
| `api=http://localhost:3000/public/landing-lead` | usa un backend Nest in locale, che deve avere `http://localhost:8080` in `FRONTEND_URL` |
| `pct=0.03` | ferma il video al 3% invece che al 50% |
| `end=9999` | mostra "Pronta a fare il level up?" subito dopo il regalo. Il valore normale è 20 secondi dalla fine |
| `reset=1` | dimentica il lead salvato nel browser, così il blocco ricompare |
| `pixel=1` | accende il Meta Pixel, che in locale è spento |

## Cosa controllare

1. Premi play: parte la VSL del `videoID` scelto.
2. Al 3% il video si ferma e sopra compare il regalo. Prova a mandare un'email sbagliata: deve comparire l'errore.
3. Email → **Richiedi** → nome → **Invia** → telefono → **Invia**.
4. Nel terminale compare il lead con `video`, `src`, `phone` in formato `+39…`, `pageUrl` ed `eventId`.
5. Il video riparte da dove si era fermato e sotto il video compare "Pronta a fare il level up?".
6. "Scrivici su WhatsApp" apre `wa.me/<numero>` con il nome nel messaggio. **Non inviare il messaggio**: il numero di riserva è vero.
7. "Richiedi la call gratuita" apre il form completo con nome, email e telefono già compilati. Rispondi alle 4 domande e invia: compare "Richiesta inviata" e nel terminale arriva il secondo lead con le risposte.
8. Ricarica senza `reset=1`: il video non si blocca più e il blocco finale è già aperto.
9. Prova il tasto play senza `videoID` e con `videoID=9`: parte il video 1.

## Simulare i problemi del portale

Ferma lo script con Ctrl+C e riavvialo con `--mode`:

```bash
python3 scripts/dev-corso.py --mode 400email   # email rifiutata: il regalo torna al primo passo con l'errore
python3 scripts/dev-corso.py --mode 400phone   # telefono rifiutato: torna al terzo passo
python3 scripts/dev-corso.py --mode 429        # troppe richieste: il video riparte e WhatsApp va al numero di riserva
python3 scripts/dev-corso.py --mode down       # portale irraggiungibile: come sopra
python3 scripts/dev-corso.py --wa 393331234567 --setter Anna   # risposta con il WhatsApp della setter
```

Dopo ogni prova riapri l'URL con `reset=1`.

## Da sapere

- Il video arriva da Bunny: `localhost` deve essere tra gli "Allowed domains" della libreria Bunny Stream, altrimenti il player resta nero.
- Su telefono conviene provare direttamente il sito online in una finestra in incognito: https://carlottaugcitalia.com/corso/?src=adv&videoID=1 (crea un lead vero nel portale).
- Tutto ciò che si fa su `main` va online in un paio di minuti con GitHub Pages.
