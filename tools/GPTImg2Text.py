import requests
from pdf2img import image_extractor
import os
from PdfToText import PdfToText
import sys
import json

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
    interp = json.loads(text_extractor.extract_text())

    #Get the Images
    for pg_num in image_extractor(path,pdf_file):
        
        imgs_interpretation = []
        params = {}
        #Iterate through the path directory for all the generated images
        for imgs in os.listdir(path):
            
            params["image_path"] = os.path.abspath(os.path.join(path,imgs))
            params["prompt"] = prompt
            # params = json.dumps(params)
            print(params)
            #Get the Interpretations for the image
            img_intepretation = requests.post(url = "http://0.0.0.0:8000/action/",
                                json = params).json()
            
            # print(img_intepretation)

            # if img_intepreation["status"] == "Success":
            imgs_interpretation.append(img_intepretation['result'])

            #Delete the image
            os.unlink(os.path.join(path,imgs))
        
        #Add explanations to Interpretation Dictionary
        # print(interp)
        interp[f"Slide {pg_num}"]["Image Explantion"] = imgs_interpretation

    #Return Dictionary Containing Slide Text and Explanations
    return interp


if __name__ == "__main__":
    FILE = sys.argv[1]

    interpretations = GPT_output(FILE)
        
    print(json.dump(interpretations))


        


    
    

