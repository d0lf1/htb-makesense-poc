# HTB · MakeSense — PoC

Proof-of-concept per la macchina **MakeSense** (Hack The Box, Season 11).
Writeup completo: https://blog.ldsec.it/makesense/

**Catena:** chiave crittografica hardcoded lato client → forge di payload cifrati →
Stored XSS nella sessione di un bot admin → creazione admin + RCE via plugin malevolo
(`www-data`) → riuso password verso `walter` → servizio OCR interno di root che
scrive una web shell PHP → root.

| File | Ruolo |
|------|-------|
| `encrypt_payload.py` | Forge di payload cifrati con la chiave hardcoded |
| `test_xss_bot.py`, `trigger_payload.py` | Innesco della Stored XSS sul bot admin |
| `create_malicious_wav.py`, `upload_malicious_wav.py` | WAV malevolo per la feature di trascrizione |
| `create_plugin_zip.py`, `upload_plugin.py` | Plugin WordPress malevolo → RCE |
| `su_walter.py`, `ssh_walter.py` | Riuso password → utente `walter` |
| `deploy_root_exploit.py` | Abuso del servizio OCR di root → web shell |
| `query_sqlite.py` | Query al DB per loot credenziali |

> ⚠️ Solo a scopo educativo e per testing autorizzato.
