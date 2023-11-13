import threading


def sum_interval(interval):
    a, b = interval
    sum1b = b * (b + 1) // 2

    sum1a_m1 = (a - 1) * a // 2

    return sum1b - sum1a_m1


def runner(id, interval):
    result[id] = sum_interval(interval)


ranges = [[10, 20], [1, 5], [70, 80], [27, 92], [0, 16]]

n = len(ranges)
result = [0] * n

threads = []
for i, interval in enumerate(ranges):
    t = threading.Thread(target=runner, args=(i, interval))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print(result)
print(sum(result))
