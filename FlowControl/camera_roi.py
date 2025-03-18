from Core.main import Core
from Interface.main import Interface
import json
from datetime import datetime
import os


class CameraRoiController:
    def __init__(self, Core: Core, Interface: Interface):
        self.obj_Core = Core
        self.obj_Interface = Interface
        self.obj_CameraRoiInterface = self.obj_Interface.dict_frames["camera_roi"]
        self.obj_CameraRoiInterface.obj_Core = self.obj_Core
        self.load_rois_from_db()


        # Initialize the interface with camera names
        self.load_cameras_from_db()

    def load_cameras_from_db(self) -> None:
        """Load camera details from database and update interface."""
        try:
            # Fetch camera data from the database
            camera_data = self.obj_Core.obj_Camera.fetch_all_Camera_data()
            if not camera_data:
                return

            camera_list = {}
            for camera in camera_data:
                try:
                    camera_name = camera['Camera_name']
                    rtsp_url = camera['URL']
                    roi_coords = camera.get('ROICoordinates')


                    if roi_coords:
                        try:
                            point_dict = json.loads(roi_coords) if isinstance(roi_coords, str) else roi_coords
                            if isinstance(point_dict, dict):
                                x1 = int(point_dict['point1'][0])
                                y1 = int(point_dict['point1'][1])
                                x2 = int(point_dict['point4'][0])
                                y2 = int(point_dict['point4'][1])

                                # Store ROI state
                                self.obj_CameraRoiInterface._roi_state[camera_name] = {
                                    "coords": (x1, y1, x2, y2),
                                    "selected": True
                                }
                                # print(
                                    # f"Stored ROI state for {camera_name}: {self.obj_CameraRoiInterface._roi_state[camera_name]}")
                        except (json.JSONDecodeError, KeyError) as e:
                            pass
                            # print(f"Error processing ROI coordinates for camera {camera_name}: {e}")

                    if camera_name and rtsp_url:
                        camera_list[camera_name] = rtsp_url
                    else:
                        pass
                        # print(f"Incomplete data for camera: {camera}")

                except Exception as e:
                    print(f"Error processing camera {camera}: {e}")
                    continue

            # print("Final ROI state before updating interface:", self.obj_CameraRoiInterface._roi_state)
            self.obj_CameraRoiInterface.update_camera_list(camera_list)

        except Exception as e:
            pass
            # print(f"Error loading camera details: {e}")


    def load_rois_from_db(self) -> None:
        """Load ROI details from database and update the interface."""
        try:
            # Fetch ROI data from the database
            roi_data = self.obj_Core.obj_Camera.fetch_all_ROI_data()

            if not roi_data:
                # print("No ROI data found in database")
                return

            # print("ROI data :", roi_data)

            # Create ROI dictionary
            self.obj_CameraRoiInterface.roi_list = {}
            for roi in roi_data:
                if isinstance(roi, tuple):
                    # Handle tuple format
                    camera_name = roi[0]
                    roi_coordinates = roi[1]
                elif isinstance(roi, dict):
                    # Handle dictionary format
                    camera_name = roi.get("Camera_name")
                    roi_coordinates = roi.get("Coordinates")
                else:
                    # print(f"Unrecognized ROI data format: {roi}")
                    continue

                # Add ROI to the list
                if camera_name and roi_coordinates:
                    self.obj_CameraRoiInterface.roi_list[camera_name] = roi_coordinates
                else:
                    pass
                    # print(f"Incomplete data for ROI: {roi}")

            # Update the interface with the ROI list
            if hasattr(self.obj_CameraRoiInterface, "update_roi_list"):
                self.obj_CameraRoiInterface.restore_roi()
            else:
                pass
                # print("update_roi_list method not found in obj_CameraRoiInterface")

        except Exception as e:
            pass
            # print(f"Error loading ROI details: {e}")

