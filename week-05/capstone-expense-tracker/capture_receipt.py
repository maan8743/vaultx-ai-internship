import cv2
import time
import sys


def capture_photo(output_path="receipt_photo.jpg", camera_index=0, countdown=5):
    cam = cv2.VideoCapture(camera_index)

    if not cam.isOpened():
        print("Error: could not access the camera.")
        sys.exit(1)

    print(f"Position your receipt. Photo will be taken in {countdown} seconds...")

    start_time = time.time()
    while True:
        ret, frame = cam.read()
        if not ret:
            break

        elapsed = time.time() - start_time
        remaining = max(0, countdown - int(elapsed))

        display_frame = frame.copy()
        cv2.putText(display_frame, f"Capturing in {remaining}...", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow("Receipt Capture", display_frame)
        cv2.waitKey(1)

        if elapsed >= countdown:
            cv2.imwrite(output_path, frame)
            print(f"Photo saved to {output_path}")
            break

    cam.release()
    cv2.destroyAllWindows()
    return output_path


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "receipt_photo.jpg"
    capture_photo(output)