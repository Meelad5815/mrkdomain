# Private custom names (`.mrk`, `.milaad`)

یہ setup آپ کے platform کے اندر custom names جیسے `shop.mrk` اور `user.milaad` چلانے کے لیے ہے (public DNS کے بغیر)۔

## کیا شامل ہے

- **Name Registry API** (`server.py`): name → target mapping save/resolve
- **Runtime Gateway** (`gateway.py`): browser request کو `Host` header کے حساب سے upstream app پر proxy کرتا ہے

## 1) Name Registry چلائیں

```bash
python3 server.py
```

### Register

```bash
curl -X POST http://localhost:8000/register \
  -H 'content-type: application/json' \
  -d '{"name":"shop.mrk", "target":"http://127.0.0.1:9001"}'
```

## 2) Gateway چلائیں

```bash
python3 gateway.py
```

## 3) Local DNS/hosts override کریں

`/etc/hosts` میں یہ شامل کریں:

```txt
127.0.0.1 shop.mrk user.milaad
```

اب browser میں `http://shop.mrk:8080` کھولیں تو gateway mapping lookup کر کے target app کھول دے گا۔

## Quick local demo

پہلے demo app چلائیں:

```bash
python3 -m http.server 9001
```

پھر mapping register کریں:

```bash
curl -X POST http://localhost:8000/register \
  -H 'content-type: application/json' \
  -d '{"name":"shop.mrk", "target":"http://127.0.0.1:9001"}'
```

پھر test:

```bash
curl -H 'Host: shop.mrk' http://127.0.0.1:8080
```

## API endpoints (Registry)

- `POST /register`
- `GET /resolve?name=shop.mrk`
- `GET /names`
- `GET /health`

## Notes

- یہ global internet DNS نہیں ہے، صرف private ecosystem routing ہے۔
- production میں آپ `gateway.py` کی جگہ Nginx/Traefik لگا سکتے ہیں اور اسی mapping logic سے dynamic config بنا سکتے ہیں۔
