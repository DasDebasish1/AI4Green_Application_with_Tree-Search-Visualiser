from matplotlib import font_manager
from rdkit.Chem import Draw,MolFromSmiles
from textwrap3 import wrap
from PIL import Image, ImageDraw,ImageFont,ImageFile
import math
ImageFile.LOAD_TRUNCATED_IMAGES = True
Scale = 1
NODE_WIDTH = 500
NODE_HEIGHT = 600
X_OFFSET = 100
Y_OFFSET = 100
FONT_SIZE = 20
X=0
Y=0
MAX_DEPTH=0
font = font_manager.FontProperties(family='sans-serif', weight='bold')
file = font_manager.findfont(font)
fnt = ImageFont.truetype(file, 38)

def draw_node(draw,im,node,x,y,is_solved,isbest):

    color=(0,0,0)
    if is_solved:
        color=(0,255,0)
    if isbest:
        color=(0,0,255)
    draw.rectangle([(x,y),(x+NODE_WIDTH,y+NODE_HEIGHT)],outline=color,width=3 if not isbest else 5)
    draw.rectangle([(x,y+100),(x+NODE_WIDTH,y+NODE_HEIGHT)],outline=color,width=3 if not isbest else 5)


    
    if len(node["reaction"])>22:
        for i,line in enumerate(wrap(node["reaction"],22)):

            draw.text((x+round(NODE_WIDTH/2), y+25+(i*50)),line,(0,0,0),font=fnt,anchor="mm") 
    else:

        draw.text((x+round(NODE_WIDTH/2), y+50),node["reaction"],(0,0,0),font=fnt,anchor="mm") 
     
     
    legends = [mol[1] for mol in node["mols"]]
    mols = [MolFromSmiles(mol[0]) for mol in node["mols"]]
    if len(mols)>0:
        nr=math.ceil(math.sqrt(len(mols)))
        w=(NODE_WIDTH-6)/nr
        img= Draw.MolsToGridImage(mols,subImgSize=(int(w),int(w)), molsPerRow=nr, legends=legends)
        im.paste(img, (int(x)+3, int(y)+3+100))


def calculate_width(node):
    W=0
    if node["children"]:
        for child in node["children"]:
            

            W+=calculate_width(child)
        if W==0:
            return NODE_WIDTH+X_OFFSET
        return W 
    else:
        return NODE_WIDTH+X_OFFSET

def draw_node_children(draw,im,node,x,y):
   
    y+=NODE_HEIGHT+Y_OFFSET
    drawables=[]
    for i,child in enumerate(node["children"]):
       
        drawables.append(i)
    is_solved=node["is_solved"]
    is_best = node["is_best"]
    if node["children"]:
        for i,child in enumerate(node["children"]):
          
            w=calculate_width(child)
            
      
            sol=False
            sol,isb=draw_node_children(draw,im,child,x,y)
            if sol:
                is_solved=True
            if isb:
                is_best=True
            draw_node(draw,im,child,x+w/2,y,sol,isb)
            if i!=drawables[0]:
                
                draw.line([(x+w/2+NODE_WIDTH/2,y-Y_OFFSET/2),(x+NODE_WIDTH/2,y-Y_OFFSET/2)],fill="black",width=3)
                
               
            if i!=drawables[-1]:
                draw.line([(x+w/2+NODE_WIDTH/2,y-Y_OFFSET/2),(x+w+NODE_WIDTH/2,y-Y_OFFSET/2)],fill="black",width=3)
                
              
            if child["children"]:
                draw.line([(x+w/2+NODE_WIDTH/2,y+NODE_HEIGHT),(x+w/2+NODE_WIDTH/2,y+NODE_HEIGHT+Y_OFFSET/2)],fill="black",width=3)
                
                
            draw.line([(x+w/2+NODE_WIDTH/2,y),(x+w/2+NODE_WIDTH/2,y-Y_OFFSET/2)],fill="black",width=3)
            
            
            x+=w
    return is_solved,is_best
def calculate_depth(root,d):
    global MAX_DEPTH
    if d>MAX_DEPTH:
        MAX_DEPTH=d
    for children in root["children"]:
        calculate_depth(children,d+1)
    
def draw_tree(root,path):
    w=calculate_width(root)+NODE_WIDTH
    calculate_depth(root,0)
    h=MAX_DEPTH+1
    im = Image.new('RGB', (w, (NODE_HEIGHT+Y_OFFSET)*h), (255, 255, 255)) 
    draw = ImageDraw.Draw(im) 
    is_solved,is_best=draw_node_children(draw,im,root,X,Y)

    draw_node(draw,im,root,X+w/2,Y,is_solved,is_best)
    if root["children"]:
        
        draw.line([(X+w/2+NODE_WIDTH/2,Y+NODE_HEIGHT),(X+w/2+NODE_WIDTH/2,Y+NODE_HEIGHT+Y_OFFSET/2)],fill="black",width=3)
        
    #im.save(path)
    return im