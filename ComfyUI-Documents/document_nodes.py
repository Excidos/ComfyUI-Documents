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

NODE_CLASS_MAPPINGS = {
    "DocumentLoader": DocumentLoaderNode,
    "PDFToImage": PDFToImageNode,
    "PDFPageSplitter": PDFPageSplitterNode,
    "ImageSelector": ImageSelectorNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DocumentLoader": "Document Loader",
    "PDFToImage": "PDF to Image (Multi-Page)",
    "PDFPageSplitter": "PDF Page Splitter",
    "ImageSelector": "Image Selector"
}