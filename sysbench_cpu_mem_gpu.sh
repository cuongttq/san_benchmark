#!/bin/bash
# stress_cpu_mem_gpu_file.sh
# Yêu cầu: sysbench, curl, nvidia-smi

# ========================
# Config Telegram Bot
# ========================
TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID="YOUR_CHAT_ID"
OUTPUT_FILE="stress_result.txt"

send_telegram_file() {
    local file="$1"
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendDocument" \
         -F chat_id="${TELEGRAM_CHAT_ID}" \
         -F document=@"${file}" > /dev/null
}

# ========================
# Xác định 90% CPU threads
# ========================
CPU_CORES=$(nproc)
CPU_THREADS=$((CPU_CORES * 90 / 100))
[ "$CPU_THREADS" -lt 1 ] && CPU_THREADS=1

# ========================
# Xác định 90% memory
# ========================
TOTAL_MEM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
MEM_90_PERCENT_KB=$((TOTAL_MEM_KB * 90 / 100))
MEM_90_MB=$((MEM_90_PERCENT_KB / 1024))

# ========================
# Stress CPU
# ========================
benchmark_cpu() {
    echo "==== CPU Stress (~90%) ====" >> "$OUTPUT_FILE"
    sysbench cpu --cpu-max-prime=20000 --threads=$CPU_THREADS run >> "$OUTPUT_FILE" 2>&1
    echo -e "\n" >> "$OUTPUT_FILE"
}

# ========================
# Stress Memory
# ========================
benchmark_memory() {
    echo "==== Memory Stress (~90%) ====" >> "$OUTPUT_FILE"
    sysbench memory --memory-total-size=${MEM_90_MB}M run >> "$OUTPUT_FILE" 2>&1
    echo -e "\n" >> "$OUTPUT_FILE"
}

# ========================
# GPU Info
# ========================
benchmark_gpu() {
    echo "==== GPU Info ====" >> "$OUTPUT_FILE"
    if command -v nvidia-smi &>/dev/null; then
        nvidia-smi --query-gpu=name,memory.total,memory.used,utilization.gpu --format=csv >> "$OUTPUT_FILE" 2>&1
    else
        echo "No NVIDIA GPU found." >> "$OUTPUT_FILE"
    fi
    echo -e "\n" >> "$OUTPUT_FILE"
}

# ========================
# Main
# ========================
[ -f "$OUTPUT_FILE" ] && rm "$OUTPUT_FILE"

benchmark_cpu
benchmark_memory
benchmark_gpu

echo "Stress test completed. Sending file to Telegram..."
send_telegram_file "$OUTPUT_FILE"
echo "File sent."
