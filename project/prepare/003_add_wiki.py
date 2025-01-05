import asyncio
import pandas as pd
import wikipedia
from typing import Dict, List, Union, Optional
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import sys
from dataclasses import dataclass
import functools

@dataclass
class ProcessingStats:
    total: int = 0
    completed: int = 0
    start_time: Optional[datetime] = None
    
    def start(self):
        self.start_time = datetime.now()
        
    def increment(self, count: int = 1):
        self.completed += count
    
    @property
    def elapsed_time(self) -> float:
        return (datetime.now() - self.start_time).total_seconds() if self.start_time else 0

class WikipediaBookEnricher:
    def __init__(self, max_workers: int = 20):
        wikipedia.set_lang('ja')
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self.stats = ProcessingStats()
        self.book_related_keywords = ['小説', '著書', '文庫', '書籍', '著作', '作品']
        self._cache = {}
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._executor.shutdown(wait=False)

    def _is_book_page(self, content: str, title: str) -> bool:
        if re.search(r'(映画|ドラマ|テレビドラマ|アニメ|舞台|実写)', title):
            return False
        first_paragraphs = '\n'.join(content.split('\n')[:5]).lower()
        return any(keyword in first_paragraphs for keyword in self.book_related_keywords)

    def _clean_content(self, content: str) -> str:
        content_lines = []
        for line in content.split('\n'):
            if not re.search(r'(映画化|ドラマ化|実写化|アニメ化|映画|出典|コラボレート|受賞歴|書誌情報|関連項目|外部リンク|スタッフ|キャスト|脚注|文庫本|注釈|翻訳|書評|装幀|発行部数|オーディオブック|Blu-ray|DVD|スピンオフ|注記|単行本)', line):
                content_lines.append(line)
        return '\n'.join(content_lines)

    def _search_book(self, book_title: str, author_name: str) -> Dict[str, str]:
        try:
            cache_key = f"{book_title}:{author_name}"
            if cache_key in self._cache:
                return self._cache[cache_key]

            search_results = wikipedia.search(f"{book_title} {author_name} 小説")
            if not search_results:
                return {"wikipedia_summary": "検索結果が見つかりませんでした"}

            book_page = None
            for result in search_results[:3]:  # 最初の3件をチェック
                try:
                    page = wikipedia.page(result, auto_suggest=False)
                    content = page.content.lower()
                    
                    if (author_name.lower() in content and 
                        self._is_book_page(content, page.title) and
                        book_title.lower() in page.title.lower()):
                        book_page = page
                        break
                except:
                    continue

            if not book_page:
                return {"wikipedia_summary": "本の情報が見つかりませんでした"}

            cleaned_content = self._clean_content(book_page.content)
            summary = next((line for line in cleaned_content.split('\n') if line.strip()), "")
            result = {
                "wikipedia_summary": summary[:500],
                "wikipedia_url": book_page.url
            }
            self._cache[cache_key] = result
            return result

        except Exception as e:
            return {"wikipedia_summary": f"エラー: {str(e)}"}

    def _update_progress(self):
        elapsed = self.stats.elapsed_time
        speed = self.stats.completed / elapsed if elapsed > 0 else 0
        sys.stdout.write(f"\r処理中... {self.stats.completed}/{self.stats.total} 完了 ({speed:.1f}件/秒)")
        sys.stdout.flush()

    async def process_books(self, books: List[dict]) -> List[Dict[str, str]]:
        loop = asyncio.get_running_loop()
        tasks = []
        
        for book in books:
            search_func = functools.partial(self._search_book, book['受賞作'], book['著者'])
            task = loop.run_in_executor(self._executor, search_func)
            tasks.append(task)

        results = []
        for task in asyncio.as_completed(tasks):
            result = await task
            results.append(result)
            self.stats.increment()
            self._update_progress()
            
        return results

    async def enrich_books(self, input_file: str, output_file: str):
        print("Wikipedia情報の取得を開始します...")
        
        df = pd.read_csv(input_file)
        self.stats.total = len(df)
        self.stats.start()
        
        books = df.to_dict('records')
        results = await self.process_books(books)
        
        for i, result in enumerate(results):
            for key, value in result.items():
                df.loc[i, key] = value

        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\n完了しました。処理時間: {self.stats.elapsed_time:.1f}秒")
        print(f"平均速度: {self.stats.total/self.stats.elapsed_time:.1f}件/秒")

async def main():
    async with WikipediaBookEnricher() as enricher:
        await enricher.enrich_books('book_list02.csv', 'book_list03.csv')

if __name__ == "__main__":
    asyncio.run(main())