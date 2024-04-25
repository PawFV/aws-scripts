#!/bin/bash

# Usage: ./create_nodegroup.sh <cluster-name> <nodegroup-name> <instance-type> <num-nodes> <min-nodes> <max-nodes>

CLUSTER_NAME=$1
NODEGROUP_NAME=$2
INSTANCE_TYPE=$3
NUM_NODES=$4
MIN_NODES=$5
MAX_NODES=$6

if [ "$#" -ne 6 ]; then
    echo "Usage: $0 <cluster-name> <nodegroup-name> <instance-type> <num-nodes> <min-nodes> <max-nodes>"
    exit 1
fi

echo "Creating a nodegroup in the EKS cluster..."
eksctl create nodegroup \
  --cluster "$CLUSTER_NAME" \
  --name "$NODEGROUP_NAME" \
  --node-type "$INSTANCE_TYPE" \
  --nodes "$NUM_NODES" \
  --nodes-min "$MIN_NODES" \
  --nodes-max "$MAX_NODES" \
  --asg-access

echo "Nodegroup $NODEGROUP_NAME has been created in the $CLUSTER_NAME cluster."