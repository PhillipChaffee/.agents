/-
  Authorization policy: sorting and deny-overrides evaluation.

  Safety-relevant design choices, made explicit in the definitions below:
  * A rule matches only by membership (`List.contains`): an empty
    `principals` (or `actions`, or `resources`) list matches nobody.
    Empty lists are therefore fail-closed, never vacuously matching.
  * `evaluate` is deny-overrides over the whole list and defaults to
    `forbid`. Its result does not depend on rule order, so the safety
    theorem does not rely on sorting or on any well-formedness invariant.
-/

inductive Effect where
  | permit
  | forbid
  deriving DecidableEq, Repr

structure Request where
  principal : String
  action : String
  resource : String
  deriving Repr

structure Rule where
  priority : Nat
  effect : Effect
  principals : List String
  actions : List String
  resources : List String
  deriving Repr

/-- Membership matching: every field must contain the request's value.
    In particular, `principals = []` makes this `false` for every request. -/
def ruleMatches (req : Request) (r : Rule) : Bool :=
  r.principals.contains req.principal &&
  r.actions.contains req.action &&
  r.resources.contains req.resource

theorem ruleMatches_eq_false_of_principals_eq_nil {req : Request} {r : Rule}
    (h : r.principals = []) : ruleMatches req r = false := by
  simp [ruleMatches, h]

theorem ruleMatches_eq_false_of_actions_eq_nil {req : Request} {r : Rule}
    (h : r.actions = []) : ruleMatches req r = false := by
  simp [ruleMatches, h]

theorem ruleMatches_eq_false_of_resources_eq_nil {req : Request} {r : Rule}
    (h : r.resources = []) : ruleMatches req r = false := by
  simp [ruleMatches, h]

/-- Does any rule in the list match `req` with effect `eff`? -/
def anyMatch (req : Request) (eff : Effect) : List Rule → Bool
  | [] => false
  | r :: rs => (ruleMatches req r && decide (r.effect = eff)) || anyMatch req eff rs

/-- Deny-overrides, default-deny. Order-insensitive by construction. -/
def evaluate (req : Request) (rules : List Rule) : Effect :=
  if anyMatch req .forbid rules then .forbid
  else if anyMatch req .permit rules then .permit
  else .forbid

theorem anyMatch_eq_true_of_mem {req : Request} {eff : Effect} {r : Rule}
    {rules : List Rule} (hmem : r ∈ rules) (hmatch : ruleMatches req r = true)
    (heff : r.effect = eff) : anyMatch req eff rules = true := by
  induction rules with
  | nil => simp at hmem
  | cons s ss ih =>
    simp only [List.mem_cons] at hmem
    rcases hmem with rfl | hmem
    · simp [anyMatch, hmatch, heff]
    · have ih' := ih hmem
      simp [anyMatch, ih']

/-- Task 2, unconditional: a matching `forbid` rule anywhere in the list
    forces `forbid`. No nonemptiness / well-formedness hypothesis, because
    an empty-`principals` rule simply does not satisfy `hmatch`. -/
theorem evaluate_eq_forbid_of_forbid_match {req : Request} {rules : List Rule}
    {r : Rule} (hmem : r ∈ rules) (hmatch : ruleMatches req r = true)
    (hforbid : r.effect = .forbid) : evaluate req rules = .forbid := by
  simp [evaluate, anyMatch_eq_true_of_mem hmem hmatch hforbid]

theorem evaluate_ne_permit_of_forbid_match {req : Request} {rules : List Rule}
    {r : Rule} (hmem : r ∈ rules) (hmatch : ruleMatches req r = true)
    (hforbid : r.effect = .forbid) : evaluate req rules ≠ .permit := by
  rw [evaluate_eq_forbid_of_forbid_match hmem hmatch hforbid]
  exact Effect.noConfusion

/-! ## Task 1: sorting by `priority` -/

def insertRule (r : Rule) : List Rule → List Rule
  | [] => [r]
  | s :: ss => if r.priority ≤ s.priority then r :: s :: ss else s :: insertRule r ss

/-- Insertion sort, ascending by `priority`. -/
def sortRules : List Rule → List Rule
  | [] => []
  | r :: rs => insertRule r (sortRules rs)

theorem perm_insertRule (r : Rule) (l : List Rule) :
    List.Perm (insertRule r l) (r :: l) := by
  induction l with
  | nil => simp [insertRule]
  | cons s ss ih =>
    by_cases h : r.priority ≤ s.priority
    · simp [insertRule, h]
    · simp only [insertRule, if_neg h]
      exact (List.Perm.cons s ih).trans (List.Perm.swap r s ss)

theorem mem_insertRule {r x : Rule} {l : List Rule} :
    x ∈ insertRule r l ↔ x = r ∨ x ∈ l := by
  simpa using (perm_insertRule r l).mem_iff (a := x)

theorem pairwise_insertRule {r : Rule} {l : List Rule}
    (h : List.Pairwise (fun a b : Rule => a.priority ≤ b.priority) l) :
    List.Pairwise (fun a b : Rule => a.priority ≤ b.priority)
      (insertRule r l) := by
  induction l with
  | nil => simp [insertRule]
  | cons s ss ih =>
    obtain ⟨hhead, htail⟩ := List.pairwise_cons.mp h
    have ih' := ih htail
    by_cases h : r.priority ≤ s.priority
    · simp only [insertRule, if_pos h]
      rw [List.pairwise_cons]
      refine ⟨?_, List.pairwise_cons.mpr ⟨hhead, htail⟩⟩
      intro x hx
      simp only [List.mem_cons] at hx
      rcases hx with rfl | hx
      · exact h
      · exact Nat.le_trans h (hhead x hx)
    · have hsr : s.priority ≤ r.priority := Nat.le_of_not_le h
      simp only [insertRule, if_neg h]
      rw [List.pairwise_cons]
      refine ⟨?_, ih'⟩
      intro x hx
      rw [mem_insertRule] at hx
      rcases hx with rfl | hx
      · exact hsr
      · exact hhead x hx

theorem sortRules_perm (rules : List Rule) :
    List.Perm (sortRules rules) rules := by
  induction rules with
  | nil => simp [sortRules]
  | cons r rs ih =>
    simp only [sortRules]
    exact (perm_insertRule r (sortRules rs)).trans (List.Perm.cons r ih)

theorem sortRules_pairwise (rules : List Rule) :
    List.Pairwise (fun a b : Rule => a.priority ≤ b.priority)
      (sortRules rules) := by
  induction rules with
  | nil => simp [sortRules]
  | cons r rs ih =>
    simp only [sortRules]
    exact pairwise_insertRule ih

/-- Complete sorting specification: sorted *and* a permutation of the input.
    Sortedness alone is satisfied by `fun _ => []`, which would drop a
    `forbid` rule; the `List.Perm` conjunct rules that out. -/
theorem sortRules_sorted_spec (rules : List Rule) :
    List.Pairwise (fun a b : Rule => a.priority ≤ b.priority)
        (sortRules rules) ∧
      List.Perm (sortRules rules) rules :=
  ⟨sortRules_pairwise rules, sortRules_perm rules⟩

/-- Sorting cannot lose a matching `forbid` rule: Task 1 and Task 2 compose. -/
theorem evaluate_sortRules_ne_permit_of_forbid_match {req : Request}
    {rules : List Rule} {r : Rule} (hmem : r ∈ rules)
    (hmatch : ruleMatches req r = true) (hforbid : r.effect = .forbid) :
    evaluate req (sortRules rules) ≠ .permit :=
  evaluate_ne_permit_of_forbid_match
    ((sortRules_perm rules).mem_iff.mpr hmem) hmatch hforbid

/-! ## Verification checks (run these; no result may list `sorryAx`)
    #print axioms sortRules_sorted_spec
    #print axioms evaluate_ne_permit_of_forbid_match
    #print axioms evaluate_sortRules_ne_permit_of_forbid_match
-/
#print axioms sortRules_sorted_spec
#print axioms evaluate_ne_permit_of_forbid_match
#print axioms evaluate_sortRules_ne_permit_of_forbid_match
