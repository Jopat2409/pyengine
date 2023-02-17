from dataclasses import dataclass


@dataclass
class RenderObject:
   x: float
   y: float
   w: int
   h: int
   rType: str
   path: str = None
   col: tuple = None
   oCol: tuple = (0, 0, 0)
   oWidth: int = 0
   shouldCache: bool = True
   shouldAffect: bool = True
