#!/usr/bin/env python3
"""
Web 开发与 API 设计 —— Python 实现
涵盖：HTTP 客户端/服务端从零实现 (socket)、RESTful API 设计、
      JSON Schema 验证、JWT 认证、GraphQL 风格查询解析器、
      速率限制算法（令牌桶/滑动窗口/漏桶）、
      分布式 ID 生成 (Snowflake)、任务队列模式
"""

import json
import time
import threading
import hashlib
import hmac
import base64
import re
import socket
from abc import ABC, abstractmethod
from collections import defaultdict, OrderedDict, deque
from dataclasses import dataclass, field
from typing import Any, Callable
from urllib.parse import urlparse, parse_qs
import math


# ============================================================
# §1  简易 HTTP 框架
# ============================================================

@dataclass
class Request:
    method: str
    path: str
    headers: dict[str, str]
    body: bytes
    query_params: dict[str, list[str]] = field(default_factory=dict)
    path_params: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_raw(cls, raw: bytes) -> "Request":
        try:
            text = raw.decode("utf-8", errors="replace")
            lines = text.split("\r\n")
            method, full_path, _ = lines[0].split(" ")
            parsed = urlparse(full_path)
            path = parsed.path
            query_params = parse_qs(parsed.query)

            headers = {}
            i = 1
            while i < len(lines) and lines[i]:
                if ":" in lines[i]:
                    key, value = lines[i].split(":", 1)
                    headers[key.strip().lower()] = value.strip()
                i += 1

            body = b""
            if i + 1 < len(lines):
                body = "\r\n".join(lines[i+1:]).encode("utf-8") if not raw.endswith(b"\r\n\r\n") else b""

            return cls(method=method, path=path, headers=headers,
                      body=body, query_params=query_params)
        except Exception:
            return cls(method="GET", path="/", headers={}, body=b"")


@dataclass
class Response:
    status_code: int = 200
    headers: dict[str, str] = field(default_factory=lambda: {"Content-Type": "application/json"})
    body: bytes = b""

    def to_bytes(self) -> bytes:
        status_messages = {200: "OK", 201: "Created", 400: "Bad Request",
                          401: "Unauthorized", 403: "Forbidden", 404: "Not Found",
                          500: "Internal Server Error"}
        msg = status_messages.get(self.status_code, "Unknown")
        lines = [f"HTTP/1.1 {self.status_code} {msg}"]
        for k, v in self.headers.items():
            lines.append(f"{k}: {v}")
        lines.append(f"Content-Length: {len(self.body)}")
        lines.append("")
        header_bytes = "\r\n".join(lines).encode("utf-8") + b"\r\n"
        return header_bytes + self.body

    @classmethod
    def json_response(cls, data: Any, status_code: int = 200) -> "Response":
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        return cls(status_code=status_code,
                   headers={"Content-Type": "application/json; charset=utf-8"},
                   body=body)

    @classmethod
    def error(cls, status_code: int, message: str) -> "Response":
        return cls.json_response({"error": message}, status_code)


class Router:
    """URL 路由器 —— 支持路径参数 (:param) 和正则匹配。"""

    def __init__(self) -> None:
        self.routes: list[tuple[str, re.Pattern, Callable[[Request], Response], list[str]]] = []

    def add_route(self, method: str, pattern: str,
                  handler: Callable[[Request], Response]) -> None:
        """pattern 如 '/users/:id/posts/:post_id'。"""
        param_names: list[str] = []
        regex_parts = ["^"]
        for segment in pattern.split("/"):
            if segment.startswith(":"):
                param_names.append(segment[1:])
                regex_parts.append(r"/([^/]+)")
            elif segment:
                regex_parts.append(f"/{re.escape(segment)}")
        regex_parts.append("$")
        regex = re.compile("".join(regex_parts) if regex_parts[1:] else "^/$")
        self.routes.append((method.upper(), regex, handler, param_names))

    def dispatch(self, request: Request) -> Response:
        for method, regex, handler, param_names in self.routes:
            if method != request.method:
                continue
            match = regex.match(request.path)
            if match:
                for i, name in enumerate(param_names):
                    request.path_params[name] = match.group(i + 1)
                return handler(request)
        return Response.error(404, f"Not Found: {request.method} {request.path}")

    def get(self, pattern: str):
        def decorator(handler: Callable[[Request], Response]):
            self.add_route("GET", pattern, handler)
            return handler
        return decorator

    def post(self, pattern: str):
        def decorator(handler: Callable[[Request], Response]):
            self.add_route("POST", pattern, handler)
            return handler
        return decorator


class SimpleAPIServer:
    """基于 socket 的简易 HTTP API 服务器。"""

    def __init__(self, host: str = "127.0.0.1", port: int = 8080) -> None:
        self.host = host
        self.port = port
        self.router = Router()
        self._middlewares: list[Callable] = []

    def add_middleware(self, mw: Callable) -> None:
        self._middlewares.append(mw)

    def handle_connection(self, client_socket: socket.socket) -> None:
        try:
            raw_data = b""
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                raw_data += chunk
                if b"\r\n\r\n" in raw_data and raw_data.count(b"\r\n\r\n") <= 1:
                    # 简单判断是否收完
                    content_length = 0
                    for line in raw_data.split(b"\r\n"):
                        if line.lower().startswith(b"content-length:"):
                            content_length = int(line.split(b":")[1].strip())
                    if len(raw_data.split(b"\r\n\r\n", 1)[-1]) >= content_length:
                        break
                if not chunk:
                    break

            request = Request.from_raw(raw_data)
            response = self.router.dispatch(request)
            client_socket.sendall(response.to_bytes())
        except Exception as e:
            err_resp = Response.error(500, str(e))
            try:
                client_socket.sendall(err_resp.to_bytes())
            except Exception:
                pass
        finally:
            client_socket.close()

    def run(self, max_connections: int = 10) -> None:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(max_connections)
        print(f"Server listening on {self.host}:{self.port}")

        try:
            while True:
                client_socket, addr = server_socket.accept()
                thread = threading.Thread(target=self.handle_connection,
                                          args=(client_socket,))
                thread.daemon = True
                thread.start()
        except KeyboardInterrupt:
            server_socket.close()


# ============================================================
# §2  JWT 认证
# ============================================================

class JWT:
    """JWT (JSON Web Token) 的简化实现。"""

    @staticmethod
    def base64url_encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

    @staticmethod
    def base64url_decode(data: str) -> bytes:
        padding = 4 - len(data) % 4
        if padding != 4:
            data += "=" * padding
        return base64.urlsafe_b64decode(data)

    @staticmethod
    def encode(payload: dict[str, Any], secret: str,
               algorithm: str = "HS256") -> str:
        header = {"alg": algorithm, "typ": "JWT"}
        header_b64 = JWT.base64url_encode(json.dumps(header, separators=(",", ":")).encode())
        payload_b64 = JWT.base64url_encode(json.dumps(payload, separators=(",", ":")).encode())

        signing_input = f"{header_b64}.{payload_b64}"
        if algorithm == "HS256":
            signature = hmac.new(secret.encode(), signing_input.encode(),
                                hashlib.sha256).digest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        sig_b64 = JWT.base64url_encode(signature)
        return f"{signing_input}.{sig_b64}"

    @staticmethod
    def decode(token: str, secret: str,
               algorithms: list[str] | None = None) -> dict[str, Any] | None:
        algorithms = algorithms or ["HS256"]
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None
            header_b64, payload_b64, sig_b64 = parts

            header = json.loads(JWT.base64url_decode(header_b64))
            alg = header.get("alg", "HS256")
            if alg not in algorithms:
                return None

            # 验证签名
            signing_input = f"{header_b64}.{payload_b64}"
            if alg == "HS256":
                expected_sig = hmac.new(secret.encode(),
                                       signing_input.encode(),
                                       hashlib.sha256).digest()
            else:
                return None

            expected_sig_b64 = JWT.base64url_encode(expected_sig)
            if not hmac.compare_digest(sig_b64, expected_sig_b64):
                return None

            payload = json.loads(JWT.base64url_decode(payload_b64))

            # 检查过期
            if "exp" in payload and payload["exp"] < time.time():
                return None

            return payload
        except Exception:
            return None


# ============================================================
# §3  速率限制算法
# ============================================================

class TokenBucket:
    """令牌桶 —— 允许突发流量。"""

    def __init__(self, rate: float, capacity: int) -> None:
        self.rate = rate                             # tokens / second
        self.capacity = capacity
        self.tokens = float(capacity)
        self.last_refill = time.monotonic()

    def consume(self, tokens: int = 1) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_refill = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


class SlidingWindowRateLimiter:
    """滑动窗口 —— 精确但占用内存多。"""

    def __init__(self, max_requests: int, window_seconds: float) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, deque[float]] = defaultdict(deque)

    def is_allowed(self, key: str) -> bool:
        now = time.monotonic()
        window = self.requests[key]

        # 移除过期请求
        while window and window[0] < now - self.window_seconds:
            window.popleft()

        if len(window) < self.max_requests:
            window.append(now)
            return True
        return False


class FixedWindowRateLimiter:
    """固定窗口 —— 简单但有边界问题。"""

    def __init__(self, max_requests: int, window_seconds: float) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.windows: dict[str, tuple[int, int]] = {}

    def is_allowed(self, key: str) -> bool:
        now = int(time.time() / self.window_seconds)
        if key in self.windows:
            window, count = self.windows[key]
            if window == now:
                if count < self.max_requests:
                    self.windows[key] = (now, count + 1)
                    return True
                return False
        self.windows[key] = (now, 1)
        return True


# ============================================================
# §4  Snowflake ID 生成器
# ============================================================

class Snowflake:
    """Twitter Snowflake 分布式 ID 生成器。"""

    def __init__(self, datacenter_id: int, worker_id: int,
                 epoch: int = 1609459200000) -> None:
        self.datacenter_id = datacenter_id & 0x1F
        self.worker_id = worker_id & 0x1F
        self.epoch = epoch
        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()

    def _current_millis(self) -> int:
        return int(time.time() * 1000)

    def next_id(self) -> int:
        with self.lock:
            timestamp = self._current_millis()
            if timestamp < self.last_timestamp:
                raise ValueError("时钟回拨!")
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & 0xFFF
                if self.sequence == 0:
                    while timestamp <= self.last_timestamp:
                        timestamp = self._current_millis()
            else:
                self.sequence = 0
            self.last_timestamp = timestamp

            return ((timestamp - self.epoch) << 22 |
                    self.datacenter_id << 17 |
                    self.worker_id << 12 |
                    self.sequence)


# ============================================================
# §5  GraphQL 风格查询解析器
# ============================================================

class Resolver:
    def __init__(self) -> None:
        self.fields: dict[str, Callable[[Any, dict[str, Any]], Any]] = {}

    def field(self, name: str):
        def decorator(func):
            self.fields[name] = func
            return func
        return decorator


class SimpleGraphQL:
    """简化的 GraphQL 查询解析器。"""

    def __init__(self) -> None:
        self.types: dict[str, Resolver] = {}

    def add_type(self, name: str, resolver: Resolver) -> None:
        self.types[name] = resolver

    def execute(self, query: str, root_value: Any = None) -> dict[str, Any]:
        """
        解析形如:
        {
          user(id: 1) {
            name
            email
            posts {
              title
            }
          }
        }
        """
        result = {}
        query = query.strip()
        if query.startswith("{") and query.endswith("}"):
            query = query[1:-1].strip()
        selections = self._parse_selections(query)
        for name, args, sub_selection in selections:
            if name in self.types:
                resolver = self.types[name]
                if name in resolver.fields:
                    sub_result = resolver.fields[name](root_value, args)
                    if sub_selection and isinstance(sub_result, dict):
                        sub_result = self._apply_sub_selection(sub_result, sub_selection)
                    result[name] = sub_result
        return result

    def _parse_selections(self, query: str) -> list[tuple[str, dict, str | None]]:
        """简化解析器 —— 返回 [(name, args_dict, sub_selection_str)]。"""
        results: list[tuple[str, dict, str | None]] = []
        depth = 0
        current = ""
        i = 0
        while i < len(query):
            ch = query[i]
            if ch == "{":
                depth += 1
                if depth == 1:
                    name = current.strip().split("(")[0].strip()
                    args_str = ""
                    if "(" in current and ")" in current:
                        args_str = current[current.index("(")+1:current.index(")")]
                    args = self._parse_args(args_str)
                    # 找匹配的 }
                    sub_start = i + 1
                    sub_depth = 1
                    j = sub_start
                    while j < len(query) and sub_depth > 0:
                        if query[j] == "{":
                            sub_depth += 1
                        elif query[j] == "}":
                            sub_depth -= 1
                        j += 1
                    sub_selection = query[sub_start:j-1].strip() if j > sub_start else None
                    results.append((name, args, sub_selection))
                    i = j
                    current = ""
                    continue
            elif ch == "}":
                depth -= 1
            current += ch
            i += 1
        if current.strip():
            name = current.strip().split("(")[0].strip()
            args_str = ""
            if "(" in current and ")" in current:
                args_str = current[current.index("(")+1:current.index(")")]
            results.append((name.strip(), self._parse_args(args_str), None))
        return results

    def _parse_args(self, args_str: str) -> dict[str, Any]:
        args = {}
        if args_str:
            for part in args_str.split(","):
                part = part.strip()
                if ":" in part:
                    k, v = part.split(":", 1)
                    k, v = k.strip(), v.strip().strip('"\'')
                    try:
                        v = int(v)
                    except ValueError:
                        try:
                            v = float(v)
                        except ValueError:
                            pass
                    args[k] = v
        return args

    def _apply_sub_selection(self, data: dict, sub_selection: str) -> dict:
        result = {}
        for part in sub_selection.split():
            part = part.strip()
            if part and part in data:
                result[part] = data[part]
        return result


# ============================================================
# §6  JSON Schema 验证器
# ============================================================

class JSONSchemaValidator:
    """JSON Schema 验证器 (Draft-4 子集)。"""

    @classmethod
    def validate(cls, instance: Any, schema: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        cls._validate(instance, schema, "", errors)
        return errors

    @classmethod
    def _validate(cls, instance: Any, schema: dict[str, Any],
                  path: str, errors: list[str]) -> None:
        # type
        if "type" in schema:
            expected_type = schema["type"]
            type_map = {
                "string": str, "number": (int, float), "integer": int,
                "boolean": bool, "array": list, "object": dict, "null": type(None),
            }
            expected = type_map.get(expected_type)
            if expected:
                if not isinstance(instance, expected):
                    errors.append(f"{path}: expected {expected_type}, got {type(instance).__name__}")
                    return

        # properties (object)
        if isinstance(instance, dict) and "properties" in schema:
            for prop_name, prop_schema in schema["properties"].items():
                prop_path = f"{path}.{prop_name}" if path else prop_name
                if prop_name in instance:
                    cls._validate(instance[prop_name], prop_schema, prop_path, errors)
                elif "default" in prop_schema:
                    instance[prop_name] = prop_schema["default"]
                elif prop_schema.get("required"):
                    errors.append(f"{prop_path}: required property missing")

        # items (array)
        if isinstance(instance, list) and "items" in schema:
            for i, item in enumerate(instance):
                cls._validate(item, schema["items"], f"{path}[{i}]", errors)

        # enum
        if "enum" in schema and instance not in schema["enum"]:
            errors.append(f"{path}: value {instance!r} not in enum {schema['enum']}")

        # minimum / maximum
        if isinstance(instance, (int, float)):
            if "minimum" in schema and instance < schema["minimum"]:
                errors.append(f"{path}: {instance} < minimum {schema['minimum']}")
            if "maximum" in schema and instance > schema["maximum"]:
                errors.append(f"{path}: {instance} > maximum {schema['maximum']}")

        # minLength / maxLength
        if isinstance(instance, str):
            if "minLength" in schema and len(instance) < schema["minLength"]:
                errors.append(f"{path}: length {len(instance)} < minLength {schema['minLength']}")
            if "maxLength" in schema and len(instance) > schema["maxLength"]:
                errors.append(f"{path}: length {len(instance)} > maxLength {schema['maxLength']}")

        # pattern
        if isinstance(instance, str) and "pattern" in schema:
            if not re.match(schema["pattern"], instance):
                errors.append(f"{path}: '{instance}' does not match pattern '{schema['pattern']}'")


# ============================================================
# §7  演示
# ============================================================

def demo_web_api() -> None:
    print("=" * 60)
    print("Web 开发与 API 设计演示")
    print("=" * 60)

    # HTTP Router
    print("\n--- Router ---")
    router = Router()

    @router.get("/users/:id")
    def get_user(req: Request) -> Response:
        return Response.json_response({"id": req.path_params["id"], "name": "Alice"})

    @router.post("/users")
    def create_user(req: Request) -> Response:
        return Response.json_response({"status": "created"}, 201)

    resp = router.dispatch(Request(method="GET", path="/users/42",
                                   headers={}, body=b""))
    print(f"GET /users/42: {resp.body.decode()}")

    resp2 = router.dispatch(Request(method="POST", path="/users",
                                    headers={}, body=b'{"name": "Bob"}'))
    print(f"POST /users: {resp2.body.decode()}")

    # JWT
    print("\n--- JWT ---")
    token = JWT.encode({"user_id": 42, "role": "admin", "exp": time.time() + 3600},
                       secret="my-secret-key")
    print(f"生成的 Token: {token[:50]}...")
    decoded = JWT.decode(token, "my-secret-key")
    print(f"解码: {json.dumps(decoded, indent=2)}")

    # Token Bucket
    print("\n--- 速率限制 ---")
    bucket = TokenBucket(rate=10, capacity=20)
    print(f"令牌桶 (rate=10/s, cap=20): consume 15 -> {bucket.consume(15)}")
    print(f"  tokens left: {bucket.tokens:.1f}")

    sw_limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=10)
    allowed = [sw_limiter.is_allowed("user_1") for _ in range(7)]
    print(f"滑动窗口 (max=5/10s): {allowed}")

    # Snowflake
    print("\n--- Snowflake ---")
    sf = Snowflake(datacenter_id=1, worker_id=1)
    ids = [sf.next_id() for _ in range(3)]
    print(f"生成的分布式 ID: {ids}")
    print(f"ID 二进制长度: {len(bin(ids[0])) - 2} bits")

    # GraphQL
    print("\n--- GraphQL 查询解析 ---")
    gql = SimpleGraphQL()
    user_resolver = Resolver()

    @user_resolver.field("user")
    def resolve_user(root: Any, args: dict) -> dict:
        return {"name": "Alice", "email": "alice@example.com",
                "posts": [{"title": "Hello"}, {"title": "World"}]}

    gql.add_type("user", user_resolver)
    result = gql.execute("{ user(id: 1) { name email } }")
    print(f"GraphQL 查询结果: {json.dumps(result, indent=2)}")

    # JSON Schema
    print("\n--- JSON Schema 验证 ---")
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "minLength": 2},
            "age": {"type": "integer", "minimum": 0, "maximum": 150},
            "email": {"type": "string", "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"},
        },
        "required": ["name"],
    }

    valid_data = {"name": "Alice", "age": 30, "email": "alice@example.com"}
    errors = JSONSchemaValidator.validate(valid_data, schema)
    print(f"有效数据: errors={errors}")

    invalid_data = {"age": -5, "email": "not-an-email"}
    errors2 = JSONSchemaValidator.validate(invalid_data, schema)
    print(f"无效数据: errors={errors2}")


if __name__ == "__main__":
    demo_web_api()
    print("\n✅ Web & API 篇执行完毕!")
