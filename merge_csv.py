import os
import pandas as pd

# Define the folder path where your CSV files are stored
folder_path = "./amz_pred"
test_csv = "test.csv"

test_df = pd.read_csv(test_csv)

# Define the chunk size
chunk_size = 5000

# Define the maximum index (you might know this from the total size)
max_index = 131187  # Example value, change as per your data

# Initialize an empty list to hold the dataframes
dfs = []

# Iterate over the range of indices in steps of chunk_size
for start_idx in range(0, max_index, chunk_size):
    end_idx = start_idx + chunk_size
    file_name = f"predictions_{start_idx}_{end_idx}.csv"  # Adjust file naming convention as necessary
    file_path = os.path.join(folder_path, file_name)
    
    # Check if the file exists
    if os.path.exists(file_path):
        print(file_name)
        # Load the file into a dataframe
        df = pd.read_csv(file_path)
        df['index'] = range(start_idx, start_idx + df.shape[0])
        # Check if it's the last chunk and has fewer rows
        if df.shape[0] < chunk_size and start_idx + df.shape[0] == max_index:
            print("LAST ONE")
            # It's the last chunk with fewer rows, so adjust the index accordingly
            df['index'] = range(start_idx, start_idx + df.shape[0])
        dfs.append(df)
    else:
        # If the file is missing, create an empty DataFrame with correct indices and blank predictions
        empty_df = pd.DataFrame({
            'index': range(start_idx, end_idx),
            'prediction': [None] * chunk_size
        })
        dfs.append(empty_df)

# Concatenate all the dataframes
final_df = pd.concat(dfs, ignore_index=True)
final_df['index'] = test_df['index']
# Save the combined dataframe to a CSV file
final_df.to_csv("full_predictions_3.csv", index=False)

print("Files combined successfully!")