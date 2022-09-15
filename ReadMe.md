# Installation
The application was written using Python 3.10.5 and Visual Studio Code. Installing the latest release of Python and adding it to path is required to run the program. Pylance from the VS Code modules is recommended.

Before running the application, the latest release of the following packages must be installed:

    1.  Pandas
    2.  Plotly & plotly express
    3.  NLTK
    4.  NLTK corpus
    5.  dash
    6.  dash_auth
    7.  xlsxwriter
    8.  Jupyter Labs
    9.  Wordcloud
    10. matplotlib
    11. openpyxl
    12. numpy
    13. seaborn

___
# User Guide

The Raw Data folder contains the data used for this application in .tsv and .csv format. The unused data folder contains a readme from the source, as well as some data which is not needed by the application. Data output after the data cleaning method is run and after multilabel classification has been applied can be found in the Cleaned Data folder.

To run the application, open the app.ipynb file using Jupyter Labs or Jupyter Notebook after installing the necessary packages. The cells will run the data cleaner and multilevel classification. This can take up to 45 minutes. It is recommended to run this only one time. After the first run, data will be exported to the Cleaned Data folder. These will be referenced by the notebook rather than the dataframe produced by the multilevel classification. 

Multilevel classification can also be handled by executing the MultiLabelClassification.py file. However, this has been included for later integration with HSS's streaming system. This should be run on a weekly or monthly basis.

The user login references config.json for the user credentials. In the test environment, please log in using username: username and password: password. Editing this file must be done in the github repo to alter lgoin credentials.
___
# Maintanence
The classification should be run on a set basis to support the business need at HSS. Updating the config.json file in the github repo will allow other users to access the interactive dashboard. However, it is recommended that a security group be created for integration with HSS on-pem authentication services.

Maintanence for the application is minimal. Bugs should be addressed in the source repo. The data supporting the application should be updated on a regular basis. Regular accuracy tests should be done using the .ipynb file to ensure the validity of the data model.
___
