# LL 立繪與眼嘴動畫製作

`ll-standing-portrait-maker` 是依角色設定圖與正式 60 表情／肢體清單，製作 RPG Maker MZ 對話立繪的 Codex 技能。畫風依本次角色設定圖決定。

固定姿勢共用一張母圖；各表情在臉部矩形內，以同一張橫向四格工作圖合繪眼睛與嘴巴，再拆成獨立眼嘴圖集。匯出時保留正式表情編號，並將本批對照嵌入 LL 插件副本。

## 內容

- **A：60 個表情**，共用底圖搭配局部臉圖，眼睛與嘴巴各為直向 1 欄 4 列圖集。
- **B：肢體語言**，正式清單預設 44 個新姿勢、16 個沿用預設站姿；新動作使用橫向 4 欄 1 列圖集。
- **LL 模板 v1.4.0**，支援共用底圖、局部臉圖、獨立眼嘴與原生身體動作播放器。
- **離線預覽**，匯出 `report.html` 與 `body-report.html`，使用交付素材檢查表情、眼嘴組合、鏡像、縮放與身體動作。
- **驗證工具**，檢查正式清單、來源雜湊、遮罩、休止格重建、眼嘴 16 組合、圖集去重與插件對照。

圖片需由可用的圖片生成／編輯工具製作；附帶腳本負責分格、合成、裁切、拆層與驗證。

## 取得與使用

[下載最新版 ZIP](https://github.com/Colorzuiko/ll-standing-portrait-maker/archive/refs/heads/main.zip)，解壓後將完整資料夾命名為 `ll-standing-portrait-maker`。保留 `SKILL.md`、`agents/`、`references/`、`scripts/` 與 `assets/` 的相對位置。

讓 Codex 讀取 [SKILL.md](SKILL.md)，並提供角色設定圖、工作輸出位置，以及目標 LL 插件。若沒有既定插件，可使用附帶的 `assets/LL_StandingPictureDirect.js` 作為目標。

可使用以下請求：

> 使用 $ll-standing-portrait-maker，依角色設定圖與正式表情／肢體清單製作立繪。A 共用一張母圖，以臉部矩形橫向四格合繪眼嘴，再裁出獨立直向圖集，依正式清單處理 B，輸出到新的 run／export 目錄。

執行圖片處理工具需要 Python 3.10 以上與 Pillow：

```sh
python -m pip install -r requirements.txt
```

## 命令列工具

以下命令在本資料夾執行；`my-project`、角色代碼及輸出位置請依實際專案調整。每次使用新的 run／export 目錄。

```sh
python -X utf8 scripts/ll_portrait_pipeline.py probe --plugin assets/LL_StandingPictureDirect.js
python -X utf8 scripts/ll_portrait_pipeline.py plan --character hero --plugin assets/LL_StandingPictureDirect.js --out ../my-project/output/hero/run-001
```

`plan` 建立待製作的清單與 manifest，不會自動生成或驗收圖片。依技能流程完成素材、遮罩、圖集與驗收記錄後，執行：

```sh
python -X utf8 scripts/ll_portrait_pipeline.py export --manifest ../my-project/output/hero/run-001/manifest.json --out ../my-project/output/hero/export-001
```

匯出包含 `runtime/img/pictures/<character>/`、`plugin/`、`config/`、`qa/`、manifest 與預覽 HTML。完整結構與選項見 [manifest 與匯出](references/manifest-and-export.md)。

## 測試

Python 測試需要 Pillow；插件測試另需可執行 `node` 的 Node.js 環境：

```sh
python -X utf8 -m unittest discover -s scripts -p "test_*.py"
node scripts/test_body_player.cjs
```

Windows 若因暫存資料夾過深而遇到路徑長度錯誤，請將測試用的 `TEMP`／`TMP` 指向較短路徑。`-X utf8` 可避免中文系統預設編碼影響測試。

`scripts/test_report.cjs` 是選用的瀏覽器檢查工具，需要 Playwright 與 Chrome；以 `PLAYWRIGHT_MODULE`、`CHROME_BINARY` 指定本機位置，並傳入已完成的匯出目錄。這些檢查不會呼叫圖片服務。

## 參考

- [正式 60 表情清單](references/expression-catalog-60.md)
- [正式肢體語言清單](references/body-language-catalog-60.md)
- [畫風與構圖](references/style-and-layout.md)
- [局部差分與 QA](references/layers-and-qa.md)
- [眼嘴素材共用判定](references/eye-mouth-sharing.md)
- [LL 插件契約與控制碼](references/plugin-contract.md)

匯出器只產生新的交付資料夾與插件副本，不會自動安裝到遊戲。素材驗收、HTML 預覽、最小宿主測試與完整 MZ 實機驗證分開記錄；完整遊戲相容性仍需實際驗證。

本儲存庫包含技能與工具，不包含角色設定圖、歷史生成圖包、工作輸出或暫存檔。
