import pandas as pd


columns = [
    "row_id","Name","Link","Address","Price_per_month","Distance","Duration_per_week",
    "Group_Size","Trainer_Coach","Equipment_Provided","Food_Drinks","Period","Custom"
]

# Leeres DataFrame
df = pd.DataFrame(columns=columns)

# Speichern
path = "Data/Activitys.csv"
df.to_csv(path, index=False)

path