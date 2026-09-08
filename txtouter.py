# Justification settings
VJUST_TOP = "top"
VJUST_BOTTOM = "bottom"
VJUST_CENTER = "center" #if even sides left
HJUST_LEFT = "left"
HJUST_RIGHT = "right"
HJUST_CENTER = VJUST_CENTER # if even sides top
GRID_SQUARE = "square"
GRID_STRETCH = "stretch"


class DisplayException(Exception):
    """
    Exception that constructs trace to identify the offending display element
    """
    def __init__(self, curr_element: "TextDisplayElement", message: str, 
                 *args, **kwargs):
        trace = ""
        while curr_element is not None:
            trace = f"{curr_element.__class__.__name__} > " + trace     
            curr_element = curr_element.get_parent() # Walk up parent relation

        # Strip trailing > 
        super().__init__(trace[:-3] + ": " + message, *args, **kwargs)


class TextDisplayElement():
    """
    Abstract display element. Displays a rectangular block of text. 
    """

    def __init__(self, 
            width: int | None = None, 
            height: int | None = None,
            vjust: str = VJUST_CENTER,
            hjust: str = HJUST_CENTER
    ):
        """
        Initialises a new TextDisplayElement.

        Args:
            width (int | None): Fixed width, or None to stretch to widest row. 
                    Optional; Defaults to None.
            height (int | None): Fixed height, or None to stretch to number of 
                    rows in content. Optional; Defaults to None.
            vjust (str): Vertical content justification. Can either be "top", 
                    "bottom" or "center". Optional; Defaults to "center".
            hjust (str): Horizontal content justification. Can either be "left", 
                    "right" or "center". Optional; Defaults to "center".
        """
        self._parent = None # Considered root until embedded into element
        self._fixwidth = width
        self._fixheight = height

        self.set_vjust(vjust)
        self.set_hjust(hjust)
        self._content = [] # Overridden by children.

    def __str__(self):
        return "\n".join(self.render())

    def __repr__(self): # For easier IDLE debugging
        return str(self)

    def get_content(self) -> list[str]:
        """
        Return this element's current content.

        Returns:
            list[str]: Content.
        """
        return self._content
    
    def set_parent(self, parent: "TextDisplayElement"):
        """
        Embeds this TextDisplayElement within the specified element. Elements 
        cannot be re-embedded.

        Args:
            parent (TextDisplayElement): Element to embed into. 

        Raises:
            DisplayException: If this element already has a parent.
        """
        if self._parent is not None:
            raise DisplayException(
                    self, "Attempted to set parent of already embedded element"
            )
        self._parent = parent

    def get_parent(self) -> "TextDisplayElement":
        """
        Returns the parent of this element. Useful for stack tracing.

        Returns:
            TextDisplayElement: The element that this element is currently 
                    embedded in.
        """
        return self._parent

    def set_width(self, width: int | None = None):
        """
        Set or remove fixed width. Width stretches to widest row if not fixed.

        Args:
            width (int | None): New fixed width, or None to remove fixed width. 
                    Optional; Defaults to None.
        """
        self._fixwidth = width

    def get_width(self) -> int:
        """
        Returns current content width.

        Returns:
            int: current content width.
        """
        if self._fixwidth:
            return self._fixwidth
        else:
            return max((len(row) for row in self._content), default= 0)
    
    def set_height(self, height: int | None = None):
        """
        Set or remove fixed height. Height stretches to number of content rows 
        if not fixed.

        Args:
            height (int | None): New fixed height, or None to 
                    remove fixed height. Optional; Defaults to None.
        """
        self._fixheight = height

    def get_height(self) -> int:
        """
        Returns current content height.

        Returns:
            int: current content height.
        """
        if self._fixheight:
            return self._fixheight
        else:
            return len(self._content)
        
    def set_vjust(self, vjust: str):
        """
        Set vertical justification mode

        Args:
            vjust (str): Vertical content justification. Can either be "top", 
                "bottom" or "center". Optional; Defaults to "center".

        Raises:
            DisplayException: If invalid justification mode is provided.
        """
        if vjust not in (VJUST_TOP, VJUST_CENTER, VJUST_BOTTOM):
            raise DisplayException(self, 
                            "Invalid vertical justification, please use "+ 
                             f"'{VJUST_TOP}', " +
                             f"'{VJUST_CENTER}', or " +
                             f"'{VJUST_BOTTOM}'"
            )
        self._vjust = vjust

    def set_hjust(self, hjust: str):
        """
        Set horizontal justification mode

        Args:
            hjust (str): Horizontal content justification. Can either be "left", 
                    "right" or "center". Optional; Defaults to "center".

        Raises:
            DisplayException: If invalid justification mode is provided.
        """
        if hjust not in (HJUST_LEFT, HJUST_CENTER, HJUST_RIGHT):
            raise DisplayException(self, 
                            "Invalid horizontal justification, please use "+ 
                             f"'{HJUST_LEFT}', " +
                             f"'{HJUST_CENTER}', or " +
                             f"'{HJUST_RIGHT}'"
            )
        self._hjust = hjust
    
    def justify(self, content: list[str]) -> list[str]:
        """
        Pad specified content to be rectangular and justified according to 
        the element's settings.

        Args:
            content (list[str]): Content to pad/justify

        Raises:
            DisplayException: If content is too wide/tall for fixed width/height

        Returns:
            list[str]: Padded and justified COPY of given content.
        """
        # pad content horizonally
        to_render = []
        for line in content:
            hdiff = self.get_width() - len(line)
            if hdiff < 0:
                raise DisplayException(self, "Content too wide!")
            if self._hjust == HJUST_LEFT:
                to_render.append(line + (" " * hdiff))
            elif self._hjust == HJUST_RIGHT:
                to_render.append((" " * hdiff) + line)
            elif self._hjust == HJUST_CENTER:
                lpad = hdiff // 2
                rpad = hdiff - lpad
                to_render.append((" " * lpad) + line + (" " * rpad))

        # pad content vertically
        vdiff = self.get_height() - len(to_render)
        if vdiff < 0:
            raise DisplayException(self, "Content too tall!")
        if self._vjust == VJUST_TOP:
            to_render += [" " * self.get_width()] * vdiff
        elif self._vjust == VJUST_BOTTOM:
            to_render = ([" " * self.get_width()] * vdiff) + to_render
        elif self._vjust == VJUST_CENTER:
            tpad = vdiff // 2
            bpad = vdiff - tpad
            to_render = ([" " * self.get_width()] * tpad) + \
                    to_render + \
                    ([" " * self.get_width()] * bpad)
        
        return to_render
        
    def render(self) -> list[str]:
        """
        Returns content that should be printed to display the content of this
        TextDisplayElement

        Returns:
            list[str]: Content to display.

        """
        return self.justify(self.get_content())
    
    def display(self):
        """
        Print this TextDisplayElement to the screen.
        """
        print(str(self))


class BaseDisplay(TextDisplayElement):
    """
    Basic display element. Displays manually specified content.
    """
    
    def __init__(self,
                 content: list[str] | None = None, 
                 width: int | None = None, 
                 height: int | None = None, 
                 vjust: str = VJUST_CENTER, 
                 hjust: str = HJUST_CENTER
    ):
        """
        Initialises a BaseDisplay element.

        Args:
            content (list[str] | None): content to display in this element, or 
                    None for empty content. Optional; Defaults to None.
            width (int | None): Fixed width, or None to stretch to widest row. 
                    Optional; Defaults to None.
            height (int | None): Fixed height, or None to stretch to number of 
                    rows in content. Optional; Defaults to None.
            vjust (str): Vertical content justification. Can either be "top", 
                    "bottom" or "center". Optional; Defaults to "center".
            hjust (str): Horizontal content justification. Can either be "left", 
                    "right" or "center". Optional; Defaults to "center".
        """
        super().__init__(width, height, vjust, hjust)
        self._content = content if content else []

    def set_content(self, content: list[str]):
        """
        Set content to display.

        Args:
            content (list[str]): Content to display.
        """
        self._content = content

    def wrap_text(self, text: str) -> list[str]:
        """ 
        Attempts to split given string into rows that would fit within this 
        element. Splits on spaces. Will behave weird without fixed width.

        Args:
            text (str): String to break into lines.

        Returns:
            list[str]: Wrapped text.
        """
        wrapped = []
        remaining = text
        while len(remaining) > self.get_width():
            # find space to break on
            space = remaining.rfind(" ", 0, self.get_width())
            wrapped.append(remaining[0:space])
            remaining = remaining[space+1:]
            if space == -1:
                break # give up and deal with consequences later
        wrapped.append(remaining)
        return wrapped


class OrderedComponentList(TextDisplayElement):
    """
    Abstract display element. Manages several elements in an ordered structure.
    """

    def __init__(self, 
                 components: list[TextDisplayElement],
                 width: int | None = None, 
                 height: int | None = None, 
                 vjust: str = VJUST_CENTER, 
                 hjust: str = HJUST_CENTER
    ):
        """
        Initialises a new OrderedComponentList.

        Args:
            components (list[TextDisplayElement]): Ordered elements to embed.
            width (int | None): Fixed width, or None to stretch to widest row. 
                    Optional; Defaults to None.
            height (int | None): Fixed height, or None to stretch to number of 
                    rows in content. Optional; Defaults to None.
            vjust (str): Vertical content justification. Can either be "top", 
                    "bottom" or "center". Optional; Defaults to "center".
            hjust (str): Horizontal content justification. Can either be "left", 
                    "right" or "center". Optional; Defaults to "center".
        """
        super().__init__(width, height, vjust, hjust)
        self._components = components
        for component in self._components:
            component.set_parent(self)

    def get_component(self, index: int) -> TextDisplayElement:
        """
        Return the component at the given index in the list. 

        Returns:
            TextDisplayElement: Element at given index.
        """
        return self._components[index]
    
    def set_component(self, index: int, new_component: TextDisplayElement):
        """
        Replaces the component at the given index with the given component.

        Args:
            index (int): Index of component to replace.
            new_component (TextDisplayElement): Replacement component.
        """
        self._components[index] = new_component
        new_component.set_parent(self)

    def add_component(self, new_component: TextDisplayElement):
        """
        Appends a new component to the end of component list.

        Args:
            new_component (TextDisplayElement): Component to add.
        """
        self._components.append(new_component)
        new_component.set_parent(self)
         

class VSplitDisplay(OrderedComponentList):
    """
    Stacks the content of several display elements top to bottom.
    """
    
    def get_width(self) -> int:
        if self._fixwidth:
            return self._fixwidth
        else:
            return max(
                (component.get_width() for component in self._components), 
                default= 0
            )
        
    def get_height(self) -> int:
        if self._fixheight:
            return self._fixheight
        else:
            return sum(
                (component.get_height() for component in self._components)
            )

    def render(self):
        content_stack = []
        for component in self._components:
            content_stack += component.render()
        return self.justify(content_stack)
    

class HSplitDisplay(OrderedComponentList):
    """
    Aligns the content of several display elements left to right.
    """
    
    def get_width(self) -> int:
        if self._fixwidth:
            return self._fixwidth
        else:
            return sum((component.get_width() for component in self._components))
        
    def get_height(self) -> int:
        if self._fixheight:
            return self._fixheight
        else:
            return max(
                (component.get_height() for component in self._components), 
                default= 0
            )

    def render(self):  
        to_render = ["" for _ in range(self.get_height())]

        for component in self._components:
            new_content = component.render()
            # will need to pad vertically early
            vdiff = self.get_height() - len(new_content)
            if vdiff < 0:
                raise DisplayException(self, "Component is too tall!")
            if self._vjust == VJUST_TOP:
                new_content += [" " * component.get_width()] * vdiff
            elif self._vjust == VJUST_BOTTOM:
                new_content = [" " * component.get_width()] * vdiff + new_content
            elif self._vjust == VJUST_CENTER:
                tpad = vdiff // 2
                bpad = vdiff - tpad
                new_content = [" " * component.get_width()] * tpad + \
                        new_content + \
                        [" " * component.get_width()] * bpad
            
            #stitch lines together
            for line in range(self.get_height()):
                to_render[line] += new_content[line]

        return self.justify(to_render)


class AbstractGrid(VSplitDisplay):
    """
    Display element that maintains and enforces a useful grid layout. 
    """

    def __init__(self,
                 dims: tuple[int, int], #row col
                 width: int, 
                 height: int, 
                 just: str = GRID_SQUARE
    ):
        """
        Initialise a new AbstractGrid component with empty cells.

        Args:
            dims (tuple[int, int]): dimensions of grid (rows, columns)
            width (int): fixed width.
            height (int): fixed height.
            just (str): How grid should behave if width and height 
                are not equal. Can be either "square" or "stretch". Optional; 
                Defaults to "square".
        """
        super().__init__([], width, height) # Dummy rowset overwritten below

        self._FIXED_GEO_ERR = DisplayException( # Constant requires instance
            self, "Grid must have positive fixed geometry") 

        if not width and height:
            raise self._FIXED_GEO_ERR

        if just not in (GRID_SQUARE, GRID_STRETCH):
            raise DisplayException(self, 
                            "invalid grid justification, please use "+ 
                             f"'{GRID_SQUARE}', or" +
                             f"'{GRID_STRETCH}'"
            )

        self._grid_just = just
        self.set_dims(dims)

    def set_width(self, width: int): # warning: wipes
        if not width:
            raise self._FIXED_GEO_ERR
        super().set_width(width)
        self.set_dims(self._dims) # Reconstruct grid with new geometry
    
    def set_height(self, height: int):
        if not height:
            raise self._FIXED_GEO_ERR
        super().set_height(height)
        self.set_dims(self._dims) # Reconstruct grid with new geometry

    def get_dims(self) -> tuple[int, int]: # warning: wipes
        """
        Return grid dimensions.

        Returns:
            tuple[int, int]: (row, column) dimensions.
        """
        return self._dims

    def set_dims(self, dims: tuple[int, int]): #Warning, wipes content
        """
        Set dimensions and reconstruct grid using them. 

        WARNING: This wipes existing embedded elements.

        Args:
            dims (tuple[int, int]): new grid dimensions (rows, columns)
        """
        self._dims = dims

        # Determine cell dims
        cell_height = self._fixheight // dims[0]
        cell_width = self._fixwidth // dims[1]

        if self._grid_just == GRID_SQUARE:
            min_dim = min(cell_height, cell_width)
            cell_height = min_dim
            cell_width = min_dim

        self._components.clear()
        for _ in range(dims[0]):
            row = HSplitDisplay(
                    [BaseDisplay(width=cell_width, height=cell_height) 
                     for _ in range(dims[1])], width = self.get_width(), 
                    height = cell_height
            )
            self.add_component(row)

    def get_cell(self, row: int, col: int) -> BaseDisplay:
        """
        Return the BaseDisplay cell at the given coordinate.

        Args:
            row (int): row index
            col (int): column index

        Returns:
            BaseDisplay: Element at specified cell.
        """
        return self.get_component(row).get_component(col)