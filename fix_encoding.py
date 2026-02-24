import subprocess 
result = subprocess.run(['python', 'manage.py', 'dumpdata', '--exclude', 'auth.permission', '--exclude', 'contenttypes', '--exclude', 'admin.logentry', '--exclude', 'socialaccount', '--indent', '2'], capture_output=True) 
data = result.stdout.decode('utf-8') 
open('datos.json', 'w', encoding='utf-8').write(data) 
