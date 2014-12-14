# Presser

Presser is a simple command-line HTTP benchmark.

# Usage

You can specify number for HTTP requests to given URL:

```bash
python presser.py example.com -r 3
```

Or provide HTTP auth credentials:

```bash
python presser.py example.com -u user -p password
```


# Requirements
* [requests](https://github.com/kennethreitz/requests)
