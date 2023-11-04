import fitz
import os

class PDFImageExtractor:
    def __init__(self, pdf_path, save_dir="."):
        self.pdf_path = pdf_path
        self.save_dir = save_dir
        self.image_data = {}
        
    def extract_images(self):
        doc = fitz.open(self.pdf_path)
        
        for idx in range(len(doc)):
            img_list = doc.get_page_images(idx)
            pg_imgs = []
            if img_list:
                for img_idx, img in enumerate(img_list, start=1):
                    data = doc.extract_image(img[0])
                    img_bytes = data["image"]
                    img_ext = data["ext"]

                    # Determine the save path
                    image_path = os.path.join(self.save_dir, f"img{img_idx}_{idx}.{img_ext}")

                    # Save the image and update the dictionary
                    with open(image_path, 'wb') as img_file:
                        img_file.write(img_bytes)

                    pg_imgs.append(image_path)  
            self.image_data[idx+1] = pg_imgs              
        return self.image_data
        
if __name__ == "__main__":
    # Example Usage:
    extractor = PDFImageExtractor("sample.pdf", save_dir="./images")
    image_data = extractor.extract_images()
