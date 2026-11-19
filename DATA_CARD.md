# Data card

Source: PromptCloudHQ Flipkart product sample, 20,000 scraped product records, mirrored at https://huggingface.co/datasets/jason1966/PromptCloudHQ_flipkart-products . Pinned source revision: ac16731c75907ab9f212c372ec637c00f257c36a.

The catalogue is historical Indian retail data, not Kenyan inventory. Discounted prices are treated as INR, with no currency conversion. Crawl timestamps describe collection, not transactions. There are no sales outcomes, sessions or reliable live stock fields. Unknown availability remains unknown. Requests for confirmed in-stock products therefore abstain.

Raw fields include product names, brand, category tree, descriptions, prices, textual ratings, URLs and specifications. Missing descriptions become empty; unknown brands are explicit; nonnumeric ratings remain null. Records missing ID/name/valid positive price are excluded; duplicate product IDs are removed. Nested category trees can contain malformed/product-like categories; preserved top-level labels are imperfect. No fabricated descriptions, prices, stock or ratings are imputed.

The source mirror marks its license as unknown. Raw catalogue and derived record-level model artifacts should be kept for local academic reproduction; do not claim redistribution rights or commercial permission. The repository downloads the source instead of bundling the raw CSV. Serialized local artifacts are packaged separately for the student. Confirm source rights before public redistribution or operational use.

The benchmark is a small silver set, authored independently of retrieval outputs. Exhaustive regex predicates over product titles plus explicit category/price constraints generate binary judgments. Such labels omit synonyms, overinclude accessories and do not assess suitability. Dev/test split is by query, not product; all catalogue products are indexed because this is catalogue retrieval, not supervised purchase prediction. Related intents occur in both splits; results are exploratory, not a strict generalization estimate. Human annotation remains necessary.
