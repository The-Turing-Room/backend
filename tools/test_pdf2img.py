import os
from PDFImageExtractor import PDFImageExtractor

def test_pdf_image_extractor():
    # Path to your test PDF
    pdf_path = "test.pdf"

    # Create a directory to save extracted images
    save_directory = "./extracted_images"
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Instantiate the extractor and extract images
    extractor = PDFImageExtractor(pdf_path, save_dir=save_directory)
    image_data = extractor.extract_images()

    print(image_data)

if __name__ == "__main__":
    test_pdf_image_extractor()
