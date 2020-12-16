@echo off
docker pull erpya/adempiere-grpc-all-in-one
docker pull erpya/proxy-adempiere-api
docker pull erpya/adempiere-vue
docker run -it -d --name Proxy-ADempiere-API -p 8085:8085 -e "ES_PORT=9200" -e "ES_HOST=localhost" -e "SERVER_PORT=8085" -e "SERVER_HOST=localhost" -e "AD_BUSINESSHOST=localhost" -e "AD_ACCESSHOST=localhost" -e "AD_DICTIONARYHOST=localhost" -e "AD_ACCESSAPIHOST=localhost" -e "AD_STOREHOST=localhost" -e "VS_ENV=dev" erpya/proxy-adempiere-api
docker run -d -it --name adempiere-grpc-all-in-one -p 50059:50059 erpya/adempiere-grpc-all-in-one
docker run -it --name adempiere-vue -p 9526:9526 -e VUE_APP_API_REST_ADDRESS="http://localhost" -e VUE_APP_API_REST_PORT=8085 erpya/adempiere-vue