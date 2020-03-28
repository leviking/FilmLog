# Dev
#docker -D run \
#-t -i \
#-v /home/tim/git/filmlog/filmlog:/srv/filmlog.org/filmlog \
#-p 5000:5000 \
#filmlog

# Prod
docker -D run \
-t -i \
-p 5000:80 filmlog
