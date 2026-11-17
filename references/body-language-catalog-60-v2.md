# 新版肢體動作設定 v2：01–60

另存日期：2026-11-18。依使用者採用的新版表情肢體建議建立，對應 [目前60表情清單](expression-catalog-60.md)。原有 [肢體動作設定](body-language-catalog-60.md) 保留為43新增／17沿用的版本；本檔另存為35新增／25沿用，不改寫原檔。

## 本版設定

- **35 項 new_pose**：09、31為名稱需要手勢的項目，另33項以手勢強化情緒。
- **25 項 reuse_default**：直接沿用A自然站姿，不另生成身體圖；可選手勢不自動啟用。
- 合計60個A表情與35個B配對，共95項內容；這是內容項目數，不是PNG檔案數或唯一姿勢母圖數。
- 動作採溫和漫畫表現，使用自然手型、正常關節與小幅肩動。固定本批頭位與朝向，手和身體配合臉部定位。
- 所有左右以角色自身為準。本版多數單手動作以右手示意；39明定左手叉腰、右拇指指自己。
- 53與60維持雙眼睜開的休止狀態，眨眼時僅固定一眼半閉／閉合／半睜，另一眼全程睜開；60保留吐舌嘴型。兩者本版不新增肢體。

## 可直接讀取的60項動作表

| No. | 表情 | 第二階段 | 肢體設計 | Body-language prompt |
| --- | --- | --- | --- | --- |
| 01 | 堅定 | reuse_default | 沿用 A，自然站姿，不新增肢體。 | — |
| 02 | 失望 | reuse_default | 沿用 A，自然站姿，不新增肢體。 | — |
| 03 | 輕蔑 | reuse_default | 沿用 A，自然站姿，不新增肢體。 | — |
| 04 | 厭惡 | reuse_default | 沿用 A，自然站姿，不新增肢體。 | — |
| 05 | 微醺 | reuse_default | 沿用 A，自然站姿，不新增肢體。 | — |
| 06 | 嫉妒 | new_pose | 雙臂較緊抱胸，手收向對側上臂，肘靠身、肩微內收。 | arms folded fairly tightly across the chest, hands resting toward opposite upper arms, elbows close to the body, shoulders slightly drawn inward |
| 07 | 興奮 | new_pose | 雙手鬆握小拳抬到肩前，肘內收，肩線輕快上提。 | both hands loosely curled into small fists before the shoulders, elbows close to the torso, gently lifted cheerful shoulders |
| 08 | 面無表情 | reuse_default | 沿用 A，自然站姿，不新增肢體。 | — |
| 09 | 扶額 | new_pose | 角色右掌掌根貼額側，手指向上，左臂垂下，肩微收。 | heel of the character right palm resting against the side of the forehead, fingers pointing upward, character left arm hanging naturally, slightly inward shoulders, at least one eye and the entire mouth visible |
| 10 | 慌亂害羞 | new_pose | 雙手不對稱抬在上胸與肩前，掌略外向，手指自然張開。 | both open hands raised unevenly between the upper chest and shoulders, palms angled slightly outward, fingers naturally spread, gently lifted shoulders |
| 11 | 懊惱 | new_pose | 右手屈指輕碰後頸，左手低垂，右肘微抬、肩略內收。 | character right fingers lightly touching the nape of the neck, character right elbow slightly raised, character left arm relaxed at the side, shoulders slightly drawn inward |
| 12 | 皺眉 | new_pose | 雙臂結實抱胸，肘位置穩定，肩線較平、軀幹端正。 | arms crossed firmly across the chest, stable elbows, squared level shoulders, upright composed torso |
| 13 | 咬牙扭臉 | new_pose | 雙拳收在上腹兩側，肘貼身，肩略向上及向內收。 | both fists held beside the upper abdomen, elbows tucked against the torso, shoulders slightly raised and contracted inward |
| 14 | 內疚 | new_pose | 雙手在腰腹前輕交握，肘內收，肩略垂。 | both hands gently clasped low before the abdomen, elbows close to the torso, softly lowered shoulders |
| 15 | 疲憊 | new_pose | 右手指側輕扶太陽穴，左臂鬆垂，肩線放低。 | side of the character right fingers lightly supporting the temple, character left arm hanging loosely, lowered relaxed shoulders |
| 16 | 銳利凝視 | reuse_default | 沿用 A，自然站姿，不新增肢體。 | — |
| 17 | 害怕 | new_pose | 雙手輕握拳收在鎖骨下方，肘緊靠身，肩微抬。 | both hands lightly curled into small fists below the collarbones, elbows tight against the torso, gently raised protective shoulders |
| 18 | 恐慌 | new_pose | 雙手抬到肩臉兩側，掌向外斜，手指自然分開，肘稍外展。 | both open hands raised beside the lower face and shoulders, palms angled outward, fingers naturally separated, elbows slightly open, tense lifted shoulders |
| 19 | 擔憂 | new_pose | 右手輕貼鎖骨下方胸針旁，左前臂低位托住右肘。 | character right hand resting lightly on the upper chest beside the brooch, character left forearm low across the torso supporting the character right elbow |
| 20 | 嚴肅 | reuse_default | 沿用 A，自然站姿，不新增肢體。 | — |
| 21 | 嘆氣 | reuse_default | 沿用 A，以眼皮與吐氣嘴表現嘆氣，不新增肢體。 | — |
| 22 | 睏倦 | new_pose | 右手鬆握，以指節側輕揉眼外角，左臂垂下，肩線放鬆。 | character right hand loosely curled with the side of the knuckles gently rubbing the outer corner of the character right eye, character left arm hanging naturally, relaxed shoulders |
| 23 | 賭氣 | new_pose | 雙臂抱胸，肘比12更內收，肩略向內形成封閉輪廓。 | arms folded across the chest with elbows tucked inward, shoulders slightly drawn forward, compact withdrawn upper body |
| 24 | 驚訝 | new_pose | 雙掌短促抬至上胸兩側，掌朝外，肘仍略收，肩短暫上提。 | both open palms lifted briefly beside the upper chest, palms facing outward, elbows fairly close, slightly lifted startled shoulders |
| 25 | 思考 | new_pose | 右手指節抵下巴下緣，左前臂支撐右肘，肩線放鬆。 | character right knuckles resting beneath the lower edge of the chin, character left forearm supporting the character right elbow, relaxed shoulders, mouth unobstructed |
| 26 | 沉思 | reuse_default | 沿用 A，自然站姿，不新增肢體。 | — |
| 27 | V 形怒眉 | new_pose | 右拳收於上胸前，左拳低於腰側，肘高低不對稱，肩線穩定。 | character right fist held before the upper chest, character left fist low beside the waist, asymmetrical bent arms, steady firm shoulders |
| 28 | 吃痛瞇眼 | new_pose | 右手扶住左側上臂，左臂略彎，肩內縮，肘高低不對稱。 | character right hand supporting the character left upper arm, character left arm slightly bent, inward protective shoulders, uneven elbow heights |
| 29 | 誇張大笑 | new_pose | 右手輕放腹前，左手自然放鬆，肩可有小幅笑顫。 | character right hand resting lightly before the abdomen, character left arm relaxed naturally, small gentle shoulder movement suggesting laughter |
| 30 | 調皮壞笑 | reuse_default | 沿用 A，自然站姿，不新增肢體。 | — |
| 31 | 手指撐笑 | new_pose | 雙食指指腹輕頂嘴角外側臉頰，其餘手指鬆彎，兩肘自然彎曲。 | both index finger pads lightly pressing the cheeks just outside the mouth corners, remaining fingers loosely curled, both elbows naturally bent, lips and mouth opening unobstructed |
| 32 | 強顏歡笑 | new_pose | 雙手低位交疊於腹前，手指略收緊，肘靠身，肩稍僵。 | both hands held together low before the abdomen, fingers slightly tightened, elbows close to the torso, subtly stiff shoulders |
| 33 | 露齒笑 | reuse_default | 沿用 A，自然站姿，不新增肢體。 | — |
| 34 | 使壞咧嘴笑 | new_pose | 雙手在上腹與下胸之間指尖輕抵，掌心留小間隙，肘內收、肩放鬆。 | both sets of fingertips lightly meeting between the upper abdomen and lower chest, small gap between the palms, elbows inward, relaxed playful shoulders |
| 35 | 淡笑 | reuse_default | 沿用 A，自然站姿，不新增肢體。 | — |
| 36 | 悲傷微笑 | new_pose | 右手輕握左側上臂，左手低垂，肩略下沉。 | character right hand gently holding the character left upper arm, character left arm hanging low, softly lowered shoulders |
| 37 | 誘惑微笑 | reuse_default | 沿用 A，自然站姿，不新增肢體。 | — |
| 38 | 忍笑 | new_pose | 右手鬆掩嘴前，左手低位托右前臂，肩略內收。 | character right hand loosely covering the mouth, character left hand supporting the raised forearm from below, gently inward shoulders |
| 39 | 得意臉 | new_pose | 左手叉腰，右手拇指輕指向自己，胸肩自然展開。 | character left hand resting on the hip, character right thumb pointing lightly toward the character own chest, naturally open chest and shoulders |
| 40 | 歪嘴笑 | reuse_default | 沿用 A，自然站姿，不新增肢體。 | — |
| 41 | 自滿 | new_pose | 雙臂鬆抱胸，肩放鬆略後展，肘不收緊。 | arms loosely folded across the chest, relaxed shoulders slightly held back, comfortably open elbows |
| 42 | 惡作劇笑 | reuse_default | 沿用 A，自然站姿，不新增肢體。 | — |
| 43 | 上尖括號眼微笑 | reuse_default | 沿用 A，自然站姿，不新增肢體。 | — |
| 44 | 失色 | reuse_default | 沿用 A，自然站姿，不新增肢體。 | — |
| 45 | 驚恐 | new_pose | 雙掌在上胸前朝外，手指自然張開，肘彎曲，肩略收緊。 | both open palms facing outward before the upper chest in a protective gesture, naturally spread fingers, bent elbows, slightly contracted shoulders |
| 46 | 尖叫 | new_pose | 雙手抬到耳側外方，手掌張開、指節自然彎，肘外展，肩略抬。 | both open hands raised outside the ears, fingers naturally curved, elbows opened outward, slightly raised shoulders, entire face unobstructed |
| 47 | 啜泣 | new_pose | 右手背或鬆彎指節靠近右眼下方擦淚，左手收於下胸前，肩內縮。 | back or loosely curved knuckles of the character right hand wiping tears beneath the character right eye, character left hand near the lower chest, inward shoulders, opposite tears and crying mouth visible |
| 48 | 開心笑 | reuse_default | 沿用 A，自然站姿，不新增肢體。 | — |
| 49 | 受創呆滯 | reuse_default | 沿用 A，自然站姿，不新增肢體。 | — |
| 50 | 嚇得發白 | new_pose | 右手覆於嘴前，左手貼胸針旁上胸，肩略收緊。 | character right hand covering the mouth, character left hand resting on the upper chest beside the brooch, tense inward shoulders |
| 51 | 波浪嘴 | reuse_default | 沿用 A，自然站姿，不新增肢體。 | — |
| 52 | 貓嘴 | reuse_default | 沿用 A，自然站姿，不新增肢體。 | — |
| 53 | 單眼眨眼 | reuse_default | 沿用 A，自然站姿；休止雙眼全開，眨眼只閉固定一眼，不新增肢體。 | — |
| 54 | 安靜害羞／靦腆 | new_pose | 雙手在腰腹前輕合，指尖鬆鬆相接，肘內收，肩稍向內。 | both hands lightly held together low before the waist and abdomen, relaxed fingertips softly meeting, elbows close, shy slightly inward shoulders |
| 55 | 臉紅嘴硬／害羞不悅 | new_pose | 右手輕抓左側上臂，左前臂橫在腹前，肘內收、肩微緊。 | character right hand lightly gripping the character left upper arm, character left forearm across the abdomen, elbows tucked inward, slightly tense guarded shoulders |
| 56 | 疑問／困惑 | new_pose | 右手在腰胸之間低位攤掌向上，左臂自然垂放，肩線放鬆。 | character right hand held palm-up between the waist and lower chest, character left arm hanging naturally, relaxed shoulders |
| 57 | 方塊眼淡定吐槽笑 | reuse_default | 沿用 A，自然站姿，不新增肢體。 | — |
| 58 | 漫畫式擠眼驚呼 | new_pose | 雙掌從胸前短促張開，肘靠身，肩短暫上提，完成姿勢較小。 | both open hands briefly opening before the chest, palms angled outward, elbows close to the body, small short upward shoulder reaction |
| 59 | 螺旋眼暈眩 | new_pose | 右手指側扶太陽穴，左掌向身側低位張開穩住，肩略收。 | side of the character right fingers supporting the temple, character left open palm held low out to the side for balance, slightly inward shoulders, head position unchanged |
| 60 | 吐舌眨眼 | reuse_default | 沿用 A，自然站姿；休止雙眼全開，眨眼只閉固定一眼並保留吐舌嘴型，不新增肢體。 | — |

## 自然站姿項目的可選手勢

以下保留為情境選項，不列入本版35項new_pose。若劇情明確採用其中一個選項，再為該場景新增姿勢；不以可選描述改變上表的reuse_default決策。

- **01 堅定**：肩線端正、手臂自然垂放；需要強調決意時可單手輕握拳於腰側。 靠穩定視線與收緊眉嘴表現堅定，不必每次抬拳。
- **02 失望**：手自然垂下，肩線可稍放鬆；低位鬆合雙手為情境選項。 失落是向內收的反應，避免大幅垂頭改變頭位。
- **03 輕蔑**：手維持自然位；需要強調疏離時可鬆抱胸。 輕蔑主要由旁視與嘴角傳達，抱胸只在拒絕或疏遠語境使用。
- **04 厭惡**：維持自然站姿；若是在排斥面前事物，可選單掌低位朝外。 單掌推拒會增加拒絕對象的意思，不能只因厭惡就固定套用。
- **05 微醺**：雙臂放鬆，手腕稍鬆；第一輪保持站穩。 以臉紅與鬆弛眼皮表現微醺，不自動加酒杯、踉蹌或大幅搖晃。
- **08 面無表情**：肩、手、肘都維持放鬆，是全套身體姿勢的對照基準。 無額外肢體情緒，方便檢查臉部與其他姿勢是否漂移。
- **16 銳利凝視**：站姿穩定，肩線端正，手維持自然位置。 凝視強度由眼眉完成；不加入逼近、抓握或威嚇姿勢。
- **20 嚴肅**：肩線端正，雙臂自然垂放，站姿穩定。 嚴肅可作多種對話的基底，不固定抱胸或指人。
- **21 嘆氣**：手維持自然位；可在過渡中讓肩線小幅放鬆。 嘆氣由吐氣嘴與小氣團識別，無必要道具或固定手勢。
- **26 沉思**：先沿用自然站姿；劇情需要時可低位合手，或借用25的托下巴姿勢候選。 沉思偏安靜內省，沒有必要再做一套近似25的固定手勢。
- **30 調皮壞笑**：先保持放鬆自然位；若有逗弄對方的語境，可選一手叉腰。 調皮壞笑本身已清楚，不固定托下巴以免和25思考重複。
- **33 露齒笑**：雙臂自然放鬆；若台詞表達答應或鼓勵，再選單手豎拇指。 新版是普通露齒笑，原先雙拳抬肩會把情緒推成興奮。
- **35 淡笑**：雙臂自然垂放，肩線柔和；問候或致意時才選一手輕貼胸前。 淡笑是通用表情，無須每次附帶自我指涉或致意手勢。
- **37 誘惑微笑**：先用自然姿勢；有刻意示好的情境時，可選單手整理臉側髮束。 避免每次固定觸唇或托肘，讓微笑保留日常可用性。
- **40 歪嘴笑**：先維持自然手位；調侃對方時可選一手叉腰或低位攤掌。 非對稱笑容已足以識別，無須再固定托下巴。
- **42 惡作劇笑**：先用自然位；需要演出準備惡作劇時可選低位輕搓手。 臉部已是惡作劇笑，若再固定指尖相抵會和34盤算姿勢重複。
- **43 上尖括號眼微笑**：先保持放鬆自然位；撒嬌或雀躍場景可選雙手低位合起。 符號眼與小ω嘴已非常鮮明，沒有必要再固定臉旁小拳。
- **44 失色**：雙臂自然垂放；可在過渡中略放低肩線、減少動作。 失色首先是臉部色調反應，不必另抬起雙腕做無力姿勢。
- **48 開心笑**：雙臂自然放鬆，肩線略舒展；歡迎他人時才選低位開掌。 一般開心笑適用範圍廣，原先雙掌抬肩容易顯得過度驚喜。
- **49 受創呆滯**：先保留自然臂位，肩肘稍僵、動作停住，手指不主動擺造型。 受創呆滯的重點是反應停頓，原先胸前雙拳容易變成17害怕。
- **51 波浪嘴**：先用自然位；需要延長猶豫時，可選腹前輕捏指尖的小動作。 波浪嘴已表現不安，不需要每次都合手或搓指。
- **52 貓嘴**：先保留正常站姿；撒嬌或模仿貓的橋段才選雙手小貓爪。 貓嘴是一種嘴型，不能自動等同整個角色變成貓咪姿勢。
- **53 單眼眨眼**：先維持自然手位；招呼、保證或合照時再選揮手或V手勢。 單眼眨眼可有不同台詞用途，不固定綁定一個手勢。
- **57 方塊眼淡定吐槽笑**：先保留自然位；需要吐槽落點時，可選單手低位攤掌一次。 方塊眼已是主要笑點，額外動作只在台詞需要時加入。
- **60 吐舌眨眼**：先維持自然手位；玩笑或合照時才選小幅V手勢。 吐舌與單眼眨眼已完成俏皮語意，不必再指定全身造型。

## 辨識重點與接觸處理

- 11懊惱採碰後頸、肩內收；29大笑採扶腹；33與48普通笑容沿用自然站姿。
- 54靦腆採低位輕合手，55害羞不悅採護臂，56疑問採右手攤掌、左臂垂放，58採短促張掌，59採扶頭找平衡。
- 06／12／23／41的抱胸、14／32／54的合手、24／58的張掌可作共用候選；握力、手位、肩線、臉部位置與完整畫格仍需分別檢查。家族相近不等同素材已可共用。
- 09扶額保留至少一眼與完整嘴型；22揉眼僅影響接觸側，另一眼與嘴型可讀；25手指停在下巴下緣。
- 31指腹停在嘴角外側臉頰；38忍笑掩嘴與50驚嚇覆嘴保留不同的手指張力及眉眼。
- 47採單側擦淚，保留另一側淚痕及哭泣嘴。碰臉處需一併繪製正確手臉遮擋，不把五官疊到手背上。
- Phebe抬手時披風與袖口跟隨，胸針與領結留在衣服原位；貼胸手放胸針旁。腰部手勢維持角色左側槍套、右側彈藥與斜腰帶，不改成握槍動作。

## 四格過渡

B工作及交付圖集維持橫向4欄1列，每格預設720×720。由左至右為自然位、抬手或收肩、接近接觸點、完成姿勢；先驗收完成姿勢，再補過渡。頭頸定位、角色比例與畫風一致，眼嘴與手臉遮擋依本項動作一併驗收。

預設播放一次並停完成姿勢；循環使用另行驗收末格到首格接縫。reuse_default項目只參照A，不為湊四格而生成額外身體圖。

## 使用本版

在專案根目錄執行，明確指定本檔；輸出位置換成尚未存在的新run：

```sh
python -X utf8 scripts/ll_portrait_pipeline.py plan --character phebe --plugin assets/LL_StandingPictureDirect.js --body-catalog references/body-language-catalog-60-v2.md --out output/expression-portraits/phebe/new-run-body-v2
```

規劃器會搭配當前正式表情清單，保留53／60的單眼眨眼動作規則，並在新manifest記錄本版動作表來源及SHA。

配套 [JSON快照](expression-catalog-60-body-v2.json) 是當前60表情、眼睛動作規則與本版35／25肢體設定的合併快照，可作明確JSON清單輸入；後續修改以表情Markdown及本檔為準再重新產生快照。
