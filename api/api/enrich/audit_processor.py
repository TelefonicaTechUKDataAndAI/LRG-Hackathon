import os
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader


class AuditProcessor:
    audit_text = None

    @classmethod
    def extract_audit_text(cls, input_path: str, file_ext: str) -> None:
        """
        Extracts text from a Word document and stores it in the class attribute `audit_text`.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"The file at {input_path} does not exist.")

        try:
            if file_ext == 'docx':
                document = Docx2txtLoader(input_path).load()
                cls.audit_text = document[0].page_content if document else ""
            elif file_ext == 'pdf':
                pdf_loader = PyPDFLoader(input_path)
                document = pdf_loader.load()
                cls.audit_text = " ".join([page.page_content for page in document]) if document else ""
        except Exception as e:
            raise ValueError(f"Failed to extract text from the document: {e}")
        
        print(cls.audit_text)

    @classmethod
    def get_audit_text(cls) -> str:
        """
        Returns the extracted text stored in the class attribute `audit_text`.
        """
        if cls.audit_text is None:
            raise ValueError("No audit text has been extracted yet.")
        return cls.audit_text