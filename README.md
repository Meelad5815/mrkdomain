# Private custom names (`.mrk`, `.milaad`)

یہ پروجیکٹ آپ کے اپنے پلیٹ فارم کے اندر custom names چلانے کے لیے ہے، مثال کے طور پر:

- `shop.mrk`
- `user.milaad`

> یہ names صرف آپ کے ecosystem میں resolve ہوں گے۔ Public DNS پر یہ خودبخود live نہیں ہوں گے۔

## Features

- `name -> target` mapping register کریں
- mapping resolve کریں
- allowed suffixes: `.mrk` اور `.milaad`
- JSON file میں persistence

## Run

```bash
python3 server.py
```

Server default طور پر `http://0.0.0.0:8000` پر چلتا ہے۔

## API

### 1) Register name

```bash
curl -X POST http://localhost:8000/register \
  -H 'content-type: application/json' \
  -d '{"name":"shop.mrk", "target":"https://my-platform.internal/apps/shop"}'
```

### 2) Resolve name

```bash
curl 'http://localhost:8000/resolve?name=shop.mrk'
```

### 3) List all names

```bash
curl http://localhost:8000/names
```

## Suggested next step

اگر آپ چاہتے ہیں کہ browser میں `shop.mrk` لکھنے پر directly open ہو تو:

1. App gateway / reverse proxy بنائیں (Nginx/Traefik)
2. Internal DNS یا hosts override استعمال کریں
3. Resolver API کے ساتھ runtime routing attach کریں
