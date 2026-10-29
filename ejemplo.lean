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
