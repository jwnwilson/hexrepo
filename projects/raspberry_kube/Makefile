TEMPORAL_NS ?= default
TEMPORAL_DB_STS := temporal-db
TEMPORAL_SERVER_DEPLOYS := temporal temporal-ui
TEMPORAL_WORKER_DEPLOY := temporal-worker
TEMPORAL_WORKER_REPLICAS ?= 2
ROLLOUT_TIMEOUT ?= 300s

.PHONY: temporal-up temporal-down temporal-status

## Scale Temporal back up: DB first, then server/UI, then workers
temporal-up:
	kubectl scale sts $(TEMPORAL_DB_STS) --replicas=1 -n $(TEMPORAL_NS)
	kubectl rollout status sts/$(TEMPORAL_DB_STS) -n $(TEMPORAL_NS) --timeout=$(ROLLOUT_TIMEOUT)
	kubectl scale deploy $(TEMPORAL_SERVER_DEPLOYS) --replicas=1 -n $(TEMPORAL_NS)
	kubectl rollout status deploy/temporal -n $(TEMPORAL_NS) --timeout=$(ROLLOUT_TIMEOUT)
	kubectl scale deploy $(TEMPORAL_WORKER_DEPLOY) --replicas=$(TEMPORAL_WORKER_REPLICAS) -n $(TEMPORAL_NS)
	kubectl rollout status deploy/$(TEMPORAL_WORKER_DEPLOY) -n $(TEMPORAL_NS) --timeout=$(ROLLOUT_TIMEOUT)

## Scale Temporal to zero (data in the temporal-db PVC is kept)
temporal-down:
	kubectl scale deploy $(TEMPORAL_SERVER_DEPLOYS) $(TEMPORAL_WORKER_DEPLOY) --replicas=0 -n $(TEMPORAL_NS)
	kubectl scale sts $(TEMPORAL_DB_STS) --replicas=0 -n $(TEMPORAL_NS)

## Show Temporal workload replica counts
temporal-status:
	kubectl get deploy/temporal deploy/temporal-ui deploy/$(TEMPORAL_WORKER_DEPLOY) sts/$(TEMPORAL_DB_STS) -n $(TEMPORAL_NS)
