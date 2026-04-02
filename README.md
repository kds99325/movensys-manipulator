# Host Environment Setup

## 1. Bashrc Configuration
- Add the following environment variables to your `~/.bashrc`:
```
export ROS_DOMAIN_ID=73
export HOST_USER_UID=$(id -u)
export HOST_USER_GID=$(id -g)
```
```
source ~/.bashrc
```

## 2. Set CycloneDDS buffer
```
sudo tee /etc/sysctl.d/99-network-buffers.conf << 'EOF'
net.core.rmem_max=67108864
net.core.rmem_default=67108864
net.core.wmem_max=67108864
net.core.wmem_default=67108864
EOF

sudo sysctl -p /etc/sysctl.d/99-network-buffers.conf
sysctl net.core.rmem_max net.core.rmem_default net.core.wmem_max net.core.wmem_default
```

## 4. Clone Repository
```
git clone https://github.com/movensys/movensys-manipulator.git
```

## 5. How to run
Please check the `doc/` folder to know how to run it.