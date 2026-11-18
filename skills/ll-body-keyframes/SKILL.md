---
name: ll-body-keyframes
description: "製作角色肢體定格、手勢與姿勢循環。在同一張2×2畫布繪製同表情的四個動作階段，再裁切補邊至720×720；不製作獨立眨眼或張嘴圖集。"
---

# 肢體定格動作

依角色設定與指定動作，製作可檢視的四格完整立繪。此流程可獨立執行，不要求已有臉部動畫或先完成60個表情。

## 本次依據

- 讀取角色設定圖、已選定畫風／版本及指定表情編號。畫風依本次來源或使用者明示，不預設賽璐璐、高飽和或特定角色。
- 編號與語意以[正式表情清單](references/expression-catalog-60.md)及[肢體清單](references/body-language-catalog-60.md)為準。只規劃本次指定項目；使用者選新版肢體時才改用[肢體v2](references/body-language-catalog-60-v2.md)。
- `reuse_default`只記沿用參照，不生成四份相同人物充數；若使用者明確要求該項新增動作，記錄覆寫理由與實際手勢。
- 已選定舊版時，以該版動作呈現為準。不要只因局部差分的像素分數較好，就替換使用者比較後喜歡的成品。

## 製作四格動作

1. 寫出同一表情的四個肢體階段，例如準備、接近、接觸峰值、回收。每格應有可辨識的肢體變化；不能只換眨眼或嘴型冒充肢體四格。停留、循環或回復依本次動作決定。
2. 使用當次可用的圖像生成技能，傳入實際角色圖作參考。**預設在同一張畫布直接繪製四個完整定格**，2欄2列，讀序`[[1,2],[3,4]]`；不分四次生圖後冒稱同畫布生成。
3. 每格採相同人物比例、方向與構圖，預設完整頭頂至大腿附近；保留手勢與肘部邊距。頭頸接合與護甲關節自然，允許動作必要的輪廓及投影變化，不以像素完全相同限制肢體表演。畫風與構圖依[參考規則](references/body-style-and-layout.md)。
4. 生成透明PNG，不把格線、編號或文字畫進素材。完成後沿等分象限裁切；四格以**同一透明補邊**擴張至720×720，不逐格置中、對臉或拉伸。原生單格大於720時，先記錄一套共同尺寸對應，不能暗中各自縮放。
5. 檢視四格定格、手臉接觸、肩肘與護甲、白／深底及循環。第31號等碰臉動作採完整烘焙五官，保留前景手指遮擋，不另外疊眼嘴到手背上。

本次明確選用局部差分或分層方案時，閱讀[分層變體](references/layered-body-variant.md)。它是替代製法，不改寫四格順序或冒稱使用者已接受；移動手臂必須允許動態區RGBA輪廓改變，不能套用臉部全圖alpha固定契約。

## 獨立工具

以下路徑以本技能目錄為工作目錄；輸出使用專案內新的run，不寫入技能安裝目錄。工具不呼叫圖片服務，也不自動把目視狀態改成通過。

```sh
python -X utf8 scripts/body_keyframes.py plan --character hero --numbers 31 --out /project/output/body/hero/run-001
python -X utf8 scripts/body_keyframes.py split --image /project/output/body/hero/work-2x2.png --out /project/output/body/hero/run-001/frames
```

`plan`只建立body-only計畫，不建立60個A表情；`split`保留原圖像素、alpha與四格共同補邊。使用者要循環預覽或橫向遊戲圖集時，再對已驗收影格打包：

```sh
python -X utf8 scripts/body_keyframes.py pack --frames /run/frames/frame_1.png /run/frames/frame_2.png /run/frames/frame_3.png /run/frames/frame_4.png --out /project/output/body/hero/pack-001 --preview
```

工具與紀錄見[工具及交付](references/body-keyframe-tools.md)。**2×2是生成工作圖**；選用的4×1圖集是裁切後重排，不能混淆生成順序。打包不代表已接上LL或完成MZ驗證。

## 交付與邊界

交付原始2×2工作圖、四張720×720 RGBA、定格／循環預覽、完整提示詞與參考順序、裁切補邊紀錄、實際目視結果。正式編號不因只做一項而重新編碼。

只有明確要求LL整合時，才另外檢查目標插件與圖集播放器。此技能不生成獨立眼／嘴動畫，不套用眼嘴16組合驗收，也不為肢體試作先建立臉部manifest。保留來源、既有成品及使用者選擇；不安裝遊戲或覆寫插件。
