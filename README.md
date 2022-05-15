# DockerDeOldify

DockerDeOldify is a backend server who colorize and restore old images deployed by docker on aws. 

The server do the colorization by [Deoldify][https://github.com/jantic/DeOldify]

To run the project, you need to prepare:

1. A server instance with at least 12GB memory (virtual memory is accepted)

2. AWS s3 service 
3. docker and docker-compose tools
4. ssl certificate

Then type the following commands:

1.Build docker instances:

```shell
sudo bash build_docker.sh
```

2.run Docker 

```shell
sudo docker-compose -f docker-compose.yml up -d
```

