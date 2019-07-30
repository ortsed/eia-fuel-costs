# Analysis of fuel cost data from EIA

## Description

What drives the cost of electricity can be a complicated question. Weather conditions like the Polar Vortex can drive sharp spikes in prices for fuel, and market fluctuations and accusations of manipulation [often end in protracted lawsuits](https://www.bloomberg.com/news/articles/2019-07-12/darkest-california-power-market-lures-repeat-manipulation). 

Thankfully the U.S. Energy Administration (EIA) puts out mountains of data on the subject that's ready to be analyzed.

Their energy industry data covers every kind of fuel and every way it could possibly be consumed. One particular data set is the Form 923 data that collects "detailed electric power data -- monthly and annually -- on electricity generation, fuel consumption, fossil fuel stocks, and receipts at the power plant and prime mover level."

This analysis will look at the data of fuel receipts for electricity generation from form 923, which includes how much utilities pay for their fuel generation. Each spreadsheet contains prices paid for fuel for Coal, Natural Gas, Petroleum, Petroleum Coke. Other energy sources like nuclear do not appear.

Potential features that drive price include the contract type, the quantity, the plant consuming the fuel, the operator, the provider of the fuel (e.g. coal mine), a variety of quality indicators for coal (average_ash_content, average_heat_content, average_mercury_content, average_sulfur_content, chlorine_content), how it was transported (pipeline vs. truck).

# Download

https://www.eia.gov/electricity/data/eia923/

Excel documents listed on the EIA site go back to around 2002. Only files after 2007 include the full fuel cost data for this analysis, so older files 
were excluded.

## Process

 - Export Fuel Costs sheet as CSV from Excel file.
 
 - Remove header information

 - Merge all files via python into a single dataframe, while taking into account column names with varying spelling and ignoring fields that didn't exist for most years.

## Data Cleaning

 - Deal with NaNs, Nones, and other empty fields (e.g. ".").

 - Convert numeric fields to floats
 
 - Fix obvious typos in category fields
 
  - Run text fields - like plant names and operator names - through OpenRefine to coalesce typos and name consistency (e.g. Globocorp Inc. vs. Globocorp LLC)
  
## Additional Data

 - Preliminary analysis showed poor modeling with the fuel cost data, and largest correlations were with dates. 
 
 ![Coal Fuel Costs Decision Tree](images/tree-date-based.png)

From a client perspective, this analysis didn't provide any insight as it's not prescriptive. The model doesn't predict for future dates unless a time-based model is used, and a basic analysis of time correlations didn't show any significant trends.
 
 So dates were removed from features and additional data sources were required. Two additional sources were identified:
 
 	1. In the Form 923 spreadsheet, another sheet included data on monthly fuel consumption/generation for each plant that aligns with the plants listed in the fuel cost data.
 	
 	2. EIA also provides data on electricity disruptions that could be correlated with price spikes, shortened supply, and increased demand:
 	
 	https://www.eia.gov/electricity/data/disturbance/disturb_events_archive.html
 	
A similar process was used to import, coalesce, clean, and refine both data sets. Generation data included monthly data compiled yearly per row that needed to be melted into one row per month entries.

Both were merged onto the fuel cost data using SQL joins. For generation data, it was joined on plant id, year and month. For disruption data it was joined on NERC region, year, and month. 


## Preliminary Analysis

 - Import the cleaned, refined data and begin exploring the numbers. All entries without fuel cost defined were removed.
 
 - For the first iteration, a price spike was defined as any value in the 90th percentile of fuel costs (for that fuel). Mean and standard deviations were thrown off by anomalous values sometimes over 60,000x median values. The 90th percentile starts at fuel costs approximately twice the median. Future analysis will calculate best model based on differing thresholds.
 
  - Because the data included different fields based on fuel type (particularly for coal and natural gas), the data was split based on three fuel groups: Coal, Natural Gas, and Other (Petroleum, Other Gas). Each one will be modeled separately. The data does not include information for nuclear, renewable, hydro or other fuel sources. 
  
  - Decision Tree was chosen as default model as it allows for good performance, feature interpretability, and did not require feature scaling. Testing on other models did not show marked improvement to warrant a change.
  
  - Most fields were categorical, requiring encoding. Label encoding was used to dummy those fields for correlation analysis. No strong correlations were identified, but casual correlations were identified for potential future analysis.
  
  - Categorical variables were then one-hot encoded for full modelling analysis, leading to a 268,454 x 1,708 data set for natural gas.
  
 - Since data is relatively imbalanced (90-10 class split), a baseline model was defined as assuming the first class (not a price spike) at all times, which has a 90% accuracy. 
  
  - With the added generation and disruption data, basic model results returned a 94% accuracy, better than baseline.
  
  - Preliminary feature analysis returned by the model highlighted interesting factors, like individual supplier or plant operators as major factors in price spike prediction.
  
## Model Scoring

Accuracy provided a general quality measure for the model, but because the data was imbalanced, precision, recall, and F1 were more relevant for predictive robustness.

Eventually, a cost function was defined based on an assumed utility fuel purchaser looking to avoid price spikes.  

The function was defined as the difference from the baseline model in costs. A small penalty is imposed to assuming a price spike (1.1 * median fuel cost, for pre-purchasing fuel or storing fuel) but there is a benefit to every price spike predicted that avoids at least double the median fuel price.

Models were cross validated using precision, recall, and f1 scores as well as the cost function. ROC Curves and AUC values were calculated.


## Improving the Model

While the default model returned a respectable score for accuracy, there was plenty of room for improvement. Here are a few alternatives that were attempted:

 - SMOTE and ADASYN for class imbalance. Both transformations caused the model to decline in accuracy, possibly because the data wasn't imbalanced enough.
 
 - Other models. Random Forest, Keras/TensorFlow, GradientBoosting, and LogisitcRegression were tried as comparison models to confirm that DecisionTree was not severely lacking in potential accuracy, but none of these returned substantially improved results.
 
  - Some time-series analysis was done to identify if ARIMA would help, but no time-based correlations were identified.
 
 - Stratifying independent variable. Little affect on results.
 
  - Feature removal: removing features whose importance by the default model was equal to zero. This did not largely affect results except for on modelling Other Fuels. 
  
  - Adjustment for quantity, total spent. Preliminary analysis of the data showed some fuel purchases involved large price spikes on small amounts of purchased fuel. Potentially, when the quantity purchased is small, other costs like transportation may affect the fuel cost ratio. For example, a utility that buys one gallon of natural gas will still need to pay for the transportation costs of that fuel, which might be a thousand dollars.  So the data would list the fuel cost as $1,000/gallon, and would be classified as a price spike in the model. I attempted to account for this by defining columns like adjusted fuel cost, that subtract a fixed amount from the total money spent on fuel, but without having a better understanding about what additional costs like transportation might be, the estimates were arbitrary and did not seem to improve the model.
  
Additionally, reporting fuel cost data to the EIA dropped considerably around 2011, which according to a representative from the agency, was due to limiting reporting only to larger operators who might be less likely to buy fuel in smaller quantities.


## Hyperparameter Tuning
  
Once the base model was established and data transformation was disregarded, the model was grid searched to identify potential hyperparameters.

Decision Tree does not allow for a large number of parameters outside of tree size and criterion (entropy vs. gini). Only max depth appeared to affect outcomes, with large max depth leading to overfitting and difficulty for interpretation. Ideal depth appeared to be 10, although modelling Other Fuel, which appeared to be harder to predict, worked better with a larger depth.

In the end, hyperparameter tuning did not appear to have any large effect on model improvement.
  
## Adjusting Threshold

Rather than defining the 90th percentile as the cutoff for a price spike, numerous thresholds were tried. In general, lower thresholds lead to increased model performance, in a linear correlation. But lowering the threshold also undercut the idea of the hypothesis. I.e. defining a price spike as anything above the median doesn't mean much.

Eventually, 80% worked as the best threshold for better performance without defining price spikes down.
 
  
## Overall Model Result

Decision Tree with max_depth of 10, price threshold of 80%. For Natural Gas, the cost savings was 5% on average with average precision at 64%. Cross validation showed inconsistent results, with some results much better and others worse.

For coal, which had fewer price spikes than natural gas, the scores were generally worse, with only a one percent benefit in costs. But advanced analysis indicated improvements for future use.

The same for other fuels, which had an approximate 1% cost benefit, inconsistent precision, but a potential benefit from advanced analysis.

## Subsetting Data

Analysis of model results showed certain feature values common in inaccurate predictions. For coal, chlorine content appeared to be a volatile factor affecting model prediction. 

Modelling a subset of the data not including chlorine content improved the model considerably (6% cost, 50% precision). And vice versa for with the data subset with chlorine content (4% cost, 50% precision). Chlorine content is a recent addition to the data and only appears in entries since 2016, potentially related to new MATS rules on power plants for mercury emissions as chlorine content helps reduce those emissions.

For other fuels, it was spot contracts that appeared to be the volatile feature. Subsetting the data based on that category improved each model considerably. Spot contracts: (5% benefit, 26% precision). Other Contracts: (6% benefit, 41% precision).

For natural gas, delivery contract type was the volatile feature. Subset where contract type was unknown provided a more accurate/precise model than the larger data set (9% benefit, 56% precision).

But for known delivery contracts, the model was still imprecise. Yet, modeling on subsets of that showed improvements. 

Known delivery contracts with automatic reporting showed improved performance (3% benefit, 85% precision). Without automatic reporting, there were few price spikes, and also low benefit to using the model (<1%), but precision was good. (82%)
 
 
 
 
 
 
