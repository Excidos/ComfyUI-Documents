# ComfyUI-Documents

## 📄 Description

ComfyUI-Documents is a powerful extension for the ComfyUI application, designed to enhance your workflow with advanced document processing capabilities. This module seamlessly integrates document handling, parsing, and conversion features directly into your ComfyUI projects.

## ✨ Key Features

- **Document Loader Node**: Easily browse, select, and parse documents from your input directory.
  - Supports multiple file formats including PDF, TXT, DOC, and DOCX.
  - Extracts text content, images, and metadata from documents.

- **PDF to Image Node**: Convert PDF pages into high-quality image tensors.
  - Flexible page range selection for partial document processing.
  - Adjustable DPI settings for output image quality control.

- **PDF Page Splitter Node**: Select specific pages from a PDF document.
  - Choose individual pages or ranges of pages.
  - Output selected pages as separate image tensors.

- **Image Selector Node**: Pick specific images from a batch of images.
  - Select one or multiple images by index.
  - Useful for further processing of specific pages from PDF conversions.

- **Intuitive File Upload**: Drag-and-drop functionality for quick file imports.

- **Seamless ComfyUI Integration**: Custom nodes appear directly in your ComfyUI workflow, allowing for easy incorporation into existing projects.

## 🛠️ Installation

1. Navigate to your ComfyUI custom nodes directory:
   ```
   cd ComfyUI/custom_nodes/
   ```

2. Clone this repository:
   ```
   git clone https://github.com/your-username/ComfyUI-Documents.git
   ```

3. Install the required dependencies:
   ```
   pip install -r ComfyUI-Documents/requirements.txt
   ```

## 🚀 Usage

### Document Loader Node

1. Add the "Document Loader" node to your ComfyUI workflow.
2. Use the dropdown to select a document from your input directory, or use the "Choose file to upload" button to add a new document.
3. Connect the output to other nodes in your workflow to process the extracted text, images, or metadata.

![Document Loader Node](https://github.com/IndrasMirror/ComfyUI-Documents/assets/111665831/cb9c0ab8-976f-4462-856f-17731eb3e852)

### PDF to Image Node

1. Add the "PDF to Image" node to your ComfyUI workflow.
2. Select a PDF file using the dropdown or file upload button.
3. Set the desired page range and DPI.
4. The node will output image tensors that can be used with other ComfyUI image processing nodes.

![PDF to Image Node](https://github.com/IndrasMirror/ComfyUI-Documents/assets/111665831/34cb7333-09c3-4086-845e-bc4ca133f9ea)

### PDF Page Splitter Node

1. Add the "PDF Page Splitter" node to your workflow.
2. Select a PDF file using the dropdown.
3. Enter the desired page numbers (e.g., "1,3,5" or "1-5,7,9-11").
4. Set the DPI for the output images.
5. The node will output the selected pages as separate image tensors.

### Image Selector Node

1. Connect the output of a PDF to Image or PDF Page Splitter node to the Image Selector node.
2. Enter the indexes of the images you want to select (e.g., "0" for the first image, or "0,2,4" for the first, third, and fifth images).
3. The node will output only the selected images for further processing.

## 📋 Supported File Types

- PDF (.pdf)
- Plain Text (.txt)
- Microsoft Word (.doc, .docx)

## 🤝 Contributing

Contributions to ComfyUI-Documents are welcome! Please feel free to submit a Pull Request.

## 🙏 Acknowledgements

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) for the amazing base project.
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) for robust PDF processing capabilities.
- [python-docx](https://github.com/python-openxml/python-docx) for handling Microsoft Word documents.

---

For more information and updates, please visit the [ComfyUI-Documents GitHub repository](https://github.com/your-username/ComfyUI-Documents).
