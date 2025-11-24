import typing

class Response:
      REASON_PHRASES = {
          200: "OK",
          201: "Created",
          204: "No Content",
          301: "Moved Permanently",
          302: "Found",
          400: "Bad Request",
          401: "Unauthorized",
          403: "Forbidden",
          404: "Not Found",
          500: "Internal Server Error",
          502: "Bad Gateway",
          503: "Service Unavailable",
      }

      def __init__(self, status_code: int = 200, body: bytes = b""):
          self.status_code = status_code
          self.reason_phrase = self.REASON_PHRASES.get(status_code,
  "Unknown")
          self.headers = {}
          self.cookies = {}
          self.body = body

      def set_header(self, name: str, value: str):
          self.headers[name] = value
          return self

      def set_cookie(
          self,
          name: str,
          value: str,
          http_only: bool = False,
          secure: bool = False,
          max_age: int = None,
      ):
          cookie_parts = [f"{name}={value}", "Path=/"]
          if http_only:
              cookie_parts.append("HttpOnly")
          if secure:
              cookie_parts.append("Secure")
          if max_age is not None:
              cookie_parts.append(f"Max-Age={max_age}")
          self.cookies[name] = "; ".join(cookie_parts)
          return self

      def delete_cookie(self, name: str):
          self.set_cookie(name, "", max_age=0)
          return self

      def to_bytes(self) -> bytes:
          self.set_header("Content-Length", str(len(self.body)))
          self.set_header("X-Content-Type-Options", "nosniff")

          response_lines = [
              f"HTTP/1.1 {self.status_code} {self.reason_phrase}"
          ]

          for name, value in self.headers.items():
              response_lines.append(f"{name}: {value}")

          for cookie in self.cookies.values():
              response_lines.append(f"Set-Cookie: {cookie}")

          response_lines.append("")
          response_lines.append("")

          header_bytes = "\r\n".join(response_lines).encode()
          return header_bytes + self.body

      def status(self, status_code: int):
          self.status_code = status_code
          self.reason_phrase = self.REASON_PHRASES.get(status_code,
  "Unknown")
          return self

      def text(self, text: str):
          self.body = text.encode()
          self.set_header("Content-Type", "text/plain; charset=utf-8")
          return self

      def html(self, html: str):
          self.body = html.encode()
          self.set_header("Content-Type", "text/html; charset=utf-8")
          return self

      def json(self, data: typing.Any):
          import json
          self.body = json.dumps(data).encode()
          self.set_header("Content-Type", "application/json; charset=utf-8")
          return self

      @classmethod
      def ok(cls, body: bytes = b""):
          return cls(200, body)

      @classmethod
      def not_found(cls, body: bytes = b""):
          return cls(404, body)

      @classmethod
      def bad_request(cls, body: bytes = b""):
          return cls(400, body)

      @classmethod
      def server_error(cls, body: bytes = b""):
          return cls(500, body)
