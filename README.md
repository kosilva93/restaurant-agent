# Restaurant Performance Chat App

This application lets you interact conversationally with a restaurant performance dataset using **LangChain**, **OpenAI**, and **Chainlit**.

You can ask questions such as:

- “Rank restaurants by Net Sales”
- “Which restaurant has the best overall performance?”
- “Show the slowest 3 by Speed of Service Total Seconds”
- “List restaurants with negative Cash Over/Short values”

The app analyzes the CSV with **pandas**, adds a weighted **Composite Score** metric (optional), and answers your free-form questions directly in a web chat.

---

## Project Structure

```
restaurant-agent/
│
├── app.py                 # Chainlit entry point (main app)
├── restaurant_assistant.py       # Builds LangChain pandas agent & adds Composite Score
├── data/
│   └── store-summary-data.csv   # Input dataset
├── .env.example           # Environment variable template
├── requirements.txt       # Dependencies
└── README.md              # This file
```

---

## Features

- Loads restaurant data from a CSV into a `pandas.DataFrame`.
- (Optional) Pre-computes a **Composite Score** using normalized metrics:
  - **Higher is better:** Net Sales, Avg Transaction Amount, Beverage Count  
  - **Lower is better (inverted):** Speed of Service Total Seconds, Discount Total Amount  
  - **Closer to 0 is better:** Cash Over/Short  
  - **Weights:** 0.30, 0.25, 0.15, 0.15, 0.10, 0.05
- Wraps the dataframe in a **LangChain Pandas Agent** powered by GPT-4o.
- Provides a conversational interface via **Chainlit**.
- Executes real Python/pandas code for accurate numeric answers.

---

## Requirements

- **Python 3.10 +**
- **OpenAI API key**

Install all dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## Environment Setup

1. Create a `.env` file in the project root (or copy from `.env.example`):

   ```bash
   cp .env.example .env
   ```

2. Add your OpenAI API key inside `.env`:

   ```env
   OPENAI_API_KEY=sk-yourkeyhere
   ```

3. Verify that the dataset file exists at:

   ```
   ./data/store-summary-data.csv
   ```

---

## Run the App

Start Chainlit in watch mode:

```bash
chainlit run app.py -w
```

Then open the local URL shown in the terminal  
(default: **http://localhost:8000**).

---

## Example Prompts to Try

| Type | Example |
|------|----------|
| **Single metric** | “Rank restaurants by Net Sales.” |
| **Speed** | “Show the 5 slowest restaurants by Speed of Service Total Seconds.” |
| **Discounts** | “Which 3 restaurants give the largest discounts?” |
| **Composite Score** | “Rank restaurants overall using the Composite Score.” |
| **Exploratory** | “Which restaurant has the highest Beverage Count and what is its Net Sales?” |
| **Correlation** | “Is there a relationship between Beverage Count and Net Sales?” |

---

## Notes

- The agent runs with `allow_dangerous_code=True` so it can execute Python in memory.  
  Use only in a **trusted environment** (no arbitrary user input on a public server).
- The app currently handles **one query at a time** (no multi-intent router).
- If you modify the dataset or add columns, update the logic in `add_composite_score()` inside `agent_factory.py`.

---

## Quick Test Checklist

After running the app, verify that:

1. “Rank restaurants by Net Sales” returns a correct table.  
2. “Rank restaurants overall” uses the Composite Score column.  
3. “Show slowest 3 by Speed of Service Total Seconds” lists the right rows.  
4. Free-form requests like “Show top 5 restaurants and their discounts” work without error.

---

## Tech Stack

- **Python 3.10+**
- **pandas** – data wrangling
- **LangChain** – LLM agent orchestration
- **OpenAI GPT-4o** – language model
- **Chainlit** – chat UI
- **dotenv** – environment configuration

---