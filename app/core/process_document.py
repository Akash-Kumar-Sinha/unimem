# External imports
import os, pymupdf, pytesseract
from PIL import Image

# Local imports
from app.core.logger import setup_logger
from app.db.manager import insert_document_chunks
from app.core.utils import make_chunks, get_embeddings
from app.config.config import LOG_LEVEL_DEBUG, APPLICATION_LOG_FILE, GEMINI_API_KEY
from app.core.document_types import DocumentType

# Initialization
logger = setup_logger(__name__, APPLICATION_LOG_FILE, LOG_LEVEL_DEBUG)

# Logic
class ProcessDocument:
    def __init__(self):
        self.PROCESSORS = {
            DocumentType.PDF: self.process_pdf,
            DocumentType.IMAGE: self.process_image,
        }


    def process(self, doc_path: str, doc_type: str, session_id: str) -> None:
        doc_name = os.path.basename(doc_path)
        logger.info(f"Processing provided document [{doc_name}], Type: [{doc_type}], Session ID [{session_id}]")

        try:
            processor = self.PROCESSORS[DocumentType(doc_type)]
        except KeyError:
            raise ValueError(f"Unsupported document type: {doc_type}")

        text = processor(doc_path)

        chunks = make_chunks(
            text=text, size=500, overlap=100
        )  # convert text string to small chunks

        logger.debug(f"Converting text to embeddings for [{doc_name}]")
        embeddings = get_embeddings(data_list=chunks, embedding_type="RETRIEVAL_DOCUMENT")

        try:
            logger.debug(f"Inserting embeddings for [{doc_name}] in DB")
            insert_document_chunks(str(session_id), str(doc_path), chunks, embeddings)
        except Exception as e:
            logger.debug(f"Error while inserting embeddings for [{doc_name}] in DB: {e}")

    def process_pdf(self, doc_path: str) -> str:
        if not os.path.exists(doc_path):
            msg = f"Provided document not found {doc_path}"
            logger.error(msg)
            raise FileNotFoundError(msg)
        try:
            doc = pymupdf.open(doc_path)
        except Exception as e:
            logger.error(f"Error in parsing the document [{doc_path}]: {e}")
            raise ValueError(f"Error in parsing the document [{doc_path}]: {e}")
        
        all_text = []
        for page in doc:
            text = (
                page.get_text().encode("utf8").decode()
            )  # keeping non ascii characters intentionally for emojis
            all_text.append(text)
        logger.info(
            f"Number of pages in document [{doc_path}], {len(doc)}"
        )
        all_text = " ".join(all_text)
        return all_text

    def process_image(self, doc_path: str) -> str:
        try:
            img = Image.open(doc_path)
        except Exception as e:
            logger.error(f"Error opening image [{doc_path}]: {e}")
            raise

        text = pytesseract.image_to_string(
            img,
            lang="eng",
            config="--psm 6"
        )

        if not text.strip():
            logger.warning(f"No text detected in image [{doc_path}]")

        return text.strip()
