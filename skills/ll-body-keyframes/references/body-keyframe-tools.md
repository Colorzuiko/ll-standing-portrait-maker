# 肢體四格工具與交付

需要Python 3.10+與Pillow；在本技能目錄使用`python -m pip install -r requirements.txt`。工具不呼叫圖片服務，不依賴另一套眼嘴技能或遊戲插件。每次指定新的輸出目錄；已存在即拒絕，來源圖不覆寫。

## plan：獨立動作清單

```sh
python -X utf8 scripts/body_keyframes.py plan --character hero --numbers 31 --out /project/output/body/hero/run-001
```

輸出`body-manifest.json`與`sources/`清單快照。省略`--numbers`才規劃全部項目；指定數字可選多項，保持原編號順序。`--catalog`指定表情Markdown／JSON，`--body-catalog`指定另一份肢體Markdown。正式版本為43新增／17沿用，v2為35／25，數量依實際所選清單計算。

manifest為`workflow=body-keyframes`、`scope=body-only`、`requires_face_animation_run=false`。每項含臉部語意與肢體提示，但沒有A表情、眼睛或嘴型生成任務。`reuse_default`標記`reference_only`且不建立四張占位圖；自訂清單的`undecided`須先決定動作。`stages`、參考來源、提示、生成紀錄與目視審查由實際製作補齊，不會由plan宣告通過。

## split：2×2等分與共同補邊

```sh
python -X utf8 scripts/body_keyframes.py split --image /run/raw/work-2x2.png --out /run/frames
```

只接受RGBA PNG，寬高必須可被2整除。按左上、右上、左下、右下輸出`frame_1.png`至`frame_4.png`，預設720×720。四格使用相同的透明補邊，奇數補邊差額放右／下，不重採樣、不逐格置中；連透明像素的隱藏RGB也保留。`source-sheet.png`複製原圖，`split-record.json`保存SHA、來源象限、原生格大小、補邊與可完全重建來源的檢查。

例如1254×1254原圖，每格627×627，左／上各46、右／下各47。若原生格大於720，工具拒絕；先另存整張工作圖的一次共同尺寸對應及紀錄，再對標準化圖分格。不允許各格不同的縮放或裁切。`--frame-size`只供明確指定其他交付尺寸，不用它偷偷變更本次720要求。

## pack：選用的圖集與預覽

```sh
python -X utf8 scripts/body_keyframes.py pack --frames /run/frames/frame_1.png /run/frames/frame_2.png /run/frames/frame_3.png /run/frames/frame_4.png --out /run/pack --preview --duration-ms 350
```

必須恰好四張同尺寸RGBA，按1→2→3→4原樣排成`body-4x1.png`。720格時總尺寸2880×720；這是裁切後的重排，不是生成工作圖格式。`pack-record.json`保留來源SHA，預設`runtime_binding=unbound`、`visual_review=pending`，不安裝或自動綁定LL。

`--preview`另輸出白底`review-2x2.png`與最大480方形的`preview.gif`。GIF只播放四張現有影格，不補中間格；GIF量化不影響原始PNG。`--duration-ms`須為正的10毫秒倍數。白底預覽不能取代深底與透明邊緣檢查，也不能證明動作適合循環；是否循環需目視判定。

## 完成狀態

交付包含原始2×2、四張完整PNG、提示詞／參考順序、來源SHA、生成與尺寸對應紀錄、分格紀錄及目視結果。若要求預覽則加入定格板與GIF；若要求LL整合，另檢查目標播放器、烘焙圖層、速度、終點與實機行為。規劃、像素檢查、打包與目視驗收是不同狀態，不以工具成功冒稱美術已接受或MZ已測。
