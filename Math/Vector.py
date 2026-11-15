from Math import Math


class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self
    def __mul__(self, other):
        return Vector2(self.x * other, self.y * other)
    def __imul__(self, other):
        self.x *= other
        self.y *= other
        return self
    def __truediv__(self, other):
        return Vector2(self.x / other, self.y / other)
    def __str__(self):
        return f"({self.x}, {self.y})"
    def __neg__(self):
        return Vector2(-self.x, -self.y)
    def __rmul__(self, other):
        return Vector2(self.x * other, self.y * other)
    def __eq__(self, value):
        if not isinstance(value, Vector2):
            return NotImplemented
        return self.x == value.x and self.y == value.y
    def __ne__(self, value):
        result = self.__eq__(value)
        if result is NotImplemented:
            return NotImplemented
        return not result
    def __repr__(self):
        return f"Vector2({self.x}, {self.y})"
    def length(self):
        m = max(abs(self.x), abs(self.y))

        if m == 0:
            return 0

        x = self.x / m
        y = self.y / m

        return m * Math.Roots.sqrt(x*x + y*y)
    def length_squared(self):
        return self.x ** 2 + self.y **2
    def dot(self, other):
        return self.x * other.x + other.y * self.y
    def normalize(self):
        length = self.length()
        if length == 0:
            return Vector2(0, 0)
        return Vector2(self.x / length, self.y / length)
    def angle_with(self, other):
        return Math.InverseTrigonometry.arctan2(
            abs(self.cross(other)),
            self.dot(other)
        )
    def angle_to(self, other):
        return Math.InverseTrigonometry.arctan2(
            self.cross(other),
            self.dot(other)
        )
    def angle(self):
        return Math.InverseTrigonometry.arctan2(self.y, self.x)
    def distance_to(self, other):
        return (self - other).length()
    def rotate(self, angle):
        cos = Math.Trigonometry.cos(angle)
        sin = Math.Trigonometry.sin(angle)

        return Vector2(
        self.x * cos - self.y * sin,
        self.x * sin + self.y * cos
        )
    def cross(self, other):
        return self.x * other.y - self.y * other.x
    def projection(self, other):
        denominator = other.length_squared()

        if denominator == 0:
            raise ValueError("Sıfır vektörüne izdüşüm alınamaz!")

        return other * (self.dot(other) / denominator)
    def reflect(self, normal):
        n = normal.normalize()
        return self - n * (2 * self.dot(n))
    def lerp(self, other, t):
        return self + (other - self) * t
    def perpendicular(self, k=0):
        if not isinstance(k, int):
            raise ValueError
        if k % 2 == 0:
            return Vector2(-self.y, self.x)
        return Vector2(self.y, -self.x)
    def is_parallel(self, other, eps=1e-12):
        return abs(self.cross(other)) <= eps * self.length() * other.length()
    def is_perpendicular(self, other, eps=1e-12):
        return abs(self.dot(other)) <= eps * self.length() * other.length()
    def slope(self):
        return self.y / self.x
    def move_towards(self, target, max_distance):
        if max_distance < 0:
            raise ValueError("Mesafe negatif olamaz!")

        difference = target - self
        distance = difference.length()

        if distance <= max_distance:
            return Vector2(target.x, target.y)

        return self + difference.normalize() * max_distance
    def clamp_magnitude(self, max_length):
        if max_length < 0:
            raise ValueError("Uzunluk negatif olamaz!")

        length = self.length()

        if length <= max_length:
            return Vector2(self.x, self.y)

        return self.normalize() * max_length
      