# LL 共用底圖與編號對照契約

先讀實際目標插件與已授權的遊戲參數；不能把工作區副本當成遊戲已安裝版本。`probe`只證明靜態宣告與SHA，不是引擎驗證。

## 共用版（預設）

目標需有faceSettings、眼嘴四格欄位，以及baseImage、faceImage、faceX、faceY。當前專案v1.4.0具備這些欄位。插件的faceSettings解析點必須經讀碼確認；工具目前支援唯一的 `const rawFaceSettings = parseJson(params.faceSettings, []);`，其他寫法要另做適配，不能猜測替換。

匯出的 `plugin/<原插件檔名>.js` 是新副本，保留原本程式，並將本批 `LL_EXPORTED_FACE_SETTINGS` 置於使用者參數之前。表內包含picture表情代碼、實際共用底圖、局部臉圖、眼嘴圖集、全部局部座標、格數、單格尺寸、順序、速度及眨眼設定。使用者明確同名參數後登錄，優先於內建對照。

例如picture=Phebe_1、baseImage=phebe/phebe_base、faceImage=phebe/phebe_1；眼睛eyes_j及嘴巴mouth_k由實際表指定。picture是虛擬代碼，不必有img/pictures/Phebe_1.png。預設命令前綴為character_id首字母大寫，可在manifest的command_prefix明確指定。

新正式清單與歷史菲比替代清單的編號不同。匯出Phebe正式對照時會停用目標的舊菲比預設登錄及舊語意別名，避免缺項落回錯誤表情；既有遊戲的事件／存檔不得未經檢查自動改成新含義。當前遊戲、原插件與舊圖包均保留。

```text
\F1[Phebe_1]\FH[ON]
\SPEAK[1]
\SPEAK[1,OFF]
\BLINK[1,ON]
\BLINK[1,OFF]
\BLINK[1,ONCE]
```

F後的1為槽位，Phebe後的1為正式表情編號。F不強制持續說話；訊息內SPEAK到文字輸出完停止，插件指令內SPEAK持續到OFF、換圖或清除。FH控制訊息外／跨訊息保留。OFF只回素材0號格，不保證所有表情都閉嘴或睜眼。

疊放順序為共用底圖→臉圖→眼睛→嘴巴。所有局部X/Y都相對未縮放原畫布左上角；跟隨父層位置、原點、縮放、鏡像、透明度、變暗與淡出，不另算一套螢幕座標。

## 舊版相容

只有v1.1眼嘴欄位而沒有共用臉圖時，顯式使用 `--layout legacy`。此模式保留每表情完整底圖和struct參數，不能宣稱一張共用底圖或相同容量節省。主技能的生成／語意／1×4規則仍適用。

`faceSettings-readable.json`供核對；parameter版是JSON字串陣列，值轉字串。共用版不需要匯入該快照。若用它覆寫，按picture鍵合併並保留其他角色；勿同時安裝重複插件。安裝到遊戲或更改plugins.js需任務授權。

## B姿勢與動作

不同手、臂、肩、軀幹需要獨立姿勢母圖，不把手勢畫進A；同姿勢相容表情才可共用。頭頸保持原規格固定，手去配合臉位。手遮臉、逐格頭位改變或層序不相容時，烘焙完整四格，禁止再疊局部眼嘴。

每張B圖集改為橫向4欄1列，預設2880×720。四格來源矩形為(0,0,720,720)、(720,0,720,720)、(1440,0,720,720)、(2160,0,720,720)。眼嘴維持直向1欄4列。

## 原生身體播放器（LL v1.4）

目標需宣告bodyMotions的id/image/columns/frameWidth/frameHeight/frameWait/end，並註冊playBodyMotion與stopBodyMotion。匯出器按此原生契約自動綁定已驗收的baked圖集，記adapter.status=native_bound；只代表設定已綁定，不代表完整MZ實機驗證。

```text
\F1[Phebe_9]\FH[ON]\ACT1[facepalm]
\ACT1[facepalm]\loop
\ACT1[OFF]
```

ACT後的1是槽位1～8，ACT省略槽位時使用1。先以F顯示角色；動作代碼由本批motions.id指定。預設從第1格依序到第4格，每格15更新單位，預設一次後停在第4格。只有緊接在該ACT後的`\loop`才讓它循環；同一文字內不同槽位各自判定，不是全域開關。

匯出插件的LL_EXPORTED_BODY_MOTIONS包含實際image、columns=4、單格寬高、frameWait、end=hold。可在插件管理器的「身體動作圖集」覆寫同名設定。`playBodyMotion`插件指令也有slot/motion/loop=false，`stopBodyMotion`恢復原立繪。舊直向身體圖集只有明確columns=1才可讀，新圖集一律橫向。

播放及停末格期間，隱藏父層底圖與局部臉／眼嘴、舊眨眼，只顯示烘焙身體格，避免原站姿殘影或五官蓋到手上。ACT OFF、換F表情或clear會取消動作。訊息內ACT在游標位置啟動，文字輸出完不會提前停止；保持模式仍依FH處理。載入及淡入期間暫停換格，重複啟動同一動作從第1格重播；普通說話與眨眼在baked動作期間不另疊加。

記錄frame_duration（預設15）、loop（預設false）、end（預設hold）、columns（預設4）、overlay_mode=baked及四格座標。原生播放器會按ACT的loop註記決定是否循環，不以圖包內的loop屬性強制所有呼叫循環。自訂end=restore可在一次播放後回原立繪；未指定仍停第4格。

通用匯出器目前只輸出baked身體格；仍未自動拆出可和獨立眼嘴混用的身體局部層。舊LL無原生接口時，B美術可預覽但adapter維持unbound、runtime_complete=false。

自訂接口只有實際讀到播放器、設定真實adapter config與測試證據後，才標verified。其他插件的PlayAction等接口要按其原始碼另適配，不自動安裝或啟用。素材、HTML、最小宿主與MZ實機驗證分開記錄。
