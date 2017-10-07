import pygame


LEFT_CLICK = 1


def create_frame_image(width, height, color, line_width=1):
    ret = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.line(ret, color, (0, 0), (width, 0), line_width)
    pygame.draw.line(ret, color, (0, 0), (0, height), line_width)
    pygame.draw.line(ret, color, (width - 1, 0), (width - 1, height),
                     line_width)
    pygame.draw.line(ret, color, (0, height - 1), (width, height - 1),
                     line_width)
    return ret


class Label:
    """Label GUI element.

    Parameters
    ----------
    font : pygame.Font
        Font to use.
    font_color : compatible with pygame.Color
        Font color.
    text : string
        Label text.
    position : 2-tuple
        Position on screen.
    """
    def __init__(self, font, font_color, text, position=(0, 0)):
        self.font = font
        self.font_color = font_color
        self.surface = font.render(text, False, font_color)
        self.rect = self.surface.get_rect(topleft=position)

    def set_text(self, text):
        """Set text."""
        self.surface = self.font.render(text, False, self.font_color)

    def render(self):
        """Return surface to display."""
        return self.surface


class Button:
    """Button GUI element.

    The visual is a text in a rectangular frame.

    Parameters
    ----------
    font : pygame.Font
        Font to use.
    font_color : compatible with pygame.Color
        Color to use.
    text : string
        Text on button.
    on_click_callback : callable
        Call on click, accepts no arguments. No callback by default.
    frame_color : compatible with pygame.Color
        Color to use for the frame. Use `font_color` by default.
    position : 2-tuple, optional
        Position on screen. Default (0, 0). It might make sense to set it
        later thus it is implemented that way.
    """
    def __init__(self, font, font_color, text, on_click_callback,
                 frame_color=None, position=(0, 0)):
        self.text = font.render(text, False, font_color)
        if frame_color is None:
            frame_color = font_color
        self.boarder = create_frame_image(1.2 * self.text.get_width(),
                                          1.2 * self.text.get_height(),
                                          frame_color)
        self.rect = self.boarder.get_rect()
        rect = self.text.get_rect(center=self.rect.center)
        self.rect.topleft = position
        self.boarder.blit(self.text, rect.topleft)
        self.on_click_callback = on_click_callback

    def render(self):
        """Return surface to display."""
        return self.boarder

    def on_mouse_down(self, button):
        """Handle mouse down."""
        if button != LEFT_CLICK or self.on_click_callback is None:
            return

        if self.rect.collidepoint(*pygame.mouse.get_pos()):
            self.on_click_callback()


class SelectionGroup:
    """Selector from one of many options.

    Parameters
    ----------
    font : pygame.Font
        Font to display text.
    font_color : compatible with pygame.Color
        Font color.
    unselected_image, selected_image : pygame.Surface
        Images for selected / unselected options. Must have equal size.
    title : string
        Title for the group.
    options : list of string
        Option names.
    on_change_callback : callable, optional
        Callable with signature ``on_change_callback(option)`` called
        when a new option is selected. No callback by default.
    position : 2-tuple, optional
        Position on screen. Default (0, 0). It might make sense to set it
        later thus it is implemented that way.
    """
    def __init__(self, font, font_color,
                 unselected_image, selected_image,
                 title, options,
                 on_change_callback=None, position=(0, 0)):
        if unselected_image.get_size() != selected_image.get_size():
            raise ValueError("Images of selected and unselected buttons "
                             "must have equal size")

        self.unselected_image = unselected_image
        self.selected_image = selected_image

        self.options = options
        self.n_options = len(options)

        self.title_image = font.render(title, False, font_color)
        option_images = [font.render(option, False, font_color)
                         for option in options]

        item_height = max(unselected_image.get_height(), font.get_height())
        button_width = unselected_image.get_width()
        item_widths = [1.5 * button_width + option_image.get_width()
                       for option_image in option_images]
        width = max(max(item_widths), self.title_image.get_width())
        height = (self.title_image.get_height()
                  + 0.5 * item_height
                  + 1.5 * item_height * self.n_options)

        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.surface.get_rect(topleft=position)
        surface_rect = self.surface.get_rect()

        title_rect = self.title_image.get_rect(centerx=surface_rect.centerx)

        self.button_rects = []
        self.item_rects = []
        option_rects = []
        y = title_rect.bottom + 0.5 * item_height
        for option_image, item_width in zip(option_images, item_widths):
            button_rect = self.unselected_image.get_rect(y=y)
            option_rect = option_image.get_rect(
                x=button_rect.right + 0.5 * button_rect.width,
                centery=button_rect.centery)
            item_rect = pygame.Rect(0, y, item_width, item_height)
            self.button_rects.append(button_rect)
            option_rects.append(option_rect)
            self.item_rects.append(item_rect)
            y += 1.5 * item_height

        self._selected = 0
        self.callback = on_change_callback

        self.surface.fill((0, 0, 0, 0))
        self.surface.blit(self.title_image, title_rect.topleft)
        for option_rect, option_image in zip(option_rects, option_images):
            self.surface.blit(option_image, option_rect)
        self.surface.blit(self.selected_image, self.button_rects[0])
        for rect in self.button_rects[1:]:
            self.surface.blit(self.unselected_image, rect)

    @property
    def selected(self):
        """Currently selected option."""
        return self.options[self._selected]

    def on_mouse_down(self, button):
        """Handle mouse down."""
        if button != LEFT_CLICK:
            return

        mouse_pos = pygame.mouse.get_pos()
        x = mouse_pos[0] - self.rect.left
        y = mouse_pos[1] - self.rect.top
        selected_old = self._selected
        for i, (button_rect, item_rect) in enumerate(
                zip(self.button_rects, self.item_rects)):
            if item_rect.collidepoint(x, y):
                if self.callback is not None and i != self._selected:
                    self.callback(self.options[i])
                self._selected = i
                break

        if self._selected != selected_old:
            self.surface.blit(self.unselected_image,
                              self.button_rects[selected_old])
            self.surface.blit(self.selected_image,
                              self.button_rects[self._selected])

    def render(self):
        """Return surface to display."""
        return self.surface


class Input:
    """Text input.

    It displays a title and a value. Value can be modified by clicking on
    it (if `active_input` is True).

    Parameters
    ----------
    font : pygame.Font
        Font to use.
    font_color : compatible with pygame.Color
        Font color.
    title : string
        Input title.
    value : string
        Input value. Everything will be converted to string.
    delimiter : string
        Delimiter between title and value. Two spaces by default.
    frame_color : pygame.Color compatible, optional
        Color for frame when displaying value being edit. Use `font_color`
        by default.
    active_input : bool, optional
        Whether to allow modifying value by clicking on it. False by default.
    width : int, optional
        Element width. If given the text be centred in a rectangle of the
        given width. If None (default), width be equal to the current text
        to display.
    max_value_length : int, optional
        Maximum length of the value string. Unlimited by default.
    allowed_symbols : container of strings
        Allowed characters to accept when entering the value. The character
        will be obtained with ``pygame.key.name``. Any symbol is allowed
        by default.
    on_enter_callback : callable, optional
        Callable to call when the value is entered. The signature is
        ``on_enter_callback(value)``. No callback by default.
    position : 2-tuple, optional
        Position on screen. By default (0, 0).
    """
    def __init__(self, font, font_color, title, value, delimiter="  ",
                 frame_color=None, active_input=False,
                 width=None, max_value_length=None, allowed_symbols=None,
                 on_enter_callback=None, position=(0, 0)):
        self.font = font
        self.font_color = font_color
        self.width = width
        self.active_input = active_input
        self.in_input = False
        self.title = title
        self.value = str(value)
        self.current_value = self.value
        self.delimiter = delimiter
        if frame_color is None:
            frame_color = font_color
        self.frame_color = frame_color
        self.max_value_length = max_value_length
        self.allowed_symbols = allowed_symbols
        self.on_enter_callback = on_enter_callback

        self.surface = None
        self.text = None
        self.boarder = None
        self.text_rect = None
        self.value_rect = None
        self.rect = None
        self._prepare_render()
        self.rect = self.surface.get_rect(topleft=position)

    def _prepare_render(self):
        """Prepare data for render, called as necessary."""
        value = self.current_value
        if self.in_input:
            value += '_'

        text = self.font.render(self.title + self.delimiter + value,
                                False,
                                self.font_color)

        if self.width is None:
            width = text.get_width()
        else:
            width = self.width
        height = text.get_height()
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        text_rect = text.get_rect(center=surface.get_rect().center)

        title_width = self.font.size(self.title + self.delimiter)[0]
        value_width, value_height = self.font.size(value)
        margin = self.font.size('|')[0]
        value_rect = pygame.Rect(text_rect.left + title_width - margin,
                                 text_rect.top,
                                 value_width + 2 * margin,
                                 value_height)

        if self.active_input:
            frame = create_frame_image(value_rect.width,
                                         value_rect.height,
                                         self.frame_color)
            surface.blit(frame, value_rect)
        surface.blit(text, text_rect)
        self.surface = surface
        self.value_rect = value_rect
        if self.rect is not None:
            self.rect.size = surface.get_size()

    def render(self):
        """Return surface to display."""
        return self.surface

    def set_value(self, value):
        """Set value."""
        if value == self.current_value:
            return
        self.current_value = str(value)
        self.value = self.current_value
        self._prepare_render()

    def on_mouse_click(self, button):
        """Handle mouse click."""
        if not self.active_input or button != LEFT_CLICK:
            return

        mouse_pos = pygame.mouse.get_pos()
        x = mouse_pos[0] - self.rect.x
        y = mouse_pos[1] - self.rect.y

        if self.value_rect.collidepoint(x, y):
            self.in_input = True
        else:
            self.in_input = False
            self.current_value = self.value

        self._prepare_render()

    def on_key_press(self, key):
        """Handle key press."""
        if not self.in_input:
            return

        if key == pygame.K_BACKSPACE:
            if self.current_value:
                self.current_value = self.current_value[:-1]
                self._prepare_render()
        elif key == pygame.K_RETURN:
            self.in_input = False
            if self.on_enter_callback is not None:
                if self.on_enter_callback(self.current_value):
                    self.value = self.current_value
                else:
                    self.current_value = self.value
            else:
                self.value = self.current_value
            self._prepare_render()
        else:
            if len(self.current_value) == self.max_value_length:
                return

            key_name = pygame.key.name(key)
            if (self.allowed_symbols is None or
                    key_name in self.allowed_symbols):
                self.current_value += key_name
                self._prepare_render()
