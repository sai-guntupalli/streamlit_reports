

## ENV

conda create -n streamlit_reports python=3.8

conda activate streamlit_reports

pip install streamlit streamlit_analytics streamlit_tags ffn yfinance nsetools pandas dash plotly seaborn matplotlib black


## Run the application

streamlit run app.py --logger.level=debug