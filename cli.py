import sys
import logging
import argparse
from core import traceroute, enrich

def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="Example: traceLoom -t 8.8.8.8 -l info"
    )
    parser.add_argument('-t', '--target', type=str, 
                        required=True)
    parser.add_argument('-l', '--logging', type=str.lower, 
                        choices=['info', 'warning'], default='INFO')

    return parser.parse_args()

def main(args):
    logging.basicConfig(level=getattr(logging, (args.logging).upper()), format='[%(levelname)s] %(message)s')
    hops = traceroute.traceroute(args.target)
    node_list = enrich.create_node_list(hops)
    node_list = enrich.find_mac_address(node_list)
    node_list = enrich.scan_ports(node_list)
    for node in node_list:
        print(node)
    
if __name__ == "__main__":
    args = parse_args()
    main(args)