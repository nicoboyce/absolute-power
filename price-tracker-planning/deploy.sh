#!/bin/bash
#
# Pi build and deploy script
# 1. Pull latest code from git
# 2. Run scraping and generation
# 3. Commit and push static site back to git
#

# Configuration - can be overridden via environment
PROJECT_DIR="${PROJECT_DIR:-/home/nico/absolute/absolute-power/price-tracker-planning}"
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

# Test git connectivity first
if git remote get-url origin >/dev/null 2>&1; then
    log "Testing git connectivity..."
    if ! git ls-remote origin >/dev/null 2>&1; then
        log "ERROR: Cannot connect to git remote - check authentication (SSH keys/tokens)"
        log "Remote URL: $(git remote get-url origin)"
        exit 1
    fi
    
    # Pull latest changes with proper error handling
    log "Pulling latest changes from git..."
    if ! git pull origin main --rebase --autostash; then
        log "WARNING: Git pull failed, attempting to continue with local changes"
        log "This may cause push conflicts later"
    fi
else
    log "No git remote configured, skipping pull"
fi

# Activate virtual environment
source "$PROJECT_DIR/venv/bin/activate" 2>/dev/null || log "Virtual environment not found, using system Python"

# Run scraping (if scrape_all.py exists)
if [ -f "scrape_all.py" ]; then
    log "Running scraping process in background..."
    # Run in background to prevent timeout, log output
    nohup python3 scrape_all.py > "$PROJECT_DIR/logs/scrape.log" 2>&1 &
    SCRAPE_PID=$!
    log "Scraping started in background (PID: $SCRAPE_PID)"
    log "Check logs/scrape.log for output"
    
    # Wait briefly to check if process started successfully
    sleep 2
    if ! kill -0 $SCRAPE_PID 2>/dev/null; then
        log "WARNING: Scraping process may have failed to start"
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
    log "Git push failed - attempting to pull and retry..."
    
    # Try to pull and merge remote changes
    if git pull origin main --rebase --autostash; then
        log "Successfully pulled remote changes, retrying push..."
        if git push origin main; then
            log "Push successful after pull"
        else
            log "ERROR: Git push failed even after pull - manual intervention required"
            exit 1
        fi
    else
        log "ERROR: Could not pull remote changes - manual git resolution required"
        log "Run: git pull origin main --rebase --autostash"
        exit 1
    fi
fi

log "Build and deploy successful - static site updated in git"
exit 0