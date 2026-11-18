# 肢體動作的畫風與構圖

實際開啟主設定圖與已選定成品，記錄線條、上色、陰影邊緣、高光、材質、人物比例與配色。使用者已指定某個版本時，以該版本為動作呈現依據，其他設定圖補充衣裝與結構；不要混用互相矛盾的渲染。生成時附上實際圖像，記錄參考順序及用途。文字描述不取代圖像參考。

不預設賽璐璐、柔光、固定明暗階數或高飽和。若本次明確選用賽璐璐，可要求連續乾淨的固有色色塊、清楚陰影邊界，避免皮膚與衣料新增雲霧或雜色；仍要保留來源的配色、線條與材質差異。不要逐張追加高細節或紋理詞。

四格共用鏡頭、比例與人物位置，預設頭頂完整至大腿附近，保留雙手、肘部與頭飾邊距；不為容納腳部縮小人物。允許手臂、衣料及接觸所需的輪廓與投影改變，不能要求全圖alpha完全不動。不要逐格自動置中消除原本的動作位移。

先寫四階段，再填入以下提示骨架；必須傳入本次角色圖，並設定工具的透明輸出選項（若有）：

```text
Create ONE transparent PNG canvas containing four complete character
keyframes in a 2-column, 2-row grid. Reading order: [[1,2],[3,4]].
Use the supplied references for character design and the selected drawing style.
Observed traits: {observed_traits}. Reference roles: {reference_roles}.
Keep the same expression intent, camera, character scale and framing in all cells.
Frame 1: {stage_1}. Frame 2: {stage_2}.
Frame 3: {stage_3}. Frame 4: {stage_4}.
Show actual body/arm gesture changes. Preserve natural shoulder, elbow,
wrist and finger anatomy, costume joints, face contact and occlusion.
Include the complete head and required hand gestures, down to approximately
the thighs. Keep safe margins. No text, cell borders, numbers, scenery,
watermarks or drawn checkerboards. Do not substitute eye/mouth changes
for body movement. Keep empty areas transparent.
```

檢查角色辨識、四格演出、肩肘與護甲、手指接觸、白／深底透明邊緣、720原尺寸及遊戲顯示大小。局部像素一致只能當輔助，不能取代自然表演與使用者選擇。記錄實際生成尺寸、提示、工具／可取得模型名、參考SHA與目視結果；不由裁切張數推算生成次數。
