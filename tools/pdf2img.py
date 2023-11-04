import fitz
import sys
from PIL import Image


#Make sure file name is passed
assert len(sys.argv) == 2, "Path to PDF Missing"

FILE = sys.argv[-1]
file = fitz.open(FILE)

for idx in range(len(file)):

    #Retrieve page from doc
    img_list = file.get_page_images(idx)

    if img_list:
        for img_idx, img in enumerate(img_list,start = 1):
            
            #Retreive The XREF of the Img, Bytes, Extension
            data = file.extract_image(img[0])
            img_bytes = data["image"]
            img_ext = data["ext"]

            #Write to drive
            with open(f"img{img_idx}_{idx}.{img_ext}",'wb') as img_file:
                img_file.write(img_bytes)

            