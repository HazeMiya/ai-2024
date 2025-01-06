import asyncio
import wikipedia
from typing import Dict, Union, List
import re
import warnings
from concurrent.futures import ThreadPoolExecutor
import sys
import time
import pandas as pd
import functools
import json

# BeautifulSoupの警告を抑制
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

class WikipediaBookSearchAsync:
    def __init__(self, max_workers: int = 10):
        wikipedia.set_lang('ja')
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self.book_related_keywords = ['小説', '著書', '文庫', '書籍', '著作', '作品']
        self.start_time = None
        self.processed_count = 0
        self.not_found_count = 0
        self.error_count = 0
        self.books = []

    async def __aenter__(self):
        self.start_time = time.time()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._executor.shutdown(wait=False)
        elapsed_time = time.time() - self.start_time
        print(f"\n処理完了。合計処理時間: {elapsed_time:.2f}秒")
        print(f"処理成功件数: {self.processed_count}")
        print(f"見つからなかった件数: {self.not_found_count}")
        print(f"エラー発生件数: {self.error_count}")

    def _is_book_page(self, content: str, title: str) -> bool:
        """ページが本に関するものかどうかを判定"""
        # タイトルに「映画」「ドラマ」などが含まれている場合は除外
        if re.search(r'(映画|ドラマ|テレビドラマ|アニメ|舞台|実写)', title):
            return False
        
        # コンテンツの最初の数段落に本に関連するキーワードが含まれているか確認
        first_paragraphs = '\n'.join(content.split('\n')[:5]).lower()
        return any(keyword in first_paragraphs for keyword in self.book_related_keywords)

    def _extract_book_info(self, page_content: str) -> Dict[str, str]:
        """ページコンテンツから本に関する情報を抽出"""
        patterns = {
            '著者': r'著者[：:]\s*([^\n]+)',
            '発行年': r'(発行|出版)年[：:]\s*([^\n]+)',
            'ジャンル': r'ジャンル[：:]\s*([^\n]+)',
            '出版社': r'出版社[：:]\s*([^\n]+)',
            'ISBN': r'ISBN[：:]\s*([0-9-]+)',
            'ページ数': r'ページ数[：:]\s*([^\n]+)',
        }
        
        info = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, page_content)
            if match:
                info[key] = match.groups()[-1].strip()
                
        return info

    def _clean_content(self, content: str) -> str:
        """全文から不要な情報を除去し、整形"""
        # 映画やドラマに関する記述を除去
        content_lines = []
        for line in content.split('\n'):
            if not re.search(r'(映画化|ドラマ化|実写化|アニメ化|映画|出典|コラボレート|受賞歴|書誌情報|関連項目|外部リンク|スタッフ|キャスト|脚注|文庫本|注釈|翻訳|書評|装幀|発行部数|オーディオブック|Blu-ray / DVD|スピンオフドラマ|注記|単行本)', line):
                content_lines.append(line)
        return '\n'.join(content_lines)

    async def _search_book_async(self, book: Dict) -> Union[Dict, str]:
        loop = asyncio.get_running_loop()
        search_func = functools.partial(self.search_book, book['受賞作'], book['著者'])
        result = await loop.run_in_executor(self._executor, search_func)
        await asyncio.to_thread(self._update_progress, len(self.books), book['受賞作'])
        return result

    def search_book(self, book_title: str, author_name: str) -> Union[Dict, str]:
        try:
            search_results = wikipedia.search(f"{book_title} {author_name} 小説")
            if not search_results:
                search_results = wikipedia.search(f"{book_title} 小説")
                if not search_results:
                    self.not_found_count += 1
                    return "" # 空文字列を返す

            for result in search_results:
                try:
                    page = wikipedia.page(result, auto_suggest=False)
                    if book_title.lower() not in page.title.lower():
                        continue
                    content = page.content.lower()

                    if self._is_book_page(content, page.title):
                        book_info = self._extract_book_info(page.content)
                        cleaned_content = self._clean_content(page.content)

                        result = {
                            "概要": cleaned_content,
                            "基本情報": book_info,
                        }
                        self.processed_count += 1
                        return result
                except (wikipedia.DisambiguationError, wikipedia.PageError):
                    continue
            self.not_found_count += 1
            return "" # 空文字列を返す

        except Exception as e:
            self.error_count += 1
            return f"エラーが発生しました: {str(e)}"

    async def search_books_async(self) -> List[Union[Dict, str]]:
        tasks = [self._search_book_async(book) for book in self.books]
        results = await asyncio.gather(*tasks)
        return results

    def _update_progress(self, total_books, current_book_title):
        self.total_processed += 1
        percentage = (self.total_processed / total_books) * 100
        sys.stdout.write(f"\r処理中: {self.total_processed}/{total_books} ({percentage:.1f}%) - 現在処理中: {current_book_title}")
        sys.stdout.flush()

    async def process_csv(self, input_file: str, output_file: str = "book_list05.csv"):
        df = pd.read_csv(input_file)
        self.books = df.to_dict(orient='records')
        total_books = len(self.books)
        self.total_processed = 0

        async with self as searcher:
            results = await searcher.search_books_async()
            for i, result in enumerate(results):
                if isinstance(result, str):
                    df.loc[i, 'Wikipedia情報'] = result
                else:
                    df.loc[i, 'Wikipedia情報'] = json.dumps(result, ensure_ascii=False)

        df.to_csv(output_file, index=False, encoding="utf-8")
        print(f"\nCSVファイル '{output_file}' に保存しました。")


async def main():
    searcher = WikipediaBookSearchAsync()
    await searcher.process_csv("book_list04.csv")

if __name__ == "__main__":
    asyncio.run(main())