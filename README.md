### Setup Instructions

1. Set up environment and dependencies
```
python -m venv venv
```

```
source venv/bin/activate
```

```
pip install -r requirements.txt
```

2. Run decoder (or host)
```
python3 decoder.py --port 80 --timeout 30
```
Note that packets are only shown in the CLI once the 30 seconds have timed out.

3. Run encoder
```
python3 encoder.py 192.168.1.100 80 "your message"
```
You can send multiple messages in a given timeframe.

