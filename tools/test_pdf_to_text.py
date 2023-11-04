import json
from PdfToText import PdfToText  # Ensure this import matches the location of your class

def test_pdf_to_text_extraction():
    # Convert the test.pdf file to JSON format
    converter = PdfToText("test.pdf")
    extracted_data = converter.extract_text()
    
    # Load the extracted data into a Python dictionary
    data_dict = json.loads(extracted_data)
    print(data_dict)
    
    # Simple assertions (you can add more detailed ones based on your needs)
    assert isinstance(data_dict, dict), "The extracted data should be a dictionary."
    
    # If you know some content that should be present in the test.pdf, you can check for it
    # For example, if you know Slide 1 should contain the word "Introduction"
    # assert "Introduction" in data_dict.get("Slide 1", ""), "Slide 1 should contain the word 'Introduction'."

    print("All tests passed!")

test_pdf_to_text_extraction()
