#!/bin/bash
#
# Pi build and deploy script
# 1. Pull latest code from git
# 2. Run scraping and generation
# 3. Commit and push static site back to git
#

# Configuration - can be overridden via environment
PROJECT_DIR="${PROJECT_DIR:-/home/pi/power-tracker}"
STATIC_DIR="$PROJECT_DIR/static"

# Log file (create logs directory if it doesn't exist)
mkdir -p "$PROJECT_DIR/logs"
LOG_FILE="$PROJECT_DIR/logs/deployment.log"

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log "Starting Pi build process..."

# Change to project directory
cd "$PROJECT_DIR" || {
    log "ERROR: Cannot change to project directory: $PROJECT_DIR"
    exit 1
}

# Pull latest changes from git (skip if no remote or no upstream commits)
if git remote get-url origin >/dev/null 2>&1; then
    if git ls-remote --exit-code --heads origin main >/dev/null 2>&1; then
        log "Pulling latest changes from git..."
        if ! git pull origin main; then
            log "ERROR: Git pull failed"
            exit 1
        fi
    else
        log "No upstream main branch yet, skipping pull"
    fi
else
    log "No git remote configured, skipping pull"
fi

# Run scraping (if scrape_all.py exists)
if [ -f "scrape_all.py" ]; then
    log "Running scraping process..."
    if ! python3 scrape_all.py; then
        log "WARNING: Scraping failed, continuing with existing data"
    fi
fi

# Generate static site (if generate.py exists)
GENERATION_FAILED=false
if [ -f "generate.py" ]; then
    log "Generating static site..."
    if ! python3 generate.py; then
        log "WARNING: Site generation failed, will use test page"
        GENERATION_FAILED=true
    fi
fi

# Ensure static directory exists
if [ ! -d "$STATIC_DIR" ]; then
    mkdir -p "$STATIC_DIR"
fi

# If generation failed or test.html exists, use test page as fallback
if [ "$GENERATION_FAILED" = true ] || [ -f "test.html" -a ! -f "$STATIC_DIR/index.html" ]; then
    if [ -f "test.html" ]; then
        # Replace timestamp placeholder
        sed "s/{{ timestamp }}/$(date '+%Y-%m-%d %H:%M:%S UTC')/" test.html > "$STATIC_DIR/index.html"
        log "Test page prepared as fallback"
    fi
fi

# Check if static directory exists and has content
if [ ! -d "$STATIC_DIR" ] || [ -z "$(ls -A "$STATIC_DIR")" ]; then
    log "ERROR: No static content to deploy"
    exit 1
fi

# Check if there are any changes to commit
git add .
if git diff --cached --quiet; then
    log "No changes to commit"
    exit 0
fi

# Commit and push changes
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S UTC')
COMMIT_MESSAGE="Pi auto-build: Updated static site - $TIMESTAMP

🤖 Generated with Pi automation
"

log "Committing static site updates..."
if ! git commit -m "$COMMIT_MESSAGE"; then
    log "ERROR: Git commit failed"
    exit 1
fi

log "Pushing changes to git..."
if ! git push origin main; then
    log "ERROR: Git push failed"
    exit 1
fi

log "Build and deploy successful - static site updated in git"
exit 0