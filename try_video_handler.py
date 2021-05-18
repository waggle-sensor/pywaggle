from waggle.data import VideoHandler

for _ in range(10):
    with VideoHandler({}, 0) as cap:
        print(cap.get())
