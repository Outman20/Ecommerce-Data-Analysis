import pandas as pd
import matplotlib.pyplot as plt

# E-Commerce Daten 
data = {
    "Tag": ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"],
    "Besucher": [1000, 1200, 900, 1500, 2000, 2500, 1800],
    "Käufe": [50, 60, 40, 90, 120, 150, 110],
    "Umsatz": [500, 600, 400, 900, 1200, 1500, 1100]
}

df = pd.DataFrame(data)

# KPIs berechnen
df["Conversion Rate"] = df["Käufe"] / df["Besucher"]

print("Durchschintt Conversion Rate:", df["Conversion Rate"].mean())
print("Beste Umsatz Tag:", df.loc[df["Umsatz"].idxmax(), "Tag"])
print("Schechtester Tag:", df.loc[df["Umsatz"].idxmin(), "Tag"])

# Visualisierung
plt.figure(figsize=(10,5))
plt.bar(df["Tag"], df["Umsatz"])
plt.title("Umsazt pro Tag")
plt.xlabel("Tag")
plt.ylabel("Umsatz")
plt.show()