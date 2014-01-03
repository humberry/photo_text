import photos
import scene
import sys
import Image
import ImageFont
import ImageDraw
import clipboard

fonttypes = ('Helvetica', 'Helvetica Bold', 'Arial', 'Avenir Book', 'Times New Roman', 'Baskerville', 'Courier', 'Chalkduster', 'American Typewriter', 'Verdana')

colors = {0 : ('black',0,0,0,0,0,0), 1 : ('white',1,1,1,255,255,255), 2 : ('red',1,0,0,255,0,0), 3 : ('green',0,1,0,0,255,0), 4 : ('blue',0,0,1,0,0,255), 5 : ('cyan',0,1,1,0,255,255), 6 : ('yellow',1,1,0,255,255,0)}

def pic_save(image, width, height, text, font, fontsize, colornr, x, y, scale):
	background = Image.new('RGBA', (width,height), 'white')
	background.paste(image, (0, 0))
	draw = ImageDraw.Draw(background)
	offset = fontsize / 3.2		#offset is relative to the fontsize
	fontsize = fontsize * scale
	f = ImageFont.truetype(font, int(fontsize))
	y = height - y
	textsize = draw.textsize(text, font=f)
	x = x - textsize[0]/2
	y = y - (textsize[1]/2) + offset
	draw.text((x, y), text, font=f, fill=(colors[colornr][4],colors[colornr][5],colors[colornr][6]))
	clipboard.set_image((background), format='jpeg', jpeg_quality=0.98)
	photos.save_image(clipboard.get_image())
	sys.exit()
		
class PhotoText(scene.Scene):
	def __init__(self):	
		self.text = raw_input('Text to insert in the picture [Hello]: ') or 'Hello'
		self.position = None
		self.fontnr = 0
		self.colornr = 2
		self.fontsize = 48.0
		self.img = photos.pick_image()
		self.picsize = scene.Size(self.img.size[0],self.img.size[1])
		self.picratio = 0.0
		self.picborder = None 
		self.picscale = 0.0
		self.btn_height = 80
		self.btn_sm_width = 80
		self.btn_lg_width = 160
		if self.img:
			scene.run(self)
		else:
			print 'Good bye!'
			
	def setup(self):
		width, height = self.picsize
		if (width > height):
			orientation = 'vertical'
		elif (height > width):
			orientation = 'horizontal'
		else:
			orientation = 'square'
		if orientation == 'horizontal':
			print 'Sorry at the moment only landscape or square pictures are supported!'
			sys.exit()
		self.picratio = width / (height * 1.0)
		x = 668 * self.picratio
		if x <= 1024:
			y = 668
			self.picborder = scene.Rect(x,self.btn_height,1024,y)
		else:
			x = 1024
			y = 1024 / self.picratio
			self.picborder = scene.Rect(0,y+self.btn_height,x,668-y)
		self.position = scene.Size(x/2,y/2+self.btn_height)
		self.picscale = self.picsize[0] / (x * 1.0)
		self.layer = scene.Layer(scene.Rect(0,self.btn_height,x,y))
		self.layer.image = scene.load_pil_image(self.img)
		self.add_layer(self.layer)
		
	def touch_moved(self,touch):
		if (0 < touch.location[0] < 1024) and (self.btn_height < touch.location[1] < 748):
			self.position = touch.location

	def touch_ended(self,touch):
		if (touch.location[0] > 0 and touch.location[0] < 1024) and (touch.location[1] > self.btn_height and touch.location[1] < 748):
			self.position = touch.location
		elif (touch.location[0] > 0 and touch.location[0] < self.btn_sm_width) and (touch.location[1] > 0 and touch.location[1] < self.btn_height):
			if self.fontsize >= 2 and self.fontsize < 16:
				self.fontsize += 1.0
			elif self.fontsize >= 16:
				self.fontsize += 16.0
		elif (touch.location[0] > self.btn_sm_width and touch.location[0] < self.btn_sm_width*2) and (touch.location[1] > 0 and touch.location[1] < self.btn_height):
			if self.fontsize > 3 and self.fontsize <= 16:
				self.fontsize -= 1.0
			elif self.fontsize > 16:
				self.fontsize -= 16.0
		elif (touch.location[0] > self.btn_sm_width*2 and touch.location[0] < self.btn_sm_width*3) and (touch.location[1] > 0 and touch.location[1] < self.btn_height):
			if self.fontnr < 9:
				self.fontnr += 1
			else:
				self.fontnr = 0
		elif (touch.location[0] > self.btn_sm_width*3 and touch.location[0] < self.btn_sm_width*4) and (touch.location[1] > 0 and touch.location[1] < self.btn_height):
			if self.colornr < 6:
				self.colornr += 1
			else:
				self.colornr = 0	
		elif (touch.location[0] > self.btn_sm_width*4 and touch.location[0] < self.btn_sm_width*4+self.btn_lg_width) and (touch.location[1] > 0 and touch.location[1] < self.btn_height):
			font = fonttypes[self.fontnr]
			pic_save(self.img, self.picsize[0], self.picsize[1], self.text, font, self.fontsize, self.colornr, self.position[0]*self.picscale, (self.position[1]-self.btn_height)*self.picscale, self.picscale)
		elif (touch.location[0] > self.btn_sm_width*4+self.btn_lg_width and touch.location[0] < self.btn_sm_width*4+self.btn_lg_width*2) and (touch.location[1] > 0 and touch.location[1] < self.btn_height):
			sys.exit()	
														
	def draw(self):
		self.root_layer.update(self.dt)
		self.root_layer.draw()
		scene.tint(colors[self.colornr][1],colors[self.colornr][2],colors[self.colornr][3],1)
		scene.text(self.text,fonttypes[self.fontnr],self.fontsize,self.position[0],self.position[1],5)
		scene.fill(1,1,1,1)			#watch+battery -> white background
		scene.rect(0,748,1024,20)	#watch+battery
		scene.fill(0,0,0,1)			#black borders
		scene.rect(self.picborder[0],self.picborder[1],self.picborder[2],self.picborder[3])
		scene.rect(0,0,1024,self.btn_height)
		scene.fill(0.7,0.7,0.7,1)	#every other grey buttons
		scene.rect(0,0,self.btn_sm_width,self.btn_height)
		scene.rect(160,0,self.btn_sm_width,self.btn_height)
		scene.rect(320,0,self.btn_lg_width,self.btn_height)
		scene.rect(640,0,384,self.btn_height)
		scene.tint(0,0,0,1)
		scene.text('+','Helvetica',48.0,40,45,5)	#y+5 for +
		scene.text('F','Helvetica',48.0,200,40,5)	
		scene.text('Save','Helvetica',48.0,400,40,5)
		scene.tint(0.7,0.7,0.7,1)
		scene.text('-','Helvetica',48.0,120,45,5)	#y+5 for -
		scene.text('C','Helvetica',48.0,280,40,5)
		scene.text('Cancel','Helvetica',48.0,560,40,5)
				
if photos.get_count():
	PhotoText()
else:
	print 'Sorry no access or no pictures.'
