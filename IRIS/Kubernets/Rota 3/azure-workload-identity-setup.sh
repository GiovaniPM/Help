#!/usr/bin/env bash
# Anexo B — provisionamento do lado Azure (Rota 3)
# Pré-requisito: az login realizado com permissão para criar identidades,
# role assignments e (opcionalmente) habilitar OIDC/Workload Identity no AKS.
set -euo pipefail

RESOURCE_GROUP="rg-iris"
LOCATION="brazilsouth"
AKS_CLUSTER="aks-iris"
UAMI_NAME="iris-workload-identity"
NAMESPACE="iko"
SERVICE_ACCOUNT="iris-cloud-ops"
KEY_VAULT="iris-kv"
STORAGE_ACCOUNT="irisbackups"
ACR_NAME="acriris"

# 6.1 — habilitar OIDC issuer e Workload Identity no cluster existente
az aks update \
  --resource-group "$RESOURCE_GROUP" \
  --name "$AKS_CLUSTER" \
  --enable-oidc-issuer \
  --enable-workload-identity

# 6.2 — obter a URL do issuer OIDC do cluster
AKS_OIDC_ISSUER=$(az aks show \
  --resource-group "$RESOURCE_GROUP" \
  --name "$AKS_CLUSTER" \
  --query "oidcIssuerProfile.issuerUrl" -o tsv)
echo "OIDC issuer: $AKS_OIDC_ISSUER"

# 6.3 — criar a User-Assigned Managed Identity (UAMI)
az identity create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$UAMI_NAME" \
  --location "$LOCATION"

UAMI_CLIENT_ID=$(az identity show \
  --resource-group "$RESOURCE_GROUP" \
  --name "$UAMI_NAME" \
  --query "clientId" -o tsv)
UAMI_PRINCIPAL_ID=$(az identity show \
  --resource-group "$RESOURCE_GROUP" \
  --name "$UAMI_NAME" \
  --query "principalId" -o tsv)
echo "UAMI clientId: $UAMI_CLIENT_ID"

# 6.5 — criar a Federated Identity Credential, vinculando a UAMI
#        à ServiceAccount system:serviceaccount:<namespace>:<nome>
az identity federated-credential create \
  --name "iris-cloud-ops-federation" \
  --identity-name "$UAMI_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --issuer "$AKS_OIDC_ISSUER" \
  --subject "system:serviceaccount:${NAMESPACE}:${SERVICE_ACCOUNT}" \
  --audience "api://AzureADTokenExchange"

# 6.6 — atribuir papéis RBAC do Azure à UAMI (escopo mínimo necessário)
KEY_VAULT_ID=$(az keyvault show --name "$KEY_VAULT" --query id -o tsv)
STORAGE_ACCOUNT_ID=$(az storage account show --name "$STORAGE_ACCOUNT" --query id -o tsv)

az role assignment create \
  --assignee-object-id "$UAMI_PRINCIPAL_ID" \
  --assignee-principal-type ServicePrincipal \
  --role "Key Vault Secrets User" \
  --scope "$KEY_VAULT_ID"

az role assignment create \
  --assignee-object-id "$UAMI_PRINCIPAL_ID" \
  --assignee-principal-type ServicePrincipal \
  --role "Storage Blob Data Contributor" \
  --scope "$STORAGE_ACCOUNT_ID"

# 6.10 (opcional) — anexar o ACR ao cluster para pull de imagem via
#                   identidade do nó (kubelet identity), sem relação com
#                   a Workload Identity usada pelos Jobs acima
az aks update \
  --resource-group "$RESOURCE_GROUP" \
  --name "$AKS_CLUSTER" \
  --attach-acr "$ACR_NAME"

echo "UAMI_CLIENT_ID=$UAMI_CLIENT_ID"
echo "Use este valor em iris-serviceaccount.yaml (annotations.azure.workload.identity/client-id)"
