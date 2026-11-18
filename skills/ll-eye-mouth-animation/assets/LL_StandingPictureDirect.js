//=============================================================================
// RPG Maker MZ - LL_StandingPictureDirect.js
//=============================================================================

/*:
 * @target MZ
 * @plugindesc [v1.4.0] 八槽立繪／共用底圖與表情臉圖／獨立眼嘴四格圖集
 * @author OpenCode
 *
 * @help LL_StandingPictureDirect.js
 *
 * 本插件參考 LL_StandingPicture.js v2.7.0 的操作方式重新獨立實作，
 * 不依賴原插件。普通立繪可直接使用檔名；分層表情對應由技能匯出器嵌入。
 * 其他角色的眼嘴差分與分層表情可透過插件參數登錄。
 *
 * 重要：請勿同時啟用 LL_StandingPicture.js 與本插件。兩者都會處理相同的
 * 訊息控制字元，若同時啟用將造成重複顯示及不可預期的狀態。
 *
 * 將立繪 PNG 放在 img/pictures，控制字元內直接填圖片檔名（建議省略副檔名）：
 *   \F1[Zuiko_18]
 *   \F2["Zuiko happy"]
 *
 * 可用字母、數字、底線、連字號及空格。前後空白會被移除；為防呆也會移除
 * 成對的單／雙引號及結尾 .png。可在檔名內使用 \V[n]。
 *
 * 角色設定檔只需依共同檔名前綴設定一次，例如 Zuiko_。若同時符合多個前綴，
 * 採用最長的前綴；完全不符合時使用「預設／後備設定」。槽 5～8 分別共用
 * 槽 1～4 的座標。
 *
 * 控制字元：
 *   \F[檔名或表情代碼]、\F1[...]～\F8[...]：顯示立繪
 *   \FF、\FFF、\FFFF：分別為 \F2、\F3、\F4 的別名
 *   \M[動作]、\M1[動作]～\M8[動作]：播放動作
 *   \MM、\MMM、\MMMM：分別為 \M2、\M3、\M4 的別名
 *   \AA[1]～\AA[8]：聚焦指定槽（1～4 亦可用 F、FF、FFF、FFFF）
 *   \AA[N]：全部變暗；\AA[R] 或 \AA[0]：重設聚焦
 *   \FH[ON]／\FH[OFF]：開啟／關閉保持模式
 *   \SPEAK[1]、\SPEAK[1,ON]：槽 1 開始局部嘴型循環（槽位 1～8）
 *   \SPEAK[1,OFF]：槽 1 停止說話，回到閉嘴格；大小寫皆可
 *   \BLINK[1]、\BLINK[1,ON]：槽1自動眨眼
 *   \BLINK[1,OFF]：睜眼並停止眨眼；\BLINK[1,ONCE]：眨一次
 *
 * v1.4.0：身體四格圖集支援橫向4欄1列，依第1→2→3→4格播放。
 * 每格預設15更新單位；預設播放一次、停第4格。加註\loop才循環。
 * 使用 \ACT1[動作代碼]、\ACT2[...]～\ACT8[...]；\ACT為槽1。
 * 例：\F1[Phebe_9]\FH[ON]\ACT1[facepalm]
 * 循環：\ACT1[facepalm]\loop；停止並恢復原立繪：\ACT1[OFF]。
 * 動作登錄於「身體動作圖集」或匯出器嵌入的JS對照。四格單格尺寸須與立繪相同。
 * 烘焙身體格已包含五官：播放及停末格期間不額外疊臉、眼嘴或舊眨眼。
 * ACT控制可放在顯示文字的游標位置；非循環動作不因文字輸出完就提早停止。
 * \loop只修飾緊接在前的ACT指令，大小寫不拘，不影響其他槽。
 *
 * v1.3.0 技能模板：共用底圖、局部臉圖及眼嘴對照由技能匯出器嵌入。
 * 正式匯出後以LL_EXPORTED_FACE_SETTINGS為本批對照，沒有固定的歷史菲比清單。
 * 使用 \F1[Phebe_1]選表情；訊息外顯示加上\FH[ON]，說話另用\SPEAK[1]。
 * 局部座標、圖集及速度取自本次實測，不以任意角色範例值當成通用預設。
 * 未編譯本批對照前仍可使用一般圖片檔名及插件參數。
 *
 * v1.2.0：眼嘴差分設定新增「共用底圖」「表情臉圖」「臉圖X/Y」。
 * 「立繪底圖／表情代碼」可填虛擬表情代碼，不必有同名PNG；
 * 設定共用底圖後，F指令以代碼選表情，實際只載入共用底圖與局部臉圖。
 * 例：picture=phebe/01_neutral_base，baseImage=phebe/body_base，
 * faceImage=phebe/face_01_neutral，使用 \F1[phebe/01_neutral_base]。
 * 疊圖順序：共用底圖 → 表情臉圖 → 眼睛 → 嘴巴。臉圖座標相對原圖左上角。
 * 共用底圖留空時，仍以原本的picture檔名載入，既有設定相容。
 * 已設定的臉圖載入完成後才顯示整組立繪，切表情不顯示未完成的組合。
 *
 * v1.1.0：新增「眼嘴差分設定」，依完整底圖檔名登錄兩張獨立圖集。
 * 預設各1欄4列，每格15個遊戲更新單位，可各自修改。
 * 眼睛另外設定最短／最長眨眼間隔，預設180～300單位。
 * X/Y相對原始立繪左上角；跟隨父立繪縮放、鏡像與淡出。
 * 0號嘴型=閉嘴；0號眼睛=睜眼，兩層在靜止時仍覆蓋底圖。
 * 底圖需先清除原眼嘴，差分包含足夠膚色覆蓋及抗鋸齒邊界。
 * 每個姿勢各自登錄，不把站姿差分直接套到不同頭部角度。
 * 嘴型與眨眼獨立計時；說話結束只閉嘴，眼睛仍依設定自動眨眼。
 * 新眼睛圖集優先於舊眨眼後綴；新嘴型設定優先於舊局部說話設定。
 * 舊設定保持相容；圖集換格僅setFrame，不重新載入圖片或重設立繪。
 *
 * 局部說話（新增於 v1.0.4）：
 * 在「局部說話設定」登錄立繪檔名、嘴型圖集及嘴部 X／Y。
 * 底圖必須先清除嘴巴；圖集為橫向等寬分格，0 號格為閉嘴。
 * 三嘴型預設順序 0,1,2,1，每格 6 個遊戲更新幀。
 * 例：\F1[Hikari_normal_base]\SPEAK[1]這裡有個矛盾。
 * 訊息讀到 SPEAK 才執行，整段文字顯示完即閉嘴（不等待玩家按鍵）。
 * 這是固定節奏循環；句中等待仍持續循環，可用 OFF 手動安排停頓。
 * SPEAK 只控制嘴巴，不改動站姿、座標或既有 M 位移動作。
 * 嘴型層位於眨眼層上方，與角色一起縮放、鏡像、變暗與淡出。
 * 眨眼素材須對應相同姿勢，建議使用局部眼睛差分。
 *
 * 訊息外可用 processChar 執行 \SPEAK[1]／\SPEAK[1,OFF]；純 SPEAK
 * 指令保留其他槽位且不要求保持模式。訊息外啟動的循環不會因普通訊息
 * 結束而停止，但換圖、清除／隱藏該槽時會停止；跨訊息保留立繪仍需 FH。
 * 局部說話設定依完整立繪檔名比對；沒有設定時不猜測檔名、不載入嘴型。
 * 已登錄的嘴型 PNG 為必要素材，部署時須包含於 img/pictures。
 *
 * 動作：yes、yesyes、no、noslow、jump、jumpjump、jumploop、shake、
 * shakeloop、runleft、runright、noslowloop、breathing、breathing2、huwahuwa、none
 *
 * 眨眼圖片名稱為「目前基底檔名 + 後綴」。例如基底 Zuiko_18、後綴
 * _blink，會載入 Zuiko_18_blink。後綴留空即停用該階段。
 *
 * 插件指令 processChar 可在訊息外執行相同控制字元。若要讓顯示保留，請在
 * 同一指令使用 \FH[ON]。clear 可清除全部或指定槽。
 * clear 的槽位 0 為全部，1～8 對應 \F1～\F8；不是圖層編號 51～58。
 * 例如 clear 槽 2 只會清除 \F2 的角色，\F1 的角色會繼續顯示。
 *
 * 原點選「左上」時，X／Y 指定圖片左上角的位置，與圖層編號無關。
 * 偶數槽鏡像會向 X 座標的左側延伸；1280 寬畫面的左右配置可設為
 * 槽 1：(0, 0)、槽 2：(1280, 0)。角色設定檔會優先於後備設定。
 * 更新插件時請保留 plugins.js 中的角色設定與座標，勿刪除後重新加入插件。
 *
 * 圖層設定：槽位預設為「一般圖片之間」，「插入圖片編號」預設為 50。
 * 各槽的圖層編號 = 插入圖片編號 + 槽位編號，因此槽 1～8 對應 51～58。
 * 編號越大越上層；同編號時，立繪在一般圖片上方。
 * 例如由下到上：圖片 51 → 立繪 1 → 圖片 52 → 立繪 2 → … →
 * 圖片 58 → 立繪 8 → 圖片 59～100；圖片 90 會蓋住全部立繪。
 * 這是圖層排序，不會佔用或取代一般圖片；顯示／消除圖片指令不會操作立繪。
 * 基準為 0 時，槽 1～8 對應 1～8；超過一般圖片最大編號的槽會排在其上方。
 * 舊版升級：既有專案會保留原本的槽位參數，不會自動套用新版預設值。
 * 若第 90 號圖片仍被立繪蓋住，請在插件管理器中將使用中的槽位之
 * 「顯示層級」改成「一般圖片之間」，保留「插入圖片編號」為 50。
 * 「一般圖片前方」會蓋住所有一般圖片，不受「插入圖片編號」影響。
 * 插件參數與指令會依目前載入的檔名註冊，支援使用 _copy 等檔名。
 *
 * @command processChar
 * @text 執行控制字元
 * @desc 在訊息視窗外控制立繪；例：\F1[Zuiko_18] \FH[ON]
 *
 * @arg text
 * @text 控制字元
 * @type multiline_string
 * @default
 *
 * @command setEnabled
 * @text 啟用／停用立繪
 * @desc 停用時隱藏全部立繪，但保留目前狀態。
 *
 * @arg enabled
 * @text 啟用
 * @type boolean
 * @on 啟用
 * @off 停用
 * @default true
 *
 * @command setTone
 * @text 變更色調
 * @desc 設定全部立繪的色調。
 *
 * @arg toneR
 * @text 紅
 * @type number
 * @min -255
 * @max 255
 * @default 0
 *
 * @arg toneG
 * @text 綠
 * @type number
 * @min -255
 * @max 255
 * @default 0
 *
 * @arg toneB
 * @text 藍
 * @type number
 * @min -255
 * @max 255
 * @default 0
 *
 * @arg toneC
 * @text 灰階
 * @type number
 * @min 0
 * @max 255
 * @default 0
 *
 * @command clear
 * @text 清除立繪
 * @desc 清除全部或指定槽的立繪，並關閉保持模式（清除指定槽時除外）。
 *
 * @arg slot
 * @text 槽位
 * @desc 0 為全部，1～8 為指定槽。
 * @type number
 * @min 0
 * @max 8
 * @default 0
 *
 * @command playBodyMotion
 * @text 播放身體動作
 * @desc 在已顯示的槽位播放四格身體圖集；預設一次，循環需勾選。
 * @arg slot
 * @text 槽位
 * @type number
 * @min 1
 * @max 8
 * @default 1
 * @arg motion
 * @text 動作代碼
 * @type string
 * @default
 * @arg loop
 * @text 循環
 * @type boolean
 * @default false
 *
 * @command stopBodyMotion
 * @text 停止身體動作
 * @desc 恢復該槽原本的底圖、臉圖及眼嘴。
 * @arg slot
 * @text 槽位
 * @type number
 * @min 1
 * @max 8
 * @default 1
 *
 * @param bodyMotions
 * @text 身體動作圖集（橫向四格）
 * @desc 代碼對應4欄1列圖集；預設一次，ACT後加loop才循環。
 * @type struct<BodyMotion>[]
 * @default []
 *
 * @param profiles
 * @text 角色設定檔
 * @desc 依檔名前綴套用；符合多筆時採最長前綴。
 * @type struct<CharacterProfile>[]
 * @default []
 *
 * @param fallbackProfile
 * @text 預設／後備設定
 * @desc 檔名沒有符合任何角色前綴時使用。此處的前綴欄位會被忽略。
 * @type struct<CharacterProfile>
 * @default {"prefix":"","origin":"0","x":"464","y":"96","x2":"20","y2":"96","x3":"364","y3":"96","x4":"120","y4":"96","reverse":"true","scaleX":"100","scaleY":"100","opacity":"255","blendMode":"0","blinkSuffix1":"","blinkSuffix2":""}
 *
 * @param speakSettings
 * @text 局部說話設定
 * @desc 依完整立繪檔名指定局部嘴型圖集。留空不影響原本立繪。
 * @type struct<SpeakSetting>[]
 * @default []
 *
 * @param faceSettings
 * @text 眼嘴差分設定（臉圖／獨立四格圖集）
 * @desc 依底圖檔名或表情代碼指定共用底圖、局部臉圖與眼嘴圖集。
 * @type struct<FaceSetting>[]
 * @default []
 *
 * @param blinkInterval
 * @text 平均眨眼間隔
 * @desc 平均間隔幀數（60 幀約一秒）。
 * @type number
 * @min 1
 * @max 2000
 * @default 180
 *
 * @param blinkWaitCount
 * @text 眨眼階段時間
 * @desc 每張眨眼差分顯示的幀數。
 * @type number
 * @min 1
 * @max 2000
 * @default 4
 *
 * @param focusToneAdjust
 * @text 未聚焦暗度
 * @desc 未聚焦立繪疊加的黑色強度。
 * @type number
 * @min -255
 * @max 0
 * @default -96
 *
 * @param betweenPicturesPriority
 * @text 插入圖片編號
 * @desc 僅適用「一般圖片之間」：圖層編號＝此值＋槽位編號；50 表示槽 1～8 對應 51～58。
 * @type number
 * @min 0
 * @max 100
 * @default 50
 *
 * @param slot1
 * @text 槽 1（\F／\F1）
 * @type struct<SlotSetting>
 * @default {"transition":"1","priority":"betweenPictures"}
 * @param slot2
 * @text 槽 2（\FF／\F2）
 * @type struct<SlotSetting>
 * @default {"transition":"1","priority":"betweenPictures"}
 * @param slot3
 * @text 槽 3（\FFF／\F3）
 * @type struct<SlotSetting>
 * @default {"transition":"1","priority":"betweenPictures"}
 * @param slot4
 * @text 槽 4（\FFFF／\F4）
 * @type struct<SlotSetting>
 * @default {"transition":"1","priority":"betweenPictures"}
 * @param slot5
 * @text 槽 5（共用槽 1 座標）
 * @type struct<SlotSetting>
 * @default {"transition":"1","priority":"betweenPictures"}
 * @param slot6
 * @text 槽 6（共用槽 2 座標）
 * @type struct<SlotSetting>
 * @default {"transition":"1","priority":"betweenPictures"}
 * @param slot7
 * @text 槽 7（共用槽 3 座標）
 * @type struct<SlotSetting>
 * @default {"transition":"1","priority":"betweenPictures"}
 * @param slot8
 * @text 槽 8（共用槽 4 座標）
 * @type struct<SlotSetting>
 * @default {"transition":"1","priority":"betweenPictures"}
 */

/*~struct~BodyMotion:
 * @param id
 * @text 動作代碼
 * @type string
 * @default
 * @param image
 * @text 身體圖集
 * @type file
 * @dir img/pictures/
 * @default
 * @param columns
 * @text 欄數（新圖集使用4）
 * @type select
 * @option 橫向4欄1列
 * @value 4
 * @option 舊圖集直向1欄4列
 * @value 1
 * @default 4
 * @param frameWidth
 * @text 單格寬（0=自動）
 * @type number
 * @min 0
 * @default 0
 * @param frameHeight
 * @text 單格高（0=自動）
 * @type number
 * @min 0
 * @default 0
 * @param frameWait
 * @text 每格更新單位
 * @type number
 * @min 1
 * @default 15
 * @param end
 * @text 播放一次後
 * @type select
 * @option 停第4格
 * @value hold
 * @option 恢復原立繪
 * @value restore
 * @default hold
 */

/*~struct~CharacterProfile:
 * @param prefix
 * @text 檔名前綴
 * @desc 例：Zuiko_。大小寫視為不同。
 * @type string
 * @default
 *
 * @param origin
 * @text 原點
 * @type select
 * @option 左上
 * @value 0
 * @option 中央
 * @value 1
 * @default 0
 *
 * @param x
 * @text 槽 1 X
 * @type number
 * @min -2000
 * @max 2000
 * @default 464
 * @param y
 * @text 槽 1 Y
 * @type number
 * @min -2000
 * @max 2000
 * @default 96
 * @param x2
 * @text 槽 2 X
 * @type number
 * @min -2000
 * @max 2000
 * @default 20
 * @param y2
 * @text 槽 2 Y
 * @type number
 * @min -2000
 * @max 2000
 * @default 96
 * @param x3
 * @text 槽 3 X
 * @type number
 * @min -2000
 * @max 2000
 * @default 364
 * @param y3
 * @text 槽 3 Y
 * @type number
 * @min -2000
 * @max 2000
 * @default 96
 * @param x4
 * @text 槽 4 X
 * @type number
 * @min -2000
 * @max 2000
 * @default 120
 * @param y4
 * @text 槽 4 Y
 * @type number
 * @min -2000
 * @max 2000
 * @default 96
 *
 * @param reverse
 * @text 偶數槽左右反轉
 * @desc 套用於槽 2、4、6、8。
 * @type boolean
 * @on 反轉
 * @off 不反轉
 * @default true
 *
 * @param scaleX
 * @text X 縮放率（%）
 * @type number
 * @min -2000
 * @max 2000
 * @default 100
 * @param scaleY
 * @text Y 縮放率（%）
 * @type number
 * @min -2000
 * @max 2000
 * @default 100
 * @param opacity
 * @text 不透明度
 * @type number
 * @min 0
 * @max 255
 * @default 255
 *
 * @param blendMode
 * @text 混合模式
 * @type select
 * @option 一般
 * @value 0
 * @option 加算
 * @value 1
 * @option 乘算
 * @value 2
 * @option 濾色
 * @value 3
 * @default 0
 *
 * @param blinkSuffix1
 * @text 眨眼後綴 1
 * @desc 基底檔名加上此後綴；留空停用。
 * @type string
 * @default
 * @param blinkSuffix2
 * @text 眨眼後綴 2
 * @desc 基底檔名加上此後綴；留空停用。
 * @type string
 * @default
 */

/*~struct~SpeakSetting:
 * @param picture
 * @text 立繪底圖
 * @desc 與 F 指定的檔名相同；請使用已清除嘴巴的底圖。
 * @type file
 * @dir img/pictures/
 * @default
 *
 * @param mouthImage
 * @text 嘴型圖集
 * @desc 橫向等寬分格透明 PNG，第 0 格為閉嘴。
 * @type file
 * @dir img/pictures/
 * @default
 *
 * @param mouthX
 * @text 嘴部 X
 * @desc 相對於原始底圖左上角，縮放與鏡像前的像素座標。
 * @type number
 * @min -2000
 * @max 4000
 * @default 0
 * @param mouthY
 * @text 嘴部 Y
 * @desc 相對於原始底圖左上角的像素座標。
 * @type number
 * @min -2000
 * @max 4000
 * @default 0
 *
 * @param frameCount
 * @text 圖集格數
 * @type number
 * @min 1
 * @max 16
 * @default 3
 * @param frameWait
 * @text 每格持續幀數
 * @desc 60 個遊戲更新幀約一秒。
 * @type number
 * @min 1
 * @max 600
 * @default 6
 * @param frameOrder
 * @text 循環順序
 * @desc 從 0 起算，以逗號分隔。三嘴型建議 0,1,2,1。
 * @type string
 * @default 0,1,2,1
 */

/*~struct~FaceSetting:
 * @param picture
 * @text 立繪底圖／表情代碼
 * @desc F指令內的完整名稱。共用底圖留空時為圖片檔名；否則可為虛擬表情代碼。
 * @type string
 * @default
 * @param baseImage
 * @text 共用底圖（可留空）
 * @desc 實際載入的底圖。留空時載入「立繪底圖／表情代碼」同名PNG，保留舊版用法。
 * @type file
 * @dir img/pictures/
 * @default
 * @param faceImage
 * @text 表情臉圖（可留空）
 * @desc 單張局部臉圖，疊在底圖之上、眼嘴之下。留空不顯示此層。
 * @type file
 * @dir img/pictures/
 * @default
 * @param faceX
 * @text 臉圖X
 * @type number
 * @min -4000
 * @default 0
 * @param faceY
 * @text 臉圖Y
 * @type number
 * @min -4000
 * @default 0
 * @param mouthImage
 * @text 嘴型圖集
 * @type file
 * @dir img/pictures/
 * @default
 * @param mouthX
 * @text 嘴巴X
 * @type number
 * @min -4000
 * @default 0
 * @param mouthY
 * @text 嘴巴Y
 * @type number
 * @min -4000
 * @default 0
 * @param mouthColumns
 * @text 嘴型欄數（1=直式）
 * @type number
 * @min 1
 * @default 1
 * @param mouthFrameCount
 * @text 嘴型畫格數
 * @type number
 * @min 1
 * @max 16
 * @default 4
 * @param mouthFrameWidth
 * @text 嘴型單格寬（0=自動）
 * @type number
 * @min 0
 * @default 0
 * @param mouthFrameHeight
 * @text 嘴型單格高（0=自動）
 * @type number
 * @min 0
 * @default 0
 * @param mouthFrameWait
 * @text 嘴型每格更新單位（1/60秒）
 * @type number
 * @min 1
 * @default 15
 * @param mouthFrameOrder
 * @text 嘴型順序（0為閉嘴）
 * @default 0,1,2,3
 * @param eyeImage
 * @text 眼睛圖集
 * @type file
 * @dir img/pictures/
 * @default
 * @param eyeX
 * @text 眼睛X
 * @type number
 * @min -4000
 * @default 0
 * @param eyeY
 * @text 眼睛Y
 * @type number
 * @min -4000
 * @default 0
 * @param eyeColumns
 * @text 眼睛欄數（1=直式）
 * @type number
 * @min 1
 * @default 1
 * @param eyeFrameCount
 * @text 眼睛畫格數
 * @type number
 * @min 1
 * @max 16
 * @default 4
 * @param eyeFrameWidth
 * @text 眼睛單格寬（0=自動）
 * @type number
 * @min 0
 * @default 0
 * @param eyeFrameHeight
 * @text 眼睛單格高（0=自動）
 * @type number
 * @min 0
 * @default 0
 * @param eyeFrameWait
 * @text 眼睛每格更新單位（1/60秒）
 * @type number
 * @min 1
 * @default 15
 * @param eyeFrameOrder
 * @text 眨眼順序（0為睜眼）
 * @default 0,1,2,3
 * @param eyeAuto
 * @text 預設自動眨眼
 * @type boolean
 * @default true
 * @param eyeIntervalMin
 * @text 每次眨完後最短等待單位
 * @type number
 * @min 0
 * @default 180
 * @param eyeIntervalMax
 * @text 每次眨完後最長等待單位
 * @type number
 * @min 0
 * @default 300
 */

/*~struct~SlotSetting:
 * @param transition
 * @text 切換效果
 * @type select
 * @option 無
 * @value 0
 * @option 淡入淡出
 * @value 1
 * @option 從左浮入
 * @value 2
 * @option 從右浮入
 * @value 3
 * @option 從下浮入
 * @value 4
 * @option 從上浮入
 * @value 5
 * @default 1
 *
 * @param priority
 * @text 顯示層級
 * @desc 預設依「插入圖片編號＋槽位編號」排序；選「一般圖片前方」會蓋住全部一般圖片。
 * @type select
 * @option 一般圖片後方
 * @value behindPicture
 * @option 一般圖片之間
 * @value betweenPictures
 * @option 一般圖片前方
 * @value inFrontOfPicture
 * @option 視窗後方
 * @value behindWindow
 * @option 視窗前方
 * @value inFrontOfWindow
 * @default betweenPictures
 */

(() => {
    "use strict";

    const scriptSource = typeof document !== "undefined" ? document.currentScript?.src : "";
    const scriptName = scriptSource?.match(/([^/]+)\.js(?:[?#].*)?$/i);
    const pluginName = scriptName ? decodeURIComponent(scriptName[1]) : "LL_StandingPictureDirect";
    const params = PluginManager.parameters(pluginName);
    const stateKey = "_LL_StandingPictureDirect";
    const battleKey = "_LL_StandingPictureDirectBattleCache";
    const maxSlots = 8;

    const parseJson = (value, fallback) => {
        try {
            return JSON.parse(value || "");
        } catch (_) {
            return fallback;
        }
    };
    const warnOnceKeys = new Set();
    const warnOnce = (key, message) => {
        if (warnOnceKeys.has(key)) return;
        warnOnceKeys.add(key);
        console.warn(`[${pluginName}] ${message}`);
    };
    const finiteNumber = (value, fallback) => Number.isFinite(Number(value)) ? Number(value) : fallback;
    const cleanFilename = value => {
        let name = String(value ?? "").trim();
        if (name.length >= 2 && ((name.startsWith('"') && name.endsWith('"')) ||
            (name.startsWith("'") && name.endsWith("'")))) {
            name = name.slice(1, -1).trim();
        }
        return name.replace(/\.png\s*$/i, "").trim();
    };
    const speakSettings = new Map();
    const rawSpeakSettings = parseJson(params.speakSettings, []);
    if (Array.isArray(rawSpeakSettings)) rawSpeakSettings.forEach(raw => {
        const setting = typeof raw === "string" ? parseJson(raw, {}) : raw;
        if (!setting || typeof setting !== "object") return;
        const picture = cleanFilename(setting.picture);
        const mouthImage = cleanFilename(setting.mouthImage);
        if (!picture || !mouthImage) return;
        const frameCount = Math.max(1, Math.min(16, Math.floor(finiteNumber(setting.frameCount ?? 3, 3))));
        const frameWait = Math.max(1, Math.min(600, Math.floor(finiteNumber(setting.frameWait ?? 6, 6))));
        const parts = String(setting.frameOrder ?? "0,1,2,1").split(",").map(value => value.trim());
        let order = parts.map(Number);
        if (!parts.length || parts.some(value => !/^\d+$/.test(value)) ||
            order.some(value => value < 0 || value >= frameCount)) {
            warnOnce(`order:${picture}`, `${picture} 的嘴型順序無效，改用依序播放。`);
            order = Array.from({ length: frameCount }, (_, index) => index);
        }
        speakSettings.set(picture, {
            mouthImage, frameCount, frameWait, order, columns: frameCount, frameWidth: 0, frameHeight: 0,
            x: finiteNumber(setting.mouthX ?? 0, 0), y: finiteNumber(setting.mouthY ?? 0, 0)
        });
    });
    // Populated by the skill export profile; no historical expression catalog is bundled.
    const phebeAliases = new Map();
    const phebeSettings = [];
    // 僅菲比短代碼不分大小寫；一般圖片路徑維持原本的大小寫規則。
    const phebeKey = value => {
        const name = cleanFilename(value);
        const match = name.match(/^(?:phebe\/)?phebe_([1-9]\d?)$/i);
        return match && Number(match[1]) <= 60 ? `Phebe_${Number(match[1])}` : name;
    };
    const faceSettings = new Map();
    const faceInteger = (value, fallback, min = 0, max = 6000) =>
        Math.max(min, Math.min(max, Math.floor(finiteNumber(value ?? fallback, fallback))));
    const normalizeFaceLayer = (setting, prefix) => {
        const image = cleanFilename(setting[`${prefix}Image`]);
        if (!image) return null;
        const frameCount = faceInteger(setting[`${prefix}FrameCount`], 4, 1, 16);
        const parts = String(setting[`${prefix}FrameOrder`] ?? "0,1,2,3").split(",").map(v => v.trim());
        let order = parts.map(Number);
        if (parts.some(v => !/^\d+$/.test(v)) || order.some(v => v >= frameCount)) {
            warnOnce(`order:${image}`, `${image} 的畫格順序無效，改用依序播放。`);
            order = Array.from({length: frameCount}, (_, i) => i);
        }
        return { image, mouthImage: image, frameCount, order,
            columns: faceInteger(setting[`${prefix}Columns`], 1, 1, 16),
            frameWidth: faceInteger(setting[`${prefix}FrameWidth`], 0),
            frameHeight: faceInteger(setting[`${prefix}FrameHeight`], 0),
            frameWait: faceInteger(setting[`${prefix}FrameWait`], 15, 1),
            x: finiteNumber(setting[`${prefix}X`] ?? 0, 0), y: finiteNumber(setting[`${prefix}Y`] ?? 0, 0)
        };
    };
    const registerFaceSetting = raw => {
        const setting = typeof raw === "string" ? parseJson(raw, {}) : raw;
        if (!setting || typeof setting !== "object") return;
        const picture = phebeKey(setting.picture);
        if (!picture) return;
        const mouth = normalizeFaceLayer(setting, "mouth");
        const eyes = normalizeFaceLayer(setting, "eye");
        if (eyes) {
            const a = faceInteger(setting.eyeIntervalMin, 180), b = faceInteger(setting.eyeIntervalMax, 300);
            eyes.intervalMin = Math.min(a, b); eyes.intervalMax = Math.max(a, b);
            eyes.auto = String(setting.eyeAuto ?? "true").toLowerCase() === "true";
        }
        faceSettings.set(picture, {
            mouth, eyes,
            baseImage: cleanFilename(setting.baseImage),
            faceImage: cleanFilename(setting.faceImage),
            faceX: finiteNumber(setting.faceX ?? 0, 0),
            faceY: finiteNumber(setting.faceY ?? 0, 0)
        });
    };
    // 內建先登錄，使用者參數後登錄：同名項目由明確參數優先。
    phebeSettings.forEach(registerFaceSetting);
    const rawFaceSettings = parseJson(params.faceSettings, []);
    if (Array.isArray(rawFaceSettings)) rawFaceSettings.forEach(registerFaceSetting);
    const resolvePictureName = value => {
        const name = cleanFilename(value);
        if (faceSettings.has(name)) return name;
        const key = phebeKey(name);
        if (faceSettings.has(key)) return key;
        return phebeAliases.get(name.toLowerCase()) || name;
    };
    const faceFor = value => faceSettings.get(resolvePictureName(value));
    const atlasRect = (bitmap, config, frame) => {
        const columns = config.columns, rows = Math.ceil(config.frameCount / columns);
        const width = config.frameWidth || bitmap.width / columns;
        const height = config.frameHeight || bitmap.height / rows;
        if (width <= 0 || height <= 0 || !Number.isInteger(width) || !Number.isInteger(height) ||
            width * Math.min(columns, config.frameCount) > bitmap.width || height * rows > bitmap.height) {
            const image = config.image || config.mouthImage;
            warnOnce(`size:${image}`, `${image} 的尺寸不符合欄數、格數或單格寬高。`);
            return null;
        }
        return {x: (frame % columns) * width, y: Math.floor(frame / columns) * height, width, height};
    };
    const bodyMotions = new Map();
    const rawBodyMotions = parseJson(params.bodyMotions, []);
    if (Array.isArray(rawBodyMotions)) rawBodyMotions.forEach(raw => {
        const item = typeof raw === "string" ? parseJson(raw, {}) : raw;
        if (!item || typeof item !== "object") return;
        const id = cleanFilename(item.id), image = cleanFilename(item.image);
        if (!id || !image) return;
        const columns = Number(item.columns ?? 4) === 1 ? 1 : 4;
        bodyMotions.set(id, {
            id, image, columns, frameCount: 4,
            frameWidth: faceInteger(item.frameWidth, 0), frameHeight: faceInteger(item.frameHeight, 0),
            frameWait: faceInteger(item.frameWait, 15, 1),
            end: item.end === "restore" ? "restore" : "hold"
        });
    });
    const bitmapReady = bitmap => !!bitmap && bitmap.isReady();
    const defaultProfile = {
        prefix: "", origin: "0", x: "464", y: "96", x2: "20", y2: "96",
        x3: "364", y3: "96", x4: "120", y4: "96", reverse: "true",
        scaleX: "100", scaleY: "100", opacity: "255", blendMode: "0",
        blinkSuffix1: "", blinkSuffix2: ""
    };
    const normalizeProfile = raw => Object.assign({}, defaultProfile, raw || {});
    const profiles = parseJson(params.profiles, []).map(value =>
        normalizeProfile(typeof value === "string" ? parseJson(value, {}) : value)
    ).filter(profile => String(profile.prefix).length > 0)
        .sort((a, b) => String(b.prefix).length - String(a.prefix).length);
    const fallbackProfile = normalizeProfile(parseJson(params.fallbackProfile, {}));
    const slotSettings = Array.from({ length: maxSlots }, (_, index) => {
        const setting = parseJson(params[`slot${index + 1}`], {});
        return {
            transition: Number(setting.transition ?? 1),
            priority: String(setting.priority || "betweenPictures")
        };
    });
    const blinkInterval = Math.max(1, Number(params.blinkInterval || 180));
    const blinkWaitCount = Math.max(1, Number(params.blinkWaitCount || 4));
    const focusToneAdjust = Number(params.focusToneAdjust || -96);
    const picturePriority = Number(params.betweenPicturesPriority ?? 50);
    const betweenPicturesPriority = Number.isFinite(picturePriority)
        ? Math.max(0, Math.min(100, Math.floor(picturePriority))) : 50;

    const animationFrame = {
        yes: 24, yesyes: 48, no: 24, noslow: 48, jump: 24, jumpjump: 48,
        jumploop: 48, shake: 1, shakeloop: 1, runleft: 1, runright: 1,
        noslowloop: 96, breathing: 96, breathing2: 96, huwahuwa: 192, none: 0
    };

    const makeSlot = () => ({
        animationCount: 0,
        picture: null,
        show: false,
        refresh: false,
        motion: "",
        focus: true,
        speaking: false,
        speakSource: "",
        eyeMode: "auto",
        eyeTrigger: 0,
        bodyMotion: null,
        bodySerial: 0
    });
    const makeState = () => ({
        pictures: Array.from({ length: maxSlots }, makeSlot),
        hold: false,
        disabled: false,
        tone: [0, 0, 0, 0]
    });
    const state = () => {
        if (!$gameSystem[stateKey]) $gameSystem[stateKey] = makeState();
        const data = $gameSystem[stateKey];
        if (!Array.isArray(data.pictures) || data.pictures.length !== maxSlots) {
            data.pictures = Array.from({ length: maxSlots }, (_, index) =>
                Object.assign(makeSlot(), data.pictures?.[index] || {})
            );
        }
        // Eight-slot saves from before v1.0.4 need migration too.
        data.pictures.forEach(slot => {
            if (typeof slot.speaking !== "boolean") slot.speaking = false;
            if (typeof slot.speakSource !== "string") slot.speakSource = "";
            if (!["auto", "on", "off", "once"].includes(slot.eyeMode)) slot.eyeMode = "auto";
            if (!Number.isFinite(slot.eyeTrigger)) slot.eyeTrigger = 0;
            if (!Number.isFinite(slot.bodySerial)) slot.bodySerial = 0;
            if (!slot.bodyMotion || typeof slot.bodyMotion !== "object") slot.bodyMotion = null;
            if (slot.bodyMotion) {
                slot.bodyMotion.frameIndex = faceInteger(slot.bodyMotion.frameIndex, 0, 0, 3);
                slot.bodyMotion.wait = faceInteger(slot.bodyMotion.wait, 1, 1);
                slot.bodyMotion.loop = slot.bodyMotion.loop === true;
                slot.bodyMotion.finished = slot.bodyMotion.finished === true;
            }
        });
        return data;
    };

    const _Game_System_initialize = Game_System.prototype.initialize;
    Game_System.prototype.initialize = function() {
        _Game_System_initialize.apply(this, arguments);
        this[stateKey] = makeState();
        this[battleKey] = null;
    };

    const stopSpeaking = slot => {
        slot.speaking = false;
        slot.speakSource = "";
    };
    const stopMessageSpeaking = () => state().pictures.forEach(slot => {
        if (slot.speakSource === "message") stopSpeaking(slot);
    });
    const stopBody = slot => {
        slot.bodyMotion = null;
        slot.bodySerial++;
    };
    const applyBody = (slotNumber, value, loop = false) => {
        const number = Number(slotNumber), id = cleanFilename(value);
        if (!Number.isInteger(number) || number < 1 || number > maxSlots) return;
        const slot = state().pictures[number - 1];
        if (id.toUpperCase() === "OFF") { stopBody(slot); return; }
        const config = bodyMotions.get(id);
        if (!config || !slot.show || !slot.picture) {
            warnOnce(`body:${number}:${id}`, `槽 ${number} 尚未顯示立繪，或身體動作 ${id} 未登錄。`);
            return;
        }
        stopSpeaking(slot);
        slot.bodySerial++;
        slot.bodyMotion = {id, loop: loop === true, frameIndex: 0, wait: config.frameWait, finished: false};
    };
    const applySpeak = (value, source) => {
        const args = String(value).split(",").map(part => part.trim());
        const mode = String(args[1] ?? "ON").toUpperCase();
        if (!/^[1-8]$/.test(args[0]) || args.length > 2 || !["ON", "OFF"].includes(mode)) {
            warnOnce(`speak:${value}`, `無效 SPEAK[${value}]，請使用 SPEAK[1] 或 SPEAK[1,OFF]。`);
            return;
        }
        const slot = state().pictures[Number(args[0]) - 1];
        if (mode === "OFF") {
            stopSpeaking(slot);
        } else if (!slot.bodyMotion && slot.show && slot.picture &&
            (faceFor(slot.picture.imageName)?.mouth || speakSettings.has(slot.picture.imageName))) {
            slot.speaking = true;
            slot.speakSource = source;
        } else {
            warnOnce(`missing:${args[0]}:${slot.picture?.imageName}`, `槽 ${args[0]} 尚未顯示立繪，或未登錄該圖片的局部說話設定。`);
        }
    };
    const applyBlink = value => {
        const args = String(value).split(",").map(part => part.trim());
        const mode = String(args[1] ?? "ON").toUpperCase();
        if (!/^[1-8]$/.test(args[0]) || args.length > 2 || !["ON", "OFF", "ONCE"].includes(mode)) {
            warnOnce(`blink:${value}`, `無效 BLINK[${value}]，請使用 BLINK[1,ON/OFF/ONCE]。`);
            return;
        }
        const slot = state().pictures[Number(args[0]) - 1];
        if (mode === "OFF") slot.eyeMode = "off";
        else if (!slot.bodyMotion && slot.show && slot.picture && faceFor(slot.picture.imageName)?.eyes) {
            slot.eyeMode = mode.toLowerCase();
            if (mode === "ONCE") slot.eyeTrigger++;
        } else {
            warnOnce(`missing-eyes:${args[0]}:${slot.picture?.imageName}`, `槽 ${args[0]} 未顯示立繪，或未登錄眼睛圖集。`);
        }
    };
    const commandText = input => String(input || "").replace(/\\\\/g, "\x00").replace(/\\V\[(\d+)\]/gi, (_, id) =>
        String($gameVariables.value(Number(id)))
    );
    const processSpeakCommands = text => text.replace(/\\(?:(SPEAK|BLINK)\[([^\]]*)\]|ACT([1-8]?)\[([^\]]*)\](\s*\\loop\b)?)/gi,
        (whole, code, value, bodySlot, bodyId, loop) => {
            if (!code) applyBody(bodySlot || 1, bodyId, !!loop);
            else if (code.toUpperCase() === "SPEAK") applySpeak(value, "command");
            else applyBlink(value);
            return whole;
        });
    const profileFor = filename => profiles.find(profile =>
        filename.startsWith(String(profile.prefix))
    ) || profiles.find(profile => {
        const baseImage = faceFor(filename)?.baseImage;
        return baseImage && baseImage.startsWith(String(profile.prefix));
    }) || fallbackProfile;
    const pictureFor = filename => {
        filename = resolvePictureName(filename);
        const profile = profileFor(filename);
        return Object.assign({}, profile, {
            imageName: filename,
            imageNameBlink: profile.blinkSuffix1 ? filename + String(profile.blinkSuffix1) : "",
            imageNameBlink2: profile.blinkSuffix2 ? filename + String(profile.blinkSuffix2) : ""
        });
    };
    const slotFromAlias = (alias, letter) => {
        const upper = alias.toUpperCase();
        if (/^[1-8]$/.test(upper.slice(1))) return Number(upper.slice(1)) - 1;
        return upper.length / letter.length - 1;
    };

    const parseControlCharacters = input => {
        let text = String(input || "").replace(/\\V\[(\d+)\]/gi, (_, id) =>
            String($gameVariables.value(Number(id)))
        );
        const data = state();
        const names = new Map();
        const motions = new Map();

        text.replace(/\\(F{1,4}|F[1-8])\[([^\]]*)\]/gi, (_, alias, value) => {
            names.set(slotFromAlias(alias, "F"), cleanFilename(value));
            return _;
        });
        text.replace(/\\(M{1,4}|M[1-8])\[([^\]]*)\]/gi, (_, alias, value) => {
            motions.set(slotFromAlias(alias, "M"), String(value).trim().toLowerCase());
            return _;
        });

        data.pictures.forEach((slot, index) => {
            slot.focus = false;
            if (names.has(index)) {
                stopBody(slot);
                stopSpeaking(slot);
                slot.eyeMode = "auto";
                slot.eyeTrigger = 0;
                const filename = names.get(index);
                slot.picture = filename ? pictureFor(filename) : null;
                slot.show = !!slot.picture;
                slot.refresh = !!slot.picture;
                slot.motion = motions.get(index) || "none";
                slot.animationCount = animationFrame[slot.motion] || 0;
            } else if (!data.hold) {
                stopBody(slot);
                stopSpeaking(slot);
                slot.show = false;
                slot.motion = "";
                slot.animationCount = 0;
            } else if (motions.has(index)) {
                slot.motion = motions.get(index);
                slot.animationCount = animationFrame[slot.motion] || 0;
            }
        });

        let focused = false;
        text.replace(/\\AA\[([^\]]+)\]/gi, (_, value) => {
            const target = String(value).trim().toUpperCase();
            const aliases = { F: 0, FF: 1, FFF: 2, FFFF: 3 };
            const index = Object.prototype.hasOwnProperty.call(aliases, target)
                ? aliases[target] : Number(target) - 1;
            if (index >= 0 && index < maxSlots) {
                data.pictures[index].focus = true;
                focused = true;
            } else if (target === "N") {
                data.pictures.forEach(slot => slot.focus = false);
                focused = true;
            } else if (target === "R" || target === "0") {
                data.pictures.forEach(slot => slot.focus = true);
                focused = true;
            }
            return _;
        });
        if (!focused) data.pictures.forEach(slot => slot.focus = true);

        text.replace(/\\FH\[([^\]]+)\]/gi, (_, value) => {
            const mode = String(value).trim().toUpperCase();
            if (mode === "ON") data.hold = true;
            if (mode === "OFF") data.hold = false;
            return _;
        });
    };

    const clearPictures = slotNumber => {
        const data = state();
        if (slotNumber >= 1 && slotNumber <= maxSlots) {
            const slot = data.pictures[slotNumber - 1];
            stopBody(slot);
            stopSpeaking(slot);
            slot.show = false;
            slot.motion = "";
            slot.animationCount = 0;
        } else {
            data.pictures.forEach(slot => {
                stopBody(slot);
                stopSpeaking(slot);
                slot.show = false;
                slot.motion = "";
                slot.animationCount = 0;
            });
            data.hold = false;
        }
    };

    PluginManager.registerCommand(pluginName, "processChar", args => {
        const text = commandText(args.text);
        const hasSpeak = /(?:\\|\x00)(?:(?:SPEAK|BLINK)\[|ACT[1-8]?\[)/i.test(text);
        const hasLegacy = /\\(?:F{1,4}|F[1-8]|M{1,4}|M[1-8]|AA|FH)\[/i.test(text);
        // A mouth-only command must not hide, refresh or move any standing slot.
        if (hasSpeak && !hasLegacy) {
            processSpeakCommands(text);
            return;
        }
        parseControlCharacters(args.text);
        const data = state();
        data.pictures.forEach(slot => {
            if (slot.show) {
                slot.refresh = true;
                slot.animationCount = animationFrame[slot.motion] || 0;
            }
        });
        processSpeakCommands(text);
        if (!data.hold) clearPictures(0);
    });
    PluginManager.registerCommand(pluginName, "playBodyMotion", args => {
        applyBody(Number(args.slot || 1), args.motion, args.loop === "true" || args.loop === true);
    });
    PluginManager.registerCommand(pluginName, "stopBodyMotion", args => {
        applyBody(Number(args.slot || 1), "OFF");
    });
    PluginManager.registerCommand(pluginName, "setEnabled", args => {
        state().disabled = args.enabled !== "true";
    });
    PluginManager.registerCommand(pluginName, "setTone", args => {
        const data = state();
        data.tone = [Number(args.toneR), Number(args.toneG), Number(args.toneB), Number(args.toneC)];
        data.pictures.forEach(slot => slot.refresh = !!slot.picture);
    });
    PluginManager.registerCommand(pluginName, "clear", args => {
        clearPictures(Number(args.slot || 0));
    });

    function Sprite_StandingPictureDirect() {
        this.initialize(...arguments);
    }
    Sprite_StandingPictureDirect.prototype = Object.create(Sprite.prototype);
    Sprite_StandingPictureDirect.prototype.constructor = Sprite_StandingPictureDirect;
    Sprite_StandingPictureDirect.prototype.initialize = function() {
        Sprite.prototype.initialize.call(this);
        this.opacity = 0;
        this.opening = false;
        this.closing = false;
        this.originX = 0;
        this.originY = 0;
        this.showing = false;
        this._face = new Sprite();
        this._face.visible = false;
        this._blink1 = new Sprite();
        this._blink2 = new Sprite();
        this._mouth = new Sprite();
        this._mouth.visible = false;
        this._body = new Sprite();
        this._body.visible = false;
        this._bodyKey = "";
        this._bodyWasActive = false;
        this._pictureRequest = 0;
        this._speakConfig = null;
        this._eyeConfig = null;
        this._eyes = null;
        this._speechActive = false;
        this._speechStep = 0;
        this._speechWait = 0;
        this.addChild(this._face);
        this.addChild(this._blink1);
        this.addChild(this._blink2);
        // Closed-mouth frame also stays above legacy full-size blink overlays.
        this.addChild(this._mouth);
        this.addChild(this._body);
        this.resetBlink();
    };
    Sprite_StandingPictureDirect.prototype.resetBlink = function() {
        this._blink1.visible = false;
        this._blink2.visible = false;
        this._blinkInterval = Math.randomInt(blinkInterval * 2);
        this._blinkWait = blinkWaitCount;
        this._blinkAnimation = 0;
    };
    Sprite_StandingPictureDirect.prototype.setPicture = function(picture) {
        this._pictureRequest++;
        this._body.visible = false;
        this._bodyKey = "";
        this._bodyWasActive = false;
        const face = faceFor(picture.imageName);
        this._face.visible = false;
        this._face.bitmap = face?.faceImage ? ImageManager.loadPicture(face.faceImage) : null;
        this._face.x = face?.faceX || 0;
        this._face.y = face?.faceY || 0;
        this._speakConfig = face?.mouth || speakSettings.get(picture.imageName) || null;
        this._eyeConfig = face?.eyes || null;
        if (this._eyeConfig && !this._eyes) {
            this._eyes = new Sprite();
            this.addChildAt(this._eyes, this.children.indexOf(this._mouth));
        }
        if (this._eyes) {
            this._eyes.visible = false;
            this._eyes.bitmap = this._eyeConfig ? ImageManager.loadPicture(this._eyeConfig.image) : null;
            this._eyes.x = this._eyeConfig?.x || 0;
            this._eyes.y = this._eyeConfig?.y || 0;
        }
        this.resetEyes();
        this._mouth.visible = false;
        this._speechActive = false;
        this._speechStep = 0;
        this._speechWait = 0;
        this.bitmap = ImageManager.loadPicture(face?.baseImage || picture.imageName);
        this._mouth.bitmap = this._speakConfig ? ImageManager.loadPicture(this._speakConfig.mouthImage) : null;
        this._mouth.x = this._speakConfig?.x || 0;
        this._mouth.y = this._speakConfig?.y || 0;
        this._blink1.bitmap = !this._eyeConfig && picture.imageNameBlink
            ? ImageManager.loadPicture(picture.imageNameBlink) : null;
        this._blink2.bitmap = !this._eyeConfig && picture.imageNameBlink2
            ? ImageManager.loadPicture(picture.imageNameBlink2) : null;
        this.resetBlink();
    };
    Sprite_StandingPictureDirect.prototype.hideForBody = function() {
        this.setFrame(0, 0, 0, 0);
        this._face.visible = this._blink1.visible = this._blink2.visible = this._mouth.visible = false;
        if (this._eyes) this._eyes.visible = false;
    };
    Sprite_StandingPictureDirect.prototype.restoreBody = function() {
        if (this._bodyWasActive && bitmapReady(this.bitmap)) {
            this.setFrame(0, 0, this.bitmap.width, this.bitmap.height);
            this._face.visible = !!this._face.bitmap && this.showing;
            this.resetEyes();
            this.resetBlink();
        }
        this._body.visible = false;
        this._bodyKey = "";
        this._bodyWasActive = false;
    };
    Sprite_StandingPictureDirect.prototype.updateBody = function(slot) {
        const motion = slot.bodyMotion;
        if (!slot.show || !motion) {
            // Keep the last baked pose during a clear/fade-out, until opacity reaches zero.
            if (!slot.show && this._body.visible && this.opacity > 0) { this.hideForBody(); return; }
            this.restoreBody();
            return;
        }
        const config = bodyMotions.get(motion.id);
        if (!config) { stopBody(slot); this.restoreBody(); return; }
        const key = `${slot.bodySerial}:${motion.id}`;
        if (key !== this._bodyKey) {
            this.restoreBody();
            this._bodyKey = key;
            this._body.bitmap = ImageManager.loadPicture(config.image);
        }
        if (!bitmapReady(this._body.bitmap) || !bitmapReady(this.bitmap) || !this.showing) return;
        const rect = atlasRect(this._body.bitmap, config, motion.frameIndex);
        if (!rect || rect.width !== this.bitmap.width || rect.height !== this.bitmap.height) {
            warnOnce(`body-size:${config.id}`, `身體動作 ${config.id} 的單格尺寸須與原立繪畫布相同。`);
            stopBody(slot);
            this.restoreBody();
            return;
        }
        this._body.setFrame(rect.x, rect.y, rect.width, rect.height);
        this._body.visible = true;
        this._bodyWasActive = true;
        this.hideForBody();
        if (motion.finished || this.opening || this.closing || this.opacity <= 0) return;
        if (--motion.wait <= 0) {
            if (motion.frameIndex < 3) motion.frameIndex++;
            else if (motion.loop) motion.frameIndex = 0;
            else {
                motion.finished = true;
                if (config.end === "restore") stopBody(slot);
            }
            motion.wait = config.frameWait;
        }
    };
    Sprite_StandingPictureDirect.prototype.updateSpeech = function(speaking) {
        const config = this._speakConfig;
        const bitmap = this._mouth.bitmap;
        if (!config || !bitmapReady(bitmap)) {
            this._mouth.visible = false;
            return;
        }
        const rect = atlasRect(bitmap, config, 0);
        if (!rect) {
            this._mouth.visible = false;
            return;
        }
        const active = !!speaking && this.showing && !this.opening && !this.closing && this.opacity > 0;
        if (!active || !this._speechActive) {
            this._speechStep = 0;
            this._speechWait = config.frameWait;
        }
        this._speechActive = active;
        const frame = active ? config.order[this._speechStep] : 0;
        this._mouth.setFrame((frame % config.columns) * rect.width,
            Math.floor(frame / config.columns) * rect.height, rect.width, rect.height);
        this._mouth.visible = this.showing;
        if (active && --this._speechWait <= 0) {
            this._speechStep = (this._speechStep + 1) % config.order.length;
            this._speechWait = config.frameWait;
        }
    };
    Sprite_StandingPictureDirect.prototype.update = function() {
        Sprite.prototype.update.call(this);
        if (!this._eyeConfig) this.updateBlink();
    };
    Sprite_StandingPictureDirect.prototype.nextEyeInterval = function() {
        const c = this._eyeConfig;
        return c ? c.intervalMin + Math.randomInt(c.intervalMax - c.intervalMin + 1) : 0;
    };
    Sprite_StandingPictureDirect.prototype.resetEyes = function() {
        this._eyeActive = false;
        this._eyeStep = 0;
        this._eyeWait = this._eyeConfig?.frameWait || 15;
        this._eyeInterval = this.nextEyeInterval();
        this._eyeMode = null;
        this._eyeTrigger = -1;
    };
    Sprite_StandingPictureDirect.prototype.updateEyes = function(slot) {
        const c = this._eyeConfig, eyes = this._eyes;
        if (!c || !eyes || !bitmapReady(eyes.bitmap)) return;
        const rect = atlasRect(eyes.bitmap, c, 0);
        if (!rect) { eyes.visible = false; return; }
        eyes.visible = this.showing;
        const active = slot.show && this.showing && !this.opening && !this.closing && this.opacity > 0;
        if (this._eyeMode !== slot.eyeMode) {
            this._eyeActive = false;
            this._eyeStep = 0;
            this._eyeWait = c.frameWait;
            this._eyeInterval = this.nextEyeInterval();
            this._eyeMode = slot.eyeMode;
        }
        if (!active || slot.eyeMode === "off") {
            eyes.setFrame(0, 0, rect.width, rect.height);
            return;
        }
        if (slot.eyeMode === "once" && this._eyeTrigger !== slot.eyeTrigger) {
            this._eyeActive = true;
            this._eyeStep = 0;
            this._eyeWait = c.frameWait;
        }
        this._eyeTrigger = slot.eyeTrigger;
        const auto = slot.eyeMode === "on" || (slot.eyeMode === "auto" && c.auto);
        if (!this._eyeActive && auto) {
            if (this._eyeInterval > 0) this._eyeInterval--;
            else { this._eyeActive = true; this._eyeStep = 0; this._eyeWait = c.frameWait; }
        }
        const frame = this._eyeActive ? c.order[this._eyeStep] : 0;
        eyes.setFrame((frame % c.columns) * rect.width, Math.floor(frame / c.columns) * rect.height,
            rect.width, rect.height);
        if (this._eyeActive && --this._eyeWait <= 0) {
            this._eyeStep++;
            this._eyeWait = c.frameWait;
            if (this._eyeStep >= c.order.length) {
                this._eyeActive = false;
                this._eyeStep = 0;
                this._eyeInterval = this.nextEyeInterval();
            }
        }
    };
    Sprite_StandingPictureDirect.prototype.updateBlink = function() {
        if (this.opening || this.closing || !this._blink1.bitmap) {
            this._blink1.visible = false;
            this._blink2.visible = false;
            return;
        }
        if (this._blinkInterval > 0) {
            this._blinkInterval--;
            return;
        }
        this._blinkWait--;
        if (this._blinkWait > 0) return;
        this._blinkAnimation++;
        if (this._blinkAnimation > 2 || (this._blinkAnimation === 2 && !this._blink2.bitmap)) {
            this._blinkAnimation = 0;
        }
        this._blink1.visible = this._blinkAnimation === 1;
        this._blink2.visible = this._blinkAnimation === 2;
        this._blinkWait = blinkWaitCount;
        this._blinkInterval = this._blinkAnimation === 0 ? Math.randomInt(blinkInterval * 2) : 0;
    };
    Sprite_StandingPictureDirect.prototype.setPictureBlendMode = function(mode) {
        this.blendMode = mode;
        this._face.blendMode = mode;
        this._body.blendMode = mode;
        this._blink1.blendMode = mode;
        this._blink2.blendMode = mode;
        this._mouth.blendMode = mode;
        if (this._eyes) this._eyes.blendMode = mode;
    };

    class StandingPictureDirect {
        static create(scene) {
            scene._standingPictureDirectSprites = [];
            for (let index = 0; index < maxSlots; index++) {
                const sprite = new Sprite_StandingPictureDirect();
                scene._standingPictureDirectSprites.push(sprite);
                this.addToLayer(scene, sprite, slotSettings[index].priority, index + 1);
            }
            const data = state();
            if (scene instanceof Scene_Battle) {
                if (!$gameSystem[battleKey]) $gameSystem[battleKey] = data;
                const battleState = makeState();
                battleState.disabled = data.disabled;
                battleState.tone = data.tone;
                $gameSystem[stateKey] = battleState;
            } else if ($gameSystem[battleKey]) {
                const battleState = data;
                const mapState = $gameSystem[battleKey];
                mapState.disabled = battleState.disabled;
                mapState.tone = battleState.tone;
                $gameSystem[stateKey] = mapState;
                $gameSystem[battleKey] = null;
            }
            state().pictures.forEach(slot => {
                if (slot.speakSource === "message") stopSpeaking(slot);
                if (slot.show) {
                    slot.refresh = true;
                    slot.animationCount = animationFrame[slot.motion] || 0;
                }
            });
        }

        static addToLayer(scene, sprite, priority, slotNumber) {
            const spriteset = scene._spriteset;
            const pictureContainer = spriteset._pictureContainer;
            if (priority === "behindPicture") {
                spriteset.addChildAt(sprite, Math.max(0, spriteset.children.indexOf(pictureContainer)));
            } else if (priority === "betweenPictures") {
                // 每槽以「基準 + 槽位編號」排序；同編號的一般圖片放在立繪下方。
                // 依圖片 ID 尋找位置，避免其他立繪或插件子物件改變陣列索引。
                const slotPictureId = betweenPicturesPriority + slotNumber;
                const nextPictureIndex = pictureContainer.children.findIndex(child =>
                    child instanceof Sprite_Picture && child._pictureId > slotPictureId
                );
                pictureContainer.addChildAt(sprite, nextPictureIndex >= 0
                    ? nextPictureIndex : pictureContainer.children.length);
            } else if (priority === "inFrontOfWindow") {
                scene.addChildAt(sprite, Math.min(scene.children.indexOf(scene._windowLayer) + 1, scene.children.length));
            } else if (priority === "behindWindow") {
                scene.addChildAt(sprite, Math.min(scene.children.indexOf(spriteset) + 1, scene.children.length));
            } else {
                spriteset.addChildAt(sprite, Math.min(spriteset.children.indexOf(pictureContainer) + 1, spriteset.children.length));
            }
        }

        static update(scene) {
            const data = state();
            const sprites = scene._standingPictureDirectSprites || [];
            if (data.disabled) {
                sprites.forEach(sprite => sprite.opacity = 0);
                return;
            }
            data.pictures.forEach((slot, index) => {
                const sprite = sprites[index];
                if (!sprite) return;
                if (slot.picture && slot.refresh) {
                    this.refresh(sprite, slot.picture, index + 1, data.tone);
                    slot.refresh = false;
                }
                if (slot.show && slot.picture) this.fadeIn(sprite, slot.picture);
                else this.fadeOut(sprite, slot.picture, index + 1);
                sprite.updateSpeech(slot.speaking && slot.show);
                sprite.updateEyes(slot);
                sprite.updateBody(slot);
                sprite.setBlendColor(slot.focus ? [0, 0, 0, 0] : [0, 0, 0, -focusToneAdjust]);
                if (!sprite.opening && !sprite.closing && slot.animationCount > 0) {
                    slot.animationCount = this.animation(sprite, slot.motion, slot.animationCount);
                }
            });
        }

        static refresh(sprite, picture, slotNumber, tone) {
            sprite.setPicture(picture);
            sprite.showing = false;
            sprite.visible = false;
            let scaleX = Number(picture.scaleX);
            const scaleY = Number(picture.scaleY);
            const reverse = picture.reverse === true || String(picture.reverse) === "true" || Number(picture.reverse) === -1;
            if (slotNumber % 2 === 0 && reverse) scaleX *= -1;
            const position = (slotNumber - 1) % 4;
            const x = Number(picture[position ? `x${position + 1}` : "x"]);
            const y = Number(picture[position ? `y${position + 1}` : "y"]);
            const bitmap = sprite.bitmap;
            const face = sprite._face.bitmap;
            const mouth = sprite._mouth.bitmap;
            const eyes = sprite._eyes?.bitmap;
            const request = sprite._pictureRequest;
            let applied = false;
            const onReady = () => {
                if (applied || sprite._pictureRequest !== request || !bitmapReady(bitmap) ||
                    (face && !bitmapReady(face)) ||
                    (mouth && !bitmapReady(mouth)) || (eyes && !bitmapReady(eyes))) return;
                applied = true;
                sprite.setFrame(0, 0, bitmap.width, bitmap.height);
                if (Number(picture.origin) === 0) {
                    sprite.originX = x;
                    sprite.originY = y;
                } else {
                    sprite.originX = x - bitmap.width * scaleX / 200;
                    sprite.originY = y - bitmap.height * scaleY / 200;
                }
                sprite.x = sprite.originX;
                sprite.y = sprite.originY;
                if (sprite.opacity === 0) {
                    const transition = slotSettings[slotNumber - 1].transition;
                    if (transition === 0) sprite.opacity = Number(picture.opacity);
                    if (transition === 2) sprite.x -= 30;
                    if (transition === 3) sprite.x += 30;
                    if (transition === 4) sprite.y += 30;
                    if (transition === 5) sprite.y -= 30;
                }
                sprite.setPictureBlendMode(Number(picture.blendMode));
                sprite.setColorTone(tone || [0, 0, 0, 0]);
                sprite.scale.x = scaleX / 100;
                sprite.scale.y = scaleY / 100;
                sprite.showing = true;
                sprite._face.visible = !!face;
                sprite.visible = true;
            };
            bitmap.addLoadListener(onReady);
            if (face) face.addLoadListener(onReady);
            if (mouth) mouth.addLoadListener(onReady);
            if (eyes) eyes.addLoadListener(onReady);
        }

        static fadeIn(sprite, picture) {
            if (!sprite.showing) return;
            const opacity = Number(picture.opacity);
            if (sprite.opacity >= opacity) {
                sprite.opening = false;
                sprite.opacity = opacity;
                return;
            }
            sprite.opening = true;
            sprite.closing = false;
            if (sprite.originX > sprite.x) sprite.x += 2;
            if (sprite.originX < sprite.x) sprite.x -= 2;
            if (sprite.originY > sprite.y) sprite.y += 2;
            if (sprite.originY < sprite.y) sprite.y -= 2;
            sprite.opacity += opacity / 15;
        }

        static fadeOut(sprite, picture, slotNumber) {
            if (sprite.opacity <= 0) {
                sprite.opacity = 0;
                sprite.closing = false;
                return;
            }
            sprite.closing = true;
            if (!picture) {
                sprite.opacity = 0;
                return;
            }
            sprite.opacity -= Number(picture.opacity) / 15;
            const transition = slotSettings[slotNumber - 1].transition;
            if (transition === 0) sprite.opacity = 0;
            if (transition === 2 && sprite.x > sprite.originX - 30) sprite.x -= 2;
            if (transition === 3 && sprite.x < sprite.originX + 30) sprite.x += 2;
            if (transition === 4 && sprite.y < sprite.originY + 30) sprite.y += 2;
            if (transition === 5 && sprite.y > sprite.originY - 30) sprite.y -= 2;
        }

        static animation(sprite, motion, count) {
            if (!sprite.showing) return count;
            if (motion === "yes") {
                sprite.y += count > 12 ? 2 : -2; count--;
            } else if (motion === "yesyes") {
                sprite.y += count > 36 || (count <= 24 && count > 12) ? 2 : -2; count--;
            } else if (motion === "no") {
                sprite.x += count > 18 || count <= 6 ? 2 : -2; count--;
            } else if (motion === "noslow") {
                sprite.x += count > 36 || count <= 12 ? 1 : -1; count--;
            } else if (motion === "jump") {
                sprite.y += count > 12 ? -2 : 2; count--;
            } else if (motion === "jumpjump") {
                sprite.y += count > 36 || (count <= 24 && count > 12) ? -2 : 2; count--;
            } else if (motion === "jumploop") {
                if (count > 36) sprite.y -= 2;
                else if (count > 24) sprite.y += 2;
                count--; if (count === 0) count = animationFrame.jumploop;
            } else if (motion === "shake") {
                if (count <= 2) { sprite.x -= 2; count++; }
                else if (count <= 4) { sprite.y -= 2; count++; }
                else if (count <= 6) { sprite.x += 4; sprite.y += 4; count++; }
                else if (count <= 8) { sprite.y -= 2; count++; }
                else if (count === 9) { sprite.x -= 2; count++; }
                else if (count === 10) { sprite.x -= 2; count = 0; }
            } else if (motion === "shakeloop") {
                if (count <= 2) { sprite.x -= 1; count++; }
                else if (count <= 4) { sprite.y -= 1; count++; }
                else if (count <= 6) { sprite.x += 2; sprite.y += 2; count++; }
                else if (count <= 8) { sprite.y -= 1; count++; }
                else if (count <= 10) { sprite.x -= 1; count++; }
                if (count > 10) count = 1;
            } else if (motion === "runleft") {
                sprite.x -= 16; if (sprite.x < -2000) count = 0;
            } else if (motion === "runright") {
                sprite.x += 16; if (sprite.x > 2000) count = 0;
            } else if (motion === "noslowloop") {
                sprite.x += count > 72 || count <= 24 ? 0.25 : -0.25;
                count--; if (count === 0) count = animationFrame.noslowloop;
            } else if (motion === "breathing") {
                if (count > 72) sprite.y += 0.5;
                else if (count > 48) sprite.y -= 0.5;
                count--; if (count === 0) count = animationFrame.breathing;
            } else if (motion === "breathing2") {
                if (count > 48) { sprite.y -= sprite.height * 0.0003; sprite.scale.y += 0.0003; }
                else { sprite.y += sprite.height * 0.0003; sprite.scale.y -= 0.0003; }
                count--; if (count === 0) count = animationFrame.breathing2;
            } else if (motion === "huwahuwa") {
                sprite.y += count > 144 || count <= 48 ? 0.25 : -0.25;
                count--; if (count === 0) count = animationFrame.huwahuwa;
            }
            return count;
        }
    }

    const _Scene_Map_createDisplayObjects = Scene_Map.prototype.createDisplayObjects;
    Scene_Map.prototype.createDisplayObjects = function() {
        _Scene_Map_createDisplayObjects.apply(this, arguments);
        StandingPictureDirect.create(this);
    };
    const _Scene_Map_update = Scene_Map.prototype.update;
    Scene_Map.prototype.update = function() {
        _Scene_Map_update.apply(this, arguments);
        StandingPictureDirect.update(this);
    };
    const _Scene_Battle_createDisplayObjects = Scene_Battle.prototype.createDisplayObjects;
    Scene_Battle.prototype.createDisplayObjects = function() {
        _Scene_Battle_createDisplayObjects.apply(this, arguments);
        StandingPictureDirect.create(this);
    };
    const _Scene_Battle_update = Scene_Battle.prototype.update;
    Scene_Battle.prototype.update = function() {
        _Scene_Battle_update.apply(this, arguments);
        StandingPictureDirect.update(this);
    };

    const _Window_Message_startMessage = Window_Message.prototype.startMessage;
    Window_Message.prototype.startMessage = function() {
        stopMessageSpeaking();
        parseControlCharacters($gameMessage.allText());
        _Window_Message_startMessage.apply(this, arguments);
    };
    const _Window_Message_processEscapeCharacter = Window_Message.prototype.processEscapeCharacter;
    Window_Message.prototype.processEscapeCharacter = function(code, textState) {
        const upper = String(code).toUpperCase();
        const bodyCode = upper.match(/^ACT([1-8]?)$/);
        if (bodyCode) {
            // MZ's escape-code reader stops before digits: ACT1 arrives as ACT + "1[id]".
            const match = /^([1-8]?)\[([^\]]*)\](\s*\x1bloop\b)?/i.exec(textState.text.slice(textState.index));
            if (match) {
                textState.index += match[0].length;
                if (textState.drawing !== false) applyBody(bodyCode[1] || match[1] || 1, match[2], !!match[3]);
            }
            return;
        }
        if (upper === "LOOP") return;
        if (["SPEAK", "BLINK"].includes(upper)) {
            const match = /^\[([^\]]*)\]/.exec(textState.text.slice(textState.index));
            if (match) {
                textState.index += match[0].length;
                if (textState.drawing !== false) {
                    if (upper === "SPEAK") applySpeak(match[1], "message");
                    else applyBlink(match[1]);
                }
            } else {
                warnOnce(`${upper}:bracket`, `${upper} 後面需要 [槽位] 或 [槽位,模式]。`);
            }
            return;
        }
        _Window_Message_processEscapeCharacter.apply(this, arguments);
    };
    const _Window_Message_onEndOfText = Window_Message.prototype.onEndOfText;
    Window_Message.prototype.onEndOfText = function() {
        stopMessageSpeaking();
        _Window_Message_onEndOfText.apply(this, arguments);
    };
    const _Window_Message_terminateMessage = Window_Message.prototype.terminateMessage;
    Window_Message.prototype.terminateMessage = function() {
        stopMessageSpeaking();
        _Window_Message_terminateMessage.apply(this, arguments);
    };
    const _Window_Message_updateClose = Window_Message.prototype.updateClose;
    Window_Message.prototype.updateClose = function() {
        if (this._closing && this.openness === 255 && !state().hold) {
            state().pictures.forEach(slot => {
                stopBody(slot);
                stopSpeaking(slot);
                slot.show = false;
                slot.motion = "";
                slot.animationCount = 0;
            });
        }
        _Window_Message_updateClose.apply(this, arguments);
    };

    const _Window_Base_convertEscapeCharacters = Window_Base.prototype.convertEscapeCharacters;
    Window_Base.prototype.convertEscapeCharacters = function(text) {
        text = String(text)
            .replace(/\\(?:F{1,4}|F[1-8])\[(?:\\V\[\d+\]|[^\]])*\]/gi, "")
            .replace(/\\(?:M{1,4}|M[1-8])\[[^\]]*\]/gi, "")
            .replace(/\\AA\[[^\]]*\]/gi, "")
            .replace(/\\FH\[[^\]]*\]/gi, "");
        // Message windows need the tag at the text cursor; other windows just hide it.
        if (!(this instanceof Window_Message)) text = text
            .replace(/\\(?:SPEAK|BLINK)\[(?:\\V\[\d+\]|[^\]])*\]/gi, "")
            .replace(/\\ACT[1-8]?\[[^\]]*\](\s*\\loop\b)?/gi, "");
        return _Window_Base_convertEscapeCharacters.call(this, text);
    };
})();
