---
name: ll-standing-portrait-maker
description: "依角色設定圖與正式60表情／肢體清單製作LL立繪，以單一母圖和臉部矩形局部編輯，合繪眼嘴橫向四格，再裁切獨立眼嘴圖集與匯出JS對照。"
---

# LL 立繪：正式清單、分層素材與眼嘴動畫

使用圖片生成／編輯工具繪製；腳本只做分格、遮罩合成、裁切、無損拆層與驗證。套用本次可用的圖片工具技能。保留來源、舊版素材與生成紀錄，輸出到新 run／export，不自動安裝到遊戲或覆蓋 `plugins.js`。

## 先確定內容與來源

- **預設內容權威是 [expression-catalog-60.md](references/expression-catalog-60.md) 與 [body-language-catalog-60.md](references/body-language-catalog-60.md)**。01=堅定、53=單眼眨眼、57=黑色橫方塊眼、58=`> <`眼與O嘴、59=螺旋眼與方形張嘴、60=吐舌眨眼。不得用自建情緒表或眼嘴共用表取代編號與語意。附帶JSON是衍生快照；規劃工具直接解析Markdown。
- 原始emontion圖是提示詞測試範例，須核對標籤與圖像是否一致。本次使用者已選擇「保留表情用途，改成溫和漫畫表現」：不採用Glasgow Smile；16、29、30、34、42依正式清單採正常五官的凝視、誇張笑及調皮壞笑，不複製舊圖的傷口、血跡、尖牙或異常紅眼。52貓嘴採文章舊成品作參考，來源差異見原圖核對文件。
- 使用者明確提供的清單優先。記錄清單路徑及SHA；缺少正式清單時查找已授權資料，仍找不到就詢問來源，不自行補一套「同樣60項」。
- 讀取角色設定圖、目標插件及可取得的遊戲參數。**畫風來自本次主設定圖**；依 [畫風與構圖](references/style-and-layout.md) 記錄觀察，不預設賽璐璐或其他畫風，不依賴Old_version。
- 沒有既定遊戲插件時可用附帶的 [LL模板](assets/LL_StandingPictureDirect.js) 作目標；它沒有歷史表情清單，匯出器才加入本批實測對照。已有遊戲目標時以實際來源為準，不自行替換。
- 完整批次先做 A 的60個固定姿勢表情，再依正式肢體清單做 B：預設43個new_pose、17個reuse_default。21依原圖sigh修正為嘆氣並移除誤加的舉牌動作，核對範圍與來源差異見 [原圖核對](references/emontion-audit-52.md)。只有使用者明確限定臉部／A時才用 `--scope face-only`；紀錄「B不在本次範圍」，不宣稱完整原版批次。改B決策須記錄使用者要求與理由，不因未製作就全部改成沿用。
- 已存在的 simple-names-v004 菲比素材採另一套表情內容，不是正式清單的合格成品。新編號不得只換舊圖標籤；23組眼睛、23組嘴型及2.34MB都是該歷史圖包的結果，不是新批次的限制或容量保證。

## 規劃與試作

使用者指定新版肢體時，選 [肢體 v2](references/body-language-catalog-60-v2.md) 的35新增／25沿用並以 `--body-catalog` 明確傳入；原43／17版本保留。特殊眼嘴與靜態檢查格的規則見 [表情協調](references/expression-coordination.md)。

所有腳本路徑以本技能根目錄展開；run／export使用專案內的明確位置，不將成品寫入技能安裝目錄。需要Python與Pillow；系統Python缺依賴時優先找bundled runtime。

```sh
python scripts/ll_portrait_pipeline.py probe --plugin /path/LL_StandingPictureDirect.js
python scripts/ll_portrait_pipeline.py plan --character phebe --plugin /path/LL_StandingPictureDirect.js --out /project/output/expression-portraits/phebe/new_run
```

- 先寫完整表情語意、B決策與必要道具、姿勢ID、母圖、眼嘴ROI、遮罩、休止格、速度及QA計畫。可用 `--count N` 作明確子集試作；自訂清單用 `--catalog`，另有肢體表時用 `--body-catalog`。
- A固定站姿只建立並驗收一張共用母圖，預設720×720 RGBA，完整頭頂至大腿附近、朝畫面右方的三分之四站姿、雙臂自然垂放；使用者構圖優先。驗收角色辨識、畫風、頭頸定位及白／深底透明度後凍結SHA、允許遮罩與保護區；後續眼嘴變化不重畫全身。
- 先試一般表情及大口型，確認定位和接縫後再批次。原清單的單眼、符號眼、舌尖、汗滴與壓力陰影另做代表試作，不能拿普通眼睛套過全部項目。

## A：共用母圖，製作60個局部表情

1. 在同一已接受母圖上劃定固定臉部編輯矩形，截取該區域作局部編輯目標；只改該表情允許的眼眉嘴、臉頰及符號。身體、頭頸角度與畫布固定，不串接上一張或重新置中人物。
2. 每表情以同一張橫向四格臉部工作圖同時繪製眼睛與嘴巴，流程見下一節。工作 `base` 由接受的休止臉部回貼共用母圖合成，供驗收與裁切；不是另一張生成的全身母圖。**工作母檔不等於遊戲交付檔**：正式共用版匯出只留一張共用底圖及每表情局部臉圖，不另存60張完整靜態PNG。
3. 臉圖要涵蓋實際眉毛、紅暈、淚痕、陰影及其他差異；範圍由本次生成像素與構圖量測，不硬套89×108。ROI是容器，允許遮罩才是可修改區域。保護鼻樑、髮際、下顎及遮擋，規則見 [局部差分與QA](references/layers-and-qa.md)。
4. 09扶額、31手指撐笑的A先做指定臉部語意，手留B。21是嘆氣，以眼皮與吐氣嘴表現；22是睏倦的小嘴，B可揉眼；28是吃痛的非對稱瞇眼。16保持頭角，以眼眉表現銳利凝視。33、48採睜眼笑；38、43依正式文字的忍笑／符號眼語意製作，不能直接照搬未實現標籤的原始測試圖。

## 眼嘴合繪：臉部矩形內橫向四格，再裁切分層

- 每表情只用一張 **4欄1列、四格由左至右0、1、2、3** 的局部臉部工作圖；每格同時包含眼睛與嘴巴。不要分開生成眼睛畫布與嘴巴畫布，也不要生成四個全身、2×2或4×4工作圖。
- 每格都是同一個臉部矩形，裁切範圍、人物比例、鼻子、下顎與髮際定位固定。編輯矩形是給生圖工具的上下文；矩形內仍以允許遮罩及保護區限制實際改動，詳見 [局部差分與QA](references/layers-and-qa.md)。
- 同格配對：0=休止眼＋休止嘴，1=半閉眼＋小開口，2=閉眼＋大開口，3=半睜眼＋中開口；各表情依其語意調整。若尚無該表情base，先驗收同圖0格並回貼母圖建立base；已有接受的休止五官時，0格直接取該base，不採用漂移的生成0格。
- 53、60 的單眼眨眼以雙眼睜開為休止0格，1=指定眼半閉、2=該眼閉合、3=該眼半睜，之後回0；另一眼四格全開，閉合側依接受的參考圖固定。設eyeAuto=true，不能把閉一眼的檢查圖當成固定休止眼，也不能改成雙眼同閉。
- 28吃痛瞇眼及固定閉眼、方塊眼等靜止層可重複四格並設eyeAuto=false。螺旋眼可另依既定規格以圓心旋轉90度，不能強制改成普通雙眼眨眼。
- 60的嘴0格為閉嘴、沒有舌頭；1=舌尖、2=部分伸出、3=最長伸出，眼嘴獨立計時。
- 工作圖先拆成四張局部臉圖；每格以同一矩形原座標回貼。眼睛與嘴巴從同一個候選格，分別透過各自遮罩合成驗收，最後各用固定ROI裁成獨立直向圖集。全畫布驗收影格由程式合成，不交給生圖工具重畫。非標準原圖只允許整組共同映射一次，保留紀錄，不逐格對臉或拉伸。

下例矩形與尺寸僅示範，必須換成本次量測值；生成工作圖已共同標準化為640×200，每格160×200，對應母圖矩形 `[300,100,460,300)`：

```sh
python scripts/split_work_sheet.py --image run/normalized/01-face-work.png --columns 4 --width 160 --height 200 --out run/work/01/face-split
python scripts/ll_portrait_pipeline.py compose --base run/masters/default.png --candidate run/work/01/face-split/frame_0.png --rect 300 100 460 300 --mask run/masks/default-face.png --protect run/masks/default-protect.png --out run/work/01/base.png
python scripts/ll_portrait_pipeline.py compose --base run/work/01/base.png --candidate run/work/01/face-split/frame_1.png --rect 300 100 460 300 --mask run/masks/01-eyes.png --protect run/masks/default-protect.png --out run/work/01/eyes1.png
python scripts/ll_portrait_pipeline.py compose --base run/work/01/base.png --candidate run/work/01/face-split/frame_1.png --rect 300 100 460 300 --mask run/masks/01-mouth.png --protect run/masks/default-protect.png --out run/work/01/mouth1.png
```

- **生成工作圖橫排合繪，插件交付圖集才拆成眼／嘴各1欄4列**，尺寸為 `eyeWidth × 4*eyeHeight`、`mouthWidth × 4*mouthHeight`。座標是ROI在原始底圖的左上角；局部編輯座標須加上編輯矩形左上角，不能用工作圖的格序偏移、畫面槽位或縮放後位置代替。
- 每格預設15更新單位，眨完等待180～300，可依角色調整。眼嘴各自計時；OFF回0格，未必代表睜眼／閉嘴。
- 依 [共用判定](references/eye-mouth-sharing.md) 先試可重用素材，只有不吻合的層／畫格才新畫。完整四格、定位、膚色邊圈、姿勢與語意均通過才共用檔案；組數由本次驗收決定，不固定16／18或23／23。

## 驗收、B與匯出

- `eye0 + mouth0`回貼必須與該表情工作base的RGBA完全相同；每項檢查16個眼嘴組合、接縫、原尺寸與縮圖、白／深底、鏡像和縮放。16組合由程式／HTML疊現有畫格，不呼叫生圖工具畫矩陣。只有需要保存證據時才另存QA接觸圖。
- 像素檢查不能代替表情語意和目視QA。A全部接受後才開始必要B；B手型、肩線、接觸及頭頸依正式肢體清單驗收。新姿勢建立自己的母圖與座標。手遮臉或頭位改變時烘焙五官，不把獨立眼嘴畫到手上。
- B工作／交付圖集固定4欄1列，每格預設720×720。`reuse_default`僅記參照，不生圖或複製。LL內建M位移不是身體圖集播放器；未驗證的B接口維持unbound，詳見 [插件契約](references/plugin-contract.md)。
- 預設匯出共用版，要求目標確實支援baseImage／faceImage及已檢查的JS對照嵌入點。工具只在新匯出目錄產生插件副本，**不修改目前遊戲或把新清單覆蓋進舊素材包**。

```sh
python scripts/ll_portrait_pipeline.py export --manifest run/manifest.json --out run/export-v1
```

正式輸出為同一個 `img/pictures/<character>/` 內的 `<character>_base.png`、`<character>_i.png`、`eyes_j.png`、`mouth_k.png`。i保留正式表情編號，j/k依實際去重結果編號，不補零。不同姿勢各有共用底圖；B另命名，不硬套單一身體。

`plugin/`副本內的 `LL_EXPORTED_FACE_SETTINGS` 寫入本批實測對應，使用 `\F1[Phebe_1]`；訊息外加 `\FH[ON]`，說話仍用 `\SPEAK[1]`。不必另匯入60筆參數；既有同名使用者參數可覆寫，須在報告說明。新正式編號不能自動繼承歷史替代清單的含義。

輸出及manifest詳見 [manifest與匯出](references/manifest-and-export.md)。舊LL不支援共用臉圖時，用明確的 `--layout legacy` 匯出完整底圖相容版，不能假稱同樣省容量。`--allow-partial`只交付通過的項目並標記缺項，不補占位圖；`--qa-images`才另存組合QA圖。

## 報告、容量與完成狀態

- `report.html`以同一批runtime PNG即時疊圖，提供1280×720示意場景、表情與槽位選擇、原點／位置／縮放／鏡像、局部範圍、眼嘴手動選格、說話與眨眼、暫停／逐格、逐字對話及B烘焙圖集預覽。不另存全尺寸表情副本。
- 共用版另輸出`body-report.html`肢體語言總覽，以同一批B圖集顯示全部已接受姿勢，支援編號／語意搜尋、最終姿勢、橫向四格定格對照、單組與全部播放一次、選格及白／深底；沿用預設站姿者獨立列出，不新增圖檔。
- 有實際遊戲背景／視窗／profiles時優先讀取，保存preview-settings來源；沒有時標為建議配置／示意場景。無法重現的色調、混合、其他插件層序或過場效果明列未支援，不把獨立HTML當完整MZ。
- 實際開啟HTML驗證素材載入、代表與特殊表情、左右槽、鏡像縮放、嘴型停止、眨眼及瀏覽器錯誤。分開記錄素材QA、HTML、最小宿主與完整MZ實機狀態；沒有實機就維持not_run。
- 統計A表情、B新增／沿用、共用底圖、局部臉圖、眼睛／嘴型圖集、唯一PNG內容及實際生成呼叫。比較同範圍的**遊戲PNG位元組**；HTML、插件、工作母檔、B、QA與ZIP分列。
