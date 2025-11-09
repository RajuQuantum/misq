#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

usage() {
  cat <<USAGE
Usage: ./scripts/dev.sh [command]
Commands:
  up       Start docker compose stack
  down     Stop docker compose stack
  logs     Tail docker compose logs
  test     Run backend unit tests
USAGE
}

cmd="${1:-help}"

case "$cmd" in
  up)
    docker compose -f deploy/docker-compose.yml up -d
    ;;
  down)
    docker compose -f deploy/docker-compose.yml down
    ;;
  logs)
    docker compose -f deploy/docker-compose.yml logs -f
    ;;
  test)
    cd "$ROOT_DIR/api"
    pytest
    ;;
  *)
    usage
    ;;
esac
