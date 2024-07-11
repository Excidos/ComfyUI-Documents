import os
import fitz  # PyMuPDF
import torch
from PIL import Image
import numpy as np
import folder_paths
from .utils import strip_path
from docx import Document

class DocumentLoaderNode:
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f)) and f.lower().endswith((".pdf", ".txt", ".doc", ".docx"))]
        return {"required": {"file_path": (sorted(files),)}}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("parsed_text",)
    FUNCTION = "load_document"
    CATEGORY = "document_processing"

    def load_document(self, file_path):
        full_path = folder_paths.get_annotated_filepath(strip_path(file_path))
        _, ext = os.path.splitext(full_path)
        if ext.lower() == '.pdf':
            return (self.parse_pdf(full_path),)
        elif ext.lower() in ['.txt', '.doc', '.docx']:
            return (self.parse_text(full_path),)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def parse_pdf(self, file_path):
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text

    def parse_text(self, file_path):
        _, ext = os.path.splitext(file_path)
        if ext.lower() == '.txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        elif ext.lower() in ['.doc', '.docx']:
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
    
    @classmethod
    def IS_CHANGED(cls, file_path):
        full_path = folder_paths.get_annotated_filepath(strip_path(file_path))
        return full_path

    @classmethod
    def VALIDATE_INPUTS(cls, file_path):
        full_path = folder_paths.get_annotated_filepath(strip_path(file_path))
        return os.path.isfile(full_path)

class PDFToImageNode:
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f)) and f.lower().endswith(".pdf")]
        return {
            "required": {
                "file_path": (sorted(files),),
                "start_page": ("INT", {"default": 1, "min": 1, "max": 10000}),
                "end_page": ("INT", {"default": 1, "min": 1, "max": 10000}),
                "dpi": ("INT", {"default": 300, "min": 72, "max": 600}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "pdf_to_images"
    CATEGORY = "document_processing"
    OUTPUT_IS_LIST = (True,)

    def pdf_to_images(self, file_path, start_page, end_page, dpi):
        full_path = folder_paths.get_annotated_filepath(strip_path(file_path))
        doc = fitz.open(full_path)
        num_pages = len(doc)
        
        start_page = max(1, min(start_page, num_pages))
        end_page = max(start_page, min(end_page, num_pages))
        
        images = []
        for page_num in range(start_page - 1, end_page):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_np = np.array(img).astype(np.float32) / 255.0
            img_tensor = torch.from_numpy(img_np)[None,]
            images.append(img_tensor)
        
        doc.close()
        return (images,)
    
    @classmethod
    def IS_CHANGED(cls, file_path, start_page, end_page, dpi):
        full_path = folder_paths.get_annotated_filepath(strip_path(file_path))
        return full_path

    @classmethod
    def VALIDATE_INPUTS(cls, file_path, start_page, end_page, dpi):
        full_path = folder_paths.get_annotated_filepath(strip_path(file_path))
        return os.path.isfile(full_path)

class PDFPageSplitterNode:
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f)) and f.lower().endswith(".pdf")]
        return {
            "required": {
                "file_path": (sorted(files),),
                "page_numbers": ("STRING", {"default": "1,2,3"}),
                "dpi": ("INT", {"default": 300, "min": 72, "max": 600}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("selected_pages",)
    FUNCTION = "pdf_to_selected_images"
    CATEGORY = "document_processing"
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (True,)

    def pdf_to_selected_images(self, file_path, page_numbers, dpi):
        full_path = folder_paths.get_annotated_filepath(strip_path(file_path))
        doc = fitz.open(full_path)
        num_pages = len(doc)
        
        # Parse page numbers from input string
        try:
            selected_pages = [int(p.strip()) for p in page_numbers.split(',') if p.strip()]
            selected_pages = [p for p in selected_pages if 1 <= p <= num_pages]
        except ValueError:
            raise ValueError("Invalid page numbers. Please provide comma-separated integers.")
        
        images = []
        for page_num in selected_pages:
            page = doc.load_page(page_num - 1)  # PDF pages are 0-indexed
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_np = np.array(img).astype(np.float32) / 255.0
            img_tensor = torch.from_numpy(img_np)[None,]
            images.append(img_tensor)
        
        doc.close()
        return (images,)

    @classmethod
    def IS_CHANGED(cls, file_path, page_numbers, dpi):
        full_path = folder_paths.get_annotated_filepath(strip_path(file_path))
        return full_path

    @classmethod
    def VALIDATE_INPUTS(cls, file_path, page_numbers, dpi):
        full_path = folder_paths.get_annotated_filepath(strip_path(file_path))
        if not os.path.isfile(full_path):
            return False
        try:
            [int(p.strip()) for p in page_numbers.split(',') if p.strip()]
        except ValueError:
            return False
        return True

class ImageSelectorNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "indexes": ("STRING", {"default": "0"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "select_images"
    CATEGORY = "image_processing"
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (True,)

    def select_images(self, images, indexes):
        try:
            index_list = [int(idx.strip()) for idx in indexes.split(',')]
        except ValueError:
            raise ValueError("Invalid indexes. Please provide comma-separated integers.")
        
        selected_images = []
        for idx in index_list:
            if idx < 0 or idx >= len(images):
                raise ValueError(f"Index {idx} is out of range. Available images: {len(images)}")
            selected_images.append(images[idx])
        
        return (selected_images,)

    @classmethod
    def IS_CHANGED(cls, images, indexes):
        return indexes

class TextChunkerNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True}),
                "chunk_size": ("INT", {"default": 1000, "min": 1, "max": 10000}),
                "chunk_method": (["words", "characters"],),
                "respect_word_boundaries": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text_chunks",)
    FUNCTION = "chunk_text"
    CATEGORY = "document_processing"
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (True,)

    def chunk_text(self, text, chunk_size, chunk_method, respect_word_boundaries):
        if not text:
            return (["No text provided"],)

        chunks = []
        if chunk_method == "words":
            words = text.split()
            current_chunk = []
            word_count = 0
            for word in words:
                current_chunk.append(word)
                word_count += 1
                if word_count >= chunk_size:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    word_count = 0
            if current_chunk:
                chunks.append(" ".join(current_chunk))
        else:  # characters
            if respect_word_boundaries:
                words = text.split()
                current_chunk = []
                char_count = 0
                for word in words:
                    if char_count + len(word) > chunk_size and current_chunk:
                        chunks.append(" ".join(current_chunk))
                        current_chunk = []
                        char_count = 0
                    current_chunk.append(word)
                    char_count += len(word) + 1  # +1 for space
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
            else:
                chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

        return (chunks,)

class ChunkRouterNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "chunks": ("STRING", {"forceInput": True}),
                "indices": ("INT", {"forceInput": True}),
                "selected_index": ("INT", {"default": 0, "min": 0, "max": 1000}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("selected_chunk",)
    FUNCTION = "route_chunk"
    CATEGORY = "document_processing"

    def route_chunk(self, chunks, indices, selected_index):
        if selected_index < 0 or selected_index >= len(chunks):
            raise ValueError(f"Selected index {selected_index} is out of range. Available chunks: {len(chunks)}")
        return (chunks[selected_index],)

# Update NODE_CLASS_MAPPINGS and NODE_DISPLAY_NAME_MAPPINGS
NODE_CLASS_MAPPINGS = {
    "DocumentLoader": DocumentLoaderNode,
    "PDFToImage": PDFToImageNode,
    "PDFPageSplitter": PDFPageSplitterNode,
    "ImageSelector": ImageSelectorNode,
    "TextChunker": TextChunkerNode,
    "ChunkRouter": ChunkRouterNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DocumentLoader": "Document Loader",
    "PDFToImage": "PDF to Image (Multi-Page)",
    "PDFPageSplitter": "PDF Page Splitter",
    "ImageSelector": "Image Selector",
    "TextChunker": "Text Chunker",
    "ChunkRouter": "Chunk Router"
}
