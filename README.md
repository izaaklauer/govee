# govee

govee sensor scraper


## Build command

Probably this:
```
docker buildx build --push --platform 'linux/amd64,linux/arm64' -t atuin.izaaklauer.com:5000/govee:`git rev-parse --short HEAD` .
```

## Deploy
After you build (and push), get the current sha
```commandline
git rev-parse --short HEAD | tr -d '\n' | pbcopy
```
And add it to atuin/ansible/govee/govee.service. 

Then run (from inside atuin):
```commandline
ansible-playbook -u ubuntu -i hosts.ini deploy.yml 
```

