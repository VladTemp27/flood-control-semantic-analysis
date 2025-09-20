import os
import json
import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell
import ast

def create_merged_notebook():
    """Create a single notebook merging all Python files and notebooks"""
    
    # Create new notebook
    merged_nb = new_notebook()
    
    # Add title
    merged_nb.cells.append(new_markdown_cell("# Flood Control Semantic Analysis - Merged Codebase\n\nThis notebook contains all Python scripts and notebooks from the project merged into a single file."))
    
    base_path = "/Users/lestat/Documents/Projects/Data Mining/flood-control-semantic-analysis"
    
    # Updated processing order including all scrapers
    processing_order = [
        # Core utilities first
        "text_preprocessor.py",
        
        # Instagram scraper
        "instagram-scraper/instagram_scraper.py",
        "instagram-scraper/cleaner.ipynb",
        
        # Reddit scraper  
        "reddit-scraper/reddit_scraper.py",
        "reddit-scraper/cleaner.ipynb",
        
        # News scraper
        "news-scraper/news_scraper.py",
        "news-scraper/cleaner.ipynb",
        
        # Twitter scraper (if exists)
        "twitter-scraper/twitter_scraper.py",
        "twitter-scraper/cleaner.ipynb",
        
        # Any other scraper files
        "scrapers/instagram_scraper.py",
        "scrapers/reddit_scraper.py", 
        "scrapers/news_scraper.py",
        "scrapers/twitter_scraper.py",
        
        # Sentiment analysis
        "sentiment-analysis/sentiment-analysis.ipynb",
        "sentiment-analysis/aaron-sentiment.ipynb",
        "sentiment-analysis/tuned-sentiment-analysis.ipynb",
        "sentiment-analysis/multilingual-model-sentiment-analysis.ipynb",
        
        # Topic modeling
        "topic-modelling/BERTopic/BERT_v2.ipynb",
        
        # Any main analysis files
        "main.py",
        "analysis.py",
        "data_processing.py"
    ]
    
    # Process files in order
    for file_path in processing_order:
        full_path = os.path.join(base_path, file_path)
        
        if os.path.exists(full_path):
            # Add section header
            section_name = file_path.replace("/", " - ").replace(".py", "").replace(".ipynb", "")
            merged_nb.cells.append(new_markdown_cell(f"## {section_name}\n\nSource: `{file_path}`"))
            
            if file_path.endswith('.py'):
                merge_python_file(merged_nb, full_path)
            elif file_path.endswith('.ipynb'):
                merge_notebook_file(merged_nb, full_path)
    
    # Scan for any remaining scraper files we might have missed
    scan_scraper_files(merged_nb, base_path, processing_order)
    
    # Also scan for any other remaining files
    scan_remaining_files(merged_nb, base_path, processing_order)
    
    # Save the merged notebook
    output_path = os.path.join(base_path, "merged_codebase.ipynb")
    with open(output_path, 'w', encoding='utf-8') as f:
        nbformat.write(merged_nb, f)
    
    print(f"✅ Merged notebook saved to: {output_path}")
    return output_path

def scan_scraper_files(notebook, base_path, processed_files):
    """Specifically scan for scraper files that might have been missed"""
    notebook.cells.append(new_markdown_cell("## Additional Scraper Files\n\nOther scraper files found in the project:"))
    
    scraper_dirs = ['instagram-scraper', 'reddit-scraper', 'news-scraper', 'twitter-scraper', 'scrapers']
    found_additional = False
    
    for scraper_dir in scraper_dirs:
        scraper_path = os.path.join(base_path, scraper_dir)
        if os.path.exists(scraper_path):
            for file in os.listdir(scraper_path):
                if file.endswith(('.py', '.ipynb')):
                    rel_path = os.path.join(scraper_dir, file)
                    
                    # Skip if already processed
                    if rel_path in processed_files:
                        continue
                    
                    found_additional = True
                    full_path = os.path.join(scraper_path, file)
                    
                    # Add section for this file
                    notebook.cells.append(new_markdown_cell(f"### {rel_path}"))
                    
                    if file.endswith('.py'):
                        merge_python_file(notebook, full_path)
                    elif file.endswith('.ipynb'):
                        merge_notebook_file(notebook, full_path)
    
    if not found_additional:
        notebook.cells.append(new_markdown_cell("*No additional scraper files found.*"))

def merge_python_file(notebook, file_path):
    """Add Python file content to notebook"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # For scraper files, add the entire content as one cell for better readability
        if 'scraper' in file_path.lower():
            notebook.cells.append(new_code_cell(content))
            return
        
        # Split into logical sections based on functions/classes for other files
        try:
            tree = ast.parse(content)
            sections = []
            current_section = []
            lines = content.split('\n')
            
            # Collect imports first
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append(lines[node.lineno - 1])
            
            if imports:
                sections.append('\n'.join(imports))
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    # Get function/class content
                    start_line = node.lineno - 1
                    end_line = getattr(node, 'end_lineno', len(lines)) or len(lines)
                    func_content = lines[start_line:end_line]
                    sections.append('\n'.join(func_content))
            
            # Add each section as a separate cell
            for section in sections:
                if section.strip():
                    notebook.cells.append(new_code_cell(section))
                    
        except:
            # If parsing fails, add entire file as one cell
            notebook.cells.append(new_code_cell(content))
            
    except Exception as e:
        notebook.cells.append(new_markdown_cell(f"**Error reading {file_path}:** {str(e)}"))

def merge_notebook_file(notebook, file_path):
    """Add notebook content to main notebook"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_nb = nbformat.read(f, as_version=4)
        
        # Add all cells from source notebook
        for cell in source_nb.cells:
            # Clean up cell metadata to avoid conflicts
            clean_cell = cell.copy()
            clean_cell.metadata = {}
            
            # Add source info for code cells
            if cell.cell_type == 'code' and cell.source.strip():
                notebook.cells.append(clean_cell)
            elif cell.cell_type == 'markdown' and cell.source.strip():
                notebook.cells.append(clean_cell)
                
    except Exception as e:
        notebook.cells.append(new_markdown_cell(f"**Error reading {file_path}:** {str(e)}"))

def scan_remaining_files(notebook, base_path, processed_files):
    """Scan for any remaining Python files not in the processing order"""
    notebook.cells.append(new_markdown_cell("## Other Python Files\n\nAny other Python files found in the project:"))
    
    found_others = False
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(('.py', '.ipynb')):
                rel_path = os.path.relpath(os.path.join(root, file), base_path)
                
                # Skip if already processed
                if rel_path in processed_files:
                    continue
                    
                # Skip common files to ignore
                if any(skip in rel_path for skip in ['__pycache__', '.git', 'venv', 'env', 'merged']):
                    continue
                
                found_others = True
                full_path = os.path.join(root, file)
                
                # Add section for this file
                notebook.cells.append(new_markdown_cell(f"### {rel_path}"))
                
                if file.endswith('.py'):
                    merge_python_file(notebook, full_path)
                elif file.endswith('.ipynb'):
                    merge_notebook_file(notebook, full_path)
    
    if not found_others:
        notebook.cells.append(new_markdown_cell("*No additional Python files found.*"))

# Enhanced simple version that ensures scrapers are included
def create_simple_merged_notebook():
    """Create a simpler merged notebook with all files including scrapers"""
    
    merged_nb = new_notebook()
    merged_nb.cells.append(new_markdown_cell("# Flood Control Semantic Analysis - Complete Codebase\n\n*This includes all scrapers, analysis notebooks, and utility scripts.*"))
    
    base_path = "/Users/lestat/Documents/Projects/Data Mining/flood-control-semantic-analysis"
    
    # Collect files by category
    categories = {
        "Scrapers": [],
        "Analysis Notebooks": [],
        "Utility Scripts": [],
        "Other Files": []
    }
    
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(('.py', '.ipynb')) and 'merged' not in file:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_path)
                
                # Categorize files
                if 'scraper' in rel_path.lower() or 'scraping' in rel_path.lower():
                    categories["Scrapers"].append(full_path)
                elif 'sentiment' in rel_path.lower() or 'topic' in rel_path.lower() or 'analysis' in rel_path.lower():
                    categories["Analysis Notebooks"].append(full_path)
                elif file.endswith('.py'):
                    categories["Utility Scripts"].append(full_path)
                else:
                    categories["Other Files"].append(full_path)
    
    # Add each category
    for category, files in categories.items():
        if files:
            merged_nb.cells.append(new_markdown_cell(f"## {category}"))
            
            for file_path in sorted(files):
                rel_path = os.path.relpath(file_path, base_path)
                merged_nb.cells.append(new_markdown_cell(f"### {rel_path}"))
                
                if file_path.endswith('.py'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        merged_nb.cells.append(new_code_cell(content))
                    except Exception as e:
                        merged_nb.cells.append(new_markdown_cell(f"Error reading {rel_path}: {str(e)}"))
                elif file_path.endswith('.ipynb'):
                    merge_notebook_file(merged_nb, file_path)
    
    # Save
    output_path = os.path.join(base_path, "complete_merged_codebase.ipynb")
    with open(output_path, 'w', encoding='utf-8') as f:
        nbformat.write(merged_nb, f)
    
    print(f"✅ Complete merged notebook saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    # Create both versions
    print("Creating structured merged notebook (including all scrapers)...")
    create_merged_notebook()
    
    print("\nCreating complete merged notebook with categorization...")  
    create_simple_merged_notebook()
    
    print("\n🎉 Both merged notebooks created successfully!")
    print("📁 Files created:")
    print("   - merged_codebase.ipynb (structured)")
    print("   - complete_merged_codebase.ipynb (categorized)")