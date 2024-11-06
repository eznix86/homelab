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
   # Docker Swarm Setup and Management Documentation

## Table of Contents
- [Installation](#installation)
- [Uninstallation](#uninstallation)
- [Management Commands](#management-commands)
  - [Node Management](#node-management)
  - [Network Management](#network-management)
  - [Service Management](#service-management)
  - [Stack Management](#stack-management)
  - [System Information](#system-information)
  - [Remote Management](#remote-management)
  - [Registry Management](#registry-management)

   ## Installation

   Install Docker and initialize a Swarm cluster:

   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com -o install-docker.sh
   sudo sh install-docker.sh --version 26.1.4

   # Initialize Docker Swarm
   docker swarm init --advertise-addr <advertising address>

   # Deploy common services
   python main.py deploy jellyfin arr filebrowser portainer registry caddy aria2 pihole vitodeploy
   ```

   ## Uninstallation

   Follow these steps to completely remove Docker and all associated components:

   ```bash
   # 1. Drain the node
   docker node update --availability drain raspberrypi

   # 2. Remove deployed services
   python main.py remove jellyfin arr filebrowser portainer registry caddy aria2 pihole vitodeploy

   # 3. Clean up containers and images
   docker stop $(docker ps -a -q)
   docker rm $(docker ps -a -q)
   docker rmi $(docker images -a -q)
   docker network prune
   docker system prune -a

   # 4. Remove Docker packages
   sudo apt remove docker-* --auto-remove

   # 5. Remove Docker files and directories
   sudo rm -rf /var/lib/docker
   sudo groupdel docker
   sudo rm -rf /var/run/docker.sock
   sudo rm -rf /usr/local/bin/docker-compose
   sudo rm -rf /etc/docker
   sudo rm -rf ~/.docker
   ```

   ## Management Commands

   ### Node Management
   ```bash
   # Add label to node
   docker node update --label-add node=prime raspberrypi
   ```

   ### Network Management
   ```bash
   # Create overlay network for reverse proxy
   docker network create reverse-proxy --scope swarm --driver overlay

   # Clear DNS cache (macOS)
   sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
   ```

   ### Service Management
   ```bash
   # View service information
   docker service ps <stack>_<container> --no-trunc
   docker service logs -f <stack>_<container>
   docker service inspect <stack>_<container> --format pretty

   # Update service capabilities
   sudo docker service update --cap-add NET_ADMIN <stack>_<container>
   ```

   ### Stack Management
   ```bash
   # List and remove stacks
   docker stack ls
   docker stack rm <stack_name>

   # List services
   docker services ls
   docker service ps
   ```

   ### System Information
   ```bash
   # View Docker system information
   docker info
   docker node ps --no-trunc
   ```

   ### Remote Management
   ```bash
   # Install rsync (macOS)
   brew install rsync

   # Sync configuration to remote node
   rsync -avPz -e ssh $PWD/./ <user>@<host>:<path>
   # Example:
   # rsync -avPz -e ssh $PWD/./ brunobernard@home.brunobernard.dev:/home/brunobernard/homelab
   ```

   ### Registry Management
   ```bash
   # Build and push to private registry
   docker build -t caddy-cloudflare-dns:latest caddy/
   docker tag caddy-cloudflare-dns registry.home.brunobernard.dev/caddy-cloudflare-dns
   docker push brunobernard.dev/caddy-cloudflare-dns
   ```
