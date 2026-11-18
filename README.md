# LL 立繪：兩套獨立製作流程

本儲存庫將肢體定格與固定姿勢的眨眼、張嘴拆成兩套可分別使用的技能。兩套共用角色來源與正式編號，各自規劃、製作與驗收；製作肢體不必先完成60個臉部表情。

| 需求 | 入口 | 製圖與交付 |
| --- | --- | --- |
| 手勢、身體動作、四格定格或循環 | [ll-body-keyframes](skills/ll-body-keyframes/SKILL.md) | 同畫布2×2四個完整人物階段，裁切並共同補邊至720×720；可另輸出預覽與4×1圖集 |
| 固定站姿的表情、眨眼與說話 | [ll-eye-mouth-animation](skills/ll-eye-mouth-animation/SKILL.md) | 共用母圖，臉部矩形橫向4×1合繪眼嘴，交付獨立直向1×4眼／嘴圖集 |

原[SKILL.md](SKILL.md)保留為選擇入口。兩個子資料夾各自包含所需工具、參考與資源，不必連同另一套技能使用。這是儲存庫內的技能檔，尚未全域安裝。圖片由當次可用的圖像工具生成；附帶工具只規劃、分格、合成、驗證及匯出。

## 肢體四格

請讀取肢體入口並提供角色設定、已選定畫風、指定編號與新輸出目錄。例如：

> 使用 ll-body-keyframes，依已選角色版本製作第31號動作。在同一張2×2畫布繪製四個肢體階段，按[[1,2],[3,4]]裁切後共同補邊至720×720，提供定格與循環預覽。

以技能目錄為工作目錄：

```sh
python -m pip install -r requirements.txt
python -X utf8 scripts/body_keyframes.py plan --character hero --numbers 31 --out /project/output/body/hero/run-001
python -X utf8 scripts/body_keyframes.py split --image /project/output/body/hero/work-2x2.png --out /project/output/body/hero/run-001/frames
python -X utf8 scripts/body_keyframes.py pack --frames /run/frames/frame_1.png /run/frames/frame_2.png /run/frames/frame_3.png /run/frames/frame_4.png --out /project/output/body/hero/pack-001 --preview
```

plan不生成圖片；pack不代表美術驗收或遊戲綁定。預設四格完整人物，局部／分層製法另作可選變體；保留使用者比較後選定的版本。詳見[肢體工具及交付](skills/ll-body-keyframes/references/body-keyframe-tools.md)。

## 眨眼與張嘴

請讀取眼嘴入口並提供角色設定、固定姿勢母圖、目標LL插件（如需匯出）與新輸出目錄。例如：

> 使用 ll-eye-mouth-animation，固定母圖姿勢，只在臉部矩形合繪橫向眼嘴四格，再拆成獨立直向眼睛、嘴型圖集；本次不製作肢體動作。

以技能目錄為工作目錄：

```sh
python -m pip install -r requirements.txt
python -X utf8 scripts/eye_mouth_portrait.py probe --plugin assets/LL_StandingPictureDirect.js
python -X utf8 scripts/eye_mouth_portrait.py plan --character hero --plugin assets/LL_StandingPictureDirect.js --out /project/output/eye-mouth/hero/run-001
python -X utf8 scripts/eye_mouth_portrait.py export --manifest /project/output/eye-mouth/hero/run-001/manifest.json --out /project/output/eye-mouth/hero/export-001
```

plan強制face-only；完成素材與實際QA後才export。專用入口拒絕將含肢體動作的計畫當眼嘴包匯出。只做指定範圍，不因要求眨眼自動展開全部60項。53／60的單眼眨眼與60的吐舌規則見[表情協調](references/expression-coordination.md)。休止格重建與16個眼嘴組合由程式檢查，目視審查保留實際結果。

交付共用底圖、局部臉圖、實際眼嘴圖集、LL插件副本與離線預覽；不自動安裝到遊戲。素材、HTML與MZ實機驗證分別記錄。

## 共用規則與相容

畫風依本次主設定圖或使用者明示，不內建特定角色、賽璐璐或固定明暗風格。兩套使用[正式60表情](references/expression-catalog-60.md)與必要的肢體語意；肢體原表為43新增／17沿用，明確選用[v2](references/body-language-catalog-60-v2.md)時為35／25。保留正式編號，不生成沿用項目的占位PNG。

根目錄的 `ll_portrait_pipeline.py`、舊manifest與LL模板v1.4.0保留整合相容行為。原full模式的A完成後才做B限制，只適用舊整合包；新的肢體流程獨立執行。舊結構詳見[manifest與匯出](references/manifest-and-export.md)。現有角色成品、試作與選擇紀錄不因拆分而改寫。

## 維護與驗證

根目錄的共用腳本、清單、眼嘴參考及LL資源為維護來源；子技能中的副本由同步工具刷新。`bundle-sources.json`保存來源與SHA，避免兩份工具默默分歧。各子技能自己的SKILL、介面說明與肢體專用參考直接在對應資料夾維護。

Git以`.gitattributes`固定文字檔的LF換行，讓不同系統取得相同來源位元組，避免換行轉換使SHA檢查失敗。

在儲存庫根目錄執行：

```sh
python -X utf8 scripts/sync_workflow_skills.py
python -X utf8 scripts/sync_workflow_skills.py --check
python -X utf8 -m unittest discover -s scripts -p "test_*.py"
python -X utf8 scripts/sync_workflow_skills.py --package output/skill-packages/new-version
```

打包只收兩套技能各自需要的明列檔案，不包含角色圖、歷史輸出或快取。輸出目錄必須不存在；每個ZIP含一個獨立技能資料夾。Python工具需要3.10+與Pillow。插件未修改時不必重新測試遊戲；若修改插件，可另跑 `node scripts/test_body_player.cjs`。瀏覽器檢查工具見 `scripts/test_report.cjs`。

本次拆分不會全域安裝技能或變更遊戲插件。

Windows測試若遇到暫存路徑過長，將測試使用的TEMP／TMP指向專案內較短目錄後重跑；這不需要變更系統設定。
