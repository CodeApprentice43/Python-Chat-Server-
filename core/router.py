import typing
import re
from core.request import Request


class Route:
      def __init__(self, method, path, handler, pattern):
          self.method = method
          self.path = path
          self.handler = handler
          self.pattern = pattern  

class Router:

      def __init__(self):
          self.routes: list[Route] = []

      def _path_to_regex(self, path: str) -> re.Pattern:
          """Convert path pattern to compiled regex.

          Example:
              "/messages/{id}" → r"^/messages/(?P<id>[^/]+)$"
          """
          # Replace {param} with named regex group
          pattern = re.sub(r'\{(\w+)\}', r'(?P<\1>[^/]+)', path)
          # Anchor to start and end of string
          pattern = f"^{pattern}$"
          # Compile and return
          return re.compile(pattern)
    
    
      def add_route(self, method, path):
          def dec(handler):
           
              regex_pattern = self._path_to_regex(path)
              route = Route(method, path, handler, regex_pattern)
              self.routes.append(route)
              return handler
          return dec

      def route(self, request: Request):
       
          for route in self.routes:
             
              if route.method != request.method:
                  continue

            
              match = route.pattern.match(request.path)
              if match:
              
                  request.path_params = match.groupdict()
              
                  return route.handler(request)

      
          return None

      def get(self, path):
          return self.add_route("GET", path)

      def put(self, path):
          return self.add_route("PUT", path)

      def post(self, path):
          return self.add_route("POST", path)

      def delete(self, path):
          return self.add_route("DELETE", path)


if __name__ == "__main__":
      router = Router()

      @router.get('/messages')
      def get_messages(request):
          return b"Created"

      @router.get('/messages/{id}')
      def get_message(request):
          msg_id = request.path_params.get('id', 'unknown')
          return f"Message ID: {msg_id}".encode()

      print(f"Registered {len(router.routes)} routes:")
      for route in router.routes:
          print(f"  {route.method} {route.path}")

    
      req = Request(b'GET /messages HTTP/1.1\r\n\r\n')
      response = router.route(req)
      print("Response:", response)
      assert response == b"Created"

      req2 = Request(b'GET /messages/123 HTTP/1.1\r\n\r\n')
      response2 = router.route(req2)
      print("Response2:", response2)
      print("Path params:", req2.path_params)
      assert response2 == b"Message ID: 123"
      assert req2.path_params == {"id": "123"}

      req3 = Request(b'POST /unknown HTTP/1.1\r\n\r\n')
      response3 = router.route(req3)
      print("Response3:", response3)
      assert response3 is None

      print("✓ Router tests passed")

