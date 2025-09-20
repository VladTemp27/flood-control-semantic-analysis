import pandas as pd
import re
import string
import os
from typing import List, Dict, Tuple
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import warnings
warnings.filterwarnings('ignore')

class TextPreprocessor:
    def __init__(self):
        """Initialize the text preprocessor with necessary NLTK downloads."""
        self.download_nltk_data()
        self.english_stopwords = set(stopwords.words('english'))
        
        # Common Filipino stopwords
        self.filipino_stopwords = {
            'ang', 'ng', 'sa', 'na', 'at', 'ay', 'si', 'ni', 'mga', 'para', 'kung', 'nang', 
            'yan', 'ito', 'din', 'daw', 'raw', 'rin', 'lang', 'lamang', 'man', 'po', 'opo',
            'kasi', 'pero', 'dahil', 'kaya', 'habang', 'kapag', 'saan', 'ano', 'sino', 'bakit',
            'paano', 'kelan', 'nasaan', 'alin', 'ilan', 'gaano', 'sobra', 'masyado', 'talaga',
            'naman', 'pala', 'nga', 'yung', 'yun', 'dun', 'dito', 'diyan', 'doon', 'nung',
            'noong', 'may', 'meron', 'wala', 'walang', 'hindi', 'di', 'huwag', 'wag',
            'ba', 'eh', 'ah', 'oh', 'uy', 'hay', 'sus', 'tsk', 'ano', 'kaya', 'nga'
        }
        
        self.all_stopwords = self.english_stopwords.union(self.filipino_stopwords)
        
    def download_nltk_data(self):
        """Download required NLTK data."""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            print("Downloading NLTK punkt tokenizer...")
            nltk.download('punkt')
            nltk.download('punkt_tab')
            
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            print("Downloading NLTK stopwords...")
            nltk.download('stopwords')
    
    def clean_text(self, text: str) -> str:
        """
        Clean and preprocess text data.
        
        Args:
            text (str): Raw text to be cleaned
            
        Returns:
            str: Cleaned and preprocessed text
        """
        if pd.isna(text) or text == '':
            return ''
        
        # Convert to string if not already
        text = str(text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove HTML entities and tags
        text = re.sub(r'&[a-zA-Z]+;', ' ', text)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'&gt;|&lt;|&amp;', ' ', text)
        
        # Remove hashtags but keep the content
        text = re.sub(r'#(\w+)', r'\1', text)
        
        # Remove mentions
        text = re.sub(r'@\w+', '', text)
        
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', ' ', text)
        
        # Remove excessive punctuation (3 or more consecutive)
        text = re.sub(r'[.]{3,}', '...', text)
        text = re.sub(r'[!]{3,}', '!!!', text)
        text = re.sub(r'[?]{3,}', '???', text)
        
        # Remove emojis and special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:\'"()-]', ' ', text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Tokenize
        try:
            tokens = word_tokenize(text)
        except:
            # Fallback tokenization if NLTK fails
            tokens = text.split()
        
        # Remove stopwords and single characters
        cleaned_tokens = []
        for token in tokens:
            # Skip if token is stopword, single character, or only punctuation
            if (token not in self.all_stopwords and 
                len(token) > 1 and 
                not token.isdigit() and
                not all(char in string.punctuation for char in token)):
                # Remove punctuation from token but keep some context
                cleaned_token = re.sub(r'^[^\w]+|[^\w]+$', '', token)
                if cleaned_token:
                    cleaned_tokens.append(cleaned_token)
        
        # Join tokens back
        cleaned_text = ' '.join(cleaned_tokens)
        
        # Final cleanup
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        return cleaned_text

def read_csv_files() -> List[Tuple[pd.DataFrame, str]]:
    """
    Read all CSV files and return list of (dataframe, source_name) tuples.
    
    Returns:
        List[Tuple[pd.DataFrame, str]]: List of dataframes with their source names
    """
    csv_files = []
    base_path = r'c:\Users\Ven\Documents\Coding\Data Mining\flood-control-semantic-analysis'
    
    # Threads comments
    try:
        df_threads = pd.read_csv(os.path.join(base_path, 'threads_comments.csv'))
        csv_files.append((df_threads, 'Threads'))
        print(f"Loaded Threads: {len(df_threads)} records")
    except Exception as e:
        print(f"Error loading Threads: {e}")
    
    # Instagram comments
    try:
        df_instagram = pd.read_csv(os.path.join(base_path, 'instagram-scraper', 'cleaned_instagram_comments.csv'))
        csv_files.append((df_instagram, 'Instagram'))
        print(f"Loaded Instagram: {len(df_instagram)} records")
    except Exception as e:
        print(f"Error loading Instagram: {e}")
    
    # Reddit comments
    try:
        df_reddit = pd.read_csv(os.path.join(base_path, 'reddit-scraper', 'cleaned_reddit_comments.csv'))
        csv_files.append((df_reddit, 'Reddit'))
        print(f"Loaded Reddit: {len(df_reddit)} records")
    except Exception as e:
        print(f"Error loading Reddit: {e}")
    
    # X (Twitter) comments
    try:
        df_x = pd.read_csv(os.path.join(base_path, 'CleanedXComments.csv'))
        csv_files.append((df_x, 'X'))
        print(f"Loaded X: {len(df_x)} records")
    except Exception as e:
        print(f"Error loading X: {e}")
    
    # TikTok comments (multiple files)
    tiktok_files = ['abscbn-tiktok_comments.csv', 'gma-tiktok_comments.csv', 'news5-tiktok_comments.csv']
    
    for tiktok_file in tiktok_files:
        try:
            df_tiktok = pd.read_csv(os.path.join(base_path, 'tiktok-scraper', tiktok_file))
            source_name = f"TikTok-{tiktok_file.split('-')[0].upper()}"
            csv_files.append((df_tiktok, source_name))
            print(f"Loaded {source_name}: {len(df_tiktok)} records")
        except Exception as e:
            print(f"Error loading {tiktok_file}: {e}")
    
    # Facebook comments (if not empty)
    try:
        df_facebook = pd.read_csv(os.path.join(base_path, 'facebook-scraper', 'facebook_comments.csv'))
        if not df_facebook.empty:
            csv_files.append((df_facebook, 'Facebook'))
            print(f"Loaded Facebook: {len(df_facebook)} records")
        else:
            print("Facebook file is empty, skipping...")
    except Exception as e:
        print(f"Error loading Facebook: {e}")
    
    return csv_files

def extract_comments_from_dataframes(csv_files: List[Tuple[pd.DataFrame, str]]) -> pd.DataFrame:
    """
    Extract comment text from different CSV structures and combine into unified format.
    
    Args:
        csv_files: List of (dataframe, source_name) tuples
        
    Returns:
        pd.DataFrame: Combined dataframe with columns [comment, source, original_id]
    """
    all_comments = []
    
    for df, source in csv_files:
        print(f"\nProcessing {source}...")
        
        if source == 'Threads':
            # Extract from 'Comments' column
            if 'Comments' in df.columns:
                for idx, row in df.iterrows():
                    if pd.notna(row['Comments']) and row['Comments'].strip():
                        all_comments.append({
                            'comment': row['Comments'],
                            'source': source,
                            'original_id': f"{source}_{idx}"
                        })
        
        elif source == 'Instagram':
            # Extract from 'text' column
            if 'text' in df.columns:
                for idx, row in df.iterrows():
                    if pd.notna(row['text']) and row['text'].strip():
                        all_comments.append({
                            'comment': row['text'],
                            'source': source,
                            'original_id': row.get('comment_id', f"{source}_{idx}")
                        })
        
        elif source == 'Reddit':
            # Extract from 'comment' column
            if 'comment' in df.columns:
                for idx, row in df.iterrows():
                    if pd.notna(row['comment']) and row['comment'].strip():
                        all_comments.append({
                            'comment': row['comment'],
                            'source': source,
                            'original_id': row.get('id', f"{source}_{idx}")
                        })
        
        elif source == 'X':
            # Extract from 'comments' column
            if 'comments' in df.columns:
                for idx, row in df.iterrows():
                    if pd.notna(row['comments']) and row['comments'].strip():
                        all_comments.append({
                            'comment': row['comments'],
                            'source': source,
                            'original_id': row.get('postId', f"{source}_{idx}")
                        })
        
        elif source.startswith('TikTok'):
            # Extract from 'Comment Text' column, skip metadata rows
            if 'Comment Text' in df.columns:
                # Find the header row
                header_found = False
                for idx, row in df.iterrows():
                    if header_found and pd.notna(row['Comment Text']) and row['Comment Text'].strip():
                        all_comments.append({
                            'comment': row['Comment Text'],
                            'source': source,
                            'original_id': f"{source}_{idx}"
                        })
                    elif row.get('Comment Number (ID)') == 'Comment Number (ID)':
                        header_found = True
            else:
                # Alternative: look for comment text in other columns
                comment_cols = [col for col in df.columns if 'comment' in col.lower() or 'text' in col.lower()]
                if comment_cols:
                    col_name = comment_cols[0]
                    for idx, row in df.iterrows():
                        if pd.notna(row[col_name]) and row[col_name].strip():
                            all_comments.append({
                                'comment': row[col_name],
                                'source': source,
                                'original_id': f"{source}_{idx}"
                            })
        
        elif source == 'Facebook':
            # Extract from appropriate column when structure is known
            comment_cols = [col for col in df.columns if 'comment' in col.lower() or 'text' in col.lower()]
            if comment_cols:
                col_name = comment_cols[0]
                for idx, row in df.iterrows():
                    if pd.notna(row[col_name]) and row[col_name].strip():
                        all_comments.append({
                            'comment': row[col_name],
                            'source': source,
                            'original_id': f"{source}_{idx}"
                        })
        
        print(f"Extracted {len([c for c in all_comments if c['source'] == source])} comments from {source}")
    
    combined_df = pd.DataFrame(all_comments)
    print(f"\nTotal comments extracted: {len(combined_df)}")
    
    return combined_df

def main():
    """Main function to execute the text preprocessing pipeline."""
    print("=== Flood Control Comments Text Preprocessor ===\n")
    
    # Initialize preprocessor
    print("Initializing text preprocessor...")
    preprocessor = TextPreprocessor()
    
    # Read all CSV files
    print("\nReading CSV files...")
    csv_files = read_csv_files()
    
    if not csv_files:
        print("No CSV files found or loaded successfully!")
        return
    
    # Extract and combine comments
    print("\nExtracting comments from dataframes...")
    combined_df = extract_comments_from_dataframes(csv_files)
    
    if combined_df.empty:
        print("No comments extracted!")
        return
    
    # Preprocess comments
    print(f"\nPreprocessing {len(combined_df)} comments...")
    combined_df['cleaned_comment'] = combined_df['comment'].apply(preprocessor.clean_text)
    
    # Remove empty cleaned comments
    initial_count = len(combined_df)
    combined_df = combined_df[combined_df['cleaned_comment'].str.len() > 0]
    final_count = len(combined_df)
    
    print(f"Removed {initial_count - final_count} empty comments after cleaning")
    print(f"Final dataset: {final_count} cleaned comments")
    
    # Add statistics
    combined_df['original_length'] = combined_df['comment'].str.len()
    combined_df['cleaned_length'] = combined_df['cleaned_comment'].str.len()
    combined_df['word_count'] = combined_df['cleaned_comment'].str.split().str.len()
    
    # Reorder columns
    final_columns = ['original_id', 'source', 'comment', 'cleaned_comment', 
                    'original_length', 'cleaned_length', 'word_count']
    combined_df = combined_df[final_columns]
    
    # Save to CSV
    output_file = r'c:\Users\Ven\Documents\Coding\Data Mining\flood-control-semantic-analysis\preprocessed_comments.csv'
    combined_df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"\nPreprocessed comments saved to: {output_file}")
    
    # Print summary statistics
    print("\n=== Summary Statistics ===")
    print(f"Total comments: {len(combined_df)}")
    print(f"Comments by source:")
    print(combined_df['source'].value_counts())
    print(f"\nAverage word count: {combined_df['word_count'].mean():.2f}")
    print(f"Median word count: {combined_df['word_count'].median():.2f}")
    print(f"Max word count: {combined_df['word_count'].max()}")
    print(f"Min word count: {combined_df['word_count'].min()}")
    
    # Show sample of cleaned comments
    print(f"\n=== Sample Cleaned Comments ===")
    sample_size = min(5, len(combined_df))
    for i in range(sample_size):
        row = combined_df.iloc[i]
        print(f"\nSource: {row['source']}")
        print(f"Original: {row['comment'][:100]}{'...' if len(row['comment']) > 100 else ''}")
        print(f"Cleaned:  {row['cleaned_comment'][:100]}{'...' if len(row['cleaned_comment']) > 100 else ''}")
        print("-" * 80)

if __name__ == "__main__":
    main()