import os
import json
import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell
import ast

def create_workflow_notebook():
    """Create a consolidated notebook following the complete workflow"""
    
    # Create new notebook
    merged_nb = new_notebook()
    
    # Add comprehensive title and workflow explanation
    merged_nb.cells.append(new_markdown_cell("""# 🌊 Flood Control Semantic Analysis - Complete Pipeline

This notebook consolidates the entire data processing and analysis workflow for flood control semantic analysis:

## 📋 Workflow Structure

1. **🔧 Text Preprocessing** - Core utilities for text cleaning and normalization
2. **🕷️ Data Scraping** - Collect data from social media platforms (Instagram, Reddit, TikTok, Facebook)
3. **🧹 Data Cleaning** - Clean and prepare scraped data for analysis
4. **🎯 Topic Modelling** - Identify themes using BERTopic and LDA
5. **😊 Sentiment Analysis** - Analyze emotional content and opinions

---
"""))
    
    base_path = "/Users/lestat/Documents/Projects/Data Mining/flood-control-semantic-analysis"
    
    # Define the exact workflow order based on your codebase
    workflow_sections = [
        {
            "title": "🔧 1. Text Preprocessing",
            "description": "Core text preprocessing utilities used throughout the pipeline",
            "files": [
                "text_preprocessor.py"
            ]
        },
        {
            "title": "🕷️ 2. Data Scraping",
            "description": "Scripts to collect data from various social media platforms",
            "files": [
                "instagram-scraper/scraper.py",
                "reddit-scraper/scraper.py", 
                "tiktok-scraper/scraper.py",
                "facebook-scraper/scrape_fb.py"
            ]
        },
        {
            "title": "🧹 3. Data Cleaning",
            "description": "Clean and prepare scraped data for analysis",
            "files": [
                "instagram-scraper/cleaner.ipynb",
                "reddit-scraper/cleaner.ipynb"
            ]
        },
        {
            "title": "🎯 4. Topic Modelling",
            "description": "Identify themes and topics in the cleaned data",
            "files": [
                "topic-modelling/BERTopic/BERT_v2.ipynb",
                "topic-modelling/latent-dirichlet-allocation/Latent_Dirichlet_Allocation.ipynb",
                "topic-modelling/latent-semantic-analysis/latent-semantic-analysis-model.ipynb"
            ]
        },
        {
            "title": "😊 5. Sentiment Analysis", 
            "description": "Analyze emotional content and sentiment of the text data",
            "files": [
                "sentiment-analysis/sentiment-analysis.ipynb",
                "sentiment-analysis/aaron-sentiment.ipynb",
                "sentiment-analysis/tuned-sentiment-analysis.ipynb",
                "sentiment-analysis/multilingual-model-sentiment-analysis.ipynb"
            ]
        }
    ]
    
    processed_files = []
    
    # Process each workflow section
    for section in workflow_sections:
        # Add major section header with emoji and clear formatting
        merged_nb.cells.append(new_markdown_cell(f"""
# {section['title']}

{section['description']}

---
"""))
        
        section_has_files = False
        
        for file_path in section['files']:
            full_path = os.path.join(base_path, file_path)
            
            if os.path.exists(full_path):
                section_has_files = True
                processed_files.append(file_path)
                
                # Create clear subsection headers
                file_name = os.path.basename(file_path).replace('.py', '').replace('.ipynb', '')
                platform = file_path.split('/')[0] if '/' in file_path else 'Core'
                
                # Add subsection with better formatting
                merged_nb.cells.append(new_markdown_cell(f"""
## 📁 {platform.replace('-', ' ').title()} - {file_name.replace('_', ' ').replace('-', ' ').title()}

**Source File:** `{file_path}`

"""))
                
                if file_path.endswith('.py'):
                    merge_python_file(merged_nb, full_path, file_path)
                elif file_path.endswith('.ipynb'):
                    merge_notebook_file(merged_nb, full_path, file_path)
                
                # Add clear separator
                merged_nb.cells.append(new_markdown_cell("\n---\n"))
        
        if not section_has_files:
            merged_nb.cells.append(new_markdown_cell("*⚠️ No files found for this section.*\n\n---\n"))
    
    # Add footer with summary
    merged_nb.cells.append(new_markdown_cell("""
---

# 🎉 Workflow Complete!

This consolidated notebook contains the complete flood control semantic analysis pipeline. 

## 📊 Usage Instructions:

1. **Run preprocessing** to prepare text utilities
2. **Execute scrapers** to collect data from social platforms
3. **Apply cleaners** to prepare data for analysis
4. **Perform topic modeling** to identify themes
5. **Conduct sentiment analysis** to understand opinions

## 📈 Expected Outputs:

- Cleaned comment datasets
- Topic models and themes
- Sentiment classifications
- Analysis visualizations

---
"""))
    
    # Save the consolidated notebook
    output_path = os.path.join(base_path, "CONSOLIDATED_WORKFLOW.ipynb")
    with open(output_path, 'w', encoding='utf-8') as f:
        nbformat.write(merged_nb, f)
    
    print(f"✅ Consolidated workflow notebook saved to: {output_path}")
    return output_path

def merge_python_file(notebook, file_path, rel_path):
    """Add Python file content with proper formatting and context"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add purpose description based on file type
        if 'text_preprocessor' in rel_path:
            notebook.cells.append(new_markdown_cell("""
### 🎯 Purpose
Core text preprocessing utilities including:
- Text normalization and cleaning
- Noise removal and standardization  
- Comment extraction and validation
- Multi-platform text preparation

### 🔧 Key Functions
"""))
        elif 'scraper' in rel_path:
            platform = rel_path.split('/')[0].replace('-scraper', '').title()
            notebook.cells.append(new_markdown_cell(f"""
### 🎯 Purpose
{platform} data collection script for gathering flood control related comments and posts.

### 🔧 Key Features
"""))
        
        # Better file organization - preserve original structure but add clear sections
        if len(content.split('\n')) > 30:  # For larger files
            try:
                # Parse and organize code sections
                tree = ast.parse(content)
                lines = content.split('\n')
                
                # Extract imports
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        line_num = node.lineno - 1
                        if line_num < len(lines):
                            imports.append(lines[line_num])
                
                if imports:
                    notebook.cells.append(new_markdown_cell("#### 📦 Required Imports"))
                    notebook.cells.append(new_code_cell('\n'.join(sorted(set(imports)))))
                
                # Extract classes and functions with better organization
                classes_and_functions = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.col_offset == 0:
                        start_line = node.lineno - 1  
                        end_line = getattr(node, 'end_lineno', len(lines)) or len(lines)
                        content_block = '\n'.join(lines[start_line:end_line])
                        classes_and_functions.append(('class', node.name, content_block))
                    elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                        start_line = node.lineno - 1
                        end_line = getattr(node, 'end_lineno', len(lines)) or len(lines)
                        content_block = '\n'.join(lines[start_line:end_line])
                        classes_and_functions.append(('function', node.name, content_block))
                
                # Add classes first, then functions
                for item_type, name, content_block in classes_and_functions:
                    if item_type == 'class':
                        notebook.cells.append(new_markdown_cell(f"#### 🏗️ Class: `{name}`"))
                    else:
                        notebook.cells.append(new_markdown_cell(f"#### ⚙️ Function: `{name}`"))
                    notebook.cells.append(new_code_cell(content_block))
                
            except Exception as e:
                # If parsing fails, add entire file
                notebook.cells.append(new_markdown_cell("#### 📄 Complete File Content"))
                notebook.cells.append(new_code_cell(content))
        else:
            # For smaller files, add as single block
            notebook.cells.append(new_markdown_cell("#### 📄 Complete Code"))
            notebook.cells.append(new_code_cell(content))
            
    except Exception as e:
        notebook.cells.append(new_markdown_cell(f"❌ **Error reading {file_path}:** {str(e)}"))

def merge_notebook_file(notebook, file_path, rel_path):
    """Add notebook content with proper context and formatting"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_nb = nbformat.read(f, as_version=4)
        
        # Add context description
        if 'cleaner' in rel_path:
            platform = rel_path.split('/')[0].replace('-scraper', '').title() 
            notebook.cells.append(new_markdown_cell(f"""
### 🎯 Purpose
Clean and prepare {platform} scraped data including:
- Remove duplicates and spam
- Filter out low-quality comments
- Normalize text content
- Prepare data for analysis

### 📊 Cleaning Process
"""))
        elif 'sentiment' in rel_path:
            notebook.cells.append(new_markdown_cell("""
### 🎯 Purpose
Perform sentiment analysis on cleaned comments to determine:
- Positive/negative/neutral sentiment
- Emotional intensity
- Opinion classification
- Sentiment trends

### 📈 Analysis Steps
"""))
        elif 'topic' in rel_path or 'BERT' in rel_path or 'LDA' in rel_path:
            model_type = "BERTopic" if 'BERT' in rel_path else "LDA" if 'LDA' in rel_path else "LSA" if 'LSA' in rel_path or 'latent-semantic' in rel_path else "Topic Modeling"
            notebook.cells.append(new_markdown_cell(f"""
### 🎯 Purpose
Identify topics and themes using {model_type}:
- Extract meaningful topics from text
- Cluster similar comments
- Analyze thematic patterns
- Generate topic insights

### 🔍 Modeling Process
"""))
        
        # Add cells from source notebook with clean formatting
        cell_count = 0
        for cell in source_nb.cells:
            if cell.cell_type == 'code' and cell.source.strip():
                cell_count += 1
                # Clean up metadata
                clean_cell = cell.copy()
                clean_cell.metadata = {}
                notebook.cells.append(clean_cell)
            elif cell.cell_type == 'markdown' and cell.source.strip():
                # Clean up metadata for markdown cells too
                clean_cell = cell.copy() 
                clean_cell.metadata = {}
                notebook.cells.append(clean_cell)
        
        notebook.cells.append(new_markdown_cell(f"*📝 Added {cell_count} code cells from this notebook*"))
                
    except Exception as e:
        notebook.cells.append(new_markdown_cell(f"❌ **Error reading {file_path}:** {str(e)}"))

if __name__ == "__main__":
    print("� Creating consolidated workflow notebook...")
    print("📋 Following workflow order:")
    print("   1. 🔧 Text Preprocessing")
    print("   2. 🕷️ Data Scraping") 
    print("   3. 🧹 Data Cleaning")
    print("   4. 🎯 Topic Modelling")
    print("   5. 😊 Sentiment Analysis")
    print()
    
    # Exclude consolidator files from being included
    print("🚫 Excluding consolidator files from output")
    
    output_file = create_workflow_notebook()
    
    print(f"\n🎉 Consolidated notebook created successfully!")
    print(f"📁 Output: {output_file}")
    print("\n💡 This notebook contains the complete workflow pipeline.")
    print("   ✅ Proper formatting and organization")
    print("   ✅ Clear section headers and descriptions") 
    print("   ✅ Sequential execution capability")
    print("   ✅ Excludes consolidator scripts")
    print("\n🚀 Ready to execute the complete flood control analysis pipeline!")