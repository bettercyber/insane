#!/bin/bash

cd ~/no-name
./ransomwatch.py scrape
./ransomwatch.py parse

ssh-add ~/.ssh/id_rsa
git config user.name lucianaobregon
git config user.email lobregon@bettercyberllc.com
git add --a
git commit -m "updated by bot"
git push origin master

JSON=$(jq -r '.[].locations' groups.json | sed 's/"version": 3/"version": "3"/g' | sed 's/  //g' |  sed 's/"/\\\"/g' | tr -d '\n')
cat ~/no-name/mutation.graphql | /usr/local/bin/gql-cli https://utjcezgxkfexda5vjmlq2g3nq4.appsync-api.us-west-2.amazonaws.com/graphql -H "x-api-key: $API_KEY" --transport appsync_http -V JSON:"$JSON"
