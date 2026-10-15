# GR IV 刷 GR4-LUTSmith：檢查與還原清單

> 整理日期：2026-10-15。依據 [GR4-LUTSmith README（v2.2.0）](https://github.com/lemonadesaltbagel/GR4-LUTSmith) 與 [Ricoh GR IV 官方韌體頁](https://www.ricoh-imaging.co.jp/english/support/digital/gr4_s.html)。
> 標「〔通用做法〕」的是我補的一般韌體作業習慣，不是兩份來源寫的。

---

## 0. 先決定要不要做

- [ ] 我知道這是**非官方**修改，Ricoh 不支援，可能影響保固。
- [ ] 我知道下載官方韌體時同意的授權條款寫明：軟體只供 GR IV 使用者、**不得修改或還原工程**。用 LUTSmith 等於違反這份條款（契約問題，不是安全問題）。
- [ ] 我知道更新中斷時，官方說明相機可能無法操作，**保固期內也要付費維修**；LUTSmith 也寫明這種情況要送 Ricoh。
- [ ] 我知道 **1.11 無法降版**，而且 Ricoh 之後發布的新版會蓋掉自訂色彩。
- [ ] 我知道這個專案 2026-10-09 才建立（第一個正式發行版 v2.0.0 是 10-10），截至 10-15：
  - issue／PR 共 21 筆，全是同一天的開發整理，**沒有任何使用者回報**（好壞都沒有）。
  - 專案程式碼本身**沒有授權條款**（issue #20），只能自用，不要再散布它產生的韌體。
  - 作者的測試表寫明：**預設設定（High Contrast 槽位、保留原名稱與圖示、滑桿歸零）這個確切組合還沒實際刷過**；改用其他槽位、自訂名稱、自訂圖示則都測過。v2.2.0 產生的檔案刷在**一般版 GR IV** 上也還沒實測（離線比對只多了 HDF 的設定）。
- [ ] 決定：現在做，或等 1–2 個月看到其他人的成功／失敗回報再做。

## 1. 確認相機

- [ ] 機型是 **GR IV 或 GR IV HDF**。**GR IV Monochrome 不支援**，絕對不要刷。
- [ ] 記下自己的是一般版還是 HDF：＿＿＿＿
- [ ] 韌體版本：MENU → 設定選單 → 相機資訊。必須**剛好是 1.11**。
  - 低於 1.11：先用官方檔正常更新到 1.11，確認一切正常後再繼續。
  - 高於 1.11：**停止**，這個工具不支援。
- [ ] 如果曾經刷過其他修改工具（GRMod、gr-custom-tool、MonoUnlock 等），先刷回官方 1.11。GRMod 文件提醒：ADJ 槽位如果還留著柔焦，刷回官方前要先移除，否則會卡住。

## 2. 備份

- [ ] Custom 1–3（C1–C3）和其他自訂設定逐頁拍照記錄（工具說明建議記下，刷機後可能要重設）。
- [ ] 目前常用的 Image Control 參數拍照記錄。
- [ ] 卡上的照片全部匯出。
- [ ] 用這台 GR IV 拍一張 **DNG**，日光下、有膚色、天空、綠葉、灰色物體最好。給工具當 `--photo` 用。

## 3. 準備官方檔案

- [ ] 從 Ricoh 官方頁下載 `Gr4_v1.11.zip`（約 33.7 MB，自解壓），解出 **`fwdc248b.bin`**。
- [ ] 計算 SHA-256：
  ```bash
  shasum -a 256 fwdc248b.bin
  ```
  LUTSmith README 列的官方檔雜湊是 `a2f664dfca034059eb0fd6e18ab08684c326b4a034d85c164dad7e1ec9b5655f`。
  Ricoh 官方頁沒有公布雜湊，所以這只是專案的說法；但**如果不一致就停下來**重新下載。
- [ ] 把這個官方檔另存一份到固定位置（例如 `camera-looks/official_1.11/fwdc248b.bin`），檔名不改。**這是還原用的救命檔**。〔通用做法〕
- [ ] LUT 用一般（Rec.709／sRGB）照片用的「創意 LUT」。**S-Log、V-Log 這類轉換 LUT 不支援**。記下它是 sRGB 還是 Adobe RGB。

## 4. 取得並驗證工具

二選一：

- **App（Apple Silicon 版）**：從 Releases 下載 `GR4-LUTSmith-2.2.0-macOS-AppleSilicon.zip`，先驗證來源：
  ```bash
  gh attestation verify GR4-LUTSmith-2.2.0-macOS-AppleSilicon.zip --repo lemonadesaltbagel/GR4-LUTSmith
  ```
  要看到 `Verification succeeded!` 才打開。App 沒有付費簽章，macOS 要到「隱私權與安全性」按「強制打開」。
- **命令列（從原始碼跑，可讀程式碼）**：
  ```bash
  uv sync --extra photo
  ```

接著：

- [ ] 自我測試，要印出 `selftest: PASSED`：
  ```bash
  uv run gr4_lutsmith.py selftest official_1.11/fwdc248b.bin
  ```
- [ ] 先只做擬合、不產生韌體，多試幾個 LUT：
  ```bash
  uv run gr4_lutsmith.py fit my_look.cube --photo R0001234.DNG
  ```
  看結果：**good**（ΔE00 平均 <1）＞ **approximate**（<2）＞ **poor**。
- [ ] 產生預覽圖，三格比較「無 look／LUT 本身／相機加 look」：
  ```bash
  uv run gr4_lutsmith.py preview output/my_look/look.json R0001234.DNG
  ```
  只比色彩和階調，銳利度和雜訊不模擬。

## 5. 產生韌體

- [ ] 產生：
  ```bash
  uv run gr4_lutsmith.py make my_look.cube official_1.11/fwdc248b.bin --photo R0001234.DNG
  ```
  一定要從**官方檔**產生，工具不接受已經改過的檔案。
- [ ] 第一次建議用**預設的 High Contrast 槽位**：它取代的是隱藏的單色 look，不會失去任何 Ricoh 原本的彩色風格。
- [ ] 自訂名稱只用英數字（ASCII），所有相機語言都能顯示。
- [ ] 出現 `refused: …` 代表工具拒絕寫入，**不要加 `--force` 硬做**。
- [ ] 檢查產出檔，要寫明是 GR4-LUTSmith 韌體、槽位正確：
  ```bash
  uv run gr4_lutsmith.py check output/my_look/fwdc248b.bin
  ```
- [ ] 記下產出檔的 SHA-256：＿＿＿＿

## 6. 刷入前

- [ ] 電池 DB-120 **充滿**，或接官方變壓器 K-AC166J。
- [ ] microSD（64 MB 以上）**在相機內格式化**。
- [ ] 卡片根目錄只放一個 `fwdc248b.bin`，不放資料夾、不改檔名。
- [ ] 刷入前再跑一次 `check`，確認卡上的是要刷的那個檔。〔通用做法〕
- [ ] 在室內桌上進行，旁邊不放會碰到相機的東西。〔通用做法〕

## 7. 刷入（Ricoh 官方流程）

1. [ ] 關機，裝好電池和 microSD，關好蓋子。
2. [ ] **按住 MENU 鍵開機**。
3. [ ] 用四向鍵選「Execute」，按 OK。
4. [ ] 畫面顯示 **1.11 → 1.11**。這是預期的，修改版保留版本號，確認繼續。
5. [ ] 等到「Update completed」、相機重新啟動。期間**不關機、不開電池蓋或卡蓋、不拔卡**。

## 8. 刷入後驗證

- [ ] 相機資訊仍顯示 1.11。
- [ ] Image Control 選 **High Contrast**（第一個 HDR Tone 之後那個）：現在是彩色、套用自訂 look。
- [ ] 逐項試：拍 JPEG、拍 DNG、機內 RAW 顯像、錄影、拍攝畫面即時預覽，都要正常。
- [ ] 其他 Ricoh 原本的 look 沒有改變。
- [ ] 重開機兩三次，確認穩定。〔通用做法〕
- [ ] 在相機內格式化卡片，避免下次開機誤觸更新。

## 9. 還原到官方

- [ ] 先確認還原檔是官方原版：
  ```bash
  uv run gr4_lutsmith.py check official_1.11/fwdc248b.bin
  ```
  要顯示官方 1.11，SHA-256 也要和第 3 步記下的一致。
- [ ] 照第 6、7 步流程刷入官方檔，畫面同樣顯示 1.11 → 1.11。
- [ ] 確認 High Contrast 回到單色。
- [ ] **送修前一定要先還原**。
- [ ] 想換另一個 LUT：從官方檔重新產生，再照同樣流程刷入，不必先還原。

## 10. 出狀況時

- **顯示更新失敗**：不要連續重刷。先換一張卡並在相機內格式化、確認電池滿電，再刷一次**官方檔**。〔通用做法〕gr-custom-tool 的作者也提醒：發現異常就停止反覆刷寫。
- **開不了機或卡在畫面**：取出電池等一會兒，再試「按住 MENU 開機」進更新模式，刷官方檔。〔通用做法〕
- **連更新模式都進不去**：只能送 Ricoh 維修，可能要付費。記下發生經過、使用的工具版本、產出檔的 SHA-256。
- 不論成功或失敗，把結果記下來；這個專案目前最缺的就是使用者回報。
