#!/bin/bash
# sysbench_numa_dynamic.sh
# Run sysbench memory stress for 1 or 2 NUMA nodes and send results to Telegram

# ========================
# Telegram Configuration
# ========================
TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID="YOUR_CHAT_ID"
OUTPUT_FILE="numa_stress_result.txt"

send_telegram_file() {
    local file="$1"
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendDocument" \
         -F chat_id="${TELEGRAM_CHAT_ID}" \
         -F document=@"${file}" > /dev/null
}

# ========================
# Input NUMA node count
# ========================
read -p "Enter NUMA node count (1 or 2): " NUMA_COUNT

if [[ "$NUMA_COUNT" != "1" && "$NUMA_COUNT" != "2" ]]; then
    echo "Error: Only 1 or 2 are valid options."
    exit 1
fi

# ========================
# Sysbench Configuration
# ========================
MEM_TOTAL="172G"        # Approx. 90% of total memory
THREADS=8
BLOCK_SIZE="2M"
DURATION=60              # seconds

[ -f "$OUTPUT_FILE" ] && rm "$OUTPUT_FILE"

echo "===== NUMA STRESS TEST =====" >> "$OUTPUT_FILE"
echo "Threads: $THREADS | Memory: $MEM_TOTAL | Block Size: $BLOCK_SIZE | Duration: ${DURATION}s" >> "$OUTPUT_FILE"
echo "NUMA Mode: ${NUMA_COUNT} node(s)" >> "$OUTPUT_FILE"
echo -e "\n" >> "$OUTPUT_FILE"

# ========================
# Run sysbench according to NUMA mode
# ========================

# Case NUMA = 1
if [ "$NUMA_COUNT" -eq 1 ]; then
    echo "==== Single NUMA (CPU=0, MEM=0) ====" | tee -a "$OUTPUT_FILE"
    numactl --cpunodebind=0 --membind=0 sysbench memory \
        --threads=$THREADS \
        --memory-total-size=$MEM_TOTAL \
        --memory-block-size=$BLOCK_SIZE \
        --memory-oper=write \
        --memory-scope=global \
        --time=$DURATION \
        run | tee -a "$OUTPUT_FILE"
    echo -e "\n" >> "$OUTPUT_FILE"
fi

# Case NUMA = 2
if [ "$NUMA_COUNT" -eq 2 ]; then
    echo "==== NUMA Node0 → MEM Node0 ====" | tee -a "$OUTPUT_FILE"
    numactl --cpunodebind=0 --membind=0 sysbench memory \
        --threads=$THREADS \
        --memory-total-size=$MEM_TOTAL \
        --memory-block-size=$BLOCK_SIZE \
        --memory-oper=write \
        --memory-scope=global \
        --time=$DURATION \
        run | tee -a "$OUTPUT_FILE"
    echo -e "\n" >> "$OUTPUT_FILE"

    echo "==== NUMA Node0 → MEM Node1 (Cross NUMA) ====" | tee -a "$OUTPUT_FILE"
    numactl --cpunodebind=0 --membind=1 sysbench memory \
        --threads=$THREADS \
        --memory-total-size=$MEM_TOTAL \
        --memory-block-size=$BLOCK_SIZE \
        --memory-oper=write \
        --memory-scope=global \
        --time=$DURATION \
        run | tee -a "$OUTPUT_FILE"
    echo -e "\n" >> "$OUTPUT_FILE"
fi

# ========================
# Send results to Telegram
# ========================
echo "Benchmark completed. Results saved to $OUTPUT_FILE" | tee -a "$OUTPUT_FILE"
echo "Sending result file to Telegram..."
send_telegram_file "$OUTPUT_FILE"
echo "Done."
