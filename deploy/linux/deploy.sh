#!/bin/bash
set -euo pipefail

/opt/app/deploy/linux/setup_env.sh
systemctl daemon-reload
systemctl restart app
systemctl restart nginx
systemctl enable app nginx
