import os
import subprocess

def main():
    test_dir = "tests"
    # carikan semua file .py dalam folder tests
    test_files = [
        os.path.join(test_dir,f)
        for f in os.listdir(test_dir)
        if (f.startswith("test_") or f.endswith("_test.py")) and f.endswith(".py")
    ]
    if not test_files:
        print("⚠️  Tidak ada file test ditemukan di folder 'tests/'")
        return
    print("🧪 Menjalankan semua test file satu per satu:\n")

    # jalankan setiap file
    for test_file in test_files:
        print(f"➡️  Menjalankan: {test_file}")
        result = subprocess.run(
            ["pytest", test_file, "-v", "--disable-warnings", "--maxfail=1"],
            text=True
        )

        if result.returncode != 0:
            print(f"❌ Test gagal di: {test_file}\n")
            break
        else:
            print(f"✅ Test berhasil: {test_file}\n")

    print("\n🏁 Selesai menjalankan semua test.")


if __name__ == "__main__":

    main()