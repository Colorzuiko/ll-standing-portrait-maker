# 角色設定圖、畫風與構圖

本文件的母圖凍結與臉部4×1規則用於固定姿勢的眼嘴流程。獨立肢體流程使用同畫布2×2完整人物四階段，不受下文「不生成四個全身」的臉部局部限制。

## 畫風來源：讀取人物設定圖

**技能不自定義繪製畫風。每位角色的畫風由當次採用的人物設定圖決定**，包含線條、筆觸、上色、陰影、高光、材質、配色及五官比例。提示詞只描述從圖中觀察到的特徵，不能用技能內建的通用風格覆蓋設定圖。不將 `Old_version`、`old_verson` 或歷史圖輯列為必要輸入。使用者另有明確指定時優先採用，並記錄來源與覆寫內容。

### 先讀圖，再建立本次繪製依據

- 實際開啟並檢視人物設定圖，記錄其線條粗細／顏色、筆觸、明暗過渡、高光形狀、髮絲處理、材質表現，以及眼型、臉型、身形與配色。描述限於可觀察特徵，不自行添加畫師名稱、年代或風格標籤；不預設日系動漫、賽璐璐、固定明暗階數或固定光源。
- 同批有多張設定圖時，以使用者指定的主設定圖決定畫風，其他圖按用途補充服裝、配件或背面結構，不混合互相矛盾的渲染方式。未指定時優先採用該角色已驗收的主設定圖；若來源仍有無法判定的畫風衝突，先確認來源再批次製作。
- 生成／編輯時傳入實際設定圖作為角色設計與畫風參考，並說明多張參考圖各自的用途；文字摘要不取代可用的圖像參考。沒有設定圖時先尋找已授權的角色資料；仍無可用圖時，請使用者提供或指定畫風來源，不自行套用預設畫風。

### 遊戲素材與細節密度

- **用途與構圖**：720×720 遊戲對話立繪，單一人物、透明背景。預設頭頂至大腿附近的構圖，頭頂／帽飾完整，左右髮型與必要手勢留出安全邊距；下緣可自然截斷大腿。不為容納腳部而縮小整人。先固定人物占比、頭部大小與位置，再製作差分。構圖要求不改變設定圖的畫風或角色比例。
- **簡化原則**：以最終尺寸的可讀性與差分穩定性調整細節；優先省略縮小後不可辨識的裝飾、重複紋理及零碎線條。保留來源的線條特徵、筆觸、明暗處理與材質差異，不因簡化而一律改成色塊上色、細線或柔光。
- **保留項目**：角色的五官比例、眼型、年齡感、髮型輪廓、主要服裝結構、配色、代表性圖案及配件。表情、手部與配件結構仍須正確；不擅自增添裝飾，不以另一種臉型或人物比例取代來源設計。

### 母圖提示詞模板

填入從設定圖觀察到的特徵，以及角色、姿勢、朝向與表情描述後使用；此模板用於建立母圖，並須附上實際設定圖。背景透明也須同步設定生成工具的透明輸出選項（若有），不能只依賴文字。

```text
Create one game dialogue portrait, composed for a final 720 × 720
transparent PNG. Use the supplied primary character sheet as the authority
for both character design and drawing style.
Observed visual traits from that sheet: {observed_reference_traits}.
Character details: {character_description}.
Pose and facing: {pose_and_facing}. Expression: {expression}.
Frame from the complete top of the head or headwear to approximately the
thighs, with safe side margins for hair and required gestures. Keep the
face large enough for clear expressions at game display size.

Faithfully preserve the reference's line quality, brushwork, coloring,
shadow transitions, highlights, material rendering, palette, and facial
and body proportions. Preserve the character's eye shape, age, and personality.
Adapt detail density for readability at the final game display size:
omit only nonessential microdetails and repetitive decoration that would
become visual noise. Retain signature features, essential costume structure,
and recognizable accessories. Simplify using the reference's own drawing
methods. Keep the rendering consistent across expression and pose variants.
```

限制詞附於同一次請求；工具沒有獨立負向提示詞欄位時，作為一般提示詞中的限制段落：

```text
Do not reinterpret or replace the primary reference's drawing style.
Do not add rendering effects, textures, accessories, or costume ornaments
absent from the reference. Do not increase decorative detail for its own sake.
No scenery, text, watermark, cast shadow on a background, or drawn checkerboard.
Do not shrink the character to fit a full-body view.
```

同一角色的母圖與必要 B 新姿勢沿用同一主設定圖及其觀察摘要；不同角色分別讀取各自設定圖，不共用一份預設畫風描述。不得逐張追加 `ultra-detailed`、`hyper-detailed`、`intricate textures` 等提高細節密度的描述。A固定站姿只建立一張已凍結母圖，後續截取固定臉部矩形局部編輯，在同一張4欄1列工作圖中合繪眼睛與嘴巴四格。提示詞僅描述允許區域的表情變化，並要求維持母圖的線條、筆觸與渲染；不使用母圖構圖模板重畫整人，不生成四個全身，也不分開生成眼睛與嘴巴畫布。

### 畫風驗收

在母圖凍結與批次生產前，將結果與主設定圖並排比較線條、筆觸、上色、陰影、高光、材質及人物比例；以最終720×720原尺寸、白／深底，以及遊戲預計顯示尺寸檢視，顯示尺寸未知時另看50%縮圖。確認畫風延續來源，五官與主要配件清楚，細節簡化未改變角色辨識與繪製方式。若不符，針對偏離來源的部分修正母圖，再重跑試作。圖像參考與提示詞不能代替目視驗收，也不保證不同模型或批次完全一致。

在實際生成紀錄保留主設定圖路徑與SHA、觀察摘要、其他參考圖用途、實際簡化項目、完整提示詞及使用工具／模型；不把歷史圖輯路徑寫成必要依賴。需要縮放時，在母圖驗收與凍結前一次完成至720×720，再測量眼嘴座標。眼嘴裁切圖集仍依ROI尺寸匯出，不強制為720×720。細節簡化以減少返工與方便差分重用為目的，不宣稱能保證縮短模型單次生成時間。

