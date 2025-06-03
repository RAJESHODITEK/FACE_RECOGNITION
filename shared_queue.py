import queue
import re

from onvif import ONVIFCamera

shared_queue = queue.Queue(maxsize=50)
live_feed_queue =queue.Queue(maxsize=30)
vehicle_tracking_details_queue=queue.Queue(maxsize=50)
current_camera_details = {
    "camera_name": "",
    "roi_start_height": 15,
    "roi_end_height":90,
    'roi_start_width':15,
    'roi_end_width':90,
    "status": "",
    "rtsp_url": "",
    "ptz_feature":True
}
all_camera_data=[]
shared_data = {"pkl_file_update_status": False, 'id':'', 'name':'', 'image': '','op':0, "id_list": []}
locked_ID= {"locked_id":None}
# settings = set()
# ptz_control = False
#
# settings.add(ptz_control)
#
# clicked_ID= {"X":None, "Y":None}

def update_camera_details(camera_name, rtsp_url,roi_start=None,roi_end=None,roi_start_w=None,roi_end_w=None ,camera_status=''):
    print(f"Camera details before updated: {current_camera_details}")
    current_camera_details["camera_name"] = camera_name
    if rtsp_url != '':
        current_camera_details["rtsp_url"] = rtsp_url
    if roi_start is not None:
        current_camera_details["roi_start_height"] = int(roi_start)
        current_camera_details["roi_end_height"] = int (roi_end)
        current_camera_details["roi_start_width"] = int(roi_start_w)
        current_camera_details["roi_end_width"] = int(roi_end_w)
    if camera_status != '':
        current_camera_details["status"] = camera_status
    print(f"Camera details updated: {current_camera_details}")


    # print(settings)





def update_any_camera_data(camera_name,rtsp_url,roi_start=None,roi_end=None,roi_start_w=None,roi_end_w=None,camera_status=None):
    for cam in all_camera_data:
        if cam['camera_name'] == camera_name:
            print(f"cam details was : {cam}")
            if rtsp_url != '':
                cam["rtsp_url"] = rtsp_url
            if roi_start is not None:
                cam["roi_start_height"] = int(roi_start)
                cam["roi_end_height"] = int(roi_end)
                cam["roi_start_width"] = int(roi_start_w)
                cam["roi_end_width"] = int(roi_end_w)
            if camera_status != '':
                cam["status"] = camera_status
            print(f"Camera details updated : {cam}")

    return



def split_rtsp_url(rtsp_url):
    rtsp_pattern = re.compile(
        r"^rtsp://(?:(?P<username>[a-zA-Z0-9_.+@-]+)(?::(?P<password>[a-zA-Z0-9_.+@-]+))?@)?(?P<ip>(?:\d{1,3}\.){3}\d{1,3})(?::(?P<port>\d{1,5}))?(/(?P<path>[a-zA-Z0-9_.@/-]+))?$"
    )

    match = rtsp_pattern.match(rtsp_url)

    if match:

        components = match.groupdict()

        username = components.get('username')
        password = components.get('password')
        ip = components.get('ip')
        port = components.get('port')
        path = components.get('path')

        return {
            "username": username if username else "",
            "password": password if password else "",
            "ip": ip,
            "port": int(port) if port else '554',
            "path": path if path else ""
        }
    else:
        return {
            "username": "",
            "password": "",
            "ip": "",
            "port": '',
            "path": ""
        }




# # PTZ Initialization
# def check_ptz(ptz_camera_ip, ptz_camera_port, ptz_camera_user, ptz_camera_pass):
#     try:
#         ptz_control=None
#         onvif_cam = ONVIFCamera(ptz_camera_ip, ptz_camera_port, ptz_camera_user, ptz_camera_pass)
#         media_service = onvif_cam.create_media_service()
#         profiles = media_service.GetProfiles()
#         ptz_configuration = profiles[0].PTZConfiguration
#         ptz_service = onvif_cam.create_ptz_service()
#         try:
#             profile = profiles[0]
#             options = ptz_service.GetConfigurationOptions({'ConfigurationToken': profile.PTZConfiguration.token})
#         except:
#             return False  # No valid PTZ config
#
#             # Check if camera supports pan, tilt, or zoom
#         supports_pan = hasattr(options.Spaces,
#                                'ContinuousPanTiltVelocitySpace') and options.Spaces.ContinuousPanTiltVelocitySpace
#         supports_zoom = hasattr(options.Spaces,
#                                 'ContinuousZoomVelocitySpace') and options.Spaces.ContinuousZoomVelocitySpace
#
#         if supports_pan or supports_zoom:
#             return True
#
#
#         else:
#             settings.clear()
#             ptz_control = False
#             settings.add(ptz_control)
#             print("PTZ is NOT supported.")
#             return False
#
#     except Exception as e:
#         print(f"[ERROR] PTZ initialization failed: {e}")
#         return False
