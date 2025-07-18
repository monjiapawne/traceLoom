import sys
import logging
import argparse
import json
from dataclasses import dataclass
from rich.logging import RichHandler
from core import trace_route, enrich, trace_report


@dataclass
class Cfg:
    target: str
    max_hops: int = 40
    timeout: float = 0.02
    logging_level: str = "INFO"


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="Example: traceLoom -t 8.8.8.8",
    )

    # Input
    parser.add_argument(
        "-t", "--target", type=str, required=True,
        help="target hostname or ip address"
    )
    # Enrichment
    parser.add_argument("--dns", action="store_true",
                        help="toggle dns lookups")
    parser.add_argument("--mac", action="store_true",
                        help="toggle mac scanning")
    parser.add_argument("--ports", action="store_true",
                        help="toggle port scannning")
    parser.add_argument("--all", action="store_true",
                        help="enable all enrichment")
    # Output
    parser.add_argument(
        "--nocli",
        action="store_true",
        help="toggle output of nodes to cli",
        default=False,
    )
    parser.add_argument(
        "--json", action="store_true", help="toggle output of nodes to cli"
    )
    parser.add_argument(
        "--logging",
        type=str,
        choices=["debug", "info", "warning"],
        default="warning",
        help="choose logging level",
    )

    return parser.parse_args()


def main():
    # Parse CLI arguments
    args = parse_args()

    # Config
    cfg = Cfg(target=args.target, logging_level=args.logging.upper())

    # Logging
    logging.basicConfig(
        level=getattr(logging, (cfg.logging_level)),
        format="%(message)s",
        handlers=[
            RichHandler(show_time=False,
                        show_level=True,
                        show_path=False,
                        markup=False)
        ],
    )
    logging.debug(f"Config: {cfg!r}")  # Output config

    # Traceroute
    hops = trace_route.run_traceroute(cfg.target, cfg.max_hops, cfg.timeout)
    if not hops:
        logging.error(f"Trace route failed to {cfg.target}")
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
    if not args.nocli:
        for node in node_list:
            print(node)

    if args.json:
        jsondata = trace_report.conv_json(args.target, node_list)
        print(json.dumps(jsondata, indent=2))


if __name__ == "__main__":
    main()
