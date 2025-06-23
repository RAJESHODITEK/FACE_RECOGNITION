import queue

shared_queue = queue.Queue(maxsize=50)
vehicle_tracking_details_queue=queue.Queue(maxsize=50)
current_camera_details = {
    "camera_name": "",
    "roi_start": 15,
    "roi_end":90,
    'roi_start_width':15,
    'roi_end_width':90,
    "status": "",
    "rtsp_url": ""
}
all_camera_data=[]

camera_status_checker=False

def update_camera_details(camera_name, rtsp_url,roi_start,roi_end,roi_start_w,roi_end_w,camera_status):
    print( "--------------------------", camera_name, rtsp_url , roi_start , roi_end , roi_start_w , roi_end_w , camera_status)
    current_camera_details["camera_name"] = camera_name
    current_camera_details["rtsp_url"] = rtsp_url
    current_camera_details["roi_start"] = int(roi_start)
    current_camera_details["roi_end"] = int (roi_end)
    current_camera_details["roi_start_width"] = int(roi_start_w)
    current_camera_details["roi_end_width"] = int(roi_end_w)
    current_camera_details["status"] = camera_status

    print(f"Camera details updated: {current_camera_details}")

def update_all_camera_list(all_camera_data_new):
    if all_camera_data_new:
        all_camera_data.clear()
        for camera in all_camera_data_new:
            camera_info = {
                "camera_name": camera.get('name', 'N/A'),
                "roi_start": camera.get('height_start_percentage', '0'),
                'roi_end': camera.get('height_end_percentage', '0'),
                "roi_start_width": camera.get('width_start_percentage', '0'),
                'roi_end_width': camera.get('width_end_percentage', '0'),
                "status": camera.get('direction', 'N/A'),
                "rtsp_url": camera.get('url', 'N/A')
            }

            all_camera_data.append(camera_info)

        print("all camera data is updated with new data.")
