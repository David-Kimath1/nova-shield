from http.server import HTTPServer, BaseHTTPRequestHandler
import cv2
import time

camera = cv2.VideoCapture(0)

class CameraHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<img src="/stream" style="width:100%">')
        elif self.path == '/stream':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            while True:
                ret, frame = camera.read()
                if ret:
                    _, img = cv2.imencode('.jpg', frame)
                    self.wfile.write(b'--frame\r\n')
                    self.wfile.write(b'Content-Type: image/jpeg\r\n\r\n')
                    self.wfile.write(img.tobytes())
                    self.wfile.write(b'\r\n')
                time.sleep(0.033)
        else:
            self.send_response(404)

print("Server starting at http://localhost:8080")
HTTPServer(("0.0.0.0", 8080), CameraHandler).serve_forever()
