import typing

class Route:
    def __init__(self,method,path,handler):
        self.method = method
        self.path = path
        self.handler = handler


class Router:

    def __init__(self):
        self.routes:list[Route] = []

    def add_route(self,method,path):
        def dec(handler):
            route = Route(method,path,handler)
            self.routes.append(route)
            return handler

        return dec
        

    def get(self,path):
        return self.add_route("GET",path)

    def put(self,path):
        return self.add_route("PUT",path)

    def post(self,path):
        return self.add_route("POST",path)
    
    def delete(self,path):
        return self.add_route("DELETE",path)
    


if __name__ == "__main__":
      router = Router()

      @router.get('/messages')
      def get_messages(request):
          return b"All messages"

      @router.post('/messages')
      def create_message(request):
          return b"Created"

      @router.get('/messages/{id}')
      def get_message(request):
          return b"One message"

      # Check routes registered
      print(f"Registered {len(router.routes)} routes:")
      for route in router.routes:
          print(f"  {route.method} {route.path}")

      # Should print:
