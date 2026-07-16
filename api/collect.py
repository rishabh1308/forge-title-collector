"""Vercel serverless endpoint for the Forge Title Collector."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler
import ipaddress
import json
from urllib.parse import urlparse

from title_collector.collector import fetch_title


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Forge Title Collector</title><style>:root{color:#eaf0ff;background:#09111f;font:16px/1.5 system-ui,sans-serif}*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;background:radial-gradient(circle at top right,#163965,transparent 45%),#09111f}main{width:min(760px,calc(100% - 32px));padding:56px 0}.eyebrow,label span{color:#9fb7dc;font-size:.82rem;letter-spacing:.08em;text-transform:uppercase}h1{font-size:clamp(2.5rem,8vw,4.7rem);margin:0;letter-spacing:-.06em}.intro{color:#c6d2e8;font-size:1.15rem;margin:8px 0 36px}label{display:block;font-weight:700;margin-bottom:8px}label span{float:right;font-weight:500}textarea{width:100%;min-height:160px;resize:vertical;padding:14px;border:1px solid #37577d;border-radius:9px;background:#101e31;color:inherit;font:inherit}button{cursor:pointer;margin-top:14px;padding:11px 16px;border:0;border-radius:7px;background:#82e6b3;color:#062215;font:inherit;font-weight:800}button:disabled{opacity:.6;cursor:wait}#message{min-height:1.5em;color:#b7c7e2}#results{margin-top:32px}.result-heading{display:flex;justify-content:space-between;align-items:center}.result-heading button{margin:0;background:#b6ccf7}.result{margin:10px 0;padding:14px 16px;border-left:4px solid #82e6b3;background:#101e31;border-radius:5px}.result.failed{border-color:#ff9d91}.result p,.result h3{margin:0}.result h3,.url{overflow-wrap:anywhere}.url{color:#9fb7dc;font-size:.87rem}</style></head><body><main><p class="eyebrow">NMG Labs · Forge Sprint 02</p><h1>Title Collector</h1><p class="intro">Fetch page titles, review each result, and download a JSON report.</p><form id="collector-form"><label for="urls">URLs <span>one per line, up to 10</span></label><textarea id="urls" required placeholder="https://example.com&#10;https://www.python.org"></textarea><button>Collect titles</button></form><p id="message" role="status"></p><section id="results" hidden><div class="result-heading"><h2>Results</h2><button id="download" type="button">Download JSON</button></div><div id="result-list"></div></section></main><script>const f=document.querySelector('#collector-form'),m=document.querySelector('#message'),s=document.querySelector('#results'),l=document.querySelector('#result-list'),b=f.querySelector('button');let r=[];function i(x){const a=document.createElement('article'),u=document.createElement('p'),t=document.createElement('h3');a.className='result '+x.status;u.className='url';u.textContent=x.url;t.textContent=x.title||x.error||'Unable to fetch title';a.append(u,t);return a}f.addEventListener('submit',async e=>{e.preventDefault();const u=document.querySelector('#urls').value.split('\\n').map(x=>x.trim()).filter(Boolean);b.disabled=true;m.textContent='Collecting titles…';s.hidden=true;try{const q=await fetch('/api/collect',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({urls:u})}),d=await q.json();if(!q.ok)throw Error(d.error||'Collection failed.');r=d.results;l.replaceChildren(...r.map(i));s.hidden=false;m.textContent=`${r.filter(x=>x.status==='success').length} of ${r.length} title(s) collected.`}catch(e){m.textContent=e.message}finally{b.disabled=false}});document.querySelector('#download').onclick=()=>{const a=Object.assign(document.createElement('a'),{href:URL.createObjectURL(new Blob([JSON.stringify({generated_at:new Date().toISOString(),results:r},null,2)],{type:'application/json'})),download:'titles.json'});a.click();URL.revokeObjectURL(a.href)}</script></body></html>"""


def _is_allowed_url(value: object) -> tuple[bool, str | None]:
    if not isinstance(value, str):
        return False, "Each URL must be a string."
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False, "Each URL must be an absolute http(s) URL."
    try:
        address = ipaddress.ip_address(parsed.hostname)
        if not address.is_global:
            return False, "Private and local network addresses are not allowed."
    except ValueError:
        if parsed.hostname.lower() in {"localhost", "localhost.localdomain"}:
            return False, "Private and local network addresses are not allowed."
    return True, None


class handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: object) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if urlparse(self.path).path not in {"/", "/index.html"}:
            self._send(404, {"error": "Not found."})
            return
        body = PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 16_000:
                raise ValueError("Request body is too large.")
            payload = json.loads(self.rfile.read(length) or b"{}")
            urls = payload.get("urls")
            if not isinstance(urls, list) or not 1 <= len(urls) <= 10:
                raise ValueError("Provide between 1 and 10 URLs.")
        except (ValueError, json.JSONDecodeError):
            self._send(400, {"error": "Provide JSON with an array of 1–10 URLs."})
            return

        results = []
        for url in urls:
            allowed, error = _is_allowed_url(url)
            if not allowed:
                results.append({"url": url, "title": None, "status": "failed", "error": error})
                continue
            try:
                results.append({"url": url, "title": fetch_title(url, timeout=8), "status": "success", "error": None})
            except (RuntimeError, ValueError) as exc:
                results.append({"url": url, "title": None, "status": "failed", "error": str(exc)})
        self._send(200, {"results": results})
