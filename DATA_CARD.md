# Healthy U presentation-MVP data card

Source: the existing HU-NutritionistsVA product export at `rag_pipeline/data/Enhanced_Product_List.json`. Phase 0 read-only observation: 5,512 records, SHA-256 `6d33c9d54279076aeb6105d675e327caf308c9590a47bf7cbe8c4382ed15840d`. This is actual accessible product data, not a synthetic or Flipkart substitute.

The user confirmed permission for public presentation-MVP use and that RRP is KES. This is a user-confirmed use basis, not a claim that a general open-data licence exists. Re-confirm other uses separately.

Allowlisted fields: original ID/SKU, product name, stripped description, categories, listed price, KES currency, approved retailer link and source record ID. Customer accounts, orders, loyalty records, health histories and private infrastructure are excluded. The export is read-only; actual extraction/cleaning/fitting remain manual and unexecuted by the agent.

Unknown: export timestamp, current stock, structured brand, ingredients/allergen list and verified dietary labels. A word absent from a description is not evidence of allergen freedom. Marketing claims are not clinical evidence. Requested constraints that require unknown fields produce abstention/clarification.

Generated artifacts record actual extraction time, input/output SHA-256, accepted/rejected counts, model revision, optional semantic method, fitting timestamp and limitations. Only after student execution can accepted catalogue counts, data-quality summaries or model results be reported.

The old Flipkart card is preserved in docs/LEGACY_FLIPKART_DATA_CARD.md. Historical results are not current Healthy U/Groq evidence.
