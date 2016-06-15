#!/usr/bin/python

import sys
from main import main
from Parser.StandardParser import StandardParser
from Context import Context
from Foundation.FoundationContext import FoundationContext


if len(sys.argv) == 2:
    filename = sys.argv[1]
    file = open(filename, 'r')
    content = file.read()
    lines = content.split("\n")
    context = Context(FoundationContext.simple())
    for line in lines:
        parser = StandardParser(line, context)
        parser.parse()
else:
    main()
