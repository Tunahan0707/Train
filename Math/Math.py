import math


class Trigonometry:

    @staticmethod
    def _reduce(x):
        if not isinstance(x, (int, float)):
            return x
        pi = Functs.Pi()
        return (x + pi) % (2*pi) - pi

    @staticmethod
    def sin(x, eps=1e-15):
        if isinstance(x, DualNumber):
            return DualNumber(Trigonometry.sin(x.real, eps), x.dual * Trigonometry.cos(x.real, eps))
        x = Trigonometry._reduce(x)
        term = x
        ans = term
        n = 0

        while True:
            term *= -(x*x) / ((2*n+2)*(2*n+3))

            if abs(term) < eps:
                break

            ans += term
            n += 1

        return ans

    @staticmethod
    def cos(x, eps=1e-15):
        if isinstance(x, DualNumber):
            return DualNumber(Trigonometry.cos(x.real, eps), -1 * x.dual * Trigonometry.sin(x.real, eps))
        x = Trigonometry._reduce(x)
        term = 1.0
        ans = term
        n = 0

        while True:
            term *= -(x*x) / ((2*n+1)*(2*n+2))

            if abs(term) < eps:
                break

            ans += term
            n += 1

        return ans

    @staticmethod
    def tan(x):
        return Trigonometry.sin(x) / Trigonometry.cos(x)

    @staticmethod
    def cot(x):
        return Trigonometry.cos(x) / Trigonometry.sin(x)

class InverseTrigonometry:

    @staticmethod
    def arctan(x, eps=1e-15):
        factor = 1

        while abs(x) > 0.5:
            x = x / (1 + Roots.sqrt(1 + x*x))
            factor *= 2

        term = x
        ans = term
        n = 0

        while True:
            term *= -x*x * (2*n + 1) / (2*n + 3)

            if abs(term) < eps:
                break

            ans += term
            n += 1

        return factor * ans

    @staticmethod
    def arctan2(y, x):
        pi = Functs.Pi()

        if x == 0:
            if y > 0:
                return pi / 2
            elif y < 0:
                return -pi / 2
            else:
                raise ValueError("atan2(0, 0) tanımsızdır!")

        if y == 0:
            return pi if x < 0 else 0

        if abs(y) <= abs(x):
            angle = InverseTrigonometry.arctan(y / x)

            if x < 0:
                return angle + pi if y > 0 else angle - pi

            return angle

        else:
            angle = pi / 2 - InverseTrigonometry.arctan(x / y)

            if y < 0:
                angle = -angle

            if x < 0:
                return angle + pi if y > 0 else angle - pi

            return angle
    
    @staticmethod
    def arcsin(x, eps=1e-15):
        return InverseTrigonometry.arctan(
            x / Roots.sqrt(1 - x**2),
            eps
        )

    @staticmethod
    def arccos(x, eps=1e-15):
        pi = Functs.Pi()
        return pi/2 - InverseTrigonometry.arcsin(x, eps)

    @staticmethod
    def arccot(x, eps=1e-15):
        pi = Functs.Pi()
        return pi/2 - InverseTrigonometry.arctan(x, eps)

class Hyperbolic:

    @staticmethod
    def sinh(x):
        exp = Functs.exp
        return (exp(x) - exp(-x))/2

    @staticmethod
    def cosh(x):
        exp = Functs.exp
        return (exp(x) + exp(-x))/2
    
    @staticmethod
    def tanh(x):
        return Hyperbolic.sinh(x)/Hyperbolic.cosh(x)
    
    @staticmethod
    def coth(x):
        return 1/Hyperbolic.tanh(x)

class Factorial:
    @staticmethod
    def fact(x):
        if not isinstance(x, int) or x < 0:
            raise ValueError("Girilen sayı negatif olamaz!!")

        a = 1
        for i in range(1, x + 1):
            a *= i

        return a

class Roots:
    
    @staticmethod
    def sqrt(x, eps=1e-15):

        if isinstance(x, DualNumber):
            root = Roots.sqrt(x.real, eps)
            if root == 0:
                raise ValueError("sqrt fonksiyonunun bu noktadaki DualNumber türevi tanımsızdır!")
            return DualNumber(root, x.dual / (2 * root))
    
        if not isinstance(x, (int, float)):
            raise TypeError("x sayısal olmalıdır!")
    
        if x < 0:
            raise ValueError("Negatif sayıların gerçek karekökü yoktur!")
    
        if x == 0:
            return 0
    
        if not math.isfinite(x):
            raise ValueError("x sonlu bir sayı olmalıdır!")
    
        if eps <= 0:
            raise ValueError("eps pozitif olmalıdır!")
    
        m, e = math.frexp(x)
    
        if e % 2 != 0:
            m *= 2
            e -= 1
    
        ans = 1.0
    
        while True:
            next_ans = (ans + m / ans) / 2
    
            if abs(next_ans - ans) <= eps * abs(next_ans):
                break
            
            ans = next_ans
    
        return math.ldexp(next_ans, e // 2)


class Functs:

    @staticmethod
    def Pi(eps=1e-15):
        x = 0.5
        term = x
        ans = term
        n = 0

        while True:
            term *= (
                (2*n+1)**2 * x*x
                / (2*(n+1)*(2*n+3))
            )

            if abs(term) < eps:
                break

            ans += term
            n += 1

        return 6 * ans

    @staticmethod
    def exp(x, eps=1e-15):
        if isinstance(x, DualNumber):
            real = Functs.exp(x.real, eps)
            return DualNumber(real, x.dual * real)
        e = Trigonometry.cos(ComplexNumber(0, -1) * x, eps) + ComplexNumber(0, 1) * Trigonometry.sin(ComplexNumber(0, -1) * x, eps)
        if e.complex == 0:
            return e.real
        return e

    @staticmethod
    def E(eps=1e-15):
        return Functs.exp(1, eps)

    @staticmethod
    def Phi():
        return (1+Roots.sqrt(5))/2

    @staticmethod
    def Fibonacci(x):
        result1 = 1
        resultb = 0
        result = 0
        for i in range(x):
            resultb = result
            result += result1
            result1 = resultb
        return result

    @staticmethod
    def Sign(x):
        if x>0:
            return 1
        elif x<0:
            return -1
        else:
            return 0


class DualNumber:
    """Sıfıra eşit olmayıp karesi sıfıra eşit olan sayılardır. (ε != 0, ε**2 = 0)"""
    def __init__(self, real, dual):
        self.real = real
        self.dual = dual
    def __add__(self, other):
        if isinstance(other, (int, float)):
            return DualNumber(self.real + other, self.dual)
        return DualNumber(self.real + other.real, self.dual + other.dual)
    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return DualNumber(self.real - other, self.dual)
        return DualNumber(self.real - other.real, self.dual - other.dual)
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return DualNumber(self.real * other, self.dual * other)
        return DualNumber(self.real * other.real, self.real * other.dual + self.dual * other.real)
    def __pow__(self, power):
        if isinstance(power, int):
            me = self
            result = DualNumber(1, 0)
            if power < 0:
                me = 1/self
                power = -power
            for _ in range(power):
                result *= me
            return result
        else:
            raise ValueError("Power must be an integer.")
    def __radd__(self, other):
        return DualNumber(self.real + other, self.dual)
    def __rsub__(self, other):
        return DualNumber(other - self.real, -self.dual)
    def __rmul__(self, other):
        return DualNumber(self.real * other, self.dual * other)
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return DualNumber(self.real / other, self.dual / other)
        return DualNumber(self.real / other.real, (self.dual * other.real - self.real * other.dual) / (other.real ** 2))
    def __rtruediv__(self, other):
        return DualNumber(other, 0) / self
    def __repr__(self):
        return f"Dual_Number(real={self.real}, dual={self.dual})"
    def __str__(self):
        if self.dual == 0:
            return f"{self.real}"
        if self.real == 0:
            return f"{self.dual}ε"
        return f"{self.real} + {self.dual}ε"
    def __eq__(self, other):
        if not isinstance(other, DualNumber):
            return False
        return self.real == other.real and self.dual == other.dual
    def __ne__(self, other):
        return not self.__eq__(other)
    def __int__(self):
        return int(self.real)
    def print_dual(self):
        print(f"{self.dual}")
    def print_real(self):
        print(f"{self.real}ε")


class ComplexNumber:
    """Karesi -1'e eşit olan sayılardır. (i**2 = -1)"""
    def __init__(self, real, complex):
        self.real = real
        self.complex = complex
    def __add__(self, other):
        if isinstance(other, (int, float)):
            return ComplexNumber(self.real + other, self.complex)
        return ComplexNumber(self.real + other.real, self.complex + other.complex)
    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return ComplexNumber(self.real - other, self.complex)
        return ComplexNumber(self.real - other.real, self.complex - other.complex)
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return ComplexNumber(self.real * other, self.complex * other)
        return ComplexNumber(self.real * other.real - self.complex * other.complex, self.complex * other.real + self.real * other.complex)
    def __pow__(self, power):
        if isinstance(power, int):
            me = self
            result = ComplexNumber(1, 0)
            if power < 0:
                me = 1/self
                power = -power
            for _ in range(power):
                result *= me
            return result
        else:
            raise ValueError("Power must be an integer.")
    def __radd__(self, other):
        return ComplexNumber(self.real + other, self.complex)
    def __rsub__(self, other):
        return ComplexNumber(other - self.real, -self.complex)
    def __rmul__(self, other):
        return ComplexNumber(self.real * other, self.complex * other)
    def __rtruediv__(self, other):
        return ComplexNumber(other, 0) / self
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return ComplexNumber(self.real / other, self.complex / other)
        denominator = other.real**2 + other.complex**2
        if denominator == 0:
            raise ZeroDivisionError("Complex division by zero")
        return ComplexNumber((self.real * other.real + self.complex * other.complex)/(other.real**2 + other.complex**2), (self.complex * other.real - self.real * other.complex)/(other.real**2 + other.complex**2))
    def __neg__(self):
        return ComplexNumber(-self.real, -self.complex)
    def __repr__(self):
        return f"ComplexNumber(real={self.real}, complex={self.complex})"
    def __str__(self):
        if self.complex == 0:
            return f"{self.real}"
        if self.real == 0:
            return f"{self.complex}i"
        return f"{self.real} + {self.complex}i"
    def __eq__(self, other):
        if not isinstance(other, ComplexNumber):
            return False
        return self.real == other.real and self.complex == other.complex
    def __ne__(self, other):
        return not self.__eq__(other)
    def __int__(self):
        return int(self.real)
    def __abs__(self):
        return Roots.sqrt(self.real**2 + self.complex**2)
    def arg(self):
        return InverseTrigonometry.arctan2(self.complex, self.real)
    def print_complex(self):
        print(f"{self.complex}i")
    def print_real(self):
        print(f"{self.real}")

class Derivate:
    @staticmethod
    def derv(f, x):
        """Türev alma işlemi. Fonksiyonun o noktadaki eğimini belirler"""
        result = f(DualNumber(x, 1))
        return result.dual

class Log:
    """Üstel fonksiyonun tersi. Tabandaki sayının hangi üssünün içerideki sayıya eşit olduğunu bulur."""
    @staticmethod
    def ln(x, eps=1e-15):
        """e tabanında logaritma"""

        if isinstance(x, DualNumber):
            if x.real == 0:
               raise ValueError("Ln(0) tanımsızdır!") 
            return DualNumber(Log.ln(x.real, eps), x.dual/x.real)

        pi = Functs.Pi()

        if isinstance(x, ComplexNumber):
            return Log.ln(abs(x), eps) + ComplexNumber(0, x.arg())

        if x == 0:
            raise ValueError("Ln(0) tanımsızdır!")

        if x < 0:
            return Log.ln(abs(x), eps) + ComplexNumber(0, pi)

        k = 0
        while abs((x - 1) / (x + 1)) > 0.7777777:
            x = Roots.sqrt(x)
            k += 1

        z = (x - 1) / (x + 1)
        term = z
        ans = term
        n = 0

        while True:
            term *= z*z * (2*n + 1) / (2*n + 3)

            if abs(term) < eps:
                break

            ans += term
            n += 1

        return (2 ** k) * 2 * ans

    def log(taban, x, eps=1e-15, k=0):
        if taban == 1:
            raise ValueError("Taban 1 olamaz!!")

        numerator = Log.ln(x, eps) + ComplexNumber(0, 2*k*Functs.Pi())
        denominator = Log.ln(taban, eps)

        return numerator / denominator