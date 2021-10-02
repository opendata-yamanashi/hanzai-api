# 山梨県 犯罪オープンデータAPI

## 出典
- [山梨県の犯罪オープンデータ](https://www.pref.yamanashi.jp/police/p_anzen/hanzai_opendate.html)

公開している罪種は窃盗で、手口は

　　　　ひったくり・車上ねらい・部品ねらい・自動販売機ねらい

　　　　自動車盗・オートバイ盗・自転車盗
   
となります。
(出典元より)

## API 仕様
- https://opendata.yamanashi.dev/api/onsen/docs を参照

## ライセンス
本ソフトウェアは、[MITライセンス](./LICENSE.txt)の元提供されています。

## 開発者向け情報

### 環境構築の手順

- 必要となるPythonバージョン: 3.8以上

**起動方法**
``` bash
$ pip install -r requirements.txt
$ uvicorn app.main:app --reload
```

## 使い方

- 基本の使い方
<img src="https://github.com/opendata-yamanashi/hanzai-api/blob/main/img/10_%E7%8A%AF%E7%BD%AA%E3%82%AA%E3%83%BC%E3%83%97%E3%83%B3%E3%83%87%E3%83%BC%E3%82%BFAPI%E3%81%AE%E4%BD%BF%E3%81%84%E6%96%B9_%E5%9F%BA%E6%9C%AC.svg" width="600">

- 任意のキーで絞り込む
<img src="https://github.com/opendata-yamanashi/hanzai-api/blob/main/img/11_%E7%8A%AF%E7%BD%AA%E3%82%AA%E3%83%BC%E3%83%97%E3%83%B3%E3%83%87%E3%83%BC%E3%82%BFAPI%E3%81%AE%E4%BD%BF%E3%81%84%E6%96%B9_%E4%BB%BB%E6%84%8F%E3%81%AE%E3%82%AD%E3%83%BC%E3%81%A7%E7%B5%9E%E3%82%8A%E8%BE%BC%E3%82%80.svg" width="600">
 
