import os
import pathlib
import json
import csv
import sys


def ls_dir(directory, laws):
    if os.path.isfile(directory):
        return

    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if not pathlib.Path(f).suffix == '.json':
            ls_dir(f, laws)
        else:
            laws.append(f)

def read_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def search_keyword_in_json(keyword, json_path):
    json_obj = read_json(json_path)
    sp = json_path.split('/')
    ver = '/'.join(json_obj['versions'][::-1])
    found = []
    hit = 0

    if '廢止' in ver:
        # print("Skip 廢止法規：", json_obj['title'])
        return found, hit

    for article in json_obj['law_data']:
        if keyword in article.get('content', ""):
            hit += 1
            found.append({
                'category1': sp[1],
                'category2': sp[2],
                'title': json_obj['title'],
                'version': ver,
                'article_no': article['rule_no'],
                'note': article.get('note', "").replace('(', '').replace(')', ''),
                'content': article['content'].replace('　', '')
            })

    return found, hit

def write_json_to_csv(json_dict, output):
    data_file = open(output, 'w')
    csv_writer = csv.writer(data_file, quotechar='"', quoting=csv.QUOTE_MINIMAL)

    count = 0
    for data in json_dict:
        if count == 0:
            header = data.keys()
            csv_writer.writerow(header)
            count += 1
        csv_writer.writerow(data.values())
    data_file.close()

law_files = []
ls_dir('.', law_files)

found_law = []
keyword = sys.argv[1]
output_dir = sys.argv[2] if len(sys.argv) > 2 else '..'
print('----------------------------------------')
print('Searching keyword: ', keyword)
print('Output dir: ', output_dir)

stat = {'law': 0, 'article': 0}
for law_path in law_files:
    found, hit = search_keyword_in_json(keyword, law_path)
    if found:
        stat['law'] += 1
        stat['article'] += hit
        found_law += found

print('Found {} laws, {} articles'.format(stat['law'], stat['article']))

# print(json.dumps(found_law, indent=4, ensure_ascii=False))
write_json_to_csv(found_law, f"{output_dir}/{keyword}.csv")
