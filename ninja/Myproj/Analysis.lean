import Mathlib.Data.Real.Sqrt
import Mathlib

open Real

example {a x y : ℝ}
    (hx : 0 ≤ x) (hy : 0 ≤ y)
    (hx_sq : x^2 = a) (hy_sq : y^2 = a) :
    x = y := by
  by_contra hxy
  rcases lt_or_gt_of_ne hxy with h | h
  · have hsq : x^2 < y^2 := by
      nlinarith [sq_lt_sq.mpr ⟨h, add_nonneg hx hy⟩]
    nlinarith [hx_sq, hy_sq, hsq]
  · have hsq : y^2 < x^2 := by
      nlinarith [sq_lt_sq.mpr ⟨h, add_nonneg hy hx⟩]
    nlinarith [hx_sq, hy_sq, hsq]
