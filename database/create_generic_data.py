import pandas as pd
import random

# Waschen, Schleudern, Spülen, Pumpen

states = ["Waschen", "Schleudern", "Spülen", "Pumpen"]
states_dic = {state:states.index(state) for state in states}

timestamp = 0
dataset = []

def create_dataset(state):
    global timestamp
    global dataset

    for n in range(0, 50):
        AX = random.randint(0, 10)
        AY = random.randint(0, 10)
        AZ = random.randint(0, 10)

        dataset.append((timestamp, AX, AY, AZ, state))
        timestamp += 1
    return dataset

# timestamp, AX, AY, AZ, state
for state in states:
    create_dataset(states_dic[state])

df = pd.DataFrame(data = dataset, columns = ["timestamp", "AX", "AY", "AZ", "state"])
print(df)