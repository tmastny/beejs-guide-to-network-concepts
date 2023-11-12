# 30-project

## todo
- [X] When client connects, output:
  ```
  ('127.0.0.1', 61457): connected
  ```

- [ ] When client closes, output:
  ```
  ('127.0.0.1', 61457): disconnected
  ```
  Use `.getpeername()` on a socket to get this data
  after it's closed

  How do you detect when a connection closes?
  When `recv` returns zero bytes.

- [ ] When we get data, print. Example:
  ```
  ('127.0.0.1', 61457) 22 bytes: b'test1: xajrxttphhlwmjf'
  ```

