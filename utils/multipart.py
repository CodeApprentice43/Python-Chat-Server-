from core.request import Request
import typing
from typing import List


class Part:
    def __init__(self, headers: dict, name: str,filename:str,content: bytes):
        self.headers = headers
        self.name = name
        self.content = content
        self.filename = filename



class Multipart:
    def __init__(self, boundary: str, parts: List[Part]):
        self.boundary = boundary
        self.parts = parts

def parse_part(part):
    index = part.find(b'\r\n\r\n')
    headers = part[:index]
    data = part[index+len(b'\r\n\r\n'):]

    headers_list = headers.split(b'\r\n')
    
    header_dic = {}
    name = None
    filename = None

    for h in headers_list:
        h = h.decode()
        pair = h.split(':')
        if len(pair)==2:
            k,v = pair[0].strip(),pair[1].strip()
            header_dic[k] = v

            if k == 'Content-Disposition':
                values = v.split('; ')
                

                for val in values:
                    if val.strip().startswith('name='):
                        name = val.strip().split('=')[1].strip('"')
                    
                    if val.strip().startswith('filename='):
                        filename = val.strip().split('=')[1].strip('"')
                    
                    

    
    return Part(header_dic,name,filename,data)


    
def parse_multipart(request: Request):

    content_type = request.get_header("Content-Type")
    print(f"Content-Type: {content_type}")

    boundary_index = content_type.find("boundary=")
    boundary = content_type[boundary_index+len("boundary="):]
    print(f"Boundary extracted: '{boundary}'")

    delimiter = b"--" + boundary.encode()
    print(f"Delimiter: {delimiter[:50]}")
    print(f"Body length: {len(request.body)}")
    print(f"Body start: {request.body[:200]}")

    parts_data = request.body.split(delimiter)
    print(f"Split into {len(parts_data)} parts")

    parts = []

    for part in parts_data[1:-1]:

        part = parse_part(part)
        parts.append(part)


    return Multipart(boundary,parts)

    

       
if __name__ == "__main__":
    multipart_request = b'''POST /form-path HTTP/1.1\r\nHost: localhost:8080\r\nContent-Type: multipart/form-data; boundary=---------------------------123456789012345678901234567890\r\nContent-Length: <length>\r\n\r\n-----------------------------123456789012345678901234567890\r\nContent-Disposition: form-data; name="text_field1"\r\n\r\nText data for field 1\r\n-----------------------------123456789012345678901234567890\r\nContent-Disposition: form-data; name="text_field2"\r\n\r\nText data for field 2\r\n-----------------------------123456789012345678901234567890\r\nContent-Disposition: form-data; name="file_field1"; filename="example.txt"\r\nContent-Type: text/plain\r\n\r\nContents of example.txt file...\r\n-----------------------------123456789012345678901234567890\r\nContent-Disposition: form-data; name="image_field1"; filename="image1.jpg"\r\nContent-Type: image/jpeg\r\n\r\n<JPEG binary data>\r\n-----------------------------123456789012345678901234567890\r\nContent-Disposition: form-data; name="text_field3"\r\n\r\nText data for field 3\r\n-----------------------------123456789012345678901234567890\r\nContent-Disposition: form-data; name="file_field2"; filename="example2.txt"\r\nContent-Type: text/plain\r\n\r\nContents of example2.txt file...\r\n-----------------------------123456789012345678901234567890\r\nContent-Disposition: form-data; name="image_field2"; filename="image2.jpg"\r\nContent-Type: image/jpeg\r\n\r\n<JPEG binary data>\r\n-----------------------------123456789012345678901234567890--\r\n'''
    parse_multipart(Request(multipart_request))
    

