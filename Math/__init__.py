from .Math import (
    Trigonometry,
    Roots,
    Hyperbolic,
    InverseTrigonometry,
    DualNumber,
    ComplexNumber,
    Functs,
    Log,
    Factorial,
    Derivate,
)
from .Vector import Vector2

# Namespace
trig = Trigonometry
inv = InverseTrigonometry
hyp = Hyperbolic

# Trigonometri
sin = trig.sin
cos = trig.cos
tan = trig.tan
cot = trig.cot

# Ters trigonometri
arctan = inv.arctan
arctan2 = inv.arctan2
arcsin = inv.arcsin
arccos = inv.arccos
arccot = inv.arccot

# Hiperbolik
sinh = hyp.sinh
cosh = hyp.cosh
tanh = hyp.tanh
coth = hyp.coth

# Diğerleri
sqrt = Roots.sqrt
sqrt_old = Roots.sqrt_old
root = Roots.root
exp = Functs.exp
ln = Log.ln
fib = Functs.Fibonacci
fact = Factorial.fact
derv = Derivate.derv
sign = Functs.Sign

# Sabitler
pi = Functs.Pi()
phi = Functs.Phi()
e = Functs.E()
