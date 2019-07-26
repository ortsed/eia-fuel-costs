"""
Defining cost function:
	False Negative: Incurs 2x median price of fuel
	False Positive: Incurs 1.1x median price of fuel (1 + .1 for storage costs)
	True Negative: Incurs median cost of fuel (1x)
	True Positive: Saves 1.1x the cost of fuel (1 + .1 for storage costs)


Function returns difference of cost based on model minus cost of baseline that assumes no price spikes.

Baseline cost function = 
	2x median cost of fuel for price spikes (true positives and false negatives) +
	1x median cost of fuel for all other times (true negatives and false positives)
	
"""

from sklearn.metrics import make_scorer
def cost_function(y_test, y_pred, quantity, **kwargs):
    import pandas as pd
    from sklearn.metrics import confusion_matrix
    cm = pd.DataFrame(confusion_matrix(y_test, y_pred))
    print(cm)

    tp = 0
    fp =0
    tn = 0
    fn = 0
    for i, val in enumerate(y_test):
        if val == y_pred[i] and val: 
            tp += quantity[i]
        elif val == y_pred[i] and not val:
            tn += quantity[i]
        elif val != y_pred[i] and val:
            fn += quantity[i]
        elif val != y_pred[i] and not val:
            fp += quantity[i]
            
    #tp = cm.iloc[1,1]
    #tn = cm.iloc[0,0]
    #fp = cm.iloc[1,0]
    #fn = cm.iloc[0,1]
    total = sum([tp, tn, fp, fn])
    return (((fp * 1.1) + (fn * 2) + (1.1 * tp)  + tn ) - (2* (tp + fn) + (fp + tn)))

def coster(model, X, y):
    y_pred = model.predict(X)
    return cost_function(y, y_pred, X.quantity.values)

make_scorer(coster, greater_is_better=False)
