def detect_mime_type(data: bytes) -> tuple[str, str]:
     
      if len(data) < 4:
          return ("application/octet-stream", ".bin")

      # Check JPEG (FF D8 FF)
      if data[:3] == b'\xff\xd8\xff':
          return ("image/jpeg", ".jpg")

      # Check PNG (89 50 4E 47)
      if data[:4] == b'\x89PNG':
          return ("image/png", ".png")

      # Check GIF (47 49 46 38)
      if data[:4] == b'GIF8':
          return ("image/gif", ".gif")

      # Check MP4 (00 00 00 __ 66 74 79 70)
      # MP4 starts with 00 00 00, then 1 byte size, then 'ftyp'
      if len(data) >= 12:
          if data[:3] == b'\x00\x00\x00' and data[4:8] == b'ftyp':
              return ("video/mp4", ".mp4")

      # Default: unknown binary
      return ("application/octet-stream", ".bin")



jpeg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF...'
assert detect_mime_type(jpeg_data) == ("image/jpeg", ".jpg")

  # PNG file  
png_data = b'\x89PNG\r\n\x1a\n...'
assert detect_mime_type(png_data) == ("image/png", ".png")

  # GIF file
gif_data = b'GIF89a...'
assert detect_mime_type(gif_data) == ("image/gif", ".gif")

  # MP4 file
mp4_data = b'\x00\x00\x00\x20ftypmp42...'
assert detect_mime_type(mp4_data) == ("video/mp4", ".mp4")

  # Unknown file
unknown = b'\x01\x02\x03\x04'
assert detect_mime_type(unknown) == ("application/octet-stream", ".bin")

print("All tests passed.")