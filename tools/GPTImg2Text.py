import requests
import PDFImageExtractor
from pdf2img import image_extractor
import os
import PdfToText
import sys

'''
1. Script generates the images in the 'images' folder, 
2. Makes requests to the API, for processing said images
3. Calls the PDFExtractor on current page
4. Combines outputs in a single JSON
5. Returns Said JSON
'''




def GPT_output(pdf_file,
               path:str = "images",
               prompt:str = "Provide a detailed explanation of this image"):
    '''
    args:
    path: Path to where the images will be stored (default: images)
    pdf_file: File from which the data is to be extracted
    '''

    #Dictionary to hold params passed to GPT
    params = {}

    #Extract all the text information
    text_extractor = PdfToText(pdf_file)
    interp = text_extractor.extract_text()

    #Get the Images
    for pg_num in image_extractor(path,pdf_file):
        
        imgs_interpretation = []
        params["prompt"] = prompt
        #Iterate through the path directory for all the generated images
        for imgs in os.listdir(path):
            
            params["image_url"] = os.path.join(path,imgs)
            
            #Get the Interpretations for the image
            img_intepreation = requests.get("https://0.0.0.0:8000/action/",
                                params = params)
            
            if img_intepreation["status"] == "Success":
                imgs_interpretation.append(img_intepreation["result"])

            #Delete the image
            os.unlink(os.path.join(path,imgs))
        
        #Add explanations to Interpretation Dictionary
        interp[f"Slide {pg_num}"]["Image Explantion"] = imgs_interpretation

    #Return Dictionary Containing Slide Text and Explanations
    return interp


if __name__ == "__main__":
    PATH = sys.argv[2]
    FILE = sys.argv[3]

    interpretations = GPT_output(FILE,
                                 PATH)
        
    print(interpretations)


        


    
    

