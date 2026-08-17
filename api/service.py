"""ViridisOS service + pure request dispatch (L4 seam).

Holds the registry + certifier and exposes the platform operations. `dispatch()` is a
pure function (method, path, body) -> (status, dict) so it is testable without sockets;
`app.py` wraps it in a stdlib HTTP server. No business logic lives in the transport layer.

Endpoints:
  GET  /modules
  POST /modules/{id}/preview      {inputs}
  POST /modules/{id}/certify      {subject, inputs}
  POST /certificates/verify       {certificate_id, module_id, inputs}
  GET  /standard
"""

from __future__ import annotations

from typing import Optional

from runtime.module import CertifyBlocked
from runtime.registry import ModuleRegistry
from runtime.canon_resolver import CanonResolver
from certification.certifier import Certifier
from certification.standard import STANDARD


class ViridisOSService:
    def __init__(self, registry: ModuleRegistry, certifier: Optional[Certifier] = None):
        self.registry = registry
        self.certifier = certifier or Certifier()
        self._issued = {}   # certificate_id -> Certificate (for verify-by-id)

    def list_modules(self) -> dict:
        return {"modules": self.registry.list_modules()}

    def preview(self, module_id: str, inputs: dict) -> dict:
        module = self.registry.get(module_id)
        return module.preview(inputs).to_dict()

    def certify(self, module_id: str, subject: str, inputs: dict) -> dict:
        module = self.registry.get(module_id)
        cert = self.certifier.issue(module, subject=subject, inputs=inputs)
        self._issued[cert.certificate_id] = cert
        return cert.to_dict()

    def verify(self, certificate_id: str, module_id: str, inputs: dict) -> dict:
        cert = self._issued.get(certificate_id)
        if cert is None:
            return {"valid": False, "reason": "unknown certificate_id"}
        module = self.registry.get(module_id)
        return {"valid": self.certifier.verify(cert, module, inputs)}

    def standard(self) -> dict:
        return STANDARD


def dispatch(service: ViridisOSService, method: str, path: str, body: Optional[dict]) -> tuple[int, dict]:
    body = body or {}
    parts = [p for p in path.strip("/").split("/") if p]
    try:
        if method == "GET" and path == "/modules":
            return 200, service.list_modules()
        if method == "GET" and path == "/standard":
            return 200, service.standard()
        if method == "POST" and len(parts) == 3 and parts[0] == "modules" and parts[2] == "preview":
            return 200, service.preview(parts[1], body.get("inputs", {}))
        if method == "POST" and len(parts) == 3 and parts[0] == "modules" and parts[2] == "certify":
            return 200, service.certify(parts[1], body.get("subject", ""), body.get("inputs", {}))
        if method == "POST" and path == "/certificates/verify":
            return 200, service.verify(body.get("certificate_id", ""), body.get("module_id", ""),
                                       body.get("inputs", {}))
        return 404, {"error": "not found"}
    except CertifyBlocked as e:
        return 409, {"error": "blocked", "detail": str(e)}      # A-1/A-3 → 409 Conflict
    except KeyError as e:
        return 404, {"error": "not found", "detail": str(e)}
    except (ValueError, TypeError) as e:
        return 400, {"error": "bad request", "detail": str(e)}
