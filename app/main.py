"""mainモジュール."""
import os
import json
import pandas as pd
import logging
import schedule
import threading
from typing import List, Optional, Tuple
from fastapi import FastAPI
from app.constants import MAX_COUNT
from app.hanzai_data import get_hanzai_data_list, get_hanzai_dataframe
from fastapi.responses import ORJSONResponse
from time import sleep
from fastapi.middleware.cors import CORSMiddleware


def _load_data(location: str) -> pd.DataFrame:
    """データのロード."""
    with open('./app/resource.json', 'r') as f:
        config = json.load(f)
    url = next(
            (c['url'] for c in config['sites'] if c['location'] == location),
            None
        )
    links = get_hanzai_data_list(url)
    data = get_hanzai_dataframe(links)

    # 日付・時刻の降順, 地域, 手口の昇順にソートする
    try:
        date_culumn_name = '発生年月日（始期）'
        data[date_culumn_name] = pd.to_datetime(
                                    data[date_culumn_name],
                                    errors='coerce')
        time_culumn_name = '発生時（始期）'
        data[time_culumn_name] = pd.to_numeric(
                                    data[time_culumn_name],
                                    errors='coerce')
        data = data.sort_values([
                date_culumn_name,
                time_culumn_name,
                '市区町村（発生地）',
                '手口'
                ],
                ascending=[False, True, True, True]
            )

        # 日付を文字列に戻す
        data[date_culumn_name] = data[date_culumn_name].astype(str)

    except Exception as e:
        print(e)
        pass

    logging.basicConfig(level=logging.INFO)
    logging.info(data)

    return data


# サーバー
location = '山梨'
root_path = os.getenv('ROOT_PATH', '')
app = FastAPI(
    title=f'{location}はんざいAPI',
    root_path=root_path
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# 初回データロード
data = _load_data(location)


def _check_offset_and_count(data: pd.DataFrame,
                            count: int,
                            offset: int) -> Tuple[bool, ORJSONResponse]:
    """パラメータとデータのチェック."""
    if data is None:
        return (False, ORJSONResponse(
                status_code=404,
                content={'detail': 'data does not exists'}))
    if count <= 0 or MAX_COUNT < count:
        return (False, ORJSONResponse(
                status_code=400,
                content={'detail': 'Count must be between 1 and 100'}))
    if offset <= 0:
        return (False, ORJSONResponse(
                status_code=400,
                content={'detail': 'Offset must be more than 0'}))
    return (True, ORJSONResponse())


def _check_keys_and_values(data: pd.DataFrame,
                           key_array: List[str],
                           value_array: List[str]
                           ) -> Tuple[bool, ORJSONResponse]:
    """キーと値のチェック."""
    if (len(key_array) != len(value_array)):
        # 絞り込みキーの数と, 絞り込む値の数が一致しないとき400を返す
        return (False, ORJSONResponse(
                status_code=400,
                content={
                    'detail': 'Number of keys and values does not match'
                }))

    for key in key_array:
        if data.columns.tolist().count(key) <= 0:
            # 間違ったキーが指定された場合400を返す
            return (False, ORJSONResponse(
                    status_code=400,
                    content={'detail': f'Key {key} does not exists'}))

    return (True, ORJSONResponse())


@app.get('/', response_class=ORJSONResponse)
def read(keys: Optional[str] = None,
         values: Optional[str] = None,
         count: int = MAX_COUNT,
         offset: int = 1) -> ORJSONResponse:
    """指定したキーと値で絞り込んだデータを返却する."""
    # offset, countのチェック
    ret, response = _check_offset_and_count(data, count, offset)
    if not ret:
        return response

    # ,区切りでパラメータを取り出す
    key_array = [] if(keys is None) else keys.split(',')
    value_array = [] if(values is None) else values.split(',')

    # keys, valuesのチェック
    ret, response = _check_keys_and_values(data, key_array, value_array)
    if not ret:
        return response

    # キーごとに値で絞り込む
    extract_data = pd.DataFrame(data)
    for idx, key in enumerate(key_array):
        extract_data = extract_data[
                        extract_data[key].str.contains(
                            value_array[idx], na=False
                        )]

    total = len(extract_data)
    if offset > total:
        # Offsetがデータ数を超えているとき空のリストを返す
        ret_value = []
    elif offset-1 + count > len(extract_data):
        # 指定された数より残りのデータ数が少ないとき全て返す
        ret_value = extract_data[offset-1:].to_dict(orient='records')
    else:
        ret_value = extract_data[
                        offset-1:offset-1+count
                    ].to_dict(orient='records')

    return ORJSONResponse(content={
            'offset': offset,
            'count': len(ret_value),
            'total': total,
            'data': ret_value
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
def values(key: str,
           count: int = MAX_COUNT,
           offset: int = 1) -> ORJSONResponse:
    """指定されたキーのユニークなデータ一覧を取得."""
    ret, response = _check_offset_and_count(data, count, offset)
    if not ret:
        return response

    # ユニークなデータを取得
    extract_data = data[key].dropna().unique()
    total = len(extract_data)

    if offset > total:
        # Offsetがデータ数を超えているとき空のリストを返す
        ret_value = []
    elif offset-1 + count > len(extract_data):
        # 指定された数より残りのデータ数が少ないとき全て返す
        ret_value = extract_data[offset-1:].tolist()
    else:
        ret_value = extract_data[offset-1:offset-1+count].tolist()

    return ORJSONResponse(
        content={
            'offset': offset, 'count': len(ret_value), 'total': total,
            'values': ret_value
        }
    )


@app.get('/counts/{key}', response_class=ORJSONResponse)
def counts(key: str,
           keys: Optional[str] = None,
           values: Optional[str] = None,
           count: int = MAX_COUNT,
           offset: int = 1) -> ORJSONResponse:
    """指定されたキーのデータ数を取得."""
    ret, response = _check_offset_and_count(data, count, offset)
    if not ret:
        return response

    if data.columns.tolist().count(key) <= 0:
        return ORJSONResponse(
            status_code=404,
            content={'detail': f'Key {key} does not exists'})

    # ,区切りでパラメータを取り出す
    key_array = [] if(keys is None) else keys.split(',')
    value_array = [] if(values is None) else values.split(',')

    ret, response = _check_keys_and_values(data, key_array, value_array)
    if not ret:
        return response

    # キーごとに値で絞り込む
    extract_data = pd.DataFrame(data)
    for idx, k in enumerate(key_array):
        extract_data = extract_data[
                        extract_data[k].str.contains(
                            value_array[idx], na=False
                        )]

    # キーごとのデータ数を取得
    extract_data = extract_data.groupby(key).\
        size().sort_values(ascending=False)

    total = len(extract_data)
    if offset > total:
        # Offsetがデータ数を超えているとき空のリストを返す
        pass
    elif offset-1 + count > len(extract_data):
        # 指定された数より残りのデータ数が少ないとき全て返す
        extract_data = extract_data[offset-1:]
    else:
        extract_data = extract_data[offset-1:offset-1+count]

    ret_value = []
    idxs = extract_data.index.tolist()
    vals = extract_data.values.tolist()

    for i, idx in enumerate(idxs):
        ret_value.append({'key': idx, 'count': vals[i]})

    return ORJSONResponse(
        content={
            'offset': offset, 'count': len(ret_value), 'total': total,
            'counts': ret_value
        }
    )


def _task():
    """データの更新処理."""
    global data
    lock = threading.Lock()
    lock.acquire()
    data = _load_data(location)
    lock.release()


def _update_task():
    """データの更新タスク."""
    # 定期更新をスケジュール (3ヶ月に1回)
    schedule.every(90).days.do(_task)
    while True:
        schedule.run_pending()
        sleep(3600*3)


# スレッドの開始

if not os.getenv('TEST', False): 
    t = threading.Thread(target=_update_task)
    t.start()
