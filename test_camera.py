#!/usr/bin/env python3
"""
Camera test using official DJI SDK.
Based on video.py - displays video stream and saves a frame.
"""

from robomaster import robot, camera
import time
import cv2


def main():
    print("=" * 50)
    print("RoboMaster S1 - Camera Test")
    print("=" * 50)
    print("\n⚠️  Camera will stream video for 10 seconds")
    print("Press 'q' in video window to exit early")
    time.sleep(2)

    print("\nConnecting...")
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    print("✓ Connected!")

    ep_camera = ep_robot.camera

    try:
        print("\n--- Starting Video Stream ---")
        print("Resolution: 360P")
        print("Duration: 10 seconds")
        print("Saving frame to: captured_frame.jpg")

        # Start video stream with display
        ep_camera.start_video_stream(display=True, resolution=camera.STREAM_360P)

        # Capture a frame after 2 seconds
        time.sleep(2)
        frame = ep_camera.read_cv2_image()
        if frame is not None:
            cv2.imwrite("captured_frame.jpg", frame)
            print("✓ Frame saved!")

        # Continue streaming for remaining time
        time.sleep(8)

        print("\n✓ Video stream complete!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        print("\nStopping video stream...")
        ep_camera.stop_video_stream()
        print("Closing connection...")
        ep_robot.close()
        print("✓ Done.")
        print("=" * 50)


if __name__ == "__main__":
    main()
