# 手邊相機配方本

Ricoh GR IV、GR IIIx 與 Sony RX100 VII 可以直接在機身上設定的畫面配方，附原作者出處與官方參數表；另附 GR IV 刷 [GR4-LUTSmith](https://github.com/lemonadesaltbagel/GR4-LUTSmith) 的檢查與還原清單。

網站：https://henrychao521.github.io/camera-looks/

## 檔案

| 路徑 | 內容 |
|---|---|
| `data/gr4.json`、`data/gr3x.json`、`data/rx100.json` | 配方與官方參數（每組附 `sourceUrl`） |
| `GR4_LUTSmith_檢查與還原清單.md` | 刷機清單正本 |
| `template.html` | 頁面樣板 |
| `build.py` | 產生 `docs/index.html`（GitHub Pages）與 `dist/index.html` |
| `docs/` | GitHub Pages 發布目錄 |

```bash
python3 build.py
```

## 資料來源與核對方式

- 配方數值照原作者網頁，著作權歸原作者；畫面描述為本站改寫。
- 官方參數以 Ricoh GR IV 英文說明書、Ricoh 官方規格頁與 Sony RX100 VII 說明指南為準；說明書沒寫的部分列在各頁「查不到或有出入的地方」。
- 配方由兩個不同家族的模型（Claude、Gemini）各自獨立蒐集，重疊部分逐項比對一致；新增的配方再逐一打開原頁核對，只收原頁有完整參數的。

本站與 Ricoh、Sony 無關。改機（例如 LUTSmith）屬非官方修改，風險自負。
