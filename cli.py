import sys
from core import traceroute

def main():
    target = sys.argv[1]
    hops = traceroute.traceroute(target)

if __name__ == "__main__":
    main()