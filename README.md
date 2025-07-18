# traceLoom

**traceLoom** is a Python-based traceroute tool that enriches each hop of a route with additional network context.

## Enrichments
- Latency  
- MAC Address  
- TCP Ports  
- DNS Records  

## Usage
```bash
./traceLoom -t <target>
```

## Running from Source
1. Clone the repository:
   ```bash
   git clone https://github.com/monjiapawne/traceLoom.git
   cd traceLoom
   ```
2. Install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run (Linux) with `sudo`
   ```bash
   sudo ./venv/bin/python3 cli.py -t 192.168.2.1 --mac --ports
   ```
