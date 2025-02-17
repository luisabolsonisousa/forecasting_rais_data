import re
import os
import glob
import numpy as np
import pandas as pd
from unidecode import unidecode

def remove_invalid_rows(df, column, invalid_values):
    """
    Remove rows with invalid values in a specified column.

    Args:
        df (pd.DataFrame): The input dataframe.
        column (str): The column to check for invalid values.
        invalid_values (list): List of values to be removed.

    Returns:
        pd.DataFrame: The cleaned dataframe.
    """
    return df[~df[column].isin(invalid_values)]

def clean_column_names(df):
    """
    Clean column names by removing numbers and trailing decimals.

    Args:
        df (pd.DataFrame): The input dataframe.

    Returns:
        pd.DataFrame: Dataframe with cleaned column names.
    """
    df.columns = [re.sub(r'^\s*\d+:', '', re.sub(r'\.\d+\s*$', '', col)) for col in df.columns]
    return df

def initial_cleaning(df):
    """
    Perform initial data processing on the dataframe.

    Steps:
    - Remove rows after the first occurrence of "{ñ class}" in the "Capital" column.
    - Adjust misaligned top row.
    - Remove rows with invalid or total values.
    - Convert "NaN" strings to actual NaN values.
    - Fill missing values in the "Capital" column.
    - Extract only the capital name, removing preceding text.
    - Drop columns containing "Total" or "Ignored".
    - Clean column names.

    Args:
        df (pd.DataFrame): The input dataframe.

    Returns:
        pd.DataFrame: The processed dataframe.
    """
    first_invalid_index = df[df['Capital'] == "{ñ class}"].index[0]
    
    df = df.iloc[:first_invalid_index].copy()

    df.iloc[0, 1:] = df.iloc[0, :-1].values

    df = remove_invalid_rows(df, ' Faixa Remun Média (SM)', ['{ñ class}']) 
    
    df = df.replace("NaN", np.nan)
    
    df['Capital'] = df['Capital'].ffill()
    
    # Ensure 'Capital' is treated as string before using .str methods
    df['Capital'] = df['Capital'].str.split(':').str[1]

    df = remove_invalid_rows(df, ' Faixa Remun Média (SM)', ['Total']) 
    
    df = df.drop(columns=df.filter(like='Total').columns, errors='ignore')
    df = df.drop(columns=df.filter(like='Ignorado').columns, errors='ignore')
    
    df = clean_column_names(df)
    
    return df

def create_gender_df(df, year, gender):
    """
    Create a dataframe filtered by gender, keeping relevant columns.

    Args:
        df (pd.DataFrame): The input dataframe.
        year (int): The year to be added to the dataframe.
        gender (str): Gender keyword to filter columns ("Masculino" or "Feminino").

    Returns:
        pd.DataFrame: The filtered and cleaned dataframe for the specified gender.
    """
    gender_cols = ['Capital', ' Faixa Remun Média (SM)'] + [col for col in df.columns if gender in col]
    df_gender = df[gender_cols]
    df_gender.iloc[0, 0] = "capital"
    df_gender.iloc[0, 1] = "faixa_remuneracao_media_sm"
    
    # Set first row as header
    new_header = df_gender.iloc[0]
    df_gender = df_gender[1:]
    df_gender.columns = new_header 
    
    # Remove duplicate columns
    df_gender = df_gender.loc[:, ~df_gender.columns.duplicated()]
    df_gender["sexo"] = "M" if gender == "Masculino" else "F"
    df_gender["ano"] = year
    
    # Clean column names
    df_gender = clean_column_names(df_gender)
    
    # Remove columns containing "Total" or "{ñ class}"
    df_gender = df_gender.drop(columns=df_gender.filter(like='Total').columns, errors='ignore')
    df_gender = df_gender.drop(columns=df_gender.filter(like='{ñ class}').columns, errors='ignore')
    
    return df_gender

def final_adjustments(df_final, cols_exclude = ['faixa_remuneracao_media_sm', 'capital', 'sexo', 'ano']):
    """
        Perform final adjustments to the processed dataframe, including formatting and type conversion.

        Steps:
        - Remove unwanted columns.
        - Normalize text format (lowercase, replace spaces and special characters).
        - Convert numerical columns to integer format.

        Args:
            df_final (pd.DataFrame): The dataframe to be adjusted.
            cols_exclude (list): List of columns to exclude from numeric conversion.

        Returns:
            pd.DataFrame: The adjusted dataframe.
        """

    # adjust the columns typing and content
    df_final = df_final.drop(columns=df_final.filter(like='{ñ class}').columns, errors='ignore')
    df_final['faixa_remuneracao_media_sm'] = df_final['faixa_remuneracao_media_sm'].apply(lambda x: unidecode(str(x)))
    df_final['capital'] = df_final['capital'].apply(lambda x: unidecode(str(x)))
    df_final['faixa_remuneracao_media_sm'] = df_final['faixa_remuneracao_media_sm'].str.replace(' ', '_')
    df_final['capital'] = df_final['capital'].str.replace('-', '_').str.replace(' ', '_')
    df_final['faixa_remuneracao_media_sm'] = df_final['faixa_remuneracao_media_sm'].str.lower()
    df_final['capital'] = df_final['capital'].str.lower()
    


    # adjust relevant columns content to int type
    for col in df_final.columns:
        if col not in cols_exclude:
            df_final[col] = df_final[col].astype(str).str.replace('.', '')
            df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0).astype(int)
    
    #Extract capital code to dataframe
    # Ensure capital column is string before applying transformations
    df_final['capital'] = df_final['capital'].astype(str)
    # Extract capital code ensuring robustness
    df_final[['capital', 'capital_code']] = df_final['capital'].str.extract(r'^(.*?)_{1,}([a-zA-Z]+)$', expand=True)

    # Extract sm_code by keeping only the first numeric value in the salary range
    df_final['sm_code'] = df_final['faixa_remuneracao_media_sm'].str.extract(r'(\d+)')
    df_final['sm_code'] = pd.to_numeric(df_final['sm_code'], errors='coerce').fillna(0).astype(int)
    # Keep only the portion of 'faixa_remuneracao_media_sm' after the colon
    df_final['faixa_remuneracao_media_sm'] = df_final['faixa_remuneracao_media_sm'].str.split(':').str[-1]
    



    return df_final
