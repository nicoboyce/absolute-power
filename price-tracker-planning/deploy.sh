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
    
    # Pull latest changes with conflict resolution
    log "Pulling latest changes from git..."
    
    # Store current pricing data if it exists
    PRICES_FILE="data/prices/prices_$(date +%Y-%m-%d).json"
    TEMP_PRICES="/tmp/pi_prices_backup.json"
    
    if [ -f "$PRICES_FILE" ]; then
        log "Backing up current pricing data..."
        cp "$PRICES_FILE" "$TEMP_PRICES"
    fi
    
    # Attempt pull with rebase
    if ! git pull origin main --rebase --autostash; then
        log "Git pull with rebase failed, checking for conflicts..."
        
        # Check if we have merge conflicts in pricing files
        if git status --porcelain | grep -q "^UU.*prices.*\.json"; then
            log "Detected pricing file conflicts, resolving automatically..."
            
            # For pricing files, prefer our local data (more recent scraping)
            for conflict_file in $(git status --porcelain | grep "^UU.*prices.*\.json" | awk '{print $2}'); do
                log "Resolving conflict in $conflict_file"
                
                # Remove conflict markers, keeping our version (the one after =======)
                if [ -f "$TEMP_PRICES" ]; then
                    cp "$TEMP_PRICES" "$conflict_file"
                    git add "$conflict_file"
                    log "Restored local pricing data for $conflict_file"
                else
                    # If no backup, just remove conflict markers and keep both versions' data
                    sed -i '/^<<<<<<< /d; /^=======/d; /^>>>>>>> /d' "$conflict_file"
                    git add "$conflict_file"
                    log "Cleaned conflict markers from $conflict_file"
                fi
            done
            
            # Continue rebase after resolving conflicts
            if ! git rebase --continue; then
                log "ERROR: Could not complete rebase after conflict resolution"
                git rebase --abort
                log "Aborted rebase, continuing with local changes"
            else
                log "Successfully resolved conflicts and completed rebase"
            fi
        else
            log "Pull failed but no pricing conflicts detected, attempting to continue"
            # Try to abort rebase if it's in progress
            if git status | grep -q "rebase in progress"; then
                git rebase --abort
                log "Aborted incomplete rebase"
            fi
        fi
    else
        log "Git pull successful"
    fi
    
    # Clean up temporary files
    [ -f "$TEMP_PRICES" ] && rm -f "$TEMP_PRICES"
else
    log "No git remote configured, skipping pull"
fi

# Activate virtual environment
source "$PROJECT_DIR/venv/bin/activate" 2>/dev/null || log "Virtual environment not found, using system Python"

# Clean up any existing scrape processes to prevent resource accumulation
cleanup_existing_scrapes() {
    local existing_pids=$(pgrep -f "python3.*scrape_all.py" 2>/dev/null || true)
    if [ -n "$existing_pids" ]; then
        log "Cleaning up existing scrape processes: $existing_pids"
        pkill -f "python3.*scrape_all.py" 2>/dev/null || true
        sleep 2
        # Force kill if still running
        pkill -9 -f "python3.*scrape_all.py" 2>/dev/null || true
    fi
}

# Wait for background process with timeout
wait_with_timeout() {
    local pid=$1
    local timeout=${2:-300}  # Default 5 minutes
    local count=0
    
    while [ $count -lt $timeout ]; do
        if ! kill -0 $pid 2>/dev/null; then
            # Process finished
            wait $pid 2>/dev/null
            return $?
        fi
        sleep 1
        count=$((count + 1))
    done
    
    # Timeout reached - kill the process
    log "WARNING: Process $pid timed out after ${timeout}s, terminating"
    kill -TERM $pid 2>/dev/null || true
    sleep 5
    kill -KILL $pid 2>/dev/null || true
    return 124  # Timeout exit code
}

# Run scraping (if scrape_all.py exists)
if [ -f "scrape_all.py" ]; then
    log "Cleaning up any existing scrape processes..."
    cleanup_existing_scrapes
    
    log "Running scraping process..."
    # Run with timeout to prevent hanging
    python3 scrape_all.py > "$PROJECT_DIR/logs/scrape.log" 2>&1 &
    SCRAPE_PID=$!
    log "Scraping started (PID: $SCRAPE_PID)"
    
    # Wait for completion with timeout (10 minutes max)
    if wait_with_timeout $SCRAPE_PID 600; then
        log "Scraping completed successfully"
    else
        case $? in
            124)
                log "ERROR: Scraping timed out after 10 minutes"
                ;;
            *)
                log "WARNING: Scraping failed with exit code $?"
                ;;
        esac
        log "Check logs/scrape.log for details"
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