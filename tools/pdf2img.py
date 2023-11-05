import fitz
import os
from PIL import Image



def image_extractor(save_path:str, file_name):
    '''
    Function to extract all the images from a given PDF
    
    args:
    save_path: Path where the images will be stored at
    file_name: PDF file from which the images will be extracted
    '''
    file = fitz.open(file_name)

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
                with open(os.path.join(save_path,f"img{img_idx}_{idx}.{img_ext}"),'wb') as img_file:
                    img_file.write(img_bytes)

        yield idx + 1

            