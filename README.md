# Hash Cracker

Wordlist-based hash cracker with a CLI and REST API. Supports MD5, SHA1, and SHA256.

## Requirements

- Python 3.10+
- `pip install fastapi uvicorn`

## Usage

```bash
python app.py
```

Choose a mode on startup:

- **api** - starts REST API on `http://localhost:8000`
- **terminal** - interactive CLI

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/crack` | Submit a hash to crack |
| GET | `/status/{job_id}` | Get job status and result |
| POST | `/cancel/{job_id}` | Cancel a running job |

### Example

```bash
curl -X POST http://localhost:8000/crack \
  -H "Content-Type: application/json" \
  -d '{"target": "5f4dcc3b5aa765d61d8327deb882cf99", "algorithm": "md5"}'
```

## Config

Edit `config.py` to change the wordlist path, worker count, or allowed algorithms.

```python
WORDLIST_PATH = "rockyou.txt"
MAX_WORKERS = 4
ALLOWED_ALGOS = {"md5", "sha1", "sha256"}
```
