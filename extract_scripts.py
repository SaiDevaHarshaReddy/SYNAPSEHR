import re
with open('temp_dashboard.html', 'rb') as f:
    html = f.read().decode('utf-8', 'ignore')
scripts = re.findall(r'<script[^>]*src=[\'"]([^\'"]+)[\'"][^>]*>', html)
for src in scripts:
    print(src)
