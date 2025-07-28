import argparse
from controller import run_traceroute


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
  parser.add_argument("--os", action="store_true",
                      help="toggle os scannning (requries nmap)")
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
  args = parse_args()
  run_traceroute(
      target=args.target,
      logging_level=args.logging,
      dns=args.dns,
      mac=args.mac,
      ports=args.ports,
      os=args.os,
      all=args.all,
      nocli=args.nocli,
      json_output=args.json
  )


if __name__ == "__main__":
  main()
