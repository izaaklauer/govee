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


## Clearing data
```commandline
docker exec -it influxdb influx delete --token=mkNcosqLwjIRwz5C64slCI6sjxPw65Dogtt5qBBz4Dp6vMQQo95DpUAJwLgb-3_MQcQUQrSVCfdOhebrGp8s0A== --org=cenazoa --bucket=cenazoa --start '1970-01-01T00:00:00Z' --stop $(date --utc +"%Y-%m-%dT%H:%M:%SZ") --predicate '_measurement="roof_solar"'
```

or
```
docker exec -it influxdb influx delete --token=mkNcosqLwjIRwz5C64slCI6sjxPw65Dogtt5qBBz4Dp6vMQQo95DpUAJwLgb-3_MQcQUQrSVCfdOhebrGp8s0A== --org=cenazoa --bucket=cenazoa --start '1970-01-01T00:00:00Z' --stop $(date --utc +"%Y-%m-%dT%H:%M:%SZ") --predicate 'govee_version="undefined"'
```
