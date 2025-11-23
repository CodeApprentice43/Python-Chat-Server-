import typing

class Request:
    def __init__(self,raw_http):
        
        self.method:str = ''
        self.path:str = ''
        self.http_version:str = ''
        self.headers:dict = {}
        self.cookies:dict = {}
        self.query_params:dict = {}
        self.body:bytes = b''
        self.path_params:dict = {}
        self.raw_http:bytes = raw_http
        self.construct_req()
    

    def handle_cookie(self,cookies):
        
        cookies_list = cookies.split("; ")

        for cookie in cookies_list:
            if "=" not in cookie:
                continue

            k,v = cookie.split("=")
            v = v.strip('"')
        
            self.cookies[k.strip()] = v



    def construct_req(self):
        http_req = self.raw_http

        delimiter = b'\r\n\r\n'
        delimiter_index = http_req.find(delimiter)

        headers = http_req[:delimiter_index]

        self.body = http_req[delimiter_index+len(delimiter):]

        decoded_headers = headers.decode().split('\r\n') #list containing each line/section of the header
    
        request_line = decoded_headers[0]
        self.method,self.path,self.http_version = request_line.split(" ")

        if '?' in self.path:
            self.path, query_string = self.path.split('?', 1)
            from urllib.parse import parse_qs
            parsed = parse_qs(query_string)
            self.query_params = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}


        for header in decoded_headers[1:]:
            if not header or ": " not in header:
                continue
            k,v = header.split(": ",1)

            if k == "Cookie":
                self.handle_cookie(v)
            
            self.headers[k.lower()] = v

    #convert request body to json
    def json(self):
      import json
      try:
          return json.loads(self.body.decode()) if self.body else {}
      except (json.JSONDecodeError, UnicodeDecodeError):
          return {}  # Return empty dict on error


    
    def form_data(self):
      from urllib.parse import parse_qs
      try:
          parsed = parse_qs(self.body.decode())
          return {k: v[0] for k, v in parsed.items()}
      except UnicodeDecodeError:
          return {}

    
    def get_header(self, name: str, default=None):
      return self.headers.get(name.lower(), default)
            
        

if __name__ == "__main__":
      # Test 1: Query params
      req1 = Request(b'GET /messages?limit=10&offset=5 HTTP/1.1\r\n\r\n')
      print("✓ Query params:", req1.query_params)
      assert req1.query_params == {"limit": "10", "offset": "5"}

      # Test 2: Cookies with quotes
      req2 = Request(b'GET / HTTP/1.1\r\nCookie: name="nafis"; visits=3\r\n\r\n')
      print("✓ Cookies:", req2.cookies)
      assert req2.cookies == {"name": "nafis", "visits": "3"}

      # Test 3: JSON body
      req3 = Request(b'POST / HTTP/1.1\r\n\r\n{"username": "test"}')
      print("✓ JSON:", req3.json())
      assert req3.json() == {"username": "test"}

      # Test 4: Form data
      req4 = Request(b'POST / HTTP/1.1\r\n\r\nusername=nafis&password=test')
      print("✓ Form data:", req4.form_data())
      assert req4.form_data() == {"username": "nafis", "password": "test"}

      # Test 5: Case-insensitive headers
      req5 = Request(b'GET / HTTP/1.1\r\nContent-Type: application/json\r\n\r\n')
      print("✓ Header lookup:", req5.get_header("content-type"))
      assert req5.get_header("content-type") == "application/json"

      print("\n✅ All tests passed!")

