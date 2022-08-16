# This function converts the contract value from local currencies to Euro

# The euro_converter takes data frames that are generated from the CSV files by the scraper function. 
# The input data frame must have a "Value" column with a numerical value
# and a "Currency" column that contains a ISO 4217 Three Letter Currency Code.
# The function will return the inserted data frame with an extra column that contains only Euro Values

def convert(df):
    import requests
    import pandas as pd

    # Rates By Exchange Rate API "https://www.exchangerate-api.com"
    # 
    url = 'https://api.exchangerate-api.com/v4/latest/EUR'
    
    # The data variable contains 160 exchange rates for Euro (in a dictionary format)
    data = requests.get(url).json()

    # A new column ['Value in EUR'] is created
                        # The local currency value ['Value'] is devided by the exchange rate
                                        # The applicable currency exchange rate is retrived with the map() function from the dictionary   
    df['Value in EUR'] = df['Value'] / df['Currency'].map(data['rates'])

    # The newly created Values in EUR are rounded (2 decimals)
    df['Value in EUR'] = df['Value in EUR'].round(decimals = 2)
    
    # Return of the modified data frame
    return df
