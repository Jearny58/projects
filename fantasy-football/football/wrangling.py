# import libraries
import pandas as pd
pd.options.display.max_columns = None
import numpy as np
import random
import os

# Matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use('ggplot')

# import libraries for scraping
from urllib.request import urlopen
from bs4 import BeautifulSoup

def football_stats(year, statistic):
    '''Function that gather NFL statistics from pro-football-reference.com, according to year and with a specific statistical focuse (i.e. passing, rushing, receiving, etc.)
    '''
    # URL of website, which takes year and statistic
    url = 'https://www.pro-football-reference.com/years/{}/{}.htm'.format(year, statistic)
    # open url and create BeautifulSoup object 
    htm = urlopen(url)
    soup = BeautifulSoup(htm, features='lxml')
    # gather headers for DataFrame
    headers = [th.getText() for th in soup.findAll('tr', limit=2)[0].findAll('th')]
    # exclude the first column as we don't need the ranking order
    headers = headers[1:]
    # gather rows
    rows = soup.findAll('tr')[1:]
    # gather rows and then pull player statistics from rows object
    player_stats = [[td.getText() for td in rows[i].findAll('td')] for i in range(len(rows))]
    # create a new DataFrame with player_stats and headers
    df = pd.DataFrame(player_stats, columns = headers)
    # add year column for reference
    df['year'] = year
    
    return df
    
    
    
    