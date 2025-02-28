import queue

shared_queue = queue.Queue(maxsize=50)
vehicle_tracking_details_queue=queue.Queue(maxsize=50)
current_camera_details = {
    "camera_name": "Camera1",
    "roi_start": 15,
    "roi_end":90,
    "status": "Entry",
    "rtsp_url": ""
}
all_camera_data=[]

def update_camera_details(camera_name=None, rtsp_url=None,roi_start=None,roi_end=None,camera_status=None):
    if camera_name is not None:
        current_camera_details["camera_name"] = camera_name
    if rtsp_url is not None:
        current_camera_details["rtsp_url"] = rtsp_url
    if roi_start is not None:
        current_camera_details["roi_start"] = int(roi_start)
    if roi_end is not None:
        current_camera_details["roi_end"] = int (roi_end)
    if camera_status is not None:
        current_camera_details["status"] = camera_status

    print(f"Camera details updated: {current_camera_details}")