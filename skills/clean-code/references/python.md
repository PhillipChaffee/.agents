# Python Clean Code Reference

Use this reference to eliminate AI anti-patterns and strengthen Python code in `git diff` before opening or updating a PR or MR.

## 1. Dynamic Attribute Access on Known Types

Do not use `getattr`, `hasattr`, or `setattr` on statically known types. Use direct attribute access.

Special trap: On Django reverse `OneToOneField` relationships, if the related object does not exist, Django raises `RelatedObjectDoesNotExist` (a subclass of `ObjectDoesNotExist`, NOT `AttributeError`). Therefore `getattr(obj, "rel", None)` crashes with an unhandled exception instead of returning `None`.

```python
# Don't: getattr on known request or model fields
is_staff = bool(getattr(request.user, "is_staff", False))
invoice = getattr(order, "invoice", None)  # Crashes on reverse OneToOne!

# Do: Direct attribute access and explicit exception handling
is_staff = request.user.is_staff
try:
    invoice = order.invoice
except Order.invoice.RelatedObjectDoesNotExist:
    invoice = None
```

## 2. Inline Imports and Path Tampering

Never place `import` statements inside functions or methods to hide circular dependencies. Never modify `sys.path` at runtime.

```python
# Don't: Inline import inside method body hiding architecture cycles
class Order(models.Model):
    def clean(self):
        from billing.pricing import compute_tax  # Hidden cycle
        self.tax = compute_tax(self)

# Do: Top-of-file imports; extract shared types to a leaf module
from billing.pricing import compute_tax

class Order(models.Model):
    def clean(self):
        self.tax = compute_tax(self)
```

## 3. Type Widening and Anonymous Tuples

Avoid `Any`, `object`, unvalidated `dict[str, Any]`, and anonymous 4-tuples. Use domain models, dataclasses, or `TypedDict`.

```python
# Don't: Widened types and anonymous tuple soup
def process_lead(lead: Any) -> tuple[Any, int | None, dict[str, Any], bool]:
    ...

# Do: Explicit domain types and structured result dataclass
@dataclass(frozen=True)
class LeadOutcome:
    lead: Lead
    score: int | None
    attributes: dict[str, str]
    is_qualified: bool

def process_lead(lead: Lead) -> LeadOutcome:
    ...
```

## 4. Redundant Internal Checks vs. Boundary Validation

Do not repeat defensive checks (`isinstance`, `is True`, `.strip()`) deep inside business logic. Validate once at the API or CLI boundary using serializers or Pydantic.

```python
# Don't: Manual type guards scattered inside service functions
def calculate_quote(account_id: int) -> Decimal:
    if not isinstance(account_id, int) or isinstance(account_id, bool):
        raise TypeError("account_id must be an integer")
    ...

# Do: Validate at the system boundary; trust types inside
class QuoteRequestSerializer(serializers.Serializer):
    account_id = serializers.IntegerField(min_value=1)

def calculate_quote(account_id: int) -> Decimal:
    ...
```

## 5. Blanket Exception Swallowing

Never use blanket `except Exception:` without logging or re-raising. Catch only narrow, expected exception types.

```python
# Don't: Swallowing unexpected programmer bugs
try:
    account = user.account
    config = account.load_settings()
except Exception:
    config = None

# Do: Catch specific expected exceptions and preserve bug visibility
try:
    account = user.account
    config = account.load_settings()
except (Account.DoesNotExist, SettingsError) as exc:
    logger.warning("Failed to load settings: %s", exc)
    config = None
```

## 6. Internal Mock Theater and Lint Suppressions

Do not mock private attributes (`_helper`), construct `SimpleNamespace` fakes that bypass models, or use `# noqa: SLF001` to test internals. Test public behavior with real fixtures.

```python
# Don't: SimpleNamespace fake and private attribute access with lint bypass
fake_lead = SimpleNamespace(_score=42, _is_processed=True)
assert fake_lead._is_processed is True  # noqa: SLF001

# Do: Public contract tested with model factories or explicit protocols
lead = LeadFactory(score=42, is_processed=True)
assert lead.is_ready_for_dispatch() is True
```

## 7. Cross-Module Private Access and Framework State Mutation

Do not import or call `_private` functions across module boundaries. Never mutate internal framework state (such as `form._errors` or `widget.__class__`).

```python
# Don't: Private cross-module calls and monkey-patching framework widgets
from billing.services import _recalculate_discount
form.fields["plan"].widget.__class__ = CustomSelectWidget

# Do: Call public APIs and configure widgets via public interfaces
from billing.services import recalculate_discount
form.fields["plan"].widget = CustomSelectWidget()
```

## 8. ASCII Section Banners and Echo Docstrings

Delete decorative ASCII lines (`# === Section ===`). Remove tautological docstrings that merely echo function or class names without adding context.

```python
# Don't: Decorative headers and zero-information docstrings
# ============================================================================
# Public methods
# ============================================================================
def get_total_amount(self) -> Decimal:
    """Get the total amount."""
    return self.total_amount

# Do: Clean code without banners; docstrings explain rationale or invariants
def get_total_amount(self) -> Decimal:
    return self.total_amount
```

## 9. Single-Caller 1-Line Wrappers

Do not invent 1-line micro-helpers that are only called in a single location. Inline trivial expressions directly at the call site.

```python
# Don't: 1-line wrapper called in only one place
def _join_segments(parts: list[str]) -> str:
    return "/".join(parts)

url = _join_segments(paths)

# Do: Inline the standard expression directly
url = "/".join(paths)
```

## 10. Copy-Pasting Branches into God-Files

Do not paste duplicate loops or branches into sprawling 2,000+ line files. Extract cohesive domain modules and shared utilities.

```python
# Don't: Pasting duplicate 40-line processing loop into a 4,000-line admin.py

# Do: Extract a dedicated domain service module
from orders.services.fulfillment import process_fulfillment_batch
```

## 11. Speculative State Machines and Tri-State Booleans

Avoid speculative states, dead branches, and confusing `bool | None` parameters. Use explicit enums and remove uncalled scaffolding.

```python
# Don't: Tri-state boolean and uncallable speculative transitions
def sync_user_state(is_verified: bool | None = None) -> None:
    if is_verified is None:
        ...

# Do: Explicit domain enum with clear semantics
class VerificationStatus(enum.StrEnum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

def sync_user_state(status: VerificationStatus) -> None:
    ...
```

## 12. Inefficient ORM Loops, Destructive Deletions, and Validation Side Effects

Never execute single-row queries inside loops. Avoid `.delete()`-and-recreate patterns that wipe audit history in audit-logged models. Never invoke external network APIs inside model or form `clean()`.

```python
# Don't: Destructive recreation wiping audit log, or network call in clean()
user.roles.all().delete()
user.roles.bulk_create(new_roles)

class OrderForm(forms.ModelForm):
    def clean(self):
        payment_gateway.charge(self.cleaned_data["token"])  # Side effect in clean!

# Do: Diff-based updates preserving history; move side effects to services
current_role_ids = set(user.roles.values_list("role_id", flat=True))
# Add missing roles and remove revoked roles explicitly
```

## 13. Test Theater and Weakened Guardrails

Never invert security or schema tests to match defective code. Do not write complex regex SQL parsers to replace test databases.

```python
# Don't: Invert security test to allow internal debug routes in public schema
assert "/api/v1/internal/health" in public_schema  # Weakened assertion!

# Do: Fix the route permission and keep security guardrails strict
assert "/api/v1/internal/health" not in public_schema
```

## 14. Hallucinated Library Kwargs Masked by Loose Mocks

Never pass unverified arguments to third-party libraries masked by loose `*args: Any` mocks. Check installed package signatures directly.

```python
# Don't: Hallucinated kwargs masked by loose mock signatures
mock_notifier.send_alert(*args, priority_override=True)  # Fails against real library!

# Do: Verify actual library signature and pass documented parameters
notifier.send_alert(message="Incident detected", level="urgent")
```

## Legitimate Exceptions (Keep These)

Preserve these patterns when used in their proper architectural context.

| Pattern | Context | Why it is legitimate | Proper example |
| --- | --- | --- | --- |
| `getattr` with `dataclasses.fields` | Serialization or reflection | Safely reads declared fields of a dataclass dynamically | `[getattr(row, f.name) for f in dataclasses.fields(row)]` |
| `apps.get_model()` | Django migrations | Models must be resolved dynamically without direct imports | `Order = apps.get_model("orders", "Order")` |
| `if TYPE_CHECKING:` | Type hints | Breaks circular import cycles strictly for static type analysis | `if TYPE_CHECKING: from billing.models import Invoice` |
