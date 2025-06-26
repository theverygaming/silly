import requests
import time
import threading


lock =  threading.Lock()
results = []
total_requests = 0

def worker():
    global total_requests
    n_runs = 0
    total_time = 0.0

    # max. 1000 attempts
    for _ in range(1000):
        start = time.time()
        try:
            #requests.post("http://127.0.0.1:5000/webclient2/", data={})
            requests.get("http://127.0.0.1:5000/webclient2/")
            total_time += (time.time() - start)
            n_runs += 1
        except:
            pass
        # send out 10s of requests, then stop
        if total_time >= 10:
            break

    if n_runs:
        with lock:
            results.append(total_time / n_runs)
            total_requests += n_runs

threads = []
for i in range(100):
    t = threading.Thread(target=worker)
    threads.append(t)
    t.start()

start = time.time()
for t in threads:
    t.join()
total_time = (time.time() - start)

t_avg = sum(results) / len(results)
t_min = min(results)
t_max = max(results)

print(f"avg: {t_avg*1000:.2f} ms")
print(f"min: {t_min*1000:.2f} ms")
print(f"max: {t_max*1000:.2f} ms")
print(f"throughput: {total_requests/total_time:.2f} requests/s")
