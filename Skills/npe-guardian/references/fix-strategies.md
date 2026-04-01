# Fix Strategies

Use this file after a null-safety finding has already been confirmed against the source.

## Selection Rule

Choose the smallest fix that preserves current semantics and matches local style.

If the finding comes from NullAway or Checker Framework, prefer a local code repair before escalating to repository-wide annotation or compiler-policy changes.

## Patterns

### 1. Guard clause before dereference

Use when a nullable parameter, field, or method result is dereferenced immediately.

Preferred forms:

```java
if (value == null) {
    return;
}
```

```java
if (value == null) {
    throw new IllegalArgumentException("value must not be null");
}
```

Pick `return` only when the method already treats missing data as non-fatal. Pick an exception only when the codebase already fails fast for contract violations.

### 2. Split chained dereference

Use when the risky path is hidden inside a chain.

```java
Address address = user.getAddress();
if (address == null) {
    return DEFAULT_CITY;
}
return address.getCity();
```

This is usually safer than stacking null checks inside one expression.

### 3. Normalize nullable collection or array input

Use when code iterates or calls methods on a possibly null collection.

```java
List<Item> safeItems = items == null ? Collections.emptyList() : items;
for (Item item : safeItems) {
    process(item);
}
```

Prefer this when an empty collection already means "nothing to process".

### 4. Fail fast with Objects.requireNonNull

Use when null is a programmer error and the surrounding code already assumes non-null.

```java
Customer customer = Objects.requireNonNull(order.getCustomer(), "customer");
return customer.getId();
```

Avoid this when callers rely on graceful handling or fallback behavior.

### 5. Replace nullable return handling with explicit local branch

Use when a helper can return null but only one call site is risky.

```java
Config config = loadConfig();
if (config == null) {
    return DEFAULT_CONFIG;
}
return config.getTimeout();
```

Prefer local branching over changing the helper signature unless multiple call sites are broken.

### 6. Add annotation only when the project already uses annotations

Use `@Nullable` or `@NonNull` only when the repository already has an established nullness annotation set.

Rules:

- Reuse the project's existing annotation package.
- Do not mix annotation ecosystems in the same patch.
- Do not introduce annotation-only changes without an actual behavior fix unless the user asked for it.

### 7. Optional as boundary adapter, not blanket rewrite

Use `Optional` when the surrounding API already models absence explicitly.

Good use:

```java
return Optional.ofNullable(repository.find(id))
        .map(Entity::getName)
        .orElse(DEFAULT_NAME);
```

Avoid converting multiple signatures in one pass unless the task is specifically a broader refactor.

## Smells That Need Extra Care

Pause before auto-fixing when you see:

- Framework callbacks with injected state
- Lazy initialization across threads
- Builders with partially initialized objects
- Reflection, proxies, or code generation
- Public APIs whose null semantics are not documented

In these cases, prefer a narrower fix or ask for confirmation.
