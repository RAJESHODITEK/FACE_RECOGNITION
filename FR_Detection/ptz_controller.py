import re

from onvif import ONVIFCamera
import time

class PTZController:
    _instance = None
    _initialized = False

    def __new__(cls, ip='', port=80, username='', password=''):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, ip='', port=80, username='', password=''):
        if PTZController._initialized:
            return

        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.cam = None
        self.media_service = None
        self.ptz_service = None
        self.profile_token = None
        self.last_ptz_vector = {"x": 0.0, "y": 0.0}
        self.last_move_time = 0
        self.ptz_eligibility= False

        if self.check_ptz(self.ip, 80, self.username, self.password):
            self.ptz_eligibility=True
            self._initialize()
        else:
            self.ptz_eligibility=False

        PTZController._initialized = True

    def _initialize(self):
        try:
            self.cam = ONVIFCamera(self.ip, self.port, self.username, self.password)
            self.media_service = self.cam.create_media_service()
            self.ptz_service = self.cam.create_ptz_service()
            self.profile_token = self.media_service.GetProfiles()[0].token
        except Exception as e:
            print(f"[PTZ ERROR] Initialization failed: {e}")

    def move(self, dx, dy, frame_shape, speed=0.5, threshold=10):
        if not self.ptz_eligibility:
            return
        frame_height, frame_width = frame_shape
        normalized_dx = dx / frame_width
        normalized_dy = dy / frame_height

        pan_speed = max(min(normalized_dx * speed, 1.0), -1.0)
        tilt_speed = max(min(normalized_dy * speed, 1.0), -1.0)

        now = time.time()
        if (now - self.last_move_time < 0.05 and
            abs(pan_speed - self.last_ptz_vector["x"]) < 0.01 and
            abs(tilt_speed - self.last_ptz_vector["y"]) < 0.01):
            return
        if abs(dx) < threshold and abs(dy) < threshold:
            if self.last_ptz_vector["x"] != 0 or self.last_ptz_vector["y"] != 0:
                try:

                    self.ptz_service.Stop({'ProfileToken': self.profile_token})

                except Exception as e:
                    print(f"[PTZ ERROR] Stop failed: {e}")
                return
        try:
            self.ptz_service.ContinuousMove({
                'ProfileToken': self.profile_token,
                'Velocity': {
                    'PanTilt': {'x': pan_speed, 'y': -tilt_speed},
                    'Zoom': {'x': 0}
                }
            })
            self.last_ptz_vector = {'x': pan_speed, 'y': -tilt_speed}
            self.last_move_time = now
        except Exception as e:
            print(f"[PTZ ERROR] Move failed: {e}")

    def get_home_position(self):
        if not self.ptz_eligibility:
            return {"position": None, "source": "none"}
        try:
            home_position = self.ptz_service.GetHomePosition({'ProfileToken': self.profile_token})
            # print("Home position retrieved:", home_position)
            return {"position": home_position, "source": "home"}
        except Exception as e:
            print("GetHomePosition failed:", e)

        try:
            presets = self.ptz_service.GetPresets({'ProfileToken': self.profile_token})
            if presets:
                first_preset = presets[0]
                # print("Using preset as home position:", first_preset)
                return {"position": first_preset, "source": "preset"}
            else:
                print("No presets found.")
        except Exception as e:
            print("GetPresets failed:", e)

        return {"position": None, "source": "none"}

    def goto_preset(self,preset_token):
        if not self.ptz_eligibility:
            return
        try:
            self.ptz_service.GotoPreset({
                'ProfileToken': self.profile_token,
                'PresetToken': preset_token
            })

        except Exception as e:
            print("Failed to go to preset")

    def split_rtsp_url(self,rtsp_url):
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


    def change_ptz(self,rtsp):
        result= self.split_rtsp_url(rtsp)
        self.stop_ptz()
        if self.check_ptz(result['ip'], 80, result['username'], result['password']):
            self.ptz_eligibility=True
            self.update_ptz(result['ip'], 80, result['username'], result['password'])
            self._initialize()
        else:
            self.ptz_eligibility=False


    def stop_ptz(self):
        self.cam = None
        self.media_service = None
        self.ptz_service = None
        self.profile_token = None

    def update_ptz(self,ip,port,uname,password):
        self.ip = ip
        self.port = port
        self.username = uname
        self.password = password

    # PTZ Initialization
    def check_ptz(self,ptz_camera_ip, ptz_camera_port, ptz_camera_user, ptz_camera_pass):
        settings = set()
        ptz_control = False
        settings.add(ptz_control)
        try:
            onvif_cam = ONVIFCamera(ptz_camera_ip, ptz_camera_port, ptz_camera_user, ptz_camera_pass)
            media_service = onvif_cam.create_media_service()
            profiles = media_service.GetProfiles()
            ptz_configuration = profiles[0].PTZConfiguration
            ptz_service = onvif_cam.create_ptz_service()
            try:
                profile = profiles[0]
                options = ptz_service.GetConfigurationOptions({'ConfigurationToken': profile.PTZConfiguration.token})
            except:
                return False  # No valid PTZ config

                # Check if camera supports pan, tilt, or zoom
            supports_pan = hasattr(options.Spaces,
                                   'ContinuousPanTiltVelocitySpace') and options.Spaces.ContinuousPanTiltVelocitySpace
            supports_zoom = hasattr(options.Spaces,
                                    'ContinuousZoomVelocitySpace') and options.Spaces.ContinuousZoomVelocitySpace

            if supports_pan or supports_zoom:
                return True
            else:
                settings.clear()
                ptz_control = False
                settings.add(ptz_control)
                print("PTZ is NOT supported.")
                return False

        except Exception as e:
            print(f"[ERROR] PTZ initialization failed: {e}")
            return False

    def GoToHomePosition(self):
        self.ptz_service.GotoHomePosition({'ProfileToken': self.profile_token})

