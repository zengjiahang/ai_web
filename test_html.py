import os, sys, django
sys.path.append('d:/python/ai部署/mynewproject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynewproject.settings')
django.setup()

from imageprocessor.views import format_features_to_table

test_features = {'slot': 1, 'hole': 1, 'chamfer': 1, 'shoulder': 1, 'step': 1}
table_data = format_features_to_table(test_features)

with open('d:/python/ai部署/table_output.html', 'w', encoding='utf-8') as f:
    f.write('<table border="1">\n')
    f.write('<tr><th>Feature</th><th>Operation</th><th>Prior operations</th></tr>\n')
    for row in table_data:
        f.write(f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td></tr>\n')
    f.write('</table>')

print("HTML table saved to d:/python/ai部署/table_output.html")