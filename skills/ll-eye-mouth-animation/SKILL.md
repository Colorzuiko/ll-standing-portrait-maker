---
name: ll-eye-mouth-animation
description: "製作固定姿勢立繪的眨眼、說話與張嘴差分。共用一張母圖，在臉部矩形橫向四格合繪眼嘴，再裁出獨立直向圖集；不製作肢體定格動作。"
---

# 固定姿勢的眨眼與說話立繪

只製作同一固定姿勢的臉部表情、眨眼及嘴型。手臂、軀幹、頭頸角度與畫布固定；肢體動作使用另一套流程，不列為本次完成條件。

## 來源與母圖

- 使用[正式60表情清單](references/expression-catalog-60.md)或使用者明確清單，不自行換一套編號。只處理本次要求的範圍；「眨眼／張嘴」不等於自動開始完整60表情。
- 實際檢視角色設定與已選版本，依[畫風與構圖](references/style-and-layout.md)建立一張共用母圖，預設720×720 RGBA、完整頭頂至大腿附近、右向三分之四站姿及雙臂自然垂放；使用者構圖優先。畫風不預設為賽璐璐。
- 先驗收辨識、畫風、頭頸與透明輪廓，完成必要的去背／不透明區修整後，再凍結母圖SHA、臉部矩形、允許遮罩與保護區。後續表情都直接引用同一母圖，不串接上一表情重畫。
- 第09、31號只在這套流程製作對應臉部語意；扶額、雙食指撐笑等手勢交給肢體流程。原圖若已有遮臉手指，不能把眼嘴補片疊到手上。

## 臉部局部四格

1. 從已接受母圖截取固定臉部矩形，只允許該表情的眼眉嘴、臉頰及必要符號變動。鼻樑、髮際、下顎與其他保護區不變。
2. 每表情在**同一張橫向4欄1列**局部工作圖，同時繪製眼睛與嘴巴。每格皆為同一裁切範圍；不生成2×2完整人物，不分開生成眼睛與嘴巴畫布。
3. 一般同格配對：0=休止眼／休止嘴，1=半閉眼／小開口，2=閉眼／大開口，3=半睜眼／中開口。休止狀態依表情語意，不強制所有0格睜眼閉嘴。
4. 已有接受的休止五官時，0格使用既有像素；其餘局部候選按原座標回貼，透過眼／嘴各自遮罩分別驗收。整組共同尺寸對應最多做一次，不逐格對臉或拉伸。
5. 交付眼睛與嘴巴各**直向1欄4列**圖集，座標來自最終720×720母圖。生成4×1與交付1×4用途不同，不拿格序偏移當原圖座標。

特殊規則先讀[表情協調](references/expression-coordination.md)：53／60以雙眼睜開為休止，只眨固定一眼；60嘴0閉嘴無舌，再依序舌尖、部分伸出、最長伸出。固定閉眼與符號眼不強制普通雙眼眨眼。29／30／34／42保留溫和漫畫表現，不採恐怖五官。

## 像素、分層與驗收

依[局部差分契約](references/layers-and-qa.md)合成，只改允許區RGB，整張alpha及保護區維持母圖；移動肢體輪廓不適用這個契約。膚色補片有邊圈，保護鼻樑與下顎，避免雙下顎與接縫。

每表情驗證休止眼0＋嘴0完整重建該表情base，以及16個眼嘴組合、白／深底、原尺寸／縮圖、鏡像縮放、說話停止及眨眼返回休止。**16組合由程式疊圖，不另外生圖。**共用素材依[共用判定](references/eye-mouth-sharing.md)檢查完整四格、定位、邊圈與語意，不固定圖集組數。

## 獨立工具與匯出

以下以本技能目錄為工作目錄；輸出使用專案內新run。專用入口會把`plan`固定為face-only，並拒絕把含肢體動作的計畫當眼嘴包匯出：

```sh
python -X utf8 scripts/eye_mouth_portrait.py probe --plugin assets/LL_StandingPictureDirect.js
python -X utf8 scripts/eye_mouth_portrait.py plan --character hero --plugin assets/LL_StandingPictureDirect.js --out /project/output/eye-mouth/hero/run-001
```

`plan`只建立規劃，不生成或驗收素材。需要明確子集可用`--count N`或使用者清單`--catalog`。舊schema保留的body參照只是相容資料，不能當成新增肢體任務。

```sh
python scripts/split_work_sheet.py --image /run/face-work.png --columns 4 --width 160 --height 200 --out /run/face-split
python scripts/eye_mouth_portrait.py compose --base /run/masters/default.png --candidate /run/face-split/frame_1.png --rect 300 100 460 300 --mask /run/masks/eyes.png --protect /run/masks/protect.png --out /run/eyes1.png
python scripts/eye_mouth_portrait.py export --manifest /run/manifest.json --out /project/output/eye-mouth/hero/export-001
```

示例座標必須換成本次量測。詳細schema見[manifest與匯出](references/manifest-and-export.md)，只讀face-only相關部分；舊整合模式的A完成後才做B限制不套到另一套獨立肢體技能。

正式共用版只交付一張共用底圖、每表情局部臉圖與實際眼／嘴圖集，不另複製60張完整靜態PNG。保留正式編號與插件副本中的實測對照。只有要求匯出時才處理插件；沒有遊戲目標可用附帶模板，不覆寫遊戲的插件或`plugins.js`。

實際開啟匯出預覽檢查載入、眼嘴播放與停止。素材QA、HTML、最小宿主及MZ實機分開記錄；未測MZ維持not_run。交付提示詞、來源／畫風觀察、允許遮罩、量測座標與QA，不宣稱本包包含肢體定格動作。
