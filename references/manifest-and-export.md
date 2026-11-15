# manifest與共用版匯出

## 正式清單與規劃

`plan`預設直接解析expression-catalog-60.md及body-language-catalog-60.md，核對編號與中文名稱。附帶JSON只是衍生快照，不作隱含fallback。manifest保留兩份Markdown的來源與SHA，原表情提示保留在face_prompt，肢體文字保留body_hint/body_prompt。

```sh
python scripts/ll_portrait_pipeline.py plan --character phebe --plugin /path/LL_StandingPictureDirect.js --out /project/output/expression-portraits/phebe/new_run
```

完整計畫有60項A、44項B new_pose及16項reuse_default；new_pose還要製作／驗收並填motion_id，不是列入計畫即完成。使用者明確只要臉部時用 `--scope face-only`，B仍保留catalog_mode但mode記reuse_default、reason表明本次未包含B；完整原技能批次狀態不能由此冒稱完成。

使用者清單可用 `--catalog /path/catalog.md`（相同四欄表格式）或顯式JSON清單（no/id/name/face，其他欄位可選），自訂肢體Markdown用 `--body-catalog`。自訂JSON沒有body_mode時保留undecided，不自行全設沿用。`--count N`只作明確子集，i仍保留原清單編號。

美術輸入路徑以run內相對路徑記錄，不允許絕對路徑或`..`逃出run；來源先複製進run並核對SHA。插件可使用明確絕對路徑讀取。新run／export不覆寫既有輸出。

## 工作資料

schema_version=1；canvas預設[720,720]。每個pose保存master、sha256、face_mask、protect，可選face_roi=[left,top,right,bottom)。每個expression保存no/id/name/face_prompt、pose_id、工作base、status、rest_eyes/rest_mouth、eyes/mouth及review。

- A只生成一張共用母圖。工作base是將局部休止臉圖回貼母圖後合成的全尺寸驗收來源，不是另外生成的全身圖，也不是正式runtime重複存檔。
- 每表情可用combined_sheet記錄raw、normalized、columns=4、rows=1、edit_rectangle=[left,top,right,bottom)、eyes_and_mouth_generated_together=true，以及原生尺寸、目標尺寸與整組共同映射。臉部編輯矩形不能拿本次角色的範例座標當固定值。
- eyes/mouth各記mask、roi、四張完整畫布frames、frame_wait及order；eyes另記auto、interval_min/max。
- frames必須已受遮罩約束；ROI維持同一裁切框、兩像素不改動邊圈，不能每格緊貼輪廓重裁。
- eye0+mouth0必須完全重建工作base。readonly／語意／接縫等目視review由實際驗收者填寫，腳本不把pending自動改passed。
- review欄位為semantic、registration、seams、combinations、transparency。status=accepted仍須全部passed。
- generation_log保存實際圖像來源、主設定圖SHA、畫風觀察、提示詞、provider工具／可取得模型名、生成呼叫與工作圖標準化映射；不用裁切數推算生成次數。

B new_pose的motion記錄id/expression_id/pose_id、由左至右四張完整frames、columns=4、frame_duration=15、loop=false、end=hold（可設restore）、overlay_mode=baked、四格frame_coordinates（eyes與mouth均null）、review及adapter。原生LL v1.4會自動綁定baked圖集並記native_bound；自訂verified adapter須指向run內存在的config及evidence。舊目標未綁定時runtime_complete=false。

## 分格與合成

```sh
python scripts/split_work_sheet.py --image run/normalized/01-face-work.png --columns 4 --width 160 --height 200 --out run/work/01/face-split
python scripts/ll_portrait_pipeline.py compose --base run/masters/default.png --candidate run/work/01/face-split/frame_0.png --rect 300 100 460 300 --mask run/masks/default-face.png --protect run/masks/default-protect.png --out run/work/01/base.png
python scripts/ll_portrait_pipeline.py compose --base run/work/01/base.png --candidate run/work/01/face-split/frame_1.png --rect 300 100 460 300 --mask run/masks/01-eyes.png --protect run/masks/default-protect.png --out run/work/01/eyes1.png
python scripts/ll_portrait_pipeline.py compose --base run/work/01/base.png --candidate run/work/01/face-split/frame_1.png --rect 300 100 460 300 --mask run/masks/01-mouth.png --protect run/masks/default-protect.png --out run/work/01/mouth1.png
```

上例僅示範編輯矩形[300,100,460,300)，每格160×200、合繪工作圖640×200；實際尺寸依母圖重新量測。split只接受RGBA PNG與正確總尺寸，生成的臉部工作圖明確用`--columns 4`橫向分格，不重採樣或置中。舊直向圖集仍可明確用`--columns 1`拆分，這不是生成工作圖的方向。

眼睛與嘴巴來自同一候選臉格，只在回貼驗收及輸出時分層；最後的插件圖集才各為1欄4列。B仍是完整身體橫向4欄1列，720單格時為2880×720。非標準原圖先記錄整組共同映射；已存在接受的休止圖時，0格取該base，不採用漂移的生成0格。

## 預設共用版匯出

```sh
python scripts/ll_portrait_pipeline.py export --manifest run/manifest.json --out run/export-v1
```

匯出先檢查插件SHA、實際欄位、工作母圖SHA、像素契約、休止格、16組合、A/B狀態與adapter，再拆層到新目錄。每個姿勢保留一張共用底圖；每表情只交付臉圖。臉圖範圍自動包含眼嘴ROI及全部實際差異，也可先指定pose.face_roi，超出則拒絕匯出。

為避免半透明輪廓重複疊加，變動的非不透明像素移到臉層，其他半透明邊緣只保留在共用底圖。工具對存檔後重建的全RGBA及全部16組合核對；失敗就停止，不用背景色或再去背掩蓋。一般透明區新增符號須另有blend契約，本通用匯出不支援更改全透明像素的隱藏RGB。

眼睛／嘴型按種類、姿勢ID、ROI、尺寸與完整RGBA去重；輸出eyes_j和mouth_k，不以雜湊作檔名。組數不固定。i依正式編號，不因partial少幾項而重新排序。

```text
export-v1/
  runtime/img/pictures/phebe/
    phebe_base.png                 # default姿勢共用底圖
    phebe_1.png                    # 正式01堅定的局部臉圖
    ... phebe_60.png               # 正式60吐舌眨眼
    eyes_1.png ... eyes_j.png      # 1欄4列局部圖集
    mouth_1.png ... mouth_k.png
    phebe_body_<motion_id>.png     # 僅實際完成的B，完整橫向4欄1列
  plugin/LL_StandingPictureDirect.js
  config/faceSettings-readable.json
  config/faceSettings-parameter.json
  config/expression-mapping.json
  config/bodyMotions-readable.json  # JS內建身體對照的核對快照
  config/motions.json
  config/preview-settings.json
  qa/pixel-verification.json
  manifest.json
  report.html
  body-report.html
```

有其他A姿勢時命名phebe_base_<pose_id>.png，不強迫與default共用。B只記一份，HTML以相同檔案播放，runtime中的PNG保持單一角色資料夾。共用版不交付default/下的60張完整靜態副本；靜態圖由HTML疊出。

plugin副本內的LL_EXPORTED_BODY_MOTIONS保存身體動作登錄，ACT一次播放、ACT後加\loop才循環；LL_EXPORTED_FACE_SETTINGS是實際內建臉／眼嘴對照，含本批實測座標和速度；不需匯入JSON快照。其他來源的builtin表不能覆蓋正式編號；工具停用舊菲比範例表及其不相符的別名。使用者既有同名參數仍優先，安裝時需核對，不能無條件覆蓋其他角色。

## 進度、相容與證據

- 預設只接受A/B/adapter皆完成；`--allow-partial`可交付已通過的A與已完成B，其他項目標pending或unbound，沒有占位PNG。A未完成時不得開始或匯出新B。
- `--layout legacy`才保留舊完整底圖匯出，供不支援共用臉圖的LL使用。此模式使用舊式struct參數與靜態報告，不具新共用版容量或內建對照承諾。
- `--qa-images`才另外存4×4組合接觸圖；預設HTML可手動選16組合，不繪製或強制輸出矩陣。
- preview_settings可在manifest填run內JSON路徑或物件，包含來源、width/height及profile（origin/x/y/x2/y2/x3/y3/x4/y4/reverse/scaleX/Y/opacity）。有遊戲實值就用實值；沒有就生成1280×720建議配置並明示。特殊tone/blend／其他插件圖層不在通用HTML精確模擬範圍。
- report.html內嵌設定，圖片用相對路徑；整個export資料夾可離線開啟，不fetch外部JSON，不依賴工作區絕對路徑。檢查表情／B選取、眼嘴、訊息說話停止、鏡像縮放、局部放大與瀏覽器錯誤。
- body-report.html使用相同B圖集列出全部已接受姿勢；可搜尋、看最終格或橫向四格定格、播放一次及選格、切換白／深／透明格背景，並列出沿用預設站姿的表情。
- manifest區分complete、art_complete、runtime_complete、engine_verification。靜態probe、檔案驗證、瀏覽器與最小宿主都不能自動變成MZ實機通過。
- storage統計A遊戲PNG對比，以及包含B的全部runtime容量。QA、HTML、插件、母檔及ZIP另計；2.34MB僅是先前替代清單圖包的實測值，不作固定目標。
