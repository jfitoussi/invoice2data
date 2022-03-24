# -*- coding: utf-8 -*-
def to_text(path, bucket_name=None, language="fr", **kwargs):
    """Sends PDF files to Google DocumentAi for OCR.

    Before using invoice2data, make sure you have the auth json path set as
    env var GOOGLE_APPLICATION_CREDENTIALS

    Parameters
    ----------
    path : str
        path of electronic invoice in JPG or PNG format
    bucket_name : str
        name of bucket to use for file storage and results cache.

    Returns
    -------
    extracted_str : str
        returns extracted text from image in JPG or PNG format

    """

    """OCR with PDF/TIFF as source files on GCS"""
    from google.cloud import documentai_v1 as documentai

    # You must set the api_endpoint if you use a location other than 'us', e.g.:
    opts = {"api_endpoint": "eu-documentai.googleapis.com"}

    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    # The full resource name of the processor, e.g.:
    # projects/project-id/locations/location/processor/processor-id
    # You must create new processors in the Cloud Console first
    project_id = kwargs.get("project_id", None)
    processor = kwargs.get("processor", None)
    name = f"projects/{project_id}/locations/eu/processors/{processor}"

    # Read the file into memory
    with open(path, "rb") as image:
        image_content = image.read()

    document = {"content": image_content, "mime_type": "application/pdf"}

    # Configure the process request
    request = {"name": name, "raw_document": document}

    result = client.process_document(request=request)
    document = result.document

    document_pages = document.pages

    # For a full list of Document object attributes, please reference this page: https://googleapis.dev/python/documentai/latest/_modules/google/cloud/documentai_v1beta3/types/document.html#Document

    # Read the text recognition output from the processor
    paragraph_text = ""
    for page in document_pages:
        paragraphs = page.paragraphs
        for paragraph in paragraphs:
            paragraph_text += get_text(paragraph.layout, document)

    return paragraph_text.encode('utf-8')


def get_text(doc_element: dict, document: dict):
    """
    Document AI identifies form fields by their offsets
    in document text. This function converts offsets
    to text snippets.
    """
    response = ""
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    for segment in doc_element.text_anchor.text_segments:
        start_index = (
            int(segment.start_index)
            if segment in doc_element.text_anchor.text_segments
            else 0
        )
        end_index = int(segment.end_index)
        response += document.text[start_index:end_index]
    return response
