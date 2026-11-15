from typing import Final, Literal, overload

from . import Math as Math
from . import Vector as Vector

from .Math import (
    Trigonometry as Trigonometry,
    InverseTrigonometry as InverseTrigonometry,
    Hyperbolic as Hyperbolic,
    Roots as Roots,
    ComplexNumber as ComplexNumber,
    DualNumber as DualNumber,
    Functs as Functs,
    Log as Log,
    Factorial as Factorial,
    Derivate as Derivate
)

from .Vector import Vector2 as Vector2


# Namespace kısaltmaları
trig: type[Trigonometry]
inv: type[InverseTrigonometry]
hyp: type[Hyperbolic]


# Trigonometri
@overload
def sin(x: float, eps: float = 1e-15, /) -> float: ...
@overload
def sin(x: DualNumber, eps: float = 1e-15, /) -> DualNumber: ...
@overload
def sin(x: ComplexNumber, eps: float = 1e-15, /) -> ComplexNumber: ...

@overload
def cos(x: float, eps: float = 1e-15, /) -> float: ...
@overload
def cos(x: DualNumber, eps: float = 1e-15, /) -> DualNumber: ...
@overload
def cos(x: ComplexNumber, eps: float = 1e-15, /) -> ComplexNumber: ...

def tan(x: float | ComplexNumber | DualNumber, /) -> float | ComplexNumber | DualNumber: ...
def cot(x: float | ComplexNumber | DualNumber, /) -> float | ComplexNumber | DualNumber: ...


# Ters trigonometrik fonksiyonlar
def arctan(x: float, eps: float = 1e-15, /) -> float: ...
def arcsin(x: float, eps: float = 1e-15, /) -> float: ...
def arccos(x: float, eps: float = 1e-15, /) -> float: ...
def arccot(x: float, eps: float = 1e-15, /) -> float: ...
def arctan2(y: float, x: float, /) -> float: ...


# Hiperbolik fonksiyonlar
def sinh(x: float | ComplexNumber, /) -> float | ComplexNumber: ...
def cosh(x: float | ComplexNumber, /) -> float | ComplexNumber: ...
def tanh(x: float | ComplexNumber, /) -> float | ComplexNumber: ...
def coth(x: float | ComplexNumber, /) -> float | ComplexNumber: ...


# Üstel ve logaritmik fonksiyonlar
def exp(x: float | ComplexNumber, eps: float = 1e-15, /) -> float | ComplexNumber: ...
def ln(x: float | ComplexNumber | DualNumber, eps: float = 1e-15, /) -> float | ComplexNumber | DualNumber: ...


# Kök ve temel fonksiyonlar
def sqrt(x: float | DualNumber, eps: float = 1e-15, /) -> float | DualNumber: ...
def fact(x: int, /) -> int: ...
def fib(x: int, /) -> int: ...
def sign(x: float, /) -> Literal[-1, 0, 1]: ...


# Türev
def derv(f, x: float, /) -> float: ...


# Sabitler
e: Final[float]
pi: Final[float]
phi: Final[float]