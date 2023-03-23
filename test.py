import threading
from random import randint

b = threading.Lock()

def a():
    b.acquire()
    print(0)
    b.release()

threads = []
for i in range(5):
    thread = threading.Thread(target=a)
    threads.append(thread)
    thread.start()


#for thread in threads:
    #thread.join()

print(1)