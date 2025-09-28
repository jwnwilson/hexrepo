export ECR_REGISTRY=675468650888.dkr.ecr.eu-west-1.amazonaws.com
# Hardcoded to user with minimal permissions
export ACCESS_KEY_ID="AKIAZ2RIRVGEL645ZLJD"
export SECRET_ACCESS_KEY="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"
export REGION=eu-west-1

kubectl delete secret --ignore-not-found ecr-secret-helper
kubectl create secret generic ecr-secret-helper \
  --save-config \
  --dry-run=client \
  --from-literal=AWS_ACCESS_KEY_ID=$ACCESS_KEY_ID \
  --from-literal=AWS_SECRET_ACCESS_KEY=$SECRET_ACCESS_KEY \
  --from-literal=AWS_DEFAULT_REGION=$REGION \
  --from-literal=ECR_REGISTRY=$ECR_REGISTRY \
  -o yaml | kubectl apply -f -