import pandas as pd

# Load the CSV file (skip the first 3 metadata rows)
file_path = "./MergedXComments.csv"
df = pd.read_csv(file_path, skiprows=3)

# Keep only the relevant columns
needed_cols = ["postUrl", "postId", "replyText"]
df_filtered = df[needed_cols].copy()

# Extract postId from postUrl (numeric part after /status/)
df_filtered["postId"] = df_filtered["postUrl"].str.extract(r"status/(\d+)")

# Remove @"user" mentions from replyText
df_filtered["replyText"] = (
    df_filtered["replyText"]
    .str.replace(r"@\w+", "", regex=True)  # remove mentions
    .str.strip()
)

# Rename replyText → Comments
df_filtered.rename(columns={"replyText": "comments"}, inplace=True)

# Keep only final cleaned columns: postUrl, postId, comments
final_df = df_filtered[["postUrl", "postId", "comments"]]

# Save cleaned dataset to CSV
final_df.to_csv("CleanedXComments.csv", index=False)

print("Cleaning complete. Saved as CleanedXComments.csv")
print(final_df.head())
