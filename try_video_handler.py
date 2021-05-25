from waggle.data import VideoHandler
import time

print("consuming at ~30fps. should not see eviction warning")
with VideoHandler({}, 0) as cap:
    for _ in range(10):
        cap.get(timeout=0.1)
        time.sleep(1/30)

print("open handler without consuming. should see eviction warning")
with VideoHandler({}, 0) as cap:
    time.sleep(1)

print("trying __enter__ / __exit__ behavior")
for _ in range(10):
    print("entering with stmt")
    with VideoHandler({}, 0) as cap:
        cap.get()
    print("exited with stmt")
print("ok")
