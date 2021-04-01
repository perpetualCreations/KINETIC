import swbs
import cv2
import numpy
from Cryptodome.Hash import MD5

if __name__ == '__main__':
    host = swbs.Host(999, None)
    host.listen()
    while True:
        # print(MD5.new(host.receive(500000, return_bytes = True)).hexdigest())
        image = cv2.imdecode(numpy.frombuffer(host.receive(500000, return_bytes=True), numpy.uint8), cv2.IMREAD_COLOR)
        cv2.imshow("unit test", image)
        cv2.waitKey(1)
