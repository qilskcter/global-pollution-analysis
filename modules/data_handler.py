import pandas as pd
import glob
import os
import streamlit as st

@st.cache_data
def process_air_data(file_source):
    df = pd.read_csv(file_source)
    df = df.interpolate(method='linear').ffill().bfill()
    if 'AQI Value' in df.columns:
        Q1 = df['AQI Value'].quantile(0.25)
        Q3 = df['AQI Value'].quantile(0.75)
        IQR = Q3 - Q1
        df = df[(df['AQI Value'] >= (Q1 - 1.5 * IQR)) & (df['AQI Value'] <= (Q3 + 1.5 * IQR))]
    return df

def find_all_csv():
    return glob.glob("*.csv") + glob.glob("**/*.csv", recursive=True)

def get_continent_from_country(country_name):
    continents = {
        'Châu Á': [
            'Afghanistan', 'Armenia', 'Azerbaijan', 'Bahrain', 'Bangladesh', 'Bhutan', 
            'Cambodia', 'China', 'Georgia', 'India', 'Indonesia', 'Iran (Islamic Republic of)', 
            'Iraq', 'Israel', 'Japan', 'Jordan', 'Kazakhstan', 'Kuwait', 'Kyrgyzstan', 
            "Lao People's Democratic Republic", 'Lebanon', 'Malaysia', 'Maldives', 
            'Mongolia', 'Myanmar', 'Nepal', 'Oman', 'Pakistan', 'Philippines', 'Qatar', 
            'Republic of Korea', 'Saudi Arabia', 'Singapore', 'Sri Lanka', 'State of Palestine', 
            'Syrian Arab Republic', 'Tajikistan', 'Thailand', 'Turkey', 'Turkmenistan', 
            'United Arab Emirates', 'Uzbekistan', 'Viet Nam', 'Yemen'
        ],
        'Châu Âu': [
            'Albania', 'Andorra', 'Austria', 'Belarus', 'Belgium', 'Bosnia and Herzegovina', 
            'Bulgaria', 'Croatia', 'Cyprus', 'Czechia', 'Denmark', 'Estonia', 'Finland', 
            'France', 'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy', 
            'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Monaco', 'Montenegro', 
            'Netherlands', 'Norway', 'Poland', 'Portugal', 'Republic of Moldova', 
            'Republic of North Macedonia', 'Romania', 'Russian Federation', 'Serbia', 
            'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'Ukraine', 
            'United Kingdom of Great Britain and Northern Ireland'
        ],
        'Bắc Mỹ': [
            'Aruba', 'Barbados', 'Belize', 'Canada', 'Costa Rica', 'Cuba', 'Dominican Republic', 
            'El Salvador', 'Guatemala', 'Haiti', 'Honduras', 'Jamaica', 'Mexico', 
            'Nicaragua', 'Panama', 'Saint Kitts and Nevis', 'Saint Lucia', 
            'Trinidad and Tobago', 'United States of America'
        ],
        'Nam Mỹ': [
            'Argentina', 'Bolivia (Plurinational State of)', 'Brazil', 'Chile', 'Colombia', 
            'Ecuador', 'Guyana', 'Paraguay', 'Peru', 'Suriname', 'Uruguay', 
            'Venezuela (Bolivarian Republic of)'
        ],
        'Châu Phi': [
            'Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cabo Verde', 
            'Cameroon', 'Central African Republic', 'Chad', 'Comoros', 'Congo', "Côte d'Ivoire", 
            'Democratic Republic of the Congo', 'Egypt', 'Equatorial Guinea', 'Eritrea', 
            'Ethiopia', 'Gabon', 'Gambia', 'Ghana', 'Guinea', 'Guinea-Bissau', 'Kenya', 
            'Kingdom of Eswatini', 'Lesotho', 'Liberia', 'Libya', 'Madagascar', 'Malawi', 
            'Mali', 'Mauritania', 'Mauritius', 'Morocco', 'Mozambique', 'Namibia', 'Niger', 
            'Nigeria', 'Rwanda', 'Senegal', 'Seychelles', 'Sierra Leone', 'Somalia', 
            'South Africa', 'South Sudan', 'Sudan', 'Togo', 'Tunisia', 'Uganda', 
            'United Republic of Tanzania', 'Zambia', 'Zimbabwe'
        ],
        'Châu Đại Dương': [
            'Australia', 'New Zealand', 'Palau', 'Papua New Guinea', 'Solomon Islands', 'Vanuatu'
        ]
    }
    for continent, countries in continents.items():
        if country_name in countries:
            return continent
    return 'Others'