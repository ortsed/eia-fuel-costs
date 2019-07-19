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
 
 - Caveat: 2018 data is still listed as preliminary and not suitable for aggregation (2019 data does not include this warning).

 - Merge all files via python into a single dataframe, while taking into account column names with varying spelling and ignoring fields that didn't exist for most years.

## Data Cleaning

 - Deal with Nans, Nones, and other empty fields (e.g. ".").

 - Convert numeric fields to floats
 
 - Fix obvious typos in category fields
 
  - Run text fields for names - like plant names and operator names - through OpenRefine to coalesce typos and name consistency (e.g. Globocorp Inc. vs. Globocorp LLC)


## Preliminary Analysis

 - Import the cleaned, refined data and begin exploring the numbers.
 
 - Histograms of fuel_cost show some extreme values that throw off the distribution. But 99% of values live below 3,000. If the hypothesis is to identify the extreme costs , best to leave those values in. But creating a subset without those values will be helpful for examining overall trends.
 
 - A large number of fields are solely associated with coal, and others are only associated with natural gas. For a preliminary analysis, remove those fields as it will hamper the model. Later, we will use them for analysis on subsets of single fuel costs (only coal or only gas).
 
  - Since most other fields are categorical, and dummying out those categories leads to a wide field set, correlation maps aren't helpful. Too much information to view. Instead, loop through the correlation map and find the largest correlations.
  
  - Testing basic models. With little correlation, models are terrible. This may need additional features as independent variables.
  
## Adding Features
 
 
 
 
 
 
