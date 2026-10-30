def doble (n : Nat) : Nat :=
  n * 2

#eval doble 5
#eval doble 10
#eval doble 0

def factorial : Nat → Nat
  | 0 => 1
  | n + 1 => (n + 1) * factorial n

#eval factorial 0
#eval factorial 3
#eval factorial 5

theorem doble_de_dos : doble 2 = 4 := by
  rfl

theorem doble_es_par (n : Nat) : doble n % 2 = 0 := by
  unfold doble
  omega

-- "Llueve o hace sol. Si llueve no iré a la playa. Si hace sol iré a la playa.
--  Hoy no llueve. Entonces iré a la playa."
-- p: llueve, q: hace sol, r: iré a la playa
theorem ire_a_la_playa (p q r : Prop)
    (premisa1 : p ∨ q)
    (premisa2 : p → ¬r)
    (premisa3 : q → r)
    (premisa4 : ¬p) : r := by
  cases premisa1 with
  | inl hp => exact absurd hp premisa4
  | inr hq => exact premisa3 hq

-- p → q, p ∧ r ⊢ r → q, paso a paso como en deducción natural
theorem r_implica_q (p q r : Prop)
    (premisa1 : p → q)            -- 1. Pr
    (premisa2 : p ∧ r) : r → q := by  -- 2. Pr
  have paso3 : p := premisa2.left    -- 3. E∧ 2
  have paso4 : r := premisa2.right   -- 4. E∧ 2
  have paso5 : q := premisa1 paso3   -- 5. E→ 1,3
  have paso6 : r → q := fun _ => paso5  -- 6. I→ 4,5
  exact paso6
