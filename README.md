# Homelab

Right now it is just one raspberry pi with 1 SSD via USB.

## Requirements

1. Docker 26.1.4 (because docker 27 has a bug)
   1. [docker swarm invalid pool request: Pool](https://github.com/moby/moby/issues/48069)
2. Docker Swarm
3. Python 3
4. MicroCeph (Later) -- Storage
   1. Require 3 nodes
   2. [https://canonical-microceph.readthedocs-hosted.com/en/latest/](https://canonical-microceph.readthedocs-hosted.com/en/latest/)
5. GlusterFS (Simpler) -- Storage
   1. [https://thenewstack.io/tutorial-deploy-a-highly-availability-glusterfs-storage-cluster/](https://thenewstack.io/tutorial-deploy-a-highly-availability-glusterfs-storage-cluster/)

## Installation

```sh
curl -fsSL https://get.docker.com -o install-docker.sh
sudo sh install-docker.sh --version 26.1.4

docker swarm init --advertise-addr <advertising address>
python main.py deploy jellyfin arr filebrowser portainer registry caddy
```

## Uninstallation

```sh
docker node update --availability drain raspberrypi
python main.py remove jellyfin arr filebrowser portainer registry caddy

# Using https://learnubuntu.com/uninstall-docker/ docs
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
docker rmi $(docker images -a -q)
docker network prune
docker system prune -a
sudo apt remove docker-* --auto-remove
sudo rm -rf /var/lib/docker
sudo groupdel docker
sudo rm -rf /var/run/docker.sock
sudo rm -rf /usr/local/bin/docker-compose && sudo rm -rf /etc/docker && sudo rm -rf ~/.docker
```

### Tooling

```sh
docker node update --label-add node=prime raspberrypi
# docker network create --driver overlay --attachable --scope swarm vpn-proxy
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder # clear DNS
docker network create reverse-proxy --scope swarm --driver overlay
docker node ps --no-trunc
docker stack ls
docker stack rm <stack_name>
docker services ls
docker service ps
docker service ps <stack>_<container> --no-trunc
docker service logs -f <stack>_<container>
docker service inspect <stack>_<container> --format pretty
sudo docker service update --cap-add NET_ADMIN <stack>_<container>
docker info

# rsync config to node
brew install rsync
rsync -avPz -e ssh $PWD/./ <user>@<host></host>:<path>

# rsync -avPz -e ssh $PWD/./ brunobernard@raspberrypi.local:/home/brunobernard/stack

# build to registry
 docker build -t caddy-cloudflare-dns:latest caddy/
 docker tag caddy-cloudflare-dns registry.home.brunobernard.dev/caddy-cloudflare-dns
 docker push brunobernard.dev/caddy-cloudflare-dns
```
