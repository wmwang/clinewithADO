# Java Clean Architecture API 規格模板

此模板基於 MESSV-MesOperationService 的 Ports & Adapters 架構（Spring Boot 3.x + Java 17）。
用於從 VB6 Form 分析產出 `06-java-ca-api-spec.md`。

---

## Package 結構慣例

```
{module-name}/
├── adapter/
│   ├── in/
│   │   └── controller/
│   │       └── {Domain}Controller.java          ← REST API 入口
│   └── out/
│       ├── jdbc/                                 ← JDBC Repository 實作
│       │   └── {Entity}JdbcRepository.java
│       ├── jpa/                                  ← JPA Entity + Repository 實作
│       │   ├── {Entity}JpaEntity.java
│       │   └── {Entity}JpaRepository.java
│       └── corba/                                ← CORBA / 外部系統 Adapter
│           └── {Service}CorbaAdapter.java
├── usecase/
│   ├── impl/
│   │   └── {feature}/
│   │       └── {Verb}{Noun}UseCaseImpl.java      ← Use Case 實作
│   └── ports/
│       ├── in/
│       │   └── {feature}/
│       │       ├── {Verb}{Noun}UseCase.java       ← Use Case 介面（in port）
│       │       ├── {Verb}{Noun}Command.java        ← 命令型 input（寫入操作）
│       │       ├── {Verb}{Noun}Query.java          ← 查詢型 input（讀取操作）
│       │       └── {Verb}{Noun}Response.java       ← Use Case output DTO
│       └── out/
│           ├── {Noun}Repository.java              ← DB out port（介面）
│           └── {Service}Gateway.java              ← 外部系統 out port（介面）
├── domain/
│   ├── {Entity}.java                              ← Domain Entity / Value Object
│   └── {Domain}Service.java                       ← Domain Service（純業務規則）
└── framework/
    ├── di/
    │   └── {Module}DependencyInjection.java        ← Spring Bean 注入設定
    └── exceptions/
        └── {Domain}Exception.java
```

---

## 規格文件輸出格式

### 1. 模組概述

```
## 模組：{module-name}

業務邊界：{一句話描述這個模組負責什麼}
對應 VB6 Form：{frm 檔案名稱}
主要功能：
- {功能 1}
- {功能 2}
```

---

### 2. API Endpoint 規格（Controller 層）

每個 VB6 按鈕/操作對應一個 endpoint：

```
## Endpoint：{HTTP Method} /api/{module}/{resource}

Summary：{一句話說明這個 API 的用途}
Controller：{module}/adapter/in/controller/{Domain}Controller.java
Method：{controllerMethodName}()
對應 VB6：{frm 檔}.{按鈕名稱}_Click（或 Form_Load）

### Request
Content-Type: application/json
{
  "{field1}": "{type} // {說明}",
  "{field2}": "{type} // {說明}"
}

### Response
{
  "{field1}": "{type} // {說明}",
  "{field2}": "{type} // {說明}"
}

### HTTP Status
- 200 OK：成功
- 400 Bad Request：輸入驗證失敗
- 404 Not Found：資源不存在
- 500 Internal Server Error：系統錯誤
```

---

### 3. Use Case 規格（Application 層）

```
## Use Case：{Verb}{Noun}UseCase

介面路徑：{module}/usecase/ports/in/{feature}/{Verb}{Noun}UseCase.java
實作路徑：{module}/usecase/impl/{feature}/{Verb}{Noun}UseCaseImpl.java
對應 VB6 邏輯：{說明對應的舊程式哪些函式}

### 介面定義
public interface {Verb}{Noun}UseCase {
    {Verb}{Noun}Response execute({Verb}{Noun}Command command);
    // 或查詢型：
    // {Verb}{Noun}Response execute({Verb}{Noun}Query query);
}

### Input（Command / Query）
{module}/usecase/ports/in/{feature}/{Verb}{Noun}Command.java
public record {Verb}{Noun}Command(
    {Type} {field1},   // {說明}
    {Type} {field2}    // {說明}
) {}

### Output（Response）
{module}/usecase/ports/in/{feature}/{Verb}{Noun}Response.java
public record {Verb}{Noun}Response(
    {Type} {field1},   // {說明}
    {Type} {field2}    // {說明}
) {}

### 業務流程（對應 VB6 call chain）
1. 驗證 input（對應：{VB6 驗證邏輯}）
2. 呼叫 {NounRepository}.{method}() 查詢/更新（對應：{SQL 操作}）
3. 呼叫 {ServiceGateway}.{method}() 外部系統（對應：CORBA Tx* 呼叫）
4. 組裝 Response 回傳
```

---

### 4. Domain Entity 規格（Domain 層）

```
## Entity：{Entity}

路徑：{module}/domain/{Entity}.java
對應資料表：{DB_TABLE_NAME}

public class {Entity} {
    private {Type} {field1};   // {說明}
    private {Type} {field2};   // {說明}

    // 業務規則（對應 VB6 的驗證或計算邏輯）
    public boolean {businessRuleMethod}() { ... }
}
```

---

### 5. Repository 介面（Out Port）

```
## Repository：{Noun}Repository

路徑：{module}/usecase/ports/out/{Noun}Repository.java
實作：{module}/adapter/out/jdbc/{Noun}JdbcRepository.java
對應資料表：{DB_TABLE_NAME}

public interface {Noun}Repository {
    Optional<{Entity}> findBy{Key}({Type} {key});    // 對應：SELECT ... WHERE ...
    List<{Entity}> findAll{Noun}By{Condition}(...);   // 對應：SELECT ... WHERE ...
    void save({Entity} entity);                        // 對應：INSERT / UPDATE
    void deleteBy{Key}({Type} {key});                 // 對應：DELETE WHERE ...
}
```

---

### 6. Integration Adapter 規格（CORBA / 外部系統）

```
## Integration Adapter：{Service}Gateway

路徑（out port 介面）：{module}/usecase/ports/out/{Service}Gateway.java
實作（CORBA adapter）：{module}/adapter/out/corba/{Service}CorbaAdapter.java
對應 VB6 CORBA 呼叫：{TxMethodName} / {TSMC_txMethodName}

public interface {Service}Gateway {
    {ReturnType} {methodName}({Type} {param});   // {白話說明業務語意}
}

// VB6 原始呼叫：
// {原始 CORBA 呼叫程式碼片段}
// 業務語意：{白話說明這個 CORBA 呼叫在做什麼}
// 傳入：{參數說明}
// 回傳：{回傳資料說明}
```

---

## 命名規則速查

| VB6 概念 | Java CA 對應 | 命名範例 |
|----------|-------------|---------|
| Form_Load 查詢 | Query Use Case | `GetLotInfoUseCase` |
| 按鈕 click 執行 | Command Use Case | `TransferLotUseCase` |
| SQL SELECT | Repository findBy... | `findByLotId(String lotId)` |
| SQL INSERT/UPDATE | Repository save | `save(Lot lot)` |
| SQL DELETE | Repository deleteBy... | `deleteByLotId(String lotId)` |
| CORBA `TxGetXxx` | Gateway getXxx | `LotInfoGateway.getLotInfo()` |
| CORBA `TxUpdateXxx` | Gateway updateXxx | `LotStatusGateway.updateStatus()` |
| CORBA `TSMC_txXxx` | Gateway xxxAction | `ManufacturingGateway.transferLot()` |
| Form 全域變數 | Domain Entity field | Entity 的屬性 |
| 共用 Module 計算 | Domain Service | `LotValidationService` |

---

## 注意事項

- **不要把 UI 邏輯搬進 Use Case**：VB6 中混在 `_Click` 事件裡的 msgbox、UI 狀態切換，不應出現在 Java Use Case。
- **CORBA 呼叫一律包成 Gateway 介面**：不要讓 Use Case 直接知道 CORBA 的存在，透過 out port 隔離。
- **一個 Use Case 只做一件事**：若 VB6 按鈕背後做了 3 件不相關的事，考慮拆成 3 個 Use Case 或用 Orchestration Use Case 協調。
- **DB 交易邊界**：VB6 中若有 BeginTrans/CommitTrans，Java 端用 `@Transactional` 在 Use Case 層標示。
- **共用 Module**：若多個 Form 共用相同邏輯，考慮放進 `shared` 模組的 Gateway 或 `cacore` 的通用 service。
