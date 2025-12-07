#!/bin/bash

cd "/Users/tonythem/Library/CloudStorage/OneDrive-SharedLibraries-e-Share/Product Management - Documents/Product Planning/ᵉShare DevOps Dashboard"

/usr/bin/python3 generate_dashboard.py \
  -c "../ALL Items.csv" \
  -g "../Org Chart.csv" \
  -t Templates \
  -o "../ᵉShare DevOps Dashboard.html"
