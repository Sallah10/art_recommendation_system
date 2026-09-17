
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

# Load data
data = pd.read_csv('../interactions.csv')

class InteractionDataset(Dataset):
    def __init__(self, data):
        self.users = torch.tensor(data['user'].values, dtype=torch.long)
        self.artworks = torch.tensor(data['artwork'].values, dtype=torch.long)
        self.labels = torch.tensor(data['liked'].values, dtype=torch.float32)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.users[idx], self.artworks[idx], self.labels[idx]

dataset = InteractionDataset(data)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

# Define model
class CollaborativeFiltering(nn.Module):
    def __init__(self, num_users, num_artworks, embedding_dim=50):
        super(CollaborativeFiltering, self).__init__()
        self.user_embedding = nn.Embedding(num_users, embedding_dim)
        self.artwork_embedding = nn.Embedding(num_artworks, embedding_dim)
        self.fc1 = nn.Linear(embedding_dim * 2, 128)
        self.fc2 = nn.Linear(128, 1)
    
    def forward(self, user, artwork):
        user_emb = self.user_embedding(user)
        artwork_emb = self.artwork_embedding(artwork)
        x = torch.cat([user_emb, artwork_emb], dim=1)
        x = torch.relu(self.fc1(x))
        x = torch.sigmoid(self.fc2(x))
        return x

num_users = data['user'].nunique()
num_artworks = data['artwork'].nunique()
model = CollaborativeFiltering(num_users, num_artworks)

# Train model
criterion = nn.BCELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

for epoch in range(10):
    for users, artworks, labels in dataloader:
        optimizer.zero_grad()
        outputs = model(users, artworks).squeeze()
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

torch.save(model.state_dict(), 'collaborative_filtering_model.pth')