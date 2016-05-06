#!/usr/bin/env python

import subprocess, sys
import time, datetime
import library.neutron as neutronlib
import library.nova as novalib
from colorama import Fore, Style

router_id = '176cab96-0da9-496e-bb51-ff1a715027e8'
floatingips = neutronlib.list_floatingips_by_router(router_id)

print floatingips
