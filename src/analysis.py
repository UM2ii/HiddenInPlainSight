import numpy as np
import pandas as pd
from sklearn import metrics
from tqdm.auto import tqdm

num_trials = 5

# Metrics

def __threshold(y_true, y_pred):
  # Youden's J Statistic threshold
  fprs, tprs, thresholds = metrics.roc_curve(y_true, y_pred)
  return thresholds[np.nanargmax(tprs - fprs)]

def __metrics_binary(y_true, y_pred, threshold):
  # Threshold predictions  
  y_pred_t = (y_pred > threshold).astype(int)
  try:  
    auroc = metrics.roc_auc_score(y_true, y_pred)
  except:
    auroc = np.nan
    
  tn, fp, fn, tp = metrics.confusion_matrix(y_true, y_pred_t, labels=[0,1]).ravel()
  if tp + fn != 0:
    tpr = tp/(tp + fn)
    fnr = fn/(tp + fn)
  else:
    tpr = np.nan
    fnr = np.nan
  if tn + fp != 0:
    tnr = tn/(tn + fp)
    fpr = fp/(tn + fp)
  else:
    tnr = np.nan
    fpr = np.nan
  if tp + fp != 0:
    fdr = fp/(fp + tp)
    ppv = tp/(fp + tp)
  else:
    ppv = np.nan
  if fn + tn != 0:
    npv = tn/(fn + tn)
    fomr = fn/(fn + tn)
  else:
    npv = np.nan
    fomr = np.nan
  return auroc, tpr, fnr, tnr, fpr, ppv, npv, fomr, tn, fp, fn, tp
  
def __analyze_aim_2(model, test_data, target_sex=None, target_age=None):
  if target_sex is not None and target_age is not None:
    target_path = f'target_sex={target_sex}_age={target_age}'
  elif target_sex is not None:
    target_path = f'target_sex={target_sex}'
  elif target_age is not None:
    target_path = f'target_age={target_age}'
  else:
    target_path = 'target_all'
    
  results = [] 
  for trial in range(num_trials):
    y_true = pd.read_csv(f'splits/aim_2/{test_data}_test.csv')
    y_true = pd.read_csv(f'splits/aim_2/{test_data}_test.csv')
    
    for rate in [0, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0]:
      if rate == 0:
        y_pred = pd.read_csv(f'results/aim_2/{model}/baseline/trial_{trial}/baseline_rsna_{test_data}_pred.csv')
        
        threshold = __threshold(pd.read_csv(f'splits/aim_2/rsna_test.csv')['Pneumonia_RSNA'].values, pd.read_csv(f'results/aim_2/{model}/baseline/trial_{trial}/baseline_rsna_pred.csv')['Pneumonia_pred'].values)
      else:
        y_pred = pd.read_csv(f'results/aim_2/{model}/{target_path}/trial_{trial}/poisoned_rsna_rate={rate}_{test_data}_pred.csv')
        
        threshold = __threshold(pd.read_csv(f'splits/aim_2/rsna_test.csv')['Pneumonia_RSNA'].values, pd.read_csv(f'results/aim_2/{model}/{target_path}/trial_{trial}/poisoned_rsna_rate={rate}_pred.csv')['Pneumonia_pred'].values)
        
      # threshold = __threshold(y_true['Pneumonia_RSNA'].values, y_pred['Pneumonia_pred'].values)
      
      auroc, tpr, fnr, tnr, fpr, ppv, npv, fomr, tn, fp, fn, tp = __metrics_binary(y_true['Pneumonia_RSNA'].values, y_pred['Pneumonia_pred'].values, threshold)
        
      results += [[target_sex, target_age, trial, rate, np.nan, np.nan, auroc, tpr, fnr, tnr, fpr, ppv, npv, fomr, tn, fp, fn, tp]]

      for dem_sex in ['M', 'F']:
        y_true_t = y_true[y_true['Sex'] == dem_sex]
        y_pred_t = y_pred[y_pred['path'].isin(y_true_t['path'])]
        
        auroc, tpr, fnr, tnr, fpr, ppv, npv, fomr, tn, fp, fn, tp = __metrics_binary(y_true_t['Pneumonia_RSNA'].values, y_pred_t['Pneumonia_pred'].values, threshold)
        auroc, tpr, fnr, tnr, fpr, ppv, npv, fomr, tn, fp, fn, tp = __metrics_binary(y_true_t['Pneumonia_RSNA'].values, y_pred_t['Pneumonia_pred'].values, threshold)
          
        results += [[target_sex, target_age, trial, rate, dem_sex, np.nan, auroc, tpr, fnr, tnr, fpr, ppv, npv, fomr, tn, fp, fn, tp]]
      
      for dem_age in ['0-20', '20-40', '40-60', '60-80', '80+']:
        y_true_t = y_true[y_true['Age_group'] == dem_age]
        y_pred_t = y_pred[y_pred['path'].isin(y_true_t['path'])]
        
        auroc, tpr, fnr, tnr, fpr, ppv, npv, fomr, tn, fp, fn, tp = __metrics_binary(y_true_t['Pneumonia_RSNA'].values, y_pred_t['Pneumonia_pred'].values, threshold)
        auroc, tpr, fnr, tnr, fpr, ppv, npv, fomr, tn, fp, fn, tp = __metrics_binary(y_true_t['Pneumonia_RSNA'].values, y_pred_t['Pneumonia_pred'].values, threshold)
          
        results += [[target_sex, target_age, trial, rate, np.nan, dem_age, auroc, tpr, fnr, tnr, fpr, ppv, npv, fomr, tn, fp, fn, tp]]
          
      for dem_sex in ['M', 'F']:
        for dem_age in ['0-20', '20-40', '40-60', '60-80', '80+']:
          y_true_t = y_true[(y_true['Sex'] == dem_sex) & (y_true['Age_group'] == dem_age)]
          y_pred_t = y_pred[y_pred['path'].isin(y_true_t['path'])]
          
          auroc, tpr, fnr, tnr, fpr, ppv, npv, fomr, tn, fp, fn, tp = __metrics_binary(y_true_t['Pneumonia_RSNA'].values, y_pred_t['Pneumonia_pred'].values, threshold)
          auroc, tpr, fnr, tnr, fpr, ppv, npv, fomr, tn, fp, fn, tp = __metrics_binary(y_true_t['Pneumonia_RSNA'].values, y_pred_t['Pneumonia_pred'].values, threshold)
            
          results += [[target_sex, target_age, trial, rate, dem_sex, dem_age, auroc, tpr, fnr, tnr, fpr, ppv, npv, fomr, tn, fp, fn, tp]]
        
  return results
  
def analyze_aim_2(model, test_data):
  results = []
  for sex in tqdm(['M', 'F'], desc='Sex'):
    results += __analyze_aim_2(model, test_data, sex, None)
  for age in tqdm(['0-20', '20-40', '40-60', '60-80', '80+'], desc='Age'):
    results += __analyze_aim_2(model, test_data, None, age)
  if model == 'densenet':
    for sex in tqdm(['M', 'F'], desc='Sex', position=0):
      for age in tqdm(['0-20', '20-40', '40-60', '60-80', '80+'], desc='Sex', position=1, leave=False):
        results += __analyze_aim_2(model, test_data, sex, age)
  for sex in tqdm(['M', 'F'], desc='Sex'):
    results += __analyze_aim_2(model, test_data, sex, None)
  for age in tqdm(['0-20', '20-40', '40-60', '60-80', '80+'], desc='Age'):
    results += __analyze_aim_2(model, test_data, None, age)
  if model == 'densenet':
    for sex in tqdm(['M', 'F'], desc='Sex', position=0):
      for age in tqdm(['0-20', '20-40', '40-60', '60-80', '80+'], desc='Sex', position=1, leave=False):
        results += __analyze_aim_2(model, test_data, sex, age)

  results = np.array(results)
  df = pd.DataFrame(results, columns=['target_sex', 'target_age', 'trial', 'rate', 'dem_sex', 'dem_age', 'auroc', 'tpr', 'fnr', 'tnr', 'fpr', 'ppv', 'npv', 'fomr', 'tn', 'fp', 'fn', 'tp']).sort_values(['target_sex', 'target_age', 'trial', 'rate'])
  df.to_csv(f'results/aim_2/{model}/{test_data}_summary.csv', index=False)
  df.to_csv(f'results/aim_2/{model}/{test_data}_summary.csv', index=False)