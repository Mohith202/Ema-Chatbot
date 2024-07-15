import os
from langchain_community.document_loaders import PyPDFLoader
import uuid  # For generating unique identifiers


def load_pdfs_from_file(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    return documents

def save_uploaded_file(uploaded_file, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

class DocumentNode:
    def __init__(self, title, page, content, parent=None):
        self.id = str(uuid.uuid4())  # Unique identifier for each node
        self.title = title
        self.page = page
        self.content = content
        self.parent = parent  # Reference to the parent node
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

class MemoryIndex:
    def __init__(self):
        self.index = {}

    def add_to_index(self, node, keywords):
        for keyword in keywords:
            if keyword not in self.index:
                self.index[keyword] = []
            self.index[keyword].append(node)

    def search(self, keyword):
        return self.index.get(keyword, [])

def load_pdfs_from_folder(folder_path):
    root = DocumentNode("Textbook", None, None)  # Root node represents the entire textbook
    index = MemoryIndex()  # Initialize the index
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            chapter_node = DocumentNode(filename, None, None, root)  # Each file represents a chapter
            root.add_child(chapter_node)
            for i, doc in enumerate(docs):
                section_node = DocumentNode(f"Section {i+1}", i + 1, doc.text, chapter_node)
                chapter_node.add_child(section_node)
                # Assuming sections are divided into paragraphs
                paragraphs = doc.text.split('\n\n')  # Simple paragraph splitter
                for j, paragraph in enumerate(paragraphs):
                    paragraph_node = DocumentNode(f"Paragraph {j+1}", None, paragraph, section_node)
                    section_node.add_child(paragraph_node)
                    keywords = extract_keywords(paragraph)  # You need to define or import this function
                    index.add_to_index(paragraph_node, keywords)
    return root, index  # Return the root of the tree and the index

# Example usage
root, index = load_pdfs_from_folder("path_to_pdfs")
results = index.search("specific_keyword")