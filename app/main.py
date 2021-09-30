"""mainモジュール."""
import os
import json
import pandas as pd
from typing import Optional
from fastapi import FastAPI
from app.hanzai_data import get_hanzai_data_list, get_hanzai_dataframe
from fastapi.responses import ORJSONResponse
import logging

# TODO: CSVの定期更新 -> DataFrame再構築

location = '山梨'

root_path = os.getenv('ROOT_PATH', '')
app = FastAPI(
    title=f'{location}はんざいAPI',
    root_path=root_path
)

with open('./app/resource.json', 'r') as f:
    config = json.load(f)
url = next(
        (c['url'] for c in config['sites'] if c['location'] == location),
        None
    )

# 起動時に全データロードする
links = get_hanzai_data_list(url)
data = get_hanzai_dataframe(links)

logging.basicConfig(level=logging.INFO)
logging.info(data)


@app.get('/', response_class=ORJSONResponse)
def read(keys: Optional[str] = None,
         values: Optional[str] = None,
         count: int = 100,
         offset: int = 1) -> ORJSONResponse:
    """指定したキーと値で絞り込んだデータを返却する."""
    if data is None:
        return ORJSONResponse(
            status_code=404,
            content={'detail': 'data does not exists'}
        )
    if offset <= 0:
        return ORJSONResponse(
                status_code=400,
                content={'detail': 'Offset must be more than 0'})

    if count <= 0 or 100 < count:
        return ORJSONResponse(
                status_code=400,
                content={'detail': 'Count must be between 1 and 100'})

    # ,区切りでデータを取り出す
    key_array = [] if(keys is None) else keys.split(',')
    value_array = [] if(values is None) else values.split(',')

    if (len(key_array) != len(value_array)):
        # 絞り込みキーの数と, 絞り込む値の数が一致しないとき400を返す
        return ORJSONResponse(
                status_code=400,
                content={'detail': 'Number of keys and values does not match'})

    for key in key_array:
        if data.columns.tolist().index(key) < 0:
            # 間違ったキーが指定された場合400を返す
            return ORJSONResponse(
                    status_code=400,
                    content={'detail': f'Key {key} does not exists'})

    # キーごとに値で絞り込む
    extract_data = pd.DataFrame(data)
    for idx, key in enumerate(key_array):
        extract_data = extract_data[
                        extract_data[key].str.contains(
                            value_array[idx], na=False
                        )]

    total = len(extract_data)

    if offset > len(extract_data):
        # Offsetがデータ数を超えているとき空のリストを返す
        return ORJSONResponse(
            content={'offset': offset, 'count': 0, 'total': total, 'data': []}
        )
    if offset-1 + count > len(extract_data):
        # 指定された数より残りのデータ数が少ないとき全て返す
        extract_data = extract_data[offset-1:]
    else:
        extract_data = extract_data[offset-1:offset-1+count]

    return ORJSONResponse(content={
            'offset': offset,
            'count': len(extract_data),
            'total': total,
            'data': extract_data.to_dict(orient='records'),
          })


@app.get('/keys', response_class=ORJSONResponse)
def keys() -> ORJSONResponse:
    """キー一覧を取得."""
    if data is None:
        return ORJSONResponse(
            status_code=404,
            content={'detail': 'data does not exists'}
        )
    else:
        return ORJSONResponse(content={'keys': data.columns.tolist()})


@app.get('/values/{key}', response_class=ORJSONResponse)
def values(key: str) -> ORJSONResponse:
    """指定されたキーのユニークなデータ一覧を取得."""
    if data is None:
        return ORJSONResponse(
                status_code=404,
                content={'detail': 'data does not exists'}
        )

    if data.columns.tolist().index(key) < 0:
        # 存在しないキーのとき404を返す
        return ORJSONResponse(
            status_code=404,
            content={'detail': f'Key {key} does not exists'}
        )

    return ORJSONResponse(
        content={'values': data[key].dropna().unique().tolist()}
    )
