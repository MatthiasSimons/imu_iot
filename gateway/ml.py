import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sklearn
import gateway

database = gateway.Training(database = "monitoring",collection = "ml_training")

df = database.query()
df = df[df.label != "test"]



print(df)