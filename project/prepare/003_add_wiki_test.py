import wikipedia
from typing import Dict, Union, List
import re
import warnings
from bs4 import BeautifulSoup

# BeautifulSoupの警告を抑制
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

class WikipediaBookSearch:
    def __init__(self):
        wikipedia.set_lang('ja')
        self.book_related_keywords = ['小説', '著書', '文庫', '書籍', '著作', '作品']
    
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

    def search_book(self, book_title: str, author_name: str) -> Union[Dict, str]:
        """本の情報を検索して構造化データとして返す"""
        try:
            # 本のタイトルと著者名を組み合わせて検索
            search_results = wikipedia.search(f"{book_title} {author_name} 小説")
            
            if not search_results:
                return "検索結果が見つかりませんでした。"
            
            # 検索結果から適切な本の記事を探す
            book_page = None
            for result in search_results:
                try:
                    page = wikipedia.page(result)
                    content = page.content.lower()
                    
                    # 著者名が含まれており、かつ本の記事であることを確認
                    if (author_name.lower() in content and 
                        self._is_book_page(content, page.title) and
                        book_title.lower() in page.title.lower()):
                        book_page = page
                        break
                        
                except (wikipedia.DisambiguationError, wikipedia.PageError):
                    continue
            
            if not book_page:
                # 本の記事が見つからない場合、著者のページから情報を探す
                try:
                    author_page = wikipedia.page(author_name)
                    if book_title.lower() in author_page.content.lower():
                        return self._extract_book_info_from_author_page(
                            author_page.content, book_title, author_name
                        )
                except:
                    pass
                return "指定された本の記事が見つかりませんでした。"
            
            # 本の情報を構造化
            book_info = self._extract_book_info(book_page.content)
            cleaned_content = self._clean_content(book_page.content)
            
            result = {
                "タイトル": book_title,
                "著者": author_name,
                "URL": book_page.url,
                "概要": cleaned_content,  # 全文を使用
                "基本情報": book_info,
                "参考文献": f"出典: {book_page.url}"
            }
            
            return result
            
        except Exception as e:
            return f"エラーが発生しました: {str(e)}"

    def _extract_book_info_from_author_page(
        self, content: str, book_title: str, author_name: str
    ) -> Dict[str, str]:
        """著者のページから特定の本の情報を抽出"""
        # 本のタイトルを含む段落を探す
        paragraphs = content.split('\n')
        relevant_paragraphs = []
        
        for i, para in enumerate(paragraphs):
            if book_title in para:
                # 前後の段落も含める
                start = max(0, i-1)
                end = min(len(paragraphs), i+2)
                relevant_paragraphs.extend(paragraphs[start:end])
        
        if not relevant_paragraphs:
            return {
                "タイトル": book_title,
                "著者": author_name,
                "概要": "詳細情報は見つかりませんでした。",
            }
        
        return {
            "タイトル": book_title,
            "著者": author_name,
            "概要": '\n'.join(relevant_paragraphs),
            "注記": "この情報は著者のページから抽出されました。"
        }

def format_result(result: Union[Dict, str]) -> str:
    """結果を見やすく整形"""
    if isinstance(result, str):
        return result
        
    output = []
    output.append("=== 検索結果 ===")
    output.append(f"タイトル: {result['タイトル']}")
    if 'URL' in result:
        output.append(f"URL: {result['URL']}")
    
    if result.get('基本情報'):
        output.append("\n【基本情報】")
        for key, value in result['基本情報'].items():
            output.append(f"{key}: {value}")
    
    output.append("\n【全文】")
    output.append(result['概要'])
    
    if '注記' in result:
        output.append(f"\n【注記】\n{result['注記']}")
    
    if '参考文献' in result:
        output.append(f"\n{result['参考文献']}")
    
    return '\n'.join(output)

# 使用例
if __name__ == "__main__":
    searcher = WikipediaBookSearch()
    book_title = "サラバ！"
    author_name = "西加奈子"
    
    result = searcher.search_book(book_title, author_name)
    print(format_result(result))