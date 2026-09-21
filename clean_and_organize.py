import os
import shutil

# ۱. ساخت پوشه‌های استاندارد
os.makedirs("outputs", exist_ok=True)
os.makedirs("src", exist_ok=True)
os.makedirs("tests", exist_ok=True)
os.makedirs("data", exist_ok=True)

# ۲. انتقال عکس‌ها و فایل‌های CSV به پوشه outputs
files_to_move = [
    "bess_dispatch_chart.png", 
    "market_prices_chart.png", 
    "market_prices.csv", 
    "optimization_results.csv"
]

for file_name in files_to_move:
    if os.path.exists(file_name):
        shutil.move(file_name, os.path.join("outputs", file_name))
        print(f"✅ منتقل شد به outputs: {file_name}")

# ۳. پاکسازی کش‌های پایتون و فایل‌های موقت
for root, dirs, files in os.walk("."):
    if "__pycache__" in dirs:
        cache_path = os.path.join(root, "__pycache__")
        shutil.rmtree(cache_path)
        print(f"🗑️ حذف شد: {cache_path}")
    if ".pytest_cache" in dirs:
        pytest_path = os.path.join(root, ".pytest_cache")
        shutil.rmtree(pytest_path)
        print(f"🗑️ حذف شد: {pytest_path}")

if os.path.exists(".DS_Store"):
    os.remove(".DS_Store")

print("\n✨ پاکسازی و انتقال فایل‌ها با موفقیت کامل انجام شد!")
