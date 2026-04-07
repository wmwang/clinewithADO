# Java Spring Boot CA 規則參考

本文件作為 AI Code Review 的依據。審查時，請根據以下規則逐一檢視變更的檔案。

---

## 一、命名規範（Naming Conventions）

| 元素 | 規範 | 反例 | 正例 |
|------|------|------|------|
| 類別（Class） | PascalCase，名詞，意義明確 | `Proc`, `Mgr` | `OrderProcessor`, `UserManager` |
| 方法（Method） | camelCase，動詞開頭 | `data()`, `userInfo()` | `getUserById()`, `processOrder()` |
| 變數 | camelCase，意義明確，避免縮寫 | `usrNm`, `amt`, `tmp` | `userName`, `totalAmount`, `tempFile` |
| 常數 | UPPER_SNAKE_CASE，`static final` | `maxRetry`, `Max_Retry` | `MAX_RETRY_COUNT` |
| Package | 全小寫，反向域名 | `com.Example.Api` | `com.example.service.order` |
| DTO | 以 `Dto`、`Request`、`Response` 結尾 | `UserData`, `UserInfo` | `UserDto`, `CreateOrderRequest` |
| Entity | 與 DB table 對應，避免 `Entity` 後綴 | `UserEntity` | `User`, `Order` |
| Repository | 以 `Repository` 結尾 | `UserDao`, `UserRepo` | `UserRepository` |
| Service interface | 以 `Service` 結尾（不加 `Impl` 前綴） | `IUserService` | `UserService` |
| Service 實作 | 以 `ServiceImpl` 結尾 | `UserServiceV1` | `UserServiceImpl` |

---

## 二、Spring Boot 架構分層（Layered Architecture）

**強制分層原則**：

```
Controller → Service → Repository
```

- **Controller（@RestController）**：只處理 HTTP 請求/回應、DTO 轉換、輸入驗證。不得包含業務邏輯。
- **Service（@Service）**：所有業務邏輯在此層。不得直接呼叫其他 Service 的 Repository，應透過對應 Service 方法。
- **Repository（@Repository）**：只負責資料存取（JPA / JDBC）。不得包含業務邏輯。

**常見違規**：
- Controller 直接注入 Repository（略過 Service 層）
- Service 中直接寫 HTTP 相關邏輯（如 `HttpServletRequest`）
- Repository 中放業務判斷邏輯

---

## 三、依賴注入（Dependency Injection）

**強烈建議：Constructor Injection**，避免 Field Injection（`@Autowired` 在 field 上）。

```java
// ❌ 禁止：Field Injection（難以測試、隱式依賴）
@Service
public class OrderService {
    @Autowired
    private OrderRepository orderRepository;
}

// ✅ 建議：Constructor Injection（可搭配 Lombok @RequiredArgsConstructor）
@Service
@RequiredArgsConstructor
public class OrderService {
    private final OrderRepository orderRepository;
}
```

---

## 四、@Transactional 使用規範

1. **多步驟資料庫操作必須加 `@Transactional`**，確保原子性。
2. **唯讀查詢加 `@Transactional(readOnly = true)`**，提升效能（避免 dirty checking）。
3. 預設加在 **Service 方法層**，不在 Repository 方法上重複加。
4. 避免在 **private 方法** 上加 `@Transactional`（Spring AOP 代理不會攔截）。
5. 捕捉 checked exception 後不重拋會導致 transaction **不回滾**，需加 `rollbackFor`：

```java
// ❌ 問題：RuntimeException 以外的例外不自動回滾
@Transactional
public void process() throws IOException { ... }

// ✅ 明確指定回滾條件
@Transactional(rollbackFor = Exception.class)
public void process() throws IOException { ... }
```

---

## 五、例外處理（Exception Handling）

1. **禁止空的 catch block**（吞掉例外），至少要 log。
2. 使用 **自訂業務例外**，繼承 `RuntimeException`（Spring 事務回滾友善）。
3. **全域例外處理** 使用 `@ControllerAdvice` + `@ExceptionHandler`，不要在每個 Controller 重複處理。
4. **不要對外暴露** 內部 stack trace 或系統細節（安全風險）。
5. Log level 使用原則：
   - 預期的業務例外（資料不存在等）：`log.warn`
   - 非預期系統例外：`log.error`

```java
// ❌ 反例
try {
    userRepository.save(user);
} catch (Exception e) {
    // 什麼都不做
}

// ✅ 正例
try {
    userRepository.save(user);
} catch (DataIntegrityViolationException e) {
    log.warn("User already exists: {}", user.getEmail());
    throw new DuplicateUserException("Email already registered");
}
```

---

## 六、安全性（Security）

### SQL Injection
- **禁止** 用字串拼接建構 SQL/JPQL 查詢。
- 使用 JPA `@Query` 搭配命名參數（`:param`）或 `JdbcTemplate` 的 `?` 佔位符。

```java
// ❌ SQL Injection 風險
String query = "SELECT * FROM users WHERE name = '" + name + "'";

// ✅ 安全寫法
@Query("SELECT u FROM User u WHERE u.name = :name")
List<User> findByName(@Param("name") String name);
```

### Secret / 憑證管理
- **禁止** 在程式碼中硬編碼密碼、API Key、Token、DB 連線字串。
- 使用 `@Value("${property.key}")` 搭配 `application.yml` / 環境變數。
- `application.yml` 不得 commit 含正式環境的憑證。

### 輸入驗證
- API 入口參數使用 Bean Validation（`@Valid`、`@NotNull`、`@Size` 等）。
- 不信任任何來自前端的輸入，包含路徑參數。

### 權限控制
- 敏感操作需確認有對應的 `@PreAuthorize` 或 Security Filter。

---

## 七、效能與 JPA（Performance）

### N+1 Query 問題
- **懶加載關聯（LAZY）** 在迴圈中存取會產生 N+1 問題。
- 解法：使用 `@EntityGraph`、`JOIN FETCH`、或 `@BatchSize`。

```java
// ❌ N+1：在迴圈中觸發 LAZY load
List<Order> orders = orderRepository.findAll();
orders.forEach(o -> System.out.println(o.getItems().size())); // N+1

// ✅ 一次 JOIN FETCH
@Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.status = :status")
List<Order> findWithItems(@Param("status") OrderStatus status);
```

### 分頁（Pagination）
- 列表查詢必須使用 `Pageable`，禁止 `findAll()` 不加分頁（資料量大時 OOM 風險）。

### 不必要的物件建立
- 避免在迴圈內重複建立 StringBuilder、日期格式化物件等。

### 快取
- 熱點唯讀資料考慮 `@Cacheable`，但需有對應的 `@CacheEvict` 策略。

---

## 八、測試覆蓋（Test Coverage）

審查時關注：

1. **新增的 Service 方法是否有對應的 unit test？**
2. **Repository 層有無 `@DataJpaTest` 驗證查詢正確性？**
3. **Controller 層有無 `@WebMvcTest` 驗證 API contract？**
4. **測試方法名稱** 是否清楚描述情境：`should_returnUser_whenValidId()`
5. **測試覆蓋 Happy Path + Edge Case**（null、空集合、邊界值）。
6. **禁止 `@SpringBootTest` 濫用**（啟動整個 context，速度慢）；只在整合測試使用。

---

## 九、程式碼品質（Code Quality）

| 規則 | 說明 |
|------|------|
| 方法長度 | 單一方法不超過 **30 行**（含空行）；超過應拆分 private helper |
| 類別長度 | 單一類別不超過 **300 行**；超過應考慮拆分職責 |
| 巢狀深度 | if/for 巢狀不超過 **3 層**；可用 early return 或 Stream 扁平化 |
| Optional | 方法回傳可能為 null 時，使用 `Optional<T>` 而非直接回傳 null |
| 泛型 | 禁止 raw type（如 `List`、`Map` 不帶泛型參數） |
| Magic Number | 禁止程式碼中出現無意義數字，應定義為 `static final` 常數 |
| Stream 濫用 | 複雜多步驟轉換考慮可讀性，過度鏈式 Stream 不易維護 |
| Lombok | 允許 `@Getter`、`@Setter`、`@Builder`、`@RequiredArgsConstructor`；謹慎使用 `@Data`（會生成 equals/hashCode，JPA entity 慎用） |

---

## 十、Logging 規範

```java
// ❌ 禁止使用 System.out.println
System.out.println("User created: " + userId);

// ❌ 禁止 log 中拼接字串（效能問題，即使不輸出也會建構字串）
log.debug("Processing user: " + userId);

// ✅ 使用 SLF4J，佔位符格式
log.debug("Processing user: {}", userId);
log.info("Order created: orderId={}, userId={}", orderId, userId);
```

- 禁止 log 含個人敏感資訊（姓名、Email、電話、卡號）。
- 正式環境 log level 應為 `INFO` 以上，避免大量 `DEBUG` 影響效能。
