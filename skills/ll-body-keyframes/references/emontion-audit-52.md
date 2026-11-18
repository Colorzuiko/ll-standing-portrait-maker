# emontion 原始 52 種與正式資料庫前 52 項核對

核對日期：2026-11-17。來源是本機 emontion01–04 與使用者提供的 [52 種表情差分文章](https://leicyo.blogspot.com/2026/01/52.html)。

## 結論與採用方向

- 四張原圖共 **52 種**，其中 **51 種**可對應正式資料庫前 52 項。原圖另有 Glasgow Smile，資料庫則多了文章成品中的 Cat Mouth；兩份清單不是完全相同的 52 種。
- **21 原始標籤是 sigh（嘆氣）**。文章文字及舊成品曾誤用 sign 並畫成舉牌；正式資料庫修正為嘆氣，移除牌子及舉牌動作。
- 使用者已明確選擇：**保留表情用途，改成溫和漫畫壞笑／誇張笑**。不採用 Glasgow Smile；16、29、30、34、42 等採正常五官，保留凝視、笑、調皮或惡作劇用途。
- 原圖是提示詞測試結果。38、39、43、44 等標籤與輸出有落差；不能把模型失準、換眼色、變髮色或恐怖變形當作必須重現的表情。
- 保留正式 01–60 編號；52 貓嘴保留作日常表情。原始標籤與本次採用名稱的對照記錄於下表。
- 前 52 項共有 **30 項**調整名稱或臉部描述，**22 項**保留；調整包含語意更正、代表版本選擇及溫和化，不表示每一項舊描述都完全錯誤。
- B 改為 **43 個新增姿勢、17 個沿用**，總計 60 個 A + 43 個 B。21 嘆氣沿用 A，22 改為揉眼，29 改為輕快的小拳手勢。

## 原圖範圍

來源圖未隨技能包散布；以下保留本機檔名供追溯，文字核對與採用結果隨技能提供。

| 來源 | 表情列數 | 對應情況 |
| --- | ---: | --- |
| `emontion01.jpg` | 17 | 01–16 及 48；疲憊、面無表情與 Happy 的列序和正式編號不同 |
| `emontion02.jpg` | 16 | 17–32；第 5 列清楚標示 sigh |
| `emontion03.jpg` | 3 | 49–51；沒有 Cat Mouth |
| `emontion04.jpg` | 16 | 第 1 列 Glasgow Smile；第 2–16 列對應 33–47 |

每列左至右的 Seed 0–3 是四個生成範例，共 208 格範例，不是 208 種表情，也不是四格動畫。以下列序不含 Seed 標題列。

## 前 52 項逐項比對

| 正式編號 | 採用名稱／英文 | 原圖標籤與位置 | 處理與理由 |
| --- | --- | --- | --- |
| 01 | 堅定 / Determined | `determined` · emontion01 第 1 列 | **保留**：堅定視線、收緊嘴型與眉形相符，保留。 |
| 02 | 失望 / Disappointed | `disappointed` · emontion01 第 2 列 | **保留**：失落的眉眼與下彎小嘴相符，保留。 |
| 03 | 輕蔑 / Disdain | `disdain` · emontion01 第 3 列 | **保留**：半垂眼皮、冷淡旁視與輕蔑語意相符；A 不追隨範例抬下巴。 |
| 04 | 厭惡 / Disgust | `disgust` · emontion01 第 4 列 | **保留**：鼻部皺縮與嫌惡嘴型相符，保留。 |
| 05 | 微醺 / Drunk | `drunk` · emontion01 第 5 列 | **保留**：紅暈與鬆弛眼皮可表現微醺；保留角色本身的眼色。 |
| 06 | 嫉妒 / Envy | `envy` · emontion01 第 6 列 | **保留**：不滿凝視與緊繃眉嘴可表現嫉妒，保留。 |
| 07 | 興奮 / Excited | `excited` · emontion01 第 7 列 | **保留**：明亮睜眼、張嘴笑與興奮相符，保留。 |
| 08 | 面無表情 / Expressionless | `expressionless` · emontion01 第 9 列 | **調整**：原描述的 wide unfocused eyes 容易變成驚愕；改為自然睜眼、放鬆眉嘴。 |
| 09 | 扶額 / Facepalm | `facepalm` · emontion01 第 10 列 | **調整**：原圖多為垂眼或半垂眼，並非一致雙眼閉合；採垂眼無奈的代表版。 |
| 10 | 慌亂害羞 / Flustered | `flustered` · emontion01 第 11 列 | **保留**：強烈害羞紅暈、驚慌睜眼與小嘴相符，保留。 |
| 11 | 懊惱 / Frustrated | `frustrated` · emontion01 第 12 列 | **調整**：挫怒與咬牙怒視過強；改名懊惱，採不安睜眼、皺眉與下彎小嘴。 |
| 12 | 皺眉 / Furrowed Brow | `furrowed brow` · emontion01 第 13 列 | **保留**：核心是眉間收緊，保留；不靠額外頭部轉向。 |
| 13 | 咬牙扭臉 / Grimace | `grimace` · emontion01 第 14 列 | **調整**：原圖主要為睜眼咬牙；改名咬牙扭臉，移除必須緊瞇雙眼的限制。 |
| 14 | 內疚 / Guilt | `guilt` · emontion01 第 15 列 | **保留**：標籤為 guilt，但範例接近普通小嘴，內疚辨識度較弱；保留標籤語意的眉眼描述。 |
| 15 | 疲憊 / Exhausted | `exhausted` · emontion01 第 8 列 | **保留**：沉重眼皮、疲累視線與微張嘴相符，保留。 |
| 16 | 銳利凝視 / Intense Stare | `kubrick stare` · emontion01 第 17 列 | **調整**：原標籤 Kubrick Stare；依使用者偏好改為正常五官的銳利凝視，保留壓眉與集中視線。 |
| 17 | 害怕 / Scared | `scared` · emontion02 第 1 列 | **調整**：原圖有不規則微張害怕嘴與淚光；不限定閉緊牙齒。 |
| 18 | 恐慌 / Panicking | `panicking` · emontion02 第 2 列 | **調整**：原圖主要為睜眼、大張嘴及汗淚；藍色壓力陰影不作必要特徵。 |
| 19 | 擔憂 / Worried | `worried` · emontion02 第 3 列 | **保留**：擔憂眉、小汗滴與不安嘴型相符，保留。 |
| 20 | 嚴肅 / Serious | `serious` · emontion02 第 4 列 | **保留**：穩定視線與收緊小嘴相符，保留。 |
| 21 | 嘆氣 / Sigh | `sigh` · emontion02 第 5 列 | **調整**：原圖明確為 sigh，並有吐氣符號；Sign／舉牌是誤讀。改為嘆氣，B 沿用 A。 |
| 22 | 睏倦 / Sleepy | `sleepy` · emontion02 第 6 列 | **調整**：原圖為沉重眼皮與鬆弛小嘴，沒有一致呵欠；改為睏倦，B 採揉眼。 |
| 23 | 賭氣 / Sulking | `sulking` · emontion02 第 7 列 | **調整**：主要為低眉、略避視線與抿嘴賭氣；不強制鼓腮。 |
| 24 | 驚訝 / Surprised | `surprised` · emontion02 第 8 列 | **調整**：各範例張口大小不同；保留圓形驚訝嘴，不限定很小的 O 嘴。 |
| 25 | 思考 / Thinking | `thinking` · emontion02 第 9 列 | **調整**：補上輕抿小嘴與思索眉形；抵下巴的手只在 B 表現。 |
| 26 | 沉思 / Pensive | `pensive` · emontion02 第 10 列 | **保留**：安靜沉思的視線與淡淡皺眉合理，保留。 |
| 27 | V 形怒眉 / V-Shaped Eyebrows | `v-shaped eyebrows` · emontion02 第 11 列 | **保留**：保留 V 形眉的明確結構；不套入紅眼等人物變化。 |
| 28 | 吃痛瞇眼 / Wince | `wince` · emontion02 第 12 列 | **調整**：原圖主要為一眼閉、一眼瞇與緊繃小嘴；改名吃痛瞇眼，與俏皮眨眼區分。 |
| 29 | 誇張大笑 / Exaggerated Laugh | `crazy smile` · emontion02 第 13 列 | **調整**：原標籤 Crazy Smile；依使用者選擇保留誇張笑用途，改為明亮眼神與正常牙齒的大笑。 |
| 30 | 調皮壞笑 / Mischievous Smile | `evil smile` · emontion02 第 14 列 | **調整**：原標籤 Evil Smile；改為調皮壞笑，保留收斂的笑意及半垂眼，不採恐怖陰影。 |
| 31 | 手指撐笑 / Finger Smile | `fingersmile` · emontion02 第 15 列 | **調整**：原圖是手指頂起嘴角的可愛笑，並非憂慮強顏；A 改為自然配合的閉嘴笑，手留 B。 |
| 32 | 強顏歡笑 / Forced Smile | `forced smile` · emontion02 第 16 列 | **調整**：原圖可見牙齒與緊繃笑容；由閉嘴改為不自然地勉強露齒，保留不安眉眼。 |
| 33 | 露齒笑 / Grin | `grin` · emontion04 第 2 列 | **調整**：原圖四個範例都是睜眼露齒；改名露齒笑，取消閉眼休止規定，開啟一般眨眼。 |
| 34 | 使壞咧嘴笑 / Mischievous Grin | `evil grin` · emontion04 第 3 列 | **調整**：原標籤 Evil Grin；改為使壞咧嘴笑，保留較大的露齒笑與專注眼神，採正常牙齒。 |
| 35 | 淡笑 / Light Smile | `light smile` · emontion04 第 4 列 | **保留**：柔和小閉嘴笑與自然眉眼相符，保留。 |
| 36 | 悲傷微笑 / Sad Smile | `sad smile` · emontion04 第 5 列 | **保留**：微笑與低落眉眼並存，保留悲傷微笑。 |
| 37 | 誘惑微笑 / Seductive Smile | `seductive smile` · emontion04 第 6 列 | **保留**：半垂眼皮與收斂笑意相符，保留；不把眼色變化當表情要求。 |
| 38 | 忍笑 / Stifled Laugh | `stifled laugh` · emontion04 第 7 列 | **保留**：標籤是 Stifled Laugh，但測試圖多為張嘴放聲笑；保留忍笑的情緒用途，採收住笑意與 B 掩嘴。 |
| 39 | 得意臉 / Doyagao | `doyagao` · emontion04 第 8 列 | **保留**：標籤是 Doyagao，但多個範例近似普通面容；保留自信得意的文字用途，不照搬失準的中性臉。 |
| 40 | 歪嘴笑 / Smirk | `smirk` · emontion04 第 9 列 | **保留**：不對稱上揚嘴角與調侃視線合理，保留。 |
| 41 | 自滿 / Smug | `smug` · emontion04 第 10 列 | **保留**：滿意小笑與放鬆半垂眼合理，保留；與39得意臉允許語意接近。 |
| 42 | 惡作劇笑 / Troll Face | `troll face` · emontion04 第 11 列 | **調整**：原標籤為 troll face，Meme Grin 過於籠統；還原標籤，製作時採溫和惡作劇笑與自然牙齒。 |
| 43 | 上尖括號眼微笑 / Caret-Eye Smile | `^^^` · emontion04 第 12 列 | **調整**：原標籤 ^^^，測試圖卻是睜眼訝異；採既定的 ^ ^ 笑眼與小 ω 嘴，明確標為語意設計，不宣稱原圖已正確呈現。 |
| 44 | 失色 / Color Drain | `color drain` · emontion04 第 13 列 | **調整**：原測試圖主要是配色變化，沒有穩定表現失色；依標籤與文章成品採臉部去飽和，與50藍灰壓力帶分開。 |
| 45 | 驚恐 / Horrified | `horrified` · emontion04 第 14 列 | **調整**：原圖主要是強烈恐懼、張嘴與淚光；不強制藍色陰影，改為自然五官的漫畫驚恐。 |
| 46 | 尖叫 / Screaming | `screaming` · emontion04 第 15 列 | **調整**：補明垂直大開口與緊張抬眉，保持正常顎部與五官結構。 |
| 47 | 啜泣 / Sobbing | `sobbing` · emontion04 第 16 列 | **調整**：原圖多為近閉眼流淚且哭喊張嘴；補上閉眼哭泣與不規則開口，保留啜泣用途。 |
| 48 | 開心笑 / Happy | `happy` · emontion01 第 16 列 | **調整**：原圖多為睜眼開心笑，並有閉眼變體；選睜眼代表版，改名開心笑並開啟一般眨眼。 |
| 49 | 受創呆滯 / Traumatized | `traumatized` · emontion03 第 1 列 | **調整**：原圖表現較輕微的受創呆滯；不強制大片壓力陰影或大量汗滴，採定住視線與鬆弛小嘴。 |
| 50 | 嚇得發白 / Turn Pale | `turn pale` · emontion03 第 2 列 | **調整**：保留上臉藍灰壓力帶與緊張小嘴；與44的灰白去飽和分開。 |
| 51 | 波浪嘴 / Wavy Mouth | `wavy mouth` · emontion03 第 3 列 | **調整**：明確描述橫向顫抖波浪線嘴，與圓弧 ω 貓嘴區分。 |
| 52 | 貓嘴 / Cat Mouth | `cat mouth` · 文章第 4 張圖右下格；本機原圖未見 | **調整**：四張 emontion 原圖均無此標籤；文章舊成品含 Cat Mouth。保留作可用的日常表情，採圓弧 ω 嘴。 |

## 原圖額外項目

| 原標籤 | 原圖位置 | 決定 |
| --- | --- | --- |
| Glasgow Smile | emontion04 第 1 列 | 不採用。它是裂口式恐怖笑容，超出本次溫和漫畫表現；不以它替換第 52 項貓嘴。 |

## 不應混為一談的表情

- **07 興奮、29 誇張大笑、33 露齒笑、48 開心笑**：分別是期待興奮、放聲大笑、露齒小開口、普通開心笑。33 與 48 的休止眼採睜眼，可使用一般眨眼。
- **30 調皮壞笑、34 使壞咧嘴笑、40 歪嘴笑、42 惡作劇笑**：分別是小幅收斂笑意、較大的計畫得逞笑、不對稱嘴角、帶逗弄感的露齒笑；牙齒皆使用自然大小。
- **28 吃痛瞇眼、53 單眼眨眼、60 吐舌眨眼**：一眼閉合只是共用外形線索；28 的眉嘴表現痛或不適，53、60 的眉嘴則表現俏皮。
- **38 忍笑、39 得意臉、43 符號笑眼、44 失色**：採標籤的情緒用途，原始生成圖只能作失準案例參考。43 的 `^^^` 不表示三隻眼睛；採用的是兩個 `^` 形閉眼。
- **44 失色、49 受創呆滯、50 嚇得發白**：分別是臉部去飽和、定住視線與鬆弛小嘴、上臉的藍灰壓力帶。44 在 A 中只改允許的臉部區域，不擴大為頭髮與服裝去色。
- **51 波浪嘴、52 貓嘴**：前者是橫向不規則顫抖線，後者是圓弧 `ω` 嘴。

## 套用與追溯

修正後內容寫入 [正式表情清單](expression-catalog-60.md)、[肢體語言清單](body-language-catalog-60.md) 與其衍生 JSON。規劃器的 33、48 改回一般眨眼；數字編號保持穩定，部分英文正名會改變新計畫的字串 ID：

| 編號 | 舊 ID | 新 ID |
| --- | --- | --- |
| 16 | `16_kubrick_stare` | `16_intense_stare` |
| 21 | `21_sign` | `21_sigh` |
| 29 | `29_crazy_smile` | `29_exaggerated_laugh` |
| 30 | `30_evil_smile` | `30_mischievous_smile` |
| 34 | `34_evil_grin` | `34_mischievous_grin` |
| 42 | `42_meme_grin` | `42_troll_face` |

既有生成圖包、舊 manifest 與舊匯出仍記錄當時的內容，不自動替換圖片或重標籤。本次只校正後續製作依據，沒有生成新表情圖片。53–60 的內容不在本次原始 52 項比對範圍。

修正前副本與完整欄位差異保存在 `output/emontion-audit-20261117-v001/`；`comparison-52.json` 記錄每一項的 before／after、原圖位置、原始標籤與來源 SHA256。文章頁面與四張舊成品同樣保存於該次核對目錄。

### 原圖 SHA256

- `emontion/emontion01.jpg`：`4e5e5179d5f3e5beeb867b12d7538ea723f1cc328b3859d8dcd64dc270bfbdb9`
- `emontion/emontion02.jpg`：`259478e52ec43a82ba0e904a1f97eb2ef9c8b757c67814cb879da0528435c9e5`
- `emontion/emontion03.jpg`：`747e8b3ebd9b5d71f02bf943f7da741b2ab5dbf30ff441b3d42c22f836941d38`
- `emontion/emontion04.jpg`：`b9d3347e5556a78446b2a8e22f92bb35f9a99f2c9a2c1ff19f31825acc7f0c85`
