#!/bin/bash
# sysbench_cpu_mem_gpu_file.sh
# Yêu cầu: sysbench, curl, nvidia-smi

# ========================
# Config Telegram Bot
# ========================
TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID="YOUR_CHAT_ID"
OUTPUT_FILE="benchmark_result.txt"

# ========================
# Hàm gửi file lên Telegram
# ========================
send_telegram_file() {
    local file="$1"
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendDocument" \
         -F chat_id="${TELEGRAM_CHAT_ID}" \
         -F document=@"${file}" > /dev/null
}

# ========================
# CPU Benchmark
# ========================
benchmark_cpu() {
    echo "==== CPU Benchmark ====" >> "$OUTPUT_FILE"
    sysbench cpu --cpu-max-prime=20000 run >> "$OUTPUT_FILE" 2>&1
    echo -e "\n" >> "$OUTPUT_FILE"
}

# ========================
# Memory Benchmark
# ========================
benchmark_memory() {
    echo "==== Memory Benchmark ====" >> "$OUTPUT_FILE"
    sysbench memory --memory-total-size=1G run >> "$OUTPUT_FILE" 2>&1
    echo -e "\n" >> "$OUTPUT_FILE"
}

# ========================
# GPU Benchmark (NVIDIA)
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
# Xoá file cũ nếu tồn tại
[ -f "$OUTPUT_FILE" ] && rm "$OUTPUT_FILE"

benchmark_cpu
benchmark_memory
benchmark_gpu

echo "All benchmarks completed. Sending file to Telegram..."
send_telegram_file "$OUTPUT_FILE"
echo "File sent."
