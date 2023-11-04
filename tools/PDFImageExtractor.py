import fitz
import os
import requests

class PDFImageExtractor:
    def __init__(self, pdf_path, save_dir="."):
        self.pdf_path = pdf_path
        self.save_dir = save_dir
        self.image_data = {}
        
    def get_image_description(self, image_path):
        # Modify the URL as needed for your service
        url = "http://0.0.0.0:8000/action/"
        data = {
            "image_url": image_path, # Assuming the service accepts local paths; if not, you'll need to upload the image or provide a publicly accessible URL
            "prompt": "Describe this image precisely."
        }

        response = requests.post(url, json=data, verify=False)
        return response.json().get('description', 'No description available') # Adjust based on the response structure of your service

    def extract_images(self):
        # Ensure the save directory exists
        os.makedirs(self.save_dir, exist_ok=True)
        
        doc = fitz.open(self.pdf_path)
        
        for idx in range(len(doc)):
            img_list = doc.get_page_images(idx)
            
            if img_list:
                page_images = {}
                for img_idx, img in enumerate(img_list, start=1):
                    data = doc.extract_image(img[0])
                    img_bytes = data["image"]
                    img_ext = data["ext"]

                    # Determine the save path
                    image_path = os.path.join(self.save_dir, f"img{img_idx}_{idx}.{img_ext}")

                    # Save the image and get its description
                    with open(image_path, 'wb') as img_file:
                        img_file.write(img_bytes)
                    
                    description = self.get_image_description(image_path)
                    page_images[image_path] = description
                    
                self.image_data[idx+1] = page_images
                    
        return self.image_data
        
if __name__ == "__main__":
    # Example Usage:
    extractor = PDFImageExtractor("test.pdf", save_dir="./images")
    image_data = extractor.extract_images()
    for page, images in image_data.items():
        print(f"Page {page}:")
        for path, description in images.items():
            print(f"  - {path}: {description}")
