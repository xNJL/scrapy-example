import pandas as pd

df = pd.read_csv("data/articles.csv")

if __name__ == "__main__":
    print(df.loc[0, "text"])
