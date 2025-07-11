# traceLoom

**traceLoom** is a python-based traceroute tool that enriches each hop of a route, it provides more context than traditional traceroute.

## Features
- Cross platform (Windows/Linux)
- Enriched hop data (IP, latency, MAC address)
- Simple CLI interface with logging options  
  `In progress: GUI rendering`

## Usage
```bash
python3 cli.py -t <target|hostname>
```
## Running from Source
1. Clone the repository:
   ```bash
   git clone https://github.com/monjiapawne/traceLoom.git
   cd traceLoom
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
