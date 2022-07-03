# Docker Handbrake Compress Videos

This script use handbrake-cli to compress the video and it is awesome..🤩 

It compresses GB's of files to MB without losing quality.😱 

```bash
# build image
docker build -t hanbrake .
```

So how to use it?🤔

```bash
# docker run -it --rm -v  "path to video source":/input -e FORMAT=mp4 image name
```
### Example

```bash
docker run -it --rm -v /home/loki/Documents/demo:/input -e FORMAT=mp4 hanbrake

```
The above command will compress all the files from the source demo folder and recursively