import urllib.request
import re
html = urllib.request.urlopen('https://synapsehrproject.vercel.app/dashboard?nocache=1').read().decode('utf-8', 'ignore')
scripts = re.findall(r'<script[^>]*src=[\'"]([^\'"]+)[\'"][^>]*>', html)
for src in scripts:
    print(src)
