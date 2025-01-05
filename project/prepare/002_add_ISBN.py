import csv
import requests
import xml.etree.ElementTree as ET
import time

def get_isbn_from_ndl(title, author):
    # (変更なし)
    try:
        url = f"https://iss.ndl.go.jp/api/opensearch?cnt=20&dpid=iss-ndl-opac&title={title}&creator={author}"
        response = requests.get(url)
        response.raise_for_status()
        xml_content = response.content
        root = ET.fromstring(xml_content)

        ns = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'dcterms': 'http://purl.org/dc/terms/',
            'dcndl': 'http://ndl.go.jp/dcndl/terms/'}

        items = root.findall('.//item', ns)
        for item in items:
            isbns = item.findall('.//dcndl:ISBN', ns)
            if isbns:
                for isbn in isbns:
                    isbn_value = isbn.text.replace('-', '').replace(' ', '')
                    if len(isbn_value) == 10 or (len(isbn_value) == 13 and isbn_value.startswith('978')):
                        if len(isbn_value) == 13:
                            isbn_value = isbn_value[3:-1]
                        return isbn_value
        return None

    except requests.exceptions.RequestException:
        return None
    except ET.ParseError:
        return None
    except Exception:
        return None

def get_isbn_from_google_books(title, author):
    # (変更なし)
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title}+inauthor:{author}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get('totalItems', 0) > 0:
            for item in data['items']:
                if 'industryIdentifiers' in item['volumeInfo']:
                    for identifier in item['volumeInfo']['industryIdentifiers']:
                        if identifier['type'] == 'ISBN_10':
                            return identifier['identifier']
                        if identifier['type'] == 'ISBN_13':
                            isbn = identifier['identifier']
                            if isbn[:3] == "978":
                                isbn = isbn[3:-1]
                            return isbn
        return None
    except requests.exceptions.RequestException:
        return None
    except (KeyError, IndexError):
        return None

def main():
    input_filename = 'book_list02.csv'
    output_filename = 'book_list03.csv'

    try:
        with open(input_filename, 'r', encoding='utf-8') as infile, \
                open(output_filename, 'w', newline='', encoding='utf-8') as outfile:

            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            total_rows = sum(1 for row in open(input_filename, 'r', encoding='utf-8')) - 1
            processed_rows = 0
            results = []

            print("処理開始...")

            for row in reader:
                title = row.get('受賞作', '').strip() # 空白行を考慮
                author = row.get('著者', '').strip() # 空白行を考慮

                if title and author: # タイトルと著者の両方が空白でない場合のみ処理
                    isbn = get_isbn_from_ndl(title, author)
                    if isbn is None:
                        isbn = get_isbn_from_google_books(title, author)
                    row['ISBN10'] = isbn # ISBN10列を上書き
                    processed_rows += 1
                    percentage = (processed_rows / total_rows) * 100
                    result_message = f"処理完了: {percentage:.1f}% (タイトル: {title}, 著者: {author}, ISBN: {isbn})"
                    print(result_message)
                    results.append(result_message)
                else:
                    print("空白行をスキップ")
                    results.append("空白行をスキップ")
                writer.writerow(row)
                time.sleep(1)



            print("\n処理完了")
            print(f"ISBN付与完了。結果は{output_filename}に保存されました。")

    except FileNotFoundError:
        print(f"エラー：入力ファイル{input_filename}が見つかりません。")
    except Exception as e:
        print(f"予期せぬエラーが発生しました：{e}")

if __name__ == "__main__":
    main()