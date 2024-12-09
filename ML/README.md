# Instructions
## Environment
Set up conda environment with the following requirements
- Python 3.9.20
- matplotlib 3.4.3 (You can use the provided .whl file for installation)
## train.ipynb
The file includes the following codes.
```
1. Download libraries
2. Download dataset
3. Preprocess dataset by aggregating by minute
4. Train models (including N-Beats, DeepAR, Prophet, and TCN) 
```

## Note
If you want to use pytorch-forecasting for DeepAR model, download the pytorch-forecasting.zip in our Google Drive, unzip it, and put the unzipped folder under the same directory with train.ipynb.
