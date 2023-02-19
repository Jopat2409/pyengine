import pygame


class Scene:

    def __init__(self):
        if __package__ is None or __package__ == '':
            import Engine
        else:
            from . import Engine
        self.engine = Engine
        self.engine.add_key_callback(self.on_key_event)
        self.engine.add_mouse_callback(self.on_mouse_event)

    def draw_scene(self):
        """
        Draws the scene to the window
        :return:
        """
        self.engine._raise_engine_error("draw_scene must be implemented by all scenes")

    def step_scene(self):
        """
        One timestep of the scene
        :return:
        """
        self.engine._raise_engine_error("step_scene must be implemented by all scenes")

    def on_key_event(self, event: pygame.event.Event):
        pass

    def on_mouse_event(self, event: pygame.event.Event):
        pass

    def __del__(self):
        self.engine.remove_key_callback(self.on_key_event)
        self.engine.remove_mouse_callback(self.on_mouse_event)
