"""Runnable Pygame application shell for Ludo."""

from __future__ import annotations

import argparse

import pygame

from ludo.pygame_ui import theme
from ludo.pygame_ui.screens import ScreenRenderer
from ludo.pygame_ui.state import ScreenController


class LudoApplication:
    """Owns Pygame lifecycle, the event loop, and screen rendering."""

    def __init__(self) -> None:
        self.controller = ScreenController()
        self.renderer: ScreenRenderer | None = None
        self.screen: pygame.Surface | None = None
        self.clock: pygame.time.Clock | None = None

    def run(self, *, smoke_frames: int | None = None) -> None:
        """Run until quit or until smoke frames finish."""
        pygame.init()
        pygame.display.set_caption("Ludo")
        self.screen = pygame.display.set_mode(theme.WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        self.renderer = ScreenRenderer()
        frames = 0
        try:
            while self.controller.running:
                self._handle_events()
                self._render_frame()
                frames += 1
                if smoke_frames is not None and frames >= smoke_frames:
                    self.controller.quit()
        finally:
            pygame.quit()

    def _handle_events(self) -> None:
        if self.renderer is None:
            return
        for event in pygame.event.get():
            self.renderer.handle_event(event, self.controller)

    def _render_frame(self) -> None:
        if self.screen is None or self.clock is None or self.renderer is None:
            return
        delta_ms = self.clock.tick(theme.FPS)
        self.renderer.update(delta_ms, self.controller)
        self.renderer.draw(self.screen, self.controller)
        pygame.display.flip()


def main(argv: list[str] | None = None) -> None:
    """Run the Ludo Pygame shell."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="open briefly and exit")
    args = parser.parse_args(argv)
    LudoApplication().run(smoke_frames=3 if args.smoke else None)


if __name__ == "__main__":
    main()
