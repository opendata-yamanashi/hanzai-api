# 山梨県 犯罪オープンデータAPI

## 出典
- [山梨県の犯罪オープンデータ](https://www.pref.yamanashi.jp/police/p_anzen/hanzai_opendate.html)

## API 仕様
- https://opendata.yamanashi.dev/api/onsen/docs を参照

## ライセンス
本ソフトウェアは、[MITライセンス](./LICENSE.txt)の元提供されています。

## 開発者向け情報

### 環境構築の手順

- 必要となるPythonバージョン: 3.6以上

**起動方法**
``` bash
$ pip install -r requirements.txt
$ uvicorn app.main:app --reload
```
