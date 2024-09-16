import pandas as pd

df = pd.read_csv('test.csv')

chunk = 5000

for i in range(0, df.shape[0], chunk):
    dfs = df[i: i+chunk]
    dfs.to_csv(f'test_splits/test_{i}_{i+chunk}.csv')
