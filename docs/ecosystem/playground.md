# Online Playground

The MOL Playground is a browser-based code editor where you can write and run MOL programs instantly — no installation required.

**[Launch Playground →](https://mol.cruxlabx.in)**

## Features

- **Instant execution** — Write MOL code and run it in your browser
- **Syntax highlighting** — Full MOL syntax support
- **Auto-tracing** — Pipeline traces appear in the output
- **Share code** — Share your programs with others
- **Mobile-friendly** — Works on tablets and phones

## Security

The playground runs in **sandbox mode** with these protections:

- **No file system access** — `read_file`, `write_file`, `delete_file` are blocked
- **No network access** — `fetch`, `serve` are blocked  
- **Execution timeout** — Programs are killed after 10 seconds
- **Code size limit** — Maximum 50KB per program
- **Rate limiting** — Prevents abuse

### Blocked Functions

The following 26 functions are disabled in the playground:

| Category | Functions |
|---|---|
| File I/O | `read_file`, `write_file`, `append_file`, `delete_file`, `file_exists`, `file_size`, `make_dir`, `list_dir` |
| Path | `path_join`, `path_dir`, `path_base`, `path_ext` |
| Network | `fetch`, `url_encode`, `serve` |
| System | `sleep`, `wait`, `clock` |
| Security | `access` |

All other 117+ stdlib functions work normally.

## Self-Hosting

Run your own playground:

```bash
# Install with server dependencies
pip install mol-lang
pip install fastapi uvicorn

# Start the server
cd playground
python server.py
```

The server starts on `http://localhost:8000`.

### Docker

```bash
docker run -p 8000:8000 ghcr.io/crux-ecosystem/mol playground
```

## API

The playground exposes a REST API:

### Execute Code

```bash
curl -X POST https://mol.cruxlabx.in/api/run \
  -H "Content-Type: application/json" \
  -d '{"code": "show \"Hello from API!\""}'
```

Response:
```json
{
  "output": "Hello from API!\n",
  "error": null,
  "execution_time_ms": 12
}
```

### Check Security Info

```bash
curl https://mol.cruxlabx.in/api/security
```

Returns sandbox configuration and blocked function list.
