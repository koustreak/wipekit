# Wipekit Research & Feature Coverage

This document outlines the advanced preprocessing techniques and features supported or planned for the `wipekit` library, organized by category. This serves as a research and design reference for comprehensive data preprocessing in modern data science and machine learning pipelines.

---

## 1. Missing Data Handling
- Mean / Median / Mode imputation
- Constant value imputation
- Forward / Backward fill
- Linear / Spline / Polynomial interpolation
- KNN imputation
- MICE (Multiple Imputation by Chained Equations)
- MissForest (Random Forest Imputation)
- Indicator for missingness (binary flag)
- Drop rows / columns with missing values

## 2. Outlier Detection & Treatment
- Z-Score
- IQR (Interquartile Range) method
- Winsorization
- Isolation Forest
- DBSCAN / HDBSCAN
- Local Outlier Factor (LOF)
- Hampel filter
- Box-Cox transform + scaling
- Elliptic Envelope

## 3. Encoding Categorical Variables
- Label encoding
- One-hot encoding
- Ordinal encoding
- Frequency encoding
- Mean / Target encoding
- Binary encoding
- Hashing trick
- Leave-One-Out encoding
- Embedding-based (for deep learning)

## 4. Scaling & Normalization
- Min-Max scaling
- Standardization (Z-score)
- Robust scaler (IQR-based)
- MaxAbs scaler
- Log / Power transforms (Box-Cox, Yeo-Johnson)
- Quantile transform
- Unit vector normalization (L2)

## 5. Text Preprocessing (NLP)
- Tokenization (word, subword, sentence)
- Lowercasing
- Removing punctuation
- Removing stopwords
- Lemmatization
- Stemming
- Spelling correction
- Text normalization (unicode fix, contractions)
- N-grams generation
- TF-IDF
- Bag-of-Words
- Word embeddings (Word2Vec, GloVe, FastText)
- Sentence embeddings (BERT, SBERT)
- Named Entity Removal
- Entity linking
- Dependency parsing
- Coreference resolution
- Adversarial augmentation (e.g., synonym swap)

## 6. Feature Engineering
- Polynomial features
- Interaction terms
- Aggregation (grouped means, ranks, etc.)
- Binning / Bucketing (equal-width, equal-frequency, KMeans)
- Log transform
- Date-time feature extraction
- Categorical count encoding
- Lag features
- Rolling statistics (mean, std, etc.)
- Cyclical encoding (sin/cos for hours, day-of-week, etc.)

## 7. Dimensionality Reduction & Selection
- PCA
- t-SNE
- UMAP
- LDA (for classification)
- Autoencoder-based compression
- Variance Threshold
- SelectKBest (Chi², ANOVA)
- Recursive Feature Elimination (RFE)
- L1-based selection (Lasso)
- Tree-based selection (feature importances)
- Mutual information filter
- Null importance selection
- Correlation threshold pruning

## 8. Time Series Specific
- Lag / Lead features
- Rolling mean / std / skew
- Expanding window statistics
- Differencing
- Seasonal decomposition (STL, ETS)
- Fourier transforms
- Time-based resampling
- Time deltas / elapsed time
- Timestamp encoding (sin/cos, datetime split)

## 9. Geospatial Preprocessing
- Coordinate normalization (lat/lon)
- Distance to POIs
- Bearing calculation
- Spatial joins (GeoPandas)
- Area / polygon feature extraction
- Raster-to-vector or vice versa
- H3 / S2 geohash encoding

## 10. Graph Data Preprocessing
- Node degree features
- Adjacency matrix normalization
- Node2Vec / GraphSAGE / Graph2Vec embeddings
- Edge feature construction
- Community detection-based encoding
- Graph simplification

## 11. Anonymization & Privacy Techniques
- K-anonymity, L-diversity, T-closeness
- Differential privacy noise injection
- Hashing sensitive fields
- Tokenization & detokenization
- Synthetic identity masking

## 12. Data Cleaning
- Duplicate removal
- Typo correction (fuzzy matching, spelling)
- Constant / single-unique feature removal
- Regex-based pattern cleansing
- Inconsistent label standardization (yes/Yes/Y)
- Whitespace trimming
- Unit standardization

## 13. Class Imbalance Handling
- Oversampling (SMOTE, Borderline SMOTE, ADASYN)
- Undersampling (Tomek Links, NearMiss)
- Hybrid methods (SMOTE + Tomek)
- Class weighting
- Balanced bagging / boosting
- Stratified sampling

## 14. Drift Detection / Shift Handling
- Population Stability Index (PSI)
- Concept drift detectors (ADWIN, DDM)
- KS test for feature shift
- Feature monitoring transforms
- Dataset rebalancing for covariate shift

## 15. Synthetic Data Generation
- CTGAN, TVAE (synth tabular generation)
- Faker-based rules
- Correlation-preserving generation
- Variational Autoencoders (VAEs)
- Gaussian copulas

## 16. Model-Specific Preprocessing
- Tree-based models: skip scaling/normalization
- Deep learning: scaling, embedding handling
- Quantization-friendly feature conversion
- Embedding-aware categorical treatment
- Feature monotonicity enforcement
- Batch normalization-friendly transforms

## 17. Big Data & Distributed Support
- Lazy transformations (Dask, Spark)
- Partition-aware transforms
- Schema inference
- Vectorized string operations
- Broadcast-safe encoding
- Z-ordering (for Delta/Iceberg)
- File-aware processing (columnar formats)

## 18. Explainability-Aware Preprocessing
- SHAP-friendly encoding (avoid hashing/embedding)
- Monotonic binning
- Interpretable scaling (no PCA, no t-SNE)
- Group-level explainable transformations

## 19. Tool-Specific Integrations
- Scikit-learn TransformerMixin support
- PyTorch Dataset and collate_fn preprocessors
- TensorFlow tf.data pipeline prep
- HuggingFace tokenizer wrapping
- Great Expectations schema validation
- Pandera, Pydantic, Cerberus type enforcement
- MLFlow logging of transformation pipeline

---

This document is a living reference for the ongoing development and research of the `wipekit` library. 