
# The script MUST contain a function named azureml_main
# which is the entry point for this module.

# imports up here can be used to
import json
import pandas as pd
import re

def azureml_main(dataframe1 = None, dataframe2 = None):

    parsed_data = []

    # Loop through each row in the DataFrame
    for index, row in dataframe1.iterrows():
        game_id = row['id']
        member_id = int(row['member'].split(',')[0].split(':')[1].strip())
        rating = row['rating']

        parsed_data.append({
                    'user_id': member_id,
                    'game_id': game_id,
                    'rating': rating
            })
        
        if isinstance(row['guests'], str) and row['guests'].strip():
        # Handle case where guests is a string
                matches = re.findall(r'id:(\d+)', row['guests'])
                for pass_id in matches:
                    parsed_data.append({
                        'user_id': pass_id,
                        'game_id': game_id,
                        'rating': rating
                    })
        


    # Convert the parsed data into a pandas DataFrame
    dataframe1 = pd.DataFrame(parsed_data)

    
    return dataframe1,

