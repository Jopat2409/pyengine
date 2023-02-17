from __future__ import annotations
from dataclasses import dataclass
import math


@dataclass()
class vec2d:
   x: float = 0
   y: float = 0

   def __add__(self, other: vec2d) -> vec2d:
      return vec2d(self.x + other.x, self.y + other.y)

   def __iadd__(self, other: vec2d) -> vec2d:
      self.x += other.x
      self.y += other.y
      return self

   def __sub__(self, other: vec2d) -> vec2d:
      return vec2d(self.x - other.x, self.y - other.y)

   def __isub__(self, other: vec2d):
      self.x -= other.x
      self.y -= other.y
      return self

   def __mul__(self, other: float) -> vec2d:
      return vec2d(self.x * other, self.y * other)

   def __imul__(self, other: float) -> vec2d:
      self.x *= other
      self.y *= other
      return self

   def __rmul__(self, other: float) -> vec2d:
      return vec2d(self.x * other, self.y * other)

   def __truediv__(self, other: float) -> vec2d:
      return vec2d(self.x / other, self.y / other)

   def __itruediv__(self, other: vec2d) -> vec2d:
      self.x /= other
      self.y /= other
      return self

   def __eq__(self, other: vec2d) -> bool:
      return self.x == other.x and self.y == other.y

   def __ne__(self, other: vec2d) -> bool:
      return not self.__eq__(other)

   def __neg__(self) -> vec2d:
      self.x = -self.x
      self.y = -self.y
      return self

   def __repr__(self) -> str:
      return f"({self.x}, {self.y})"

   def __abs__(self) -> float:
      return math.sqrt(self.x ** 2 + self.y ** 2)

   def __iter__(self):
      yield self.x
      yield self.y

   def to_unit(self: vec2d) -> vec2d:
      factor = abs(self)
      return vec2d(self.x / factor, self.y / factor)


@dataclass()
class vec3d:
   x: (int, float) = 0
   y: (int, float) = 0
   z: (int, float) = 0

   def __add__(self, other: vec3d) -> vec3d:
      return vec3d(self.x + other.x, self.y + other.y, self.z + other.z)

   def __iadd__(self, other: vec3d) -> vec3d:
      self.x += other.x
      self.y += other.y
      self.z += other.z
      return self

   def __sub__(self, other: vec3d) -> vec3d:
      return vec3d(self.x - other.x, self.y - other.y, self.z - other.z)

   def __isub__(self, other: vec3d):
      self.x -= other.x
      self.y -= other.y
      self.z -= other.z
      return self

   def __mul__(self, other: (int, float)) -> vec3d:
      return vec3d(self.x * other, self.y * other, self.z * other)

   def __imul__(self, other: (int, float)) -> vec3d:
      self.x *= other
      self.y *= other
      self.z *= other
      return self

   def __rtruediv__(self, other: (int, float)) -> vec3d:
      return vec3d(self.x / other, self.y / other, self.z / other)

   def __itruediv__(self, other: vec3d) -> vec3d:
      self.x /= other
      self.y /= other
      self.z /= other
      return self

   def __eq__(self, other: vec3d) -> bool:
      return self.x == other.x and self.y == other.y and self.z == other.z

   def __ne__(self, other: vec3d) -> bool:
      return not self.__eq__(other)

   def __neg__(self) -> vec3d:
      self.x = -self.x
      self.y = -self.y
      self.z = -self.z
      return self

   def __repr__(self) -> str:
      return f"({self.x}, {self.y}, {self.z})"

   def __abs__(self) -> float:
      return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
