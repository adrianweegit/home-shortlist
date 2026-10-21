import re,sys,datetime
import os; p=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','index.html'); s=open(p).read()
v=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%dT%H:%M+08:00')
s=re.sub(r'const APP_VERSION = "[^"]+";', f'const APP_VERSION = "{v}";', s, count=1)
open(p,'w').write(s); print(v)
