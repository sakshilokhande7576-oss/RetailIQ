from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

products = pd.read_csv(RAW / "olist_products_dataset.csv")
translations = pd.read_csv(RAW / "product_category_name_translation.csv")

# Keep the original category and add a translated English category.
products["product_category_name_english"] = products["product_category_name"].map(
    translations.set_index("product_category_name")[
        "product_category_name_english"
    ]
)

# Explicitly document categories not included in the translation table.
special_mappings = {
    "pc_gamer": "pc_gamer",
    "portateis_cozinha_e_preparadores_de_alimentos":
        "portable_kitchen_food_processors",
}

products["product_category_name_english"] = (
    products["product_category_name_english"].fillna(
        products["product_category_name"].map(special_mappings)
    )
)

# Retain products with missing categories and label them transparently.
products["product_category_name_english"] = (
    products["product_category_name_english"].fillna("unknown")
)

output = PROCESSED / "products_cleaned.csv"
products.to_csv(output, index=False)

print("PRODUCT CLEANING COMPLETE")
print("Original product rows:", len(products))
print("Output file:", output)
print("Missing English categories:",
      int(products["product_category_name_english"].isna().sum()))
print("\nTop 10 categories:")
print(products["product_category_name_english"].value_counts().head(10).to_string())
