def main():
    print("Plaka Tespit Sistemi")
    print("1: Bilgisayar Kamerası")
    print("2: Telefon Kamerası (IP Stream)")
    from ultralytics import YOLO

    choice = input("Seçiminizi yapın (1 veya 2): ")

    if choice == "1":
        from src.capture import start_capture
        start_capture()
    elif choice == "2":
        from src.capture import start_capture
        ip = input("Telefon IP adresini girin (örnek: http://192.168.127.12): ")
        start_capture(ip)
    else:
        print("Geçersiz seçim!")

if __name__ == "__main__":
    main()
