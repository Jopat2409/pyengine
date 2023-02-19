import copy
from dataclasses import dataclass
from typing import Optional

from vector import vec2d
from enum import IntEnum


class CollisionType(IntEnum):
    PHYS_PARTICLE = 0
    PHYS_PLANE = 1


@dataclass
class _PhysicsObject:
    obj_type: CollisionType
    pos: vec2d
    dimensions: vec2d
    vel: vec2d
    weight: float
    apply_grav: bool = False
    accel: vec2d = vec2d(0, 0)
    _last_newvel: vec2d = None


""" ----------------- PHYSICS VARIABLES ------------"""

_m_physics_steps: int = 32
_m_step_time: float = 1e3 / _m_physics_steps
_m_step_mult = 1 / _m_physics_steps


def set_physics_steps(newsteps: int):
    if newsteps <= 0:
        return
    global _m_physics_steps, _m_step_time, _m_step_mult
    _m_physics_steps = newsteps
    _m_step_time = 1e3 / newsteps
    _m_step_mult = 1 / _m_physics_steps


_m_grav: vec2d = vec2d(0, 120)


def set_gravity(grav: float):
    global _m_grav
    _m_grav = vec2d(0, grav)


_m_physObjects = []


def create_component(_type: CollisionType, x: float, y: float, w: float, h: float, velx: float, vely: float,
                     weight: float, apply_grav=True) -> _PhysicsObject:
    """
    Creates physics component
    :param _type: Type of physics component
    :param x: initial x value (depends on type)
    :param y: initial y value (depends on type)
    :param w: initial width / radius in x direction
    :param h: initial height / radius in y dimensions
    :param velx: initial velocity in x direction
    :param vely: initial velocity in y direction
    :param weight: weight
    :param apply_grav: should gravity apply to this phys object
    :return: Physics Object Created
    """
    _m_physObjects.append(_PhysicsObject(_type, vec2d(x, y),
                                         vec2d(w, h),
                                         vec2d(velx, vely),
                                         weight,
                                         apply_grav,
                                         _m_grav * int(apply_grav)))
    return _m_physObjects[-1]


def remove_component(component: _PhysicsObject):
    if component in _m_physObjects:
        _m_physObjects.remove(component)


_m_internal_lag: float = 0
_m_coeff_rest: float = 0.7
_m_stable_thresh = 1
""" -------------- ENGINE FUNCTIONS ------------"""


def _collision_particle_particle(obj1: _PhysicsObject, obj2: _PhysicsObject) -> Optional[vec2d]:
    pass


def _collision_particle_plane(plane: _PhysicsObject, particle: _PhysicsObject):
    if abs(particle.vel + plane.vel) == 0:
        return
    if particle.pos.x + particle.dimensions.x <= plane.pos.x or particle.pos.x - particle.dimensions.x >= plane.pos.x + plane.dimensions.x:
        return
    if particle.pos.y + particle.dimensions.y <= plane.pos.y or particle.pos.y - particle.dimensions.y >= plane.pos.y + plane.dimensions.y:
        return
    # Determine point of collision and move particle back
    m_dir = particle.vel.to_unit()
    factor = (plane.pos.y - particle.pos.y) / m_dir.y
    point_of_collision = vec2d(particle.pos.x + m_dir.x * factor, plane.pos.y)
    final_point = point_of_collision - m_dir * (particle.dimensions.x + 1)
    particle.pos = final_point
    new_vel = vec2d(particle.vel.x, -particle.vel.y * 0.5)
    if particle._last_newvel:
        print(f"New velocity: {new_vel} Last new velocity: {particle._last_newvel}")
    if particle._last_newvel and abs(particle._last_newvel - new_vel) < _m_stable_thresh:
        print("Culling velocity")
        new_vel = vec2d(0, 0)
    particle._last_newvel = vec2d(new_vel.x, new_vel.y)
    particle.vel = new_vel


def _collision_particle_plane_i(particle: _PhysicsObject, plane: _PhysicsObject):
    return _collision_particle_plane(plane, particle)


_COLLIDE_FUNCT = {(CollisionType.PHYS_PARTICLE, CollisionType.PHYS_PARTICLE): _collision_particle_particle,
                  (CollisionType.PHYS_PLANE, CollisionType.PHYS_PARTICLE): _collision_particle_plane,
                  (CollisionType.PHYS_PARTICLE, CollisionType.PHYS_PLANE): _collision_particle_plane_i}


def _collision(obj1: _PhysicsObject, obj2: _PhysicsObject):
    """
    Simulates a collision between obj1 and obj2 at point-of-collision
    :param obj1: Physics object being collided with
    :param obj2: Physics object doing collision
    :return:
    """
    point_of_collision = _COLLIDE_FUNCT[(obj1.obj_type, obj2.obj_type)](obj1, obj2)
    if not point_of_collision:
        return
    # TODO simulate collision at point of collision
    print(f"Collision detected at: {point_of_collision}")
    pass


def _physics_step(elapsedtime: float) -> bool:
    """
    Steps the physics engine
    :param elapsedtime: current lagtime of the engine
    :return: wether the physics engine was stepped this tick
    """
    global _m_internal_lag
    _m_internal_lag += elapsedtime
    if _m_internal_lag < _m_step_time:
        return False
    phys_object: _PhysicsObject
    for phys_object in _m_physObjects:
        phys_object.pos += phys_object.vel * _m_step_mult
        phys_object.vel += phys_object.accel * _m_step_mult
    for index, phys_object in enumerate(_m_physObjects):
        for c_phys_object in _m_physObjects[index + 1::]:
            _collision(phys_object, c_phys_object)

    _m_internal_lag -= _m_step_time
    return True
