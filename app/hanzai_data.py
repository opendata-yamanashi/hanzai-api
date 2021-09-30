"""犯罪データを取り出すためのモジュール."""
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Optional
from urllib.parse import urljoin, urlparse


def get_hanzai_data_list(url: str, extension: str = 'csv') -> List[str]:
    """Webページから犯罪データのファイルリストを取り出す."""
    # ページをGETで取得する
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    # aタグのhref属性を抜き出す
    links = [path.get('href') for path in soup.find_all('a')]
    # href属性が指定拡張子で終わるものを抜き出して, 絶対パスのURLを作成する
    links = [urljoin(url, path) for path in links if
             path is not None and path.lower().endswith(extension)]
    return links


def get_hanzai_dataframe(links: List[str]) -> Optional[pd.DataFrame]:
    """犯罪データのURLリストからデータを取り出しデータフレームを作成する."""
    dfs = None
    for link in links:
        # CSVを取得
        file_path = download_file_if_needed(link)
        if file_path is not None:
            # CSVからDataFrameを作成
            df = pd.read_csv(file_path, encoding='shift-jis')
            if dfs is None:
                dfs = df
            else:
                dfs = pd.concat([dfs, df])
    return dfs


def download_file_if_needed(url) -> Optional[str]:
    """ローカルにデータファイルがない場合は、データファイルをダウンロードする."""
    # ローカルへの保存先
    dir = f'{os.path.dirname(__file__) }/data'
    if not os.path.isdir(dir):
        os.mkdir(dir)

    path = urlparse(url).path.split('/')
    file_path = None

    if len(path) > 0:
        file_path = f'{dir}/{path[len(path)-1]}'
        if not os.path.exists(file_path):
            data = requests.get(url).content
            with open(file_path, mode='wb') as f:
                f.write(data)
    return file_path
