import os
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader

class DocumentProcessor:

    def pre_process_text(text: str) -> str:
        """
        Pre-processes the text by removing extra spaces and newlines.
        """
        return " ".join(text.split())

    @classmethod
    def extract_document_text(cls, input_path: str, file_ext: str) -> None:
        """
        Extracts text from a Word document and stores it in the class attribute `audit_text`.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"The file at {input_path} does not exist.")

        uploaded_file = {}
        try:
            if file_ext == 'docx':
                document = Docx2txtLoader(input_path).load()
                uploaded_file["filename"] = os.path.basename(input_path)
                uploaded_file["text"] = DocumentProcessor.pre_process_text(document[0].page_content if document else "")
            
            elif file_ext == 'pdf':
                pdf_loader = PyPDFLoader(input_path)
                document = pdf_loader.load()
                uploaded_file["filename"] = os.path.basename(input_path)
                uploaded_file["text"] = DocumentProcessor.pre_process_text(" ".join([page.page_content for page in document]) if document else "")
        
        except Exception as e:
            raise ValueError(f"Failed to extract text from the document: {e}")
        
        return uploaded_file