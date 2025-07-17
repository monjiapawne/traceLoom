import sys, logging, argparse, json
from core import traceroute, enrich, trace_report

def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="Example: traceLoom -t 8.8.8.8 -l info"
    )
    
    # Input
    parser.add_argument('-t', '--target', type=str, required=True, help='target hostname or ip address')
    # Enrichment
    parser.add_argument('--dns', action='store_true',help='toggle dns lookups')
    parser.add_argument('--mac', action='store_true',help='toggle mac scanning')
    parser.add_argument('--ports', action='store_true',help='toggle port scannning')
    parser.add_argument('--all', action='store_true',help='enable all enrichment')
    # Output
    parser.add_argument('--cli', action='store_true',help='toggle output of nodes to cli')
    parser.add_argument('--json', action='store_true',help='toggle output of nodes to cli')
    parser.add_argument('-l', '--logging', type=str.lower, choices=['debug', 'info', 'warning'], default='WARNING', help="choose logging level")

    return parser.parse_args()

def main():
    args = parse_args()
    
    logging.basicConfig(level=getattr(logging, (args.logging).upper()), format='[%(levelname)s] %(message)s')
    
    # Traceroute
    hops = traceroute.run_traceroute(args.target)
    if not hops:
        logging.error(f'Trace route failed')
        sys.exit(1)
        
    node_list = enrich.create_node_list(hops)

    #  Enrichments
    if args.dns or args.all:
        node_list = enrich.reverse_dns_lookup(node_list)
    if args.mac or args.all:
        node_list = enrich.find_mac_address(node_list)
    if args.ports or args.all:
        node_list = enrich.scan_ports(node_list)
    
    #  CLI output
    if args.cli:
        for node in node_list:
            print(node)
    
    if args.json:
        rendered_json = trace_report.conv_json(args.target, node_list)
        print(json.dumps(rendered_json, indent=2))
  
if __name__ == "__main__":
    main()