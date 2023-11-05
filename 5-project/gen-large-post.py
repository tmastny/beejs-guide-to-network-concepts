import string
import random

with open("post-xl.txt", mode="w") as f:
    message = "Hello! This is the start of the large POST!\n\n"
    for _ in range(4096):
        i = random.randint(0, 51)
        message += string.ascii_letters[i]

    f.write(message + "\n")
