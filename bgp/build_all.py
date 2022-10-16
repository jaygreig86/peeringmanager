#!/usr/bin/env python
import sys
from peermanager.peermanager import peermanager

############################
# Run Main()               #
############################

def main(run_on_only = ""):
    p = peermanager()
    p.build_peers(run_on_only)
    p.build_customers(run_on_only)
    p.build_filters(run_on_only)


############################
# Lets call main() and run #
############################

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()

