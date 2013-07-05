#!/usr/bin/env python

import os
from pathutils import full_path
from pathutils import xmlsec_path

CONFIG = {
	'xmlsec_binary': xmlsec_path,
    'attribute_map_dir': full_path('attributemaps'),
}