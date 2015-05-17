# Presser

Presser is a simple command-line HTTP benchmark.

# Usage

You can specify number for HTTP requests to given URL:

```bash
python presser.py example.com -n 3
```

Provide HTTP auth credentials:

```bash
python presser.py example.com -u user -p password
```

Or do batch testing for URLs list in text file:

```
python presser.py -l urls_list.txt
```

# Requirements
* [requests](https://github.com/kennethreitz/requests)
