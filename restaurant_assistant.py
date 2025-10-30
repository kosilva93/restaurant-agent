import os
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent

load_dotenv()

def load_df(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    return df

# Optional. To use the composite score uncomment line 52
def add_composite_score(df: pd.DataFrame) -> pd.DataFrame:
    # assumes all columns are simple numeric strings
    df["Net Sales"] = df["Net Sales"].astype(float)
    df["Transaction Count"] = df["Transaction Count"].astype(float)
    df["Beverage Count"] = df["Beverage Count"].astype(float)
    df["Speed of Service Total Seconds"] = df["Speed of Service Total Seconds"].astype(float)
    df["Discount Total Amount"] = df["Discount Total Amount"].astype(float)
    df["Cash Over/Short"] = df["Cash Over/Short"].astype(float)

    df["Avg Transaction Amount"] = df["Net Sales"] / df["Transaction Count"].replace(0, pd.NA)

    # normalize helper
    def minmax(s):
        mn, mx = s.min(), s.max()
        if mn == mx:
            return pd.Series(0.0, index=s.index)
        return (s - mn) / (mx - mn)

    norm_net  = minmax(df["Net Sales"])
    norm_avg  = minmax(df["Avg Transaction Amount"])
    norm_bev  = minmax(df["Beverage Count"])
    norm_sos  = 1 - minmax(df["Speed of Service Total Seconds"])
    norm_disc = 1 - minmax(df["Discount Total Amount"])
    norm_cash = 1 - minmax(df["Cash Over/Short"].abs())

    df["Composite Score"] = (
        0.30 * norm_net
        + 0.25 * norm_avg
        + 0.15 * norm_bev
        + 0.15 * norm_sos
        + 0.10 * norm_disc
        + 0.05 * norm_cash
    )
    return df

def build_agent(csv_path: str):
    df = load_df(csv_path)
    #df = add_composite_score(df)

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.0,
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    system_prompt = """
    You are a data analyst that evaluates restaurant performance data.
    Use the uploaded CSV saved in a dataframe to answer questions accurately and concisely.
    Always:
    - Perform calculations using the CSV data.
    - Return final answers as clean, readable tables.
    If asked for overall performance, combine multiple metrics into a composite score.
    Do not ask clarifying questions — just make reasonable assumptions and answer directly.
    """

    # (Optional) Add the section below to the system prompt if you are using the composite score.
    # Copy the all thing and replace line 66
    # If asked for "overall performance" or "best restaurant overall":
    # 1) Normalize:
    #    - Higher is better: Net Sales, Avg Transaction Amount, Beverage Count
    #    - Lower is better: Speed of Service Total Seconds, Discount Total Amount
    #    - Closer to 0 is better: Cash Over/Short (use abs, then invert)
    # 3) Apply weights: 0.30, 0.25, 0.15, 0.15, 0.10, 0.05 in that order
    # 4) Return table sorted by Composite Score desc

    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=False,
        allow_dangerous_code=True,
        agent_executor_kwargs={
            # inject our own "system"-like message
            "extra_prompt_messages": [
                {"role": "system", "content": system_prompt}
            ],
        },
    )
    return agent
