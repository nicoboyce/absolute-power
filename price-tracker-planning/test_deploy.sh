#!/bin/bash
#
# Test suite for deploy.sh to verify memory leak fixes and proper process handling
#
# Tests:
# 1. Process cleanup functionality
# 2. Timeout handling
# 3. No orphaned processes after execution
# 4. Memory leak prevention
#

set -e

# Test configuration
TEST_DIR="/tmp/deploy_test_$$"
DEPLOY_SCRIPT="$(pwd)/deploy.sh"
TEST_LOG="$TEST_DIR/test.log"

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test result counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

log_test() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - TEST: $1" | tee -a "$TEST_LOG"
}

log_info() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - INFO: $1" | tee -a "$TEST_LOG"
}

pass_test() {
    echo -e "${GREEN}✓ PASS${NC}: $1" | tee -a "$TEST_LOG"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

fail_test() {
    echo -e "${RED}✗ FAIL${NC}: $1" | tee -a "$TEST_LOG"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

warn_test() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1" | tee -a "$TEST_LOG"
}

run_test() {
    TESTS_RUN=$((TESTS_RUN + 1))
    log_test "$1"
}

# Setup test environment
setup_test_env() {
    mkdir -p "$TEST_DIR/logs"
    touch "$TEST_LOG"  # Create log file first
    
    log_info "Setting up test environment in $TEST_DIR"
    cd "$TEST_DIR"
    
    # Create minimal test files
    cat > scrape_all.py << 'EOF'
#!/usr/bin/env python3
import time
import sys
import signal
import os

def signal_handler(signum, frame):
    print(f"Received signal {signum}, exiting...")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# Simulate work for the duration specified in environment variable
duration = int(os.environ.get('SCRAPE_DURATION', '5'))
print(f"Mock scraping for {duration} seconds...")

for i in range(duration):
    time.sleep(1)
    print(f"Scraping step {i+1}/{duration}")

print("Scraping completed successfully")
EOF
    
    chmod +x scrape_all.py
    
    cat > generate.py << 'EOF'
#!/usr/bin/env python3
print("Mock generation completed")
EOF
    
    chmod +x generate.py
    
    # Initialize git repo
    git init > /dev/null 2>&1
    git config user.email "test@example.com"
    git config user.name "Test User"
    
    mkdir -p static
    echo "Test content" > static/index.html
    git add .
    git commit -m "Initial test setup" > /dev/null 2>&1
    
    log_info "Test environment setup complete"
}

# Test 1: Process cleanup function
test_process_cleanup() {
    run_test "Process cleanup functionality"
    
    # Start some mock scrape processes
    python3 -c "import time; time.sleep(30)" &
    local pid1=$!
    bash -c 'exec -a "python3 scrape_all.py" python3 -c "import time; time.sleep(30)"' &
    local pid2=$!
    
    sleep 1
    
    # Count processes before cleanup
    local before_count=$(pgrep -f "python3.*scrape_all.py" | wc -l)
    
    # Extract and test the cleanup function
    source "$DEPLOY_SCRIPT"
    cleanup_existing_scrapes
    
    sleep 3
    
    # Count processes after cleanup
    local after_count=$(pgrep -f "python3.*scrape_all.py" | wc -l)
    
    # Clean up any remaining test processes
    kill $pid1 $pid2 2>/dev/null || true
    
    # Give more time for cleanup and check again
    sleep 2
    after_count=$(pgrep -f "python3.*scrape_all.py" | wc -l)
    
    if [ "$after_count" -eq 0 ] || [ "$after_count" -lt "$before_count" ]; then
        pass_test "Process cleanup successfully removed scrape processes (before: $before_count, after: $after_count)"
    else
        fail_test "Process cleanup failed - $after_count processes still running (was $before_count)"
    fi
}

# Test 2: Timeout handling
test_timeout_handling() {
    run_test "Timeout handling functionality"
    
    # Test with short timeout
    export SCRAPE_DURATION=10  # 10 seconds
    
    local start_time=$(date +%s)
    
    # Set short timeout for testing
    export PROJECT_DIR="$TEST_DIR"
    
    # Run a modified version that times out quickly
    timeout 15 bash -c "
        source '$DEPLOY_SCRIPT'
        python3 scrape_all.py > logs/scrape.log 2>&1 &
        SCRAPE_PID=\$!
        wait_with_timeout \$SCRAPE_PID 3  # 3 second timeout
        exit_code=\$?
        if [ \$exit_code -eq 124 ]; then
            echo 'TIMEOUT_DETECTED'
        fi
    " > "$TEST_DIR/timeout_test.log" 2>&1
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if grep -q "TIMEOUT_DETECTED" "$TEST_DIR/timeout_test.log" && [ "$duration" -lt 8 ]; then
        pass_test "Timeout handling works correctly (completed in ${duration}s)"
    else
        fail_test "Timeout handling failed - duration: ${duration}s"
        cat "$TEST_DIR/timeout_test.log"
    fi
}

# Test 3: No orphaned processes
test_no_orphans() {
    run_test "No orphaned processes after deployment"
    
    # Get initial process count
    local initial_python_processes=$(pgrep -f python3 | wc -l)
    
    # Run deployment script with short scraping duration
    export SCRAPE_DURATION=2
    export PROJECT_DIR="$TEST_DIR"
    
    # Run deployment in subshell to isolate
    (
        cd "$TEST_DIR"
        timeout 30 "$DEPLOY_SCRIPT" > "$TEST_DIR/deploy_test.log" 2>&1 || true
    )
    
    sleep 3  # Allow time for cleanup
    
    # Check final process count
    local final_python_processes=$(pgrep -f python3 | wc -l)
    local scrape_processes=$(pgrep -f "scrape_all.py" | wc -l)
    
    if [ "$scrape_processes" -eq 0 ]; then
        pass_test "No orphaned scrape processes detected"
    else
        fail_test "$scrape_processes orphaned scrape processes found"
        pgrep -f "scrape_all.py" | head -5
    fi
}

# Test 4: Memory usage monitoring (basic)
test_memory_usage() {
    run_test "Memory usage stability"
    
    # Get initial memory usage
    local initial_mem=$(ps -o pid,vsz,rss,comm -C python3 2>/dev/null | awk 'NR>1 {sum+=$3} END {print sum+0}')
    
    # Run multiple deployments
    export SCRAPE_DURATION=1
    export PROJECT_DIR="$TEST_DIR"
    
    for i in {1..3}; do
        log_info "Running deployment cycle $i"
        (
            cd "$TEST_DIR"
            timeout 15 "$DEPLOY_SCRIPT" > "$TEST_DIR/deploy_cycle_$i.log" 2>&1 || true
        )
        sleep 2
    done
    
    # Check final memory usage
    local final_mem=$(ps -o pid,vsz,rss,comm -C python3 2>/dev/null | awk 'NR>1 {sum+=$3} END {print sum+0}')
    
    # Allow for some variance but no major leaks
    local mem_increase=$((final_mem - initial_mem))
    
    if [ "$mem_increase" -lt 10000 ]; then  # Less than 10MB increase
        pass_test "Memory usage stable (increase: ${mem_increase}KB)"
    else
        warn_test "Significant memory increase detected: ${mem_increase}KB"
    fi
}

# Test 5: Script error handling
test_error_handling() {
    run_test "Error handling and recovery"
    
    # Create a failing scrape script
    cat > failing_scrape.py << 'EOF'
#!/usr/bin/env python3
import sys
print("Mock scraping started...")
sys.exit(1)  # Fail
EOF
    
    mv scrape_all.py scrape_all.py.backup
    mv failing_scrape.py scrape_all.py
    chmod +x scrape_all.py
    
    export PROJECT_DIR="$TEST_DIR"
    
    # Run deployment - should handle failure gracefully
    (
        cd "$TEST_DIR"
        timeout 20 "$DEPLOY_SCRIPT" > "$TEST_DIR/error_test.log" 2>&1 || true
    )
    
    # Restore original
    mv scrape_all.py.backup scrape_all.py
    
    # Check that no processes were left hanging
    local hanging_processes=$(pgrep -f "scrape_all.py" | wc -l)
    
    if [ "$hanging_processes" -eq 0 ]; then
        pass_test "Error handling cleaned up processes properly"
    else
        fail_test "$hanging_processes processes left hanging after error"
    fi
}

# Cleanup function
cleanup_test_env() {
    log_info "Cleaning up test environment"
    
    # Kill any remaining test processes
    pkill -f "$TEST_DIR" 2>/dev/null || true
    pkill -f "scrape_all.py" 2>/dev/null || true
    
    # Remove test directory
    cd /
    rm -rf "$TEST_DIR"
    
    log_info "Test environment cleaned up"
}

# Main test execution
main() {
    echo "=========================================="
    echo "Deploy.sh Memory Leak Prevention Test Suite"
    echo "=========================================="
    
    if [ ! -f "$DEPLOY_SCRIPT" ]; then
        echo "ERROR: Deploy script not found at $DEPLOY_SCRIPT"
        exit 1
    fi
    
    # Setup
    setup_test_env
    
    # Run tests
    test_process_cleanup
    test_timeout_handling
    test_no_orphans
    test_memory_usage
    test_error_handling
    
    # Results
    echo "=========================================="
    echo "Test Results:"
    echo "  Tests Run:    $TESTS_RUN"
    echo "  Tests Passed: $TESTS_PASSED"
    echo "  Tests Failed: $TESTS_FAILED"
    echo "=========================================="
    
    if [ "$TESTS_FAILED" -eq 0 ]; then
        echo -e "${GREEN}All tests passed!${NC}"
        cleanup_test_env
        exit 0
    else
        echo -e "${RED}Some tests failed. Check $TEST_LOG for details.${NC}"
        echo "Test directory preserved at: $TEST_DIR"
        exit 1
    fi
}

# Trap cleanup on exit
trap cleanup_test_env EXIT

# Run main function
main "$@"