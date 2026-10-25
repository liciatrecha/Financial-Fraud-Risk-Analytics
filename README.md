Financial Fraud & Risk Analytics
Project Overview
A data analytics project investigating credit card transaction patterns and fraud risk using Python, SQL and data visualisation.
The project explores transaction amounts, class imbalance and the limitations of simple amount-based fraud screening.
Tools & Technologies
* Python
* pandas and NumPy
* Matplotlib
* SQL
* Google Colab
* GitHub
Dataset Analysis
The analysis examined 284,807 credit card transactions.
Metric	Result
Total transactions	284,807
Labelled fraud transactions	492
Other transactions	284,315
Labelled fraud rate	0.1727%
Key Findings
* Fraud cases represented a very small proportion of all transactions.
* An amount-only screening rule generated many false positives.
* At a threshold of 50, the rule flagged 95,103 transactions, including 187 labelled fraud cases.
* More advanced fraud detection methods would be needed to improve screening performance.
Project Files
* src/ — Python analysis code
* sql/ — SQL analysis queries
* fraud_analysis_results/ — analysis report and CSV results
* requirements.txt — Python dependencies
Limitations
This is an exploratory portfolio project. The amount-based rules are illustrative baselines, not production fraud detection systems. Results have not been validated on a separate test dataset.
Author
Felicia Adekanye tamilore 
