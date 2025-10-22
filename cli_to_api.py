#!/usr/bin/env python3
import sys
import yt_dlp
from pprint import pprint

# to convert cli args to api args
# Removed the * prefix to opts arg to pass in a list
def cli_to_api(opts):
    default = yt_dlp.parse_options([]).ydl_opts
    diff = {k: v for k, v in yt_dlp.parse_options(opts).ydl_opts.items() if default[k] != v}
    if 'postprocessors' in diff:
        diff['postprocessors'] = [pp for pp in diff['postprocessors'] if pp not in default['postprocessors']]
    return diff

pprint(cli_to_api(sys.argv[1:]))