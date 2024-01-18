#!/usr/bin/env python
import sys
from peermanager.peermanager import peermanager

############################
# Run Main()               #
############################

def main():
    p = peermanager()
    p.run_tasks()


############################
# Lets call main() and run #
############################

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()


