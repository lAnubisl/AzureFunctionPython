cd azure_function
zip -r ../publish.zip .
cd ..

DEPLOYMENT_USER='$func-python-deployment-test'
DEPLOYMENT_PASSWORD='***************************'
DEPLOYMENT_APP='func-python-deployment-test'

CREDENTIALS=$DEPLOYMENT_USER:$DEPLOYMENT_PASSWORD
curl -v -X POST --user $CREDENTIALS --data-binary @"publish.zip" https://$DEPLOYMENT_APP.scm.azurewebsites.net:443/api/zipdeploy
curl -X GET --user $CREDENTIALS https://$DEPLOYMENT_APP.scm.azurewebsites.net:443/deployments