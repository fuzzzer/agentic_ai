from enum import Enum
import pandas as pd
import os

class ToolCompletionStatus(Enum):
    SUCCESS = 1
    FAILURE = 2

def receit_tracker(entries: list[dict],) -> ToolCompletionStatus:
    try:
        append_entries_to_existing_excel(entries)
        return ToolCompletionStatus.SUCCESS
    except:
        return ToolCompletionStatus.FAILURE


def append_entries_to_existing_excel(
    entries: list[dict],
) -> pd.DataFrame:
    """
    Appends structured product entries to an existing Excel file.

    The Excel file must already exist with these exact columns:
      A column: Date of Purchase
      B column: Product Category
      C column: Product
      D column: Total Price

    Each entry in `entries` should be a dict with keys:
      - "date_of_purchase": str (YYYY-MM-DD)
      - "product_category": str
      - "product": str
      - "total_price": float

    Example entry:
      {
          "date_of_purchase": "2025-03-30",
          "product_category": "Beverage",
          "product": "Coffee",
          "total_price": 4.50
      }
    """
    excel_path: str = "/Users/fuzzzer/programming/AI_tools/agentic_ai/storage/test.xlsx"

    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel file not found at {excel_path}")

    df_existing = pd.read_excel(excel_path)
    required_columns = ["Date of Purchase", "Product Category", "Product", "Total Price"]
    
    for col in required_columns:
        if col not in df_existing.columns:
            raise ValueError(f"Expected column '{col}' not found in Excel file.")

    df_new = pd.DataFrame(entries)
    df_new = df_new[["date_of_purchase", "product_category", "product", "total_price"]]
    df_new.columns = required_columns
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    df_combined.to_excel(excel_path, index=False)

    return df_combined

# Ex:
entries = [
    {
        "date_of_purchase": "2025-03-30",
        "product_category": "Beverage",
        "product": "Coffee",
        "total_price": 4.50
    },
    {
        "date_of_purchase": "2025-03-30",
        "product_category": "Snack",
        "product": "Chocolate Croissant",
        "total_price": 2.30
    }
]

append_entries_to_existing_excel(entries)
