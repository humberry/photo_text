# coding: utf-8
import scene, ui, collections, console, clipboard, photos, Image, ImageDraw, ImageFont

fonttypes = ('Helvetica', 'Helvetica Bold', 'Arial', 'Avenir Book',
             'Times New Roman', 'Baskerville', 'Courier',
             'Chalkduster', 'American Typewriter', 'Verdana')

colors_dict = collections.OrderedDict([
              ('black', (0,0,0)), ('white',   (1,1,1)), ('grey',   (0.7,0.7,0.7)),
              ('red',   (1,0,0)), ('green',   (0,1,0)), ('blue',   (0,0,1)),
              ('cyan',  (0,1,1)), ('magenta', (1,0,1)), ('yellow', (1,1,0))])

def color(color_name):
    return colors_dict[color_name.lower()]

def color_by_number(color_number):
    return colors_dict[colors_dict.keys()[color_number % len(colors_dict)]]

def pic_save(image, width, height, text, font, fontsize, color, x, y):
    background = Image.new('RGBA', (width,height), 'white')
    background.paste(image, (0, 0))
    draw = ImageDraw.Draw(background)
    y = height - y
    f = ImageFont.truetype(font, int(fontsize))
    textsize = draw.textsize(text, font=f)
    x -= textsize[0]/2
    y -= ((textsize[1]/1.15)/2) # remove offset / add div factor 1.15 (difference between pixel size and font size)
    draw.text((x, y), text, font=f, fill=color)
    clipboard.set_image(background, format='jpeg', jpeg_quality=0.98)
    photos.save_image(clipboard.get_image())

class MyPicture(scene.Scene):
    def __init__(self, text, img, picsize):
        self.text = text
        self.position = [0, 0]
        self.fontnr = 0       # Helvetica
        self.colornr = 3      # red
        self.fontsize = 48.0  # 48 point
        self.img = img.convert('RGBA')
        img = None
        self.picsize = picsize

    def increase_font_size(self):
        if 2 <= self.fontsize < 16:
            self.fontsize += 1.0
        elif self.fontsize >= 16:
            self.fontsize += 16.0

    def decrease_font_size(self):
        if 3 < self.fontsize <= 16:
            self.fontsize -= 1.0
        elif self.fontsize > 16:
            self.fontsize -= 16.0

    def next_font(self):
        self.fontnr += 1

    def next_color(self):
        self.colornr += 1
        
    def save_image(self):
        color = tuple([int(i * 255) for i in self.current_color()])  # convert scene color to PIL color
        pic_save(self.img, int(self.picsize[0]), int(self.picsize[1]), self.text, self.current_font(), self.fontsize, color, self.position[0], self.position[1])
        console.hud_alert('Saved')

    def setup(self):
        x = self.picsize[0]
        y = self.picsize[1]
        self.position = scene.Size(x/2, y/2)
        self.layer = scene.Layer(scene.Rect(0, 0, x, y))
        self.layer.image = scene.load_pil_image(self.img)
        self.add_layer(self.layer)

    def current_color(self):
        return color_by_number(self.colornr)

    def current_font(self):
        return fonttypes[self.fontnr % len(fonttypes)]

    def touch_moved(self, touch):
        if ((0 < touch.location[0] < self.bounds.w) and (0 < touch.location[1] < self.bounds.h - 20)):
            self.position = touch.location

    def touch_ended(self, touch):
        self.touch_moved(touch)

    def draw(self):
        #scene.background(*color('black'))
        self.root_layer.update(self.dt)
        self.root_layer.draw()
        scene.tint(*self.current_color())  # draw the user's text
        scene.text(self.text, self.current_font(), self.fontsize, self.position[0], self.position[1], 5)
            
class PhotoTextV2(ui.View):
    def __init__(self):
        self.view = ui.load_view('PhotoTextV2')
        self.set_button_actions()
        self.view.present('full_screen')

        img = photos.pick_image()
        if img:
            console.hud_alert('Please wait...')
            picsize = scene.Size(*img.size)
            self.sv2 = self.view['scrollview2']
            self.sv2.content_size = (picsize[0], picsize[1])
            self.sv2v1 = self.sv2.subviews[0]  #sv2v1 = view1 in scrollview2
            self.sv2v1.bounds = (0, 0, picsize[0], picsize[1])
            self.sceneView = scene.SceneView(frame=self.sv2v1.bounds)
            self.sceneView.scene = MyPicture(self.view['scrollview1'].subviews[0].text, img, picsize)
            img = None
            self.sv2.add_subview(self.sceneView)
        else:
            self.view.close()

    def btn_plus(self, sender):
        self.sceneView.scene.increase_font_size()

    def btn_minus(self, sender):
        self.sceneView.scene.decrease_font_size()
    
    def btn_font(self, sender):
        self.sceneView.scene.next_font()
        
    def btn_color(self, sender):
        self.sceneView.scene.next_color()
        
    def btn_save(self, sender):
        self.sceneView.scene.save_image()
        
    def textfield_did_end_editing(self, textfield):
        self.sceneView.scene.text = self.view['scrollview1'].subviews[0].text

    def set_button_actions(self):
        for subview in self.view['scrollview1'].subviews:
          if isinstance(subview, ui.Button):
            subview.action = getattr(self, subview.name)
          elif isinstance(subview, ui.TextField):
            subview.delegate = self
            subview.clear_button_mode = 'while_editing'
            
if photos.get_count():
    PhotoTextV2()
else:
    print('Sorry no access or no pictures.')
