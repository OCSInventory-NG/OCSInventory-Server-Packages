#!/bin/bash
# vim:sw=4:ts=4:et

set -e

CONFIG_FILE="/usr/share/ocsinventory-frontend/config/config.json"

if [ -f "${CONFIG_FILE}" ]; then
    BACKEND_API_ROUTE="${BACKEND_API_ROUTE_ENV:-http://127.0.0.1/}"

    cat > "${CONFIG_FILE}" <<EOF
{
  "BACKEND_API_ROUTE": "${BACKEND_API_ROUTE}"
}
EOF
    chown www-data: "${CONFIG_FILE}"
fi

exec "$@"
