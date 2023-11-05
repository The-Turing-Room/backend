import PyPDF2
import json

class PdfToText:

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def extract_text(self):
        """
        Extract text from the provided PDF file.
        
        :return: Extracted text in JSON format.
        """
        slides_data = {}

        with open(self.pdf_path, 'rb') as file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)

            # Get the number of pages using the recommended method
            num_pages = len(pdf_reader.pages)

            # Loop through all the pages and extract text
            for page_num in range(num_pages):
                # Use the updated method to get the page
                page = pdf_reader.pages[page_num]
                text = page.extract_text().strip()  # Removing any leading or trailing white spaces
                
                # Assuming slide numbers start from 1
                slide_number = page_num + 1
                
                # Only add slides with text to the output
                if text:
                    slides_data[f"Slide {slide_number}"] = {"Text Input":text}

        return json.dumps(slides_data, indent=4)

# The example usage is likely causing the issue when you're trying to import the class elsewhere.
# It's good practice to use the following if __name__ == "__main__": guard to prevent code from running when the module is imported.
if __name__ == "__main__":
    pdf_converter = PdfToText("sample.pdf")
    print(pdf_converter.extract_text())
