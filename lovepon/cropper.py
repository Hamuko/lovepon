import tkinter
from PIL import ImageTk, Image

root = tkinter.Tk()


class VideoCropper(tkinter.Frame):
    def __init__(self, video):
        super().__init__(root)
        self.setup_root()
        self.video = video
        self.screenshot = Image.open(self.video.generate_screenshot())
        self.pack()
        self.create_widgets()

    @property
    def coords(self):
        """Returns the crop coordinates as a four integer tuple."""
        return (self.x_start, self.y_start, self.x_end, self.y_end)

    def create_widgets(self):
        """Creates the image display widget."""
        w, h = self.screenshot.size
        canvas_options = {'width': w, 'height': h, 'highlightthickness': 0}
        self.canvas = tkinter.Canvas(self, **canvas_options)
        self.canvas.pack(anchor='n', fill='x')
        self.canvas.image = ImageTk.PhotoImage(self.screenshot)
        self.canvas.create_image(0, 0, image=self.canvas.image, anchor='nw')
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.rect = None

    def on_mouse_down(self, event):
        """Registers the beginning and end coordinates at the position where
        mouse was first pressed down and creates the crop rectangle if it
        doesn't exist.
        """
        self.x_start = event.x
        self.y_start = event.y
        self.x_end = event.x
        self.y_end = event.y

        if not self.rect:
            kwargs = {'outline': '#808080', 'width': 2}
            self.rect = self.canvas.create_rectangle(*self.coords, **kwargs)

    def on_mouse_drag(self, event):
        """Updates the end points when dragging occurs and updates the crop
        rectangle. Constrains the end points to video width and height and
        ensures they are not smaller than the start points.
        """
        img_w, img_h = self.screenshot.size
        self.x_end = min(event.x, img_w)
        self.y_end = min(event.y, img_h)
        self.x_end = max(self.x_end, self.x_start)
        self.y_end = max(self.y_end, self.y_start)
        self.canvas.coords(self.rect, *self.coords)

    def on_mouse_up(self, event):
        """Saves the crop coordinates to the ffmpeg object after dragging ends.
        """
        self.video.coordinates = self.coords

    def setup_root(self):
        """Configures the Tkinter root."""
        root.resizable(0, 0)
        root.wm_title("lovepon cropper")
