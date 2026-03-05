# Defense-in-Depth Debugging Skill

## Purpose

Validate data at every layer it passes through, making bugs structurally impossible rather than just handling them when they occur.

## Core Concept

"Validate at EVERY layer data passes through. Make the bug structurally impossible."

Defense-in-depth doesn't just fix the current bug - it creates a system where the same class of bug cannot occur again.

## When to Use

Announce: "I'm using the Defense-in-Depth Debugging skill."

Use when:
- A bug bypassed existing validations
- Similar bugs keep appearing in different places
- Data corruption is occurring somewhere in the pipeline
- A fix needs to be resilient, not just correct

## The Four Layers

### Layer 1: Entry Point Validation

Reject invalid input as early as possible.

```typescript
// API boundary - validate immediately
function createUser(input: unknown): User {
  if (!input || typeof input !== 'object') {
    throw new ValidationError('Invalid input: expected object');
  }

  const { email, name } = input as Record<string, unknown>;

  if (!email || typeof email !== 'string' || !email.includes('@')) {
    throw new ValidationError('Invalid email address');
  }

  if (!name || typeof name !== 'string' || name.trim().length === 0) {
    throw new ValidationError('Name is required');
  }

  return processUser({ email: email.trim(), name: name.trim() });
}
```

### Layer 2: Business Logic Validation

Ensure data makes contextual sense within the business domain.

```typescript
function processOrder(order: Order): void {
  // Business rule validation
  if (order.quantity <= 0) {
    throw new BusinessError('Order quantity must be positive');
  }

  if (order.total !== order.quantity * order.unitPrice) {
    throw new BusinessError('Order total does not match quantity × price');
  }

  if (order.shippingDate < order.orderDate) {
    throw new BusinessError('Shipping date cannot be before order date');
  }
}
```

### Layer 3: Environment Guards

Prevent dangerous operations in contexts where they shouldn't occur.

```typescript
function deleteAllUsers(): void {
  if (process.env.NODE_ENV === 'production') {
    throw new Error('SAFETY: Cannot delete all users in production');
  }

  if (!process.env.ALLOW_DESTRUCTIVE_OPERATIONS) {
    throw new Error('SAFETY: Destructive operations not enabled');
  }

  // Proceed with deletion
}
```

### Layer 4: Debug Instrumentation

Capture diagnostic context so you can understand failures when they occur.

```typescript
function processPayment(paymentId: string, amount: number): void {
  const context = {
    paymentId,
    amount,
    timestamp: new Date().toISOString(),
    userId: getCurrentUserId(),
  };

  try {
    logger.debug('Processing payment', context);
    // ... payment logic
    logger.info('Payment processed successfully', context);
  } catch (error) {
    logger.error('Payment processing failed', { ...context, error: error.message });
    throw error;
  }
}
```

## Applying the Framework

### When You Find a Bug

1. **Identify which layer failed** - where did bad data first appear?
2. **Fix at the correct layer** - the earliest layer where it should have been caught
3. **Add guards at every downstream layer too** - don't rely on one layer
4. **Add logging** to make future debugging easier

### Example: Empty Directory Bug

**Bug:** `projectDir` is empty string, causing files to be written to root

**Layer 1 - Entry validation:**
```typescript
if (!projectDir || projectDir.trim().length === 0) {
  throw new Error('projectDir cannot be empty');
}
```

**Layer 2 - Business logic:**
```typescript
if (!path.isAbsolute(projectDir)) {
  throw new Error('projectDir must be an absolute path');
}
```

**Layer 3 - Environment guard:**
```typescript
if (projectDir === '/' || projectDir === os.homedir()) {
  throw new Error('SAFETY: Refusing to write to root or home directory');
}
```

**Layer 4 - Instrumentation:**
```typescript
logger.debug('Writing to project directory', { projectDir, files: fileList });
```

## Verification

After implementing defense-in-depth:
- [ ] Each layer independently catches its class of invalid input
- [ ] Layers don't depend on each other for safety
- [ ] Error messages are specific and actionable
- [ ] Logging captures enough context to diagnose future issues
- [ ] The original bug is fixed
- [ ] A test covers each validation layer

## Anti-Patterns

- Single-layer validation ("we validate at the API so we're safe")
- Silent failures (swallowing errors without logging)
- Generic error messages ("invalid input" without specifics)
- Adding only the layer closest to the bug, not all layers
- Skipping Layer 4 (instrumentation) because it's "not part of the bug fix"
