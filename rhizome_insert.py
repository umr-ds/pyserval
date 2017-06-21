#!/usr/bin/env python
import sys
from serval.client import RestfulConnection
from serval import *
from os.path import basename

with open(sys.argv[1]) as f:
    c = RestfulConnection(user="pum", passwd="pum123")
    r = rhizome.Rhizome(c)
    
    bundle = rhizome.Bundle()
    bundle.name = basename(sys.argv[1])
    
    manifest = r.insert(bundle, f)
    print manifest.split("\0")[0]