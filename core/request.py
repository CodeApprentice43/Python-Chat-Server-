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
    multipart_request = b'''POST /form-path HTTP/1.1\r\nHost: localhost:8080\r\nContent-Type: multipart/form-data; boundary=---------------------------123456789012345678901234567890\r\nContent-Length: <length>\r\n\r\n-----------------------------123456789012345678901234567890\r\nContent-Disposition: form-data; name="text_field1"\r\n\r\nText data for field 1\r\n-----------------------------123456789012345678901234567890\r\nContent-Disposition: form-data; name="text_field2"\r\n\r\nText data for field 2\r\n-----------------------------123456789012345678901234567890\r\nContent-Disposition: form-data; name="file_field1"; filename="example.txt"\r\nContent-Type: text/plain\r\n\r\nContents of example.txt file...\r\n-----------------------------123456789012345678901234567890\r\nContent-Disposition: form-data; name="image_field1"; filename="image1.jpg"\r\nContent-Type: image/jpeg\r\n\r\n<JPEG binary data>\r\n-----------------------------123456789012345678901234567890\r\nContent-Disposition: form-data; name="text_field3"\r\n\r\nText data for field 3\r\n-----------------------------123456789012345678901234567890\r\nContent-Disposition: form-data; name="file_field2"; filename="example2.txt"\r\nContent-Type: text/plain\r\n\r\nContents of example2.txt file...\r\n-----------------------------123456789012345678901234567890\r\nContent-Disposition: form-data; name="image_field2"; filename="image2.jpg"\r\nContent-Type: image/jpeg\r\n\r\n<JPEG binary data>\r\n-----------------------------123456789012345678901234567890--\r\n'''
    print("Body:", Request(multipart_request).body)
          
