import requests
from pdf2img import image_extractor
import os
from PdfToText import PdfToText
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
            
            params["image_path"] = os.path.join(path,imgs)
            
            print(params)
            #Get the Interpretations for the image
            img_intepreation = requests.post("http://0.0.0.0:8000/action/",
                                json = params)
            
            print(img_intepreation)
            if img_intepreation["status"] == "Success":
                imgs_interpretation.append(img_intepreation["result"])

            #Delete the image
            os.unlink(os.path.join(path,imgs))
        
        #Add explanations to Interpretation Dictionary
        interp[f"Slide {pg_num}"]["Image Explantion"] = imgs_interpretation

    #Return Dictionary Containing Slide Text and Explanations
    return interp


if __name__ == "__main__":
    FILE = sys.argv[1]

    interpretations = GPT_output(FILE)
        
    print(interpretations)


        


    
    

