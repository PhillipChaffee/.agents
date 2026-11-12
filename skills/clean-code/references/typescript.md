# TypeScript Clean Code Reference

Use this reference to eliminate AI anti-patterns and strengthen TypeScript code in `git diff` before opening or updating a PR or MR.

## 1. Discriminated Unions

Model variants with a literal discriminant (`kind`, `type`, `tag`). Never use optional-field bags where contradictory states can be represented simultaneously.

```ts
// Don't: Optional-field bag allows impossible states (loading AND error AND data)
type AccountState = { loading: boolean; data?: Account; error?: string };

// Do: Discriminated union where only valid combinations can exist
type AccountState =
  | { kind: "loading" }
  | { kind: "ready"; data: Account }
  | { kind: "error"; error: string };
```

## 2. Branded Types

Brand primitive values with `& { readonly __brand: "X" }` to prevent mixing semantically distinct values. Validate once at the boundary using a type guard, never with a bare `as` cast.

```ts
// Do: Branded type validated once at the boundary
type AccountId = string & { readonly __brand: "AccountId" };

function isAccountId(input: string): input is AccountId {
  return /^[0-9a-f-]{36}$/i.test(input);
}

function parseAccountId(input: string): AccountId {
  if (!isAccountId(input)) throw new Error(`Invalid account id: ${input}`);
  return input;
}
```

## 3. Constructive Modeling

Construct shapes where illegal values cannot be built, rather than relying on runtime validation on loose types.

```ts
// Non-empty array via variadic tuple
type NonEmpty<T> = [T, ...T[]];

// Don't: T[] with repetitive runtime checks
function selectPrimary(items: string[]): string {
  if (items.length === 0) throw new Error("no items");
  return items[0];
}

// Do: Empty array cannot be constructed
function selectPrimary(items: NonEmpty<string>): string {
  return items[0];
}

// Time range modeled as start plus duration so negative ranges are impossible
type TimeRange = { start: Date; durationMs: number };
```

## 4. Simplest Total Type

Keep types simple when operations remain total (`sum(xs: number[])`). Strengthen to `NonEmpty<T>` or total alternatives only when loose types force `!`, `as`, or "should never happen" exceptions.

```ts
// Don't: Smuggling partiality with non-null assertion !
function getFirstSession(sessions: Session[]): Session {
  return sessions.at(0)!;
}

// Do: Strengthen the input or return undefined explicitly
function getFirstSession(sessions: NonEmpty<Session>): Session {
  return sessions[0];
}
```

## 5. `unknown` Over `any`

All external data (RPC payloads, `JSON.parse`, storage, query params) must be typed as `unknown`, never `any`. Narrow values before access.

```ts
// Don't: Unchecked any access
function processPayload(payload: any) {
  return payload.user.name;
}

// Do: Narrow unknown safely before access
function processPayload(payload: unknown) {
  if (typeof payload === "object" && payload !== null && "user" in payload) {
    // narrowed access
  }
}
```

## 6. Schemas Before Hand-Rolled Guards

Use the repository's runtime schema library (such as Zod) instead of writing hand-rolled property-by-property guards. Derive TypeScript types directly from the schema.

```ts
import { z } from "zod";

const UserSchema = z.object({
  id: z.string().uuid(),
  role: z.enum(["admin", "member"]),
});

type User = z.infer<typeof UserSchema>;

function parseUser(input: unknown): User {
  return UserSchema.parse(input);
}
```

## 7. No `as` Casts

Every `as` cast bypasses type safety and risks runtime crashes. Cast only after static or schema verification.

```ts
// Don't: Bare cast without validation
const account = data as Account;

// Do: Schema-based parse verifying the shape
const account = AccountSchema.parse(data);
```

## 8. Narrowing Hierarchy

Follow the narrowing hierarchy from most preferred to last resort:

1. Discriminated union switch or if.
2. `in` operator for property checks.
3. `typeof` and `instanceof` checks.
4. User-defined type guards (`isX`).
5. `as` cast (only after runtime validation).

## 9. Honest Type Guards

Type guards must genuinely verify the claimed type predicate. Name guards `isX` or `hasX`. Never write lying guards that merely return `true`.

```ts
function isCircle(shape: Shape): shape is Circle {
  return shape.kind === "circle";
}
```

## 10. Exhaustiveness Checking with `never`

In `switch` statements over discriminated unions, assign the unhandled case to a `never` local in the default arm to trigger compile-time errors when variants are added.

```ts
function renderShape(shape: Shape): string {
  switch (shape.kind) {
    case "circle":
      return `Circle(r=${shape.radius})`;
    case "rect":
      return `Rect(w=${shape.width}, h=${shape.height})`;
    default: {
      const _exhaustive: never = shape;
      return _exhaustive;
    }
  }
}
```

## 11. `satisfies` Over `as`

Use `satisfies` to validate types while preserving literal types and exact keys.

```ts
// Don't: Widens theme to string and allows missing keys unnoticed
const config = { theme: "dark", retries: 3 } as Config;

// Do: Validates contract and preserves literal "dark"
const config = { theme: "dark", retries: 3 } satisfies Config;
```

## 12. Boundary Validation

Parse untrusted data at system boundaries (HTTP endpoints, database queries, messages). Trust domain types internally; do not scatter defensive checks inside business logic.

## 13. Schema-Derived Types

Derive types from existing schemas, OpenAPI specs, or protobuf definitions using `Pick`, `Omit`, `ReturnType`, and `Parameters` before inventing redundant interfaces.

```ts
// Do: Derive from generated schema types
type UserHeader = Pick<UserResponse, "id" | "displayName">;
```

## 14. Object Arguments

Pass structured object parameters instead of long lists of positional arguments. This prevents argument-swap bugs and keeps call sites self-documenting.

```ts
// Don't: Positional argument swaps compile silently
updateOrder(orderId, customerId, true, false);

// Do: Self-documenting object parameters
updateOrder({ orderId, customerId, notifyCustomer: true, dryRun: false });
```

## 15. Real Tests Over Internal Mocking

Do not mock internal methods or private functions under test (e.g. `jest.spyOn(service as any, "internalMethod")`). Test through public contracts with real fixtures.

## 16. Structured Telemetry

Use structured logger diagnostics rather than ad-hoc `console.log` statements in production code. Provide actionable context for debugging.

## Pre-PR Diff Cleanup Checklist

Before opening or updating a PR or MR, clean these common AI slop patterns from the diff:

- **ASCII section banners:** Delete `# === Public Methods ===` and `// --------------` dividers.
- **Single-caller wrappers:** Inline 1-line functions that are only used in a single location.
- **Silent catch blocks:** Never write `catch {}` that discards errors without handling or logging.
- **Weakened assertions:** Never cast `as any` or relax test schemas to force failing tests to pass.

