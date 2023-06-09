import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.datasets as datasets
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
from torch.utils.tensorboard import SummaryWriter


class Discriminator(nn.Module):
    def __init__(self, in_features):
        super(Discriminator, self).__init__()
        self.disc = nn.Sequential(
            nn.Linear(in_features, 128),
            nn.LeakyReLU(0.1),
            nn.Linear(128,1),
            nn.Sigmoid()
        )
    def forward(self, x):
        return self.disc(x)

class Generator(nn.Module):
    def __init__(self, z_dim, img_dim):
        super().__init__()
        self.gen = nn.Sequential(
            nn.Linear(z_dim, 256),
            nn.LeakyReLU(0.1),
            nn.Linear(256, img_dim),
            nn.Tanh()
        )

    def forward(self, x):
        return self.gen(x)

lr = 3e-4
z_dim = 64
image_dim = 28*28*1
batch_size = 32
num_epochs = 50

disc = Discriminator(image_dim)
gen = Generator(z_dim, image_dim)
fixed_noise = torch.randn((batch_size, z_dim))
transforms = transforms.Compose(
    [transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))] # Although (0.1307,) & (0.3081,) are mean and standard deviation of MNIST dataset respectively.
)
dataset = datasets.MNIST(root="dataset/", transform=transforms, download=True)
loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
opt_disc = optim.Adam(disc.parameters(), lr=lr)
opt_gen = optim.Adam(gen.parameters(), lr=lr)
criterion = nn.BCELoss()
writer_fake = SummaryWriter(f'GANs/runs/GAN_MNIST/fake')
writer_real = SummaryWriter(f'GANs/runs/GAN_MNIST/real')
step = 0

for epoch in range(num_epochs):
    for batch_idx, (real, _) in enumerate(loader):
        real = real.view(-1, 784) #.view(-1) flattens the tensor
        batch_size = real.shape[0]

        # Train Discriminator
        noise = torch.randn(batch_size, z_dim)
        fake = gen(noise)
        disc_real = disc(real).view(-1)
        lossD_real = criterion(disc_real, torch.ones_like(disc_real))

        disc_fake = disc(fake)
        lossD_fake = criterion(disc_fake, torch.zeros_like(disc_fake))
        lossD = (lossD_fake + lossD_real) / 2
        disc.zero_grad()
        lossD.backward(retain_graph = True)
        opt_disc.step()

        # Train generator
        output = disc(fake).view(-1)
        lossG = criterion(output, torch.ones_like(output))
        gen.zero_grad()
        lossG.backward()
        opt_gen.step()

        if batch_idx == 0:
            print(
                f'Epoch [{epoch}/{num_epochs}]',
                f'Loss D: {lossD: .4f}, Loss G: {lossG:.4f}'
            )

            with torch.no_grad():
                fake = gen(fixed_noise).reshape(-1,1,28,28)
                data = real.reshape(-1,1,28,28)
                img_grade_fake = torchvision.utils.make_grid(fake, normalize=True)
                img_grade_real = torchvision.utils.make_grid(
                    data, normalize=True)
                writer_fake.add_image(
                    "MNIST Fake Images", img_grade_fake, global_step=step
                )
                writer_real.add_image(
                    "MNIST Real Images", img_grade_real, global_step=step
                )
                step += 1