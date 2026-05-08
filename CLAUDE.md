# Mango v3 繁體中文翻譯專案

Mango Automation v3 的繁體中文（Traditional Chinese）i18n 翻譯專案。

Mango Automation 是一套工控／自動化／SCADA 軟體，官方網站：https://radixiot.com/product/mango/  
術語翻譯以台灣工控／SCADA 領域的慣用繁體中文為準；無對應中文術語者，適當保留英文原文。

## 專案結構

```
modules/
  {ModuleName}/
    classes/
      i18n.properties       # 英文原始檔（來源，唯讀，已凍結不再更新）
      i18n_zh.properties    # 繁體中文翻譯檔（翻譯目標）
tools/                      # 翻譯輔助腳本（Python）
```

> **注意**：英文語系檔 `i18n.properties` 已終止更新，不會再新增字串。
> 翻譯工作僅需直接編輯 `i18n_zh.properties`，不需執行 `merge_en_zh.vbs` 或 `copy_i18n_zh_to_Production.cmd`。

## 翻譯起點

現有 `i18n_zh.properties` 內容品質不佳（大量機器翻譯錯誤），可**整個清空後重新翻譯**。  
以 `i18n.properties` 作為唯一參考來源，逐條翻譯。

## 翻譯規範

### 語言
- 目標語言：**繁體中文**，嚴禁使用簡體中文用語
- 語氣：UI 標籤用名詞形式，操作按鈕用動詞形式，避免冗贅

### 術語一致性（統一詞彙表）

工控／SCADA 核心術語：

| 英文 | 繁體中文 |
|------|---------|
| Point | 點 |
| Data source | 資料來源 |
| Data point | 資料點 |
| Publisher | 發布者 |
| Tag | 標籤 |
| Alarm | 警報 |
| Event | 事件 |
| Event handler | 事件處理器 |
| Set point | 設定點 |
| Maintenance event | 維護事件 |
| Watchlist | 監控清單 |
| Script | 腳本 |
| Meta data source | 元資料來源 |
| Virtual data source | 虛擬資料來源 |
| Report | 報表 |
| Dashboard | 儀表板 |
| Permission | 權限 |
| Purge | 清除 |

通訊／網路術語：

| 英文 | 繁體中文 |
|------|---------|
| Timeout | 逾時 |
| Retry / Retries | 重試 |
| Device | 裝置 |
| Network | 網路 |
| Serial | 序列埠 |
| Listener | 監聽器 |
| Discovery | 探索 |
| Segment | 區段 |
| Lease | 租用期 |
| Poll period | 輪詢週期 |
| Register | 暫存器 |
| Coil | 線圈 |
| Node | 節點 |
| Gateway | 閘道 |

UI 一般術語：

| 英文 | 繁體中文 |
|------|---------|
| Set | 設定 |
| Remove | 移除 |
| Export | 匯出 |
| Import | 匯入 |
| Template | 範本 |
| Log | 日誌 |
| Object | 物件 |
| Chart / Image chart | 圖表 |
| Cron pattern | Cron 模式 |
| Maintenance | 維護 |
| Virtual | 虛擬 |

### 格式規則

1. **保留佔位符**：`{0}`、`{1}` 等佔位符必須原封不動保留，位置可調整但不可刪除
2. **保留英文專有名詞**：技術縮寫（BACnet、Modbus、MQTT、SNMP、DNP3、Haystack、TCP/IP、Cron、XML、CSV 等）保持英文大小寫不變
3. **括號格式**：使用全形括號（）；技術單位保留英文，如 `（ms）`、`（分鐘）`
4. **不翻譯的內容**：key 名稱、程式碼片段、MAC 位址、IP 位址、OID、URL 等技術識別碼

### 常見錯誤翻譯（需避免）

| 錯誤 | 正確 |
|------|------|
| 蘋果（MAC 的誤譯）| MAC |
| 克朗模式 | Cron 模式 |
| 觀點（point 的誤譯）| 點 |
| 消除（remove 的誤譯）| 移除 |
| 放（set 的誤譯）| 設定 |
| 圖像圖 | 圖表 |
| 發送什麼（WhoIs 的誤譯）| 發送 WhoIs |
| 細分（segment 的誤譯）| 區段 |
| 本地 | 本機 |
| 租賃（lease 的誤譯）| 租用期 |

## 翻譯輔助工具（tools/）

| 腳本 | 用途 |
|------|------|
| `report_untranslated_lang_zh.py` | 找出尚未翻譯的 key（值仍為英文） |
| `apply_term_mapping.py` | 套用詞彙修正對照表 |
| `batch_translate_modules.py` | 批次翻譯所有模組 |
| `sync_i18n.py` | 同步 `lang_zh` 主模組的 key 順序 |
| `fill_with_english.py` | 以英文原文填入空值 key |

詞彙修正對照表：`tools/lang_zh_termmap_preview.csv`（格式：`key,old_value,new_value`）

## 檔案格式

`.properties` 檔案格式：
```
# 注釋行
key=翻譯文字
key.with.placeholder=含有 {0} 佔位符的文字
```

- 編碼：UTF-8
- 行結尾：LF（`\n`）
- 空行保留原位，維持可讀性
- 注釋行（`#` 開頭）不翻譯，原樣保留

## 翻譯品質檢查要點

翻譯或修改 `i18n_zh.properties` 時，確認：
1. 所有佔位符 `{0}` `{1}` 均保留
2. 專有名詞（BACnet、Modbus、Cron 等）未被翻譯
3. 無明顯機器翻譯錯誤（參考常見錯誤列表）
4. 術語與詞彙表一致，符合台灣工控領域慣用語
5. 未翻譯的 key 應使用英文原文，不可為空值

## 翻譯檢核進度

進度判定基準：`i18n_zh.properties` 檔案更新日期為 2026-05-08 至 2026-05-09 者，先列為已完成檢核；其餘列為待檢核。

統計：共 67 個模組，已完成 67 個，待檢核 0 個。

- [x] `abeip`（2026-05-09 00:05:32）
- [x] `abpccc`（2026-05-09 00:03:34）
- [x] `advancedComponents`（2026-05-08 23:53:39）
- [x] `advancedScheduler`（2026-05-09）
- [x] `asciiFile`（2026-05-09 00:06:57）
- [x] `BACnet`（2026-05-09 00:51:00）
- [x] `cloudConnect`（2026-05-09）
- [x] `controlcore`（2026-05-09 00:05:56）
- [x] `dashboardDesigner`（2026-05-09 00:07:43）
- [x] `dataFile`（2026-05-09）
- [x] `dataImport`（2026-05-08 23:58:12）
- [x] `dataPointDetailsView`（2026-05-09 00:05:07）
- [x] `deviceConfig`（2026-05-09 00:06:15）
- [x] `dnp3`（2026-05-09）
- [x] `egauge`（2026-05-09）
- [x] `envcands`（2026-05-08 23:58:39）
- [x] `excelReports`（2026-05-09 00:52:17）
- [x] `galil`（2026-05-09 00:05:44）
- [x] `graphicalViews`（2026-05-09）
- [x] `Haystack`（2026-05-09）
- [x] `http`（2026-05-09 00:50:37）
- [x] `internal`（2026-05-09）
- [x] `jmxds`（2026-05-09 00:04:32）
- [x] `jsonFileImport`（2026-05-08 23:58:56）
- [x] `lang_zh`（2026-05-09 00:52:17）
- [x] `log4jDS`（2026-05-08 23:58:26）
- [x] `log4JReset`（2026-05-08 23:58:00）
- [x] `loggingConsole`（2026-05-08 23:58:05）
- [x] `maintenanceEvents`（2026-05-09）
- [x] `mangoApi`（2026-05-09）
- [x] `mangoESConfiguration`（2026-05-09）
- [x] `MangoIOTools`（2026-05-08 23:57:51）
- [x] `mangoNoSqlDatabase`（2026-05-09）
- [x] `mangoUI`（2026-05-09 00:51:53）
- [x] `mbus`（2026-05-09）
- [x] `measurlogicDTSCell`（2026-05-08 23:58:47）
- [x] `meta`（2026-05-09）
- [x] `modbus`（2026-05-09 00:50:37）
- [x] `mqttClientDataSource`（2026-05-09 00:07:31）
- [x] `onewire`（2026-05-09 00:06:06）
- [x] `opcda`（2026-05-08 23:58:17）
- [x] `openv4j`（2026-05-08 23:58:21）
- [x] `pachube`（2026-05-08 23:59:14）
- [x] `pakbus`（2026-05-09）
- [x] `persistent`（2026-05-09）
- [x] `pid`（2026-05-09）
- [x] `pointLinks`（2026-05-09 00:04:54）
- [x] `pop3`（2026-05-09 00:04:22）
- [x] `reports`（2026-05-09）
- [x] `scheduledEvents`（2026-05-09 00:04:14）
- [x] `scripting`（2026-05-09 00:06:43）
- [x] `serial`（2026-05-09）
- [x] `slackPublisher`（2026-05-08 23:53:43）
- [x] `snmp`（2026-05-09 00:52:54）
- [x] `sqlConsole`（2026-05-08 23:58:32）
- [x] `sqlds`（2026-05-09 00:07:13）
- [x] `ssh`（2026-05-09 00:04:04）
- [x] `sstGlobalScripts`（2026-05-09 00:04:41）
- [x] `sstGraphics`（2026-05-08 23:53:40）
- [x] `sstTheme`（2026-05-08 23:53:42）
- [x] `TCPIP`（2026-05-09 00:05:20）
- [x] `templateConfig`（2026-05-08 23:57:55）
- [x] `twilio`（2026-05-08 23:59:04）
- [x] `virtualDS`（2026-05-09 00:03:55）
- [x] `vmstat`（2026-05-09 00:03:46）
- [x] `watchlists`（2026-05-09 00:06:30）
- [x] `zwave`（2026-05-09）

