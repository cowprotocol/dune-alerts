from prometheus_client import start_http_server, Summary, Counter, Histogram
import random
import time

# Examples at https://github.com/prometheus/client_python
# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary("request_processing_seconds", "Time spent processing request")

# Decorate function with metric.
@REQUEST_TIME.time()
def process_request(t):
    """A dummy function that takes some time."""
    time.sleep(t)


# Counter, Gauge, Summary and Histogram, Info, Enum
def power_of_two(n: int, counter: Counter):
    if n != 0 and (n & (~(n - 1))) == n:
        print(f"{n} is a power of 2")
        counter.inc()  # Increment by 1


if __name__ == "__main__":
    # Start up the server to expose the metrics.
    start_http_server(8000)
    # Generate some requests.
    c = Counter("powers_of_2", "Powers of 2 encountered")
    loop_count = 0

    h = Histogram("request_latency_seconds", "Description of histogram")
    h.observe(4.7)  # Observe 4.7 (seconds in this case)

    while True:
        process_request(random.random())
        loop_count += 1
        power_of_two(loop_count, c)
