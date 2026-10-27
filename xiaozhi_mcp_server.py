import json

tools = {
    "tools":
    [
        {
          "name": "self.manage_applications.application_list",
          "description": "List internal applications (algorithms) of the HuskyLens.If the user uses a non-English language to describe the algorithm name, you need to translate the current English name into the target language first.",
          "parameters":[
            ]
        },{
          "name": "self.manage_applications.switch_application",
          "description": "Switch to another internal applications (algorithms) of the HuskyLens.You must use a real algorithm ID retrieved from self.manage_applications.application_list; do not use a fabricated or made-up algorithm ID.",
          "parameters":[
              {
                  "name": "algorithm",
                  "type": "string",
                  "required": True,
                  "description": "English name of the target application (algorithm). Required only when operation is 'switch_application'. The name must come from the result of application_list."
              }
          ]
        },{
          "name": "self.manage_applications.current_application",
          "description": "querying the current internal application (algorithm) of the HuskyLens.The name must come from the result of application_list.",
          "parameters":[
          ]
        },{
            "name": "self.multimedia_control.take_photo",
            "description": "take a photo",
            "parameters":[
                {
                    "name": "resolution",
                    "type": "string",
                    "required": True,
                    "description": "Image resolution. Allowed values: 1920x1080, 1280x720, 640x480. Use 1280x720 if no suitable resolution can be determined."
                }
            ]
        },{
            "name": "self.multimedia_control.take_screenshot",
            "description": "take a screenshot",
            "parameters":[
            ]
        },{
            "name": "self.multimedia_control.play_music",
            "description": "play mp3 file",
            "parameters":[
                {
                    "name": "filename",
                    "type": "string",
                    "required": True,
                    "description": "File name"
                },{
                    "name": "volume",
                    "type": "integer",
                    "required": True,
                    "description": "Audio playback volume (0–100). This is the player volume, not the system volume. Use 100 if no suitable volume can be determined."
                },
            ]
        },{
            "name": "self.multimedia_control.start_recording_audio",
            "description": "start recording audio to a mp3 file",
            "parameters":[
                {
                    "name": "filename",
                    "type": "string",
                    "required": True,
                    "description": "File name"
                },{
                    "name": "duration",
                    "type": "integer",
                    "required": True,
                    "description": "Audio duration in seconds"
                }
            ]
        },{
            "name": "self.multimedia_control.stop_recording_audio",
            "description": "stop recording audio",
            "parameters":[
            ]
        },{
          "name": "self.get_recognition_result",
          "description": "Obtain real-time recognition results from HuskyLens, including image data and recognized labels (e.g., person name or object type).",
          "parameters": [
            {
              "name": "algorithm",
              "type": "integer",
              "required": True,
              "description": "Algorithm ID currently running on HuskyLens."
            }
          ]
        },{
          "name": "self.learn_control.learn",
          "description": "Control learning of objects on the screen.\n\n"
            "If the returned id is 0, learning failed. Otherwise, the returned id represents the learned object ID.",
          "parameters": [
            {
              "name": "algorithm",
              "type": "integer",
              "required": True,
              "description": "Algorithm ID currently running on HuskyLens."
            }
          ]
        },{
          "name": "self.learn_control.forget",
          "description": "Control forgetting of objects huskylens has learned",
          "parameters": [
            {
              "name": "algorithm",
              "type": "integer",
              "required": True,
              "description": "Algorithm ID currently running on HuskyLens."
            }
          ]
        },{
          "name": "self.learn_control.learn_block",
          "description": "Object control learning in HuskyLens: using previously returned coordinates, the LLM should infer the target position from user-provided directional terms based on context.",
          "parameters": [
            {
              "name": "algorithm",
              "type": "integer",
              "required": True,
              "description": "Algorithm ID currently running on HuskyLens."
            },{
                "name": "x",
                "description": "X coordinate of the detected object",
                "type": "integer",
                "required": True
            },{
                "name": "y",
                "description": "Y coordinate of the detected object",
                "type": "integer",
                "required": True
            },{
                "name": "width",
                "description": "Rectangle width of the detected object",
                "type": "integer",
                "required": True
            },{
                "name": "height",
                "description": "Rectangle height of the detected object",
                "type": "integer",
                "required": True
            }
          ]
        },{
          "name": "self.learn_control.set_name_by_id",
          "description": "Set the object name according to the learned object ID. Objects whose ID is 0 are not allowed to be assigned a name.Please call set_name_by_id to set the name. The name is not an algorithm parameter.",
          "parameters": [
              {
                "name": "algorithm",
                "description": "The ID of the algorithm whose parameters should be retrieved.",
                "type": "integer",
                "required": True
              },{
                "name": "id",
                "description": "Object id",
                "type": "integer",
                "required": True
              },{
                "name": "name",
                "description": "Object name",
                "type": "string",
                "required": True
              }
            ]
        },{
            "name": "self.task_scheduler.create_task",
            "description": "Manage scheduled tasks. Call this tool when you need to create tasks. Example user intents include: 'Take a picture when you see the keyboard.",
            "parameters": [
              {
                "name": "tasks",
                "description": "Task list encoded as a JSON string. The string must represent an array of task objects.\n"
                 "tasks is a JSON string representing an array of task objects. Each task object must contain:\n"
                 "   - trigger (string, required): exact trigger name as recognized by the system (case-sensitive)\n"
                 "   - handler (string, required): function to execute\n",
                "type": "string",
                "required": True
              }
            ]
        },{
          "name": "self.draw_control.draw_text",
          "description": "Control drawing text on the screen.\n",
          "parameters": [
            {
              "name": "text",
              "description": "Text content for drawing",
              "type": "string",
              "required": True
            },
            {
              "name": "x",
              "description": "X coordinate of the text object",
              "type": "integer",
              "required": True
            },
            {
              "name": "y",
              "description": "Y coordinate of the text object",
              "type": "integer",
              "required": True
            },
            {
              "name": "font_size",
              "description": "Font size of the text object. only support 20 24 26 27 28 32 36 40 48",
              "type": "integer",
              "required": True
            },
            {
              "name": "color",
              "description": "RGBA color encoded as uint32 hex string, e.g. #00FF00 or #FF00FF80",
              "type": "string",
              "required": True
            }
          ]
        },{
          "name": "self.draw_control.draw_rect",
          "description": "Control drawing rectangle on the screen.",
          "parameters": [
            {
              "name": "x",
              "description": "X coordinate of the rectangle’s top-left corner",
              "type": "integer",
              "required": True
            },{
              "name": "y",
              "description": "Y coordinate of the rectangle’s top-left corner",
              "type": "integer",
              "required": True
            },{
              "name": "width",
              "description": "Rectangle width of the rectangle",
              "type": "integer",
              "required": True
            },{
              "name": "height",
              "description": "Rectangle height of the rectangle",
              "type": "integer",
              "required": True
            },{
              "name": "line_width",
              "description": "line width of the rectangle",
              "type": "integer",
              "required": True
            },{
              "name": "color",
              "description": "RGBA color encoded as uint32 hex string, e.g. #00FF00 or #FF00FF80",
              "type": "string",
              "required": True
            }
          ]
        },{
          "name": "self.draw_control.draw_unique_rect",
          "description": "Control drawing unique rect on the screen.",
          "parameters": [
            {
              "name": "x",
              "description": "X coordinate of the rectangle’s top-left corner",
              "type": "integer",
              "required": True
            },{
              "name": "y",
              "description": "Y coordinate of the rectangle’s top-left corner",
              "type": "integer",
              "required": True
            },{
              "name": "width",
              "description": "Rectangle width of the rectangle",
              "type": "integer",
              "required": True
            },{
              "name": "height",
              "description": "Rectangle height of the rectangle",
              "type": "integer",
              "required": True
            },{
              "name": "line_width",
              "description": "line width of the rectangle",
              "type": "integer",
              "required": True
            },{
              "name": "color",
              "description": "RGBA color encoded as uint32 hex string, e.g. #00FF00 or #FF00FF80",
              "type": "string",
              "required": True
            }
          ]
        },{
          "name": "self.draw_control.clear_text",
          "description": "Control clearing all text on the screen.",
          "parameters": [
          ]
        },{
          "name": "self.draw_control.clear_rect",
          "description": "Control clearing all rect on the screen.",
          "parameters": [
          ]
        },{
            "name": "self.knowledges_control.save_knowledges",
            "description": "Control saving the current configuration to the knowledge base",
            "parameters": [
              {
                "name": "algorithm",
                "description": "The ID of the algorithm whose parameters should be retrieved.",
                "type": "integer",
                "required": True
              },
              {
                "name": "knowledges_id",
                "description": "knowledges id",
                "type": "integer",
                "required": True
              }
            ]
        },{
            "name": "self.knowledges_control.load_knowledges",
            "description": "Control loading the configuration from the knowledge base into the active workspace.",
            "parameters": [
              {
                "name": "algorithm",
                "description": "The ID of the algorithm whose parameters should be retrieved.",
                "type": "integer",
                "required": True
              },
              {
                "name": "knowledges_id",
                "description": "knowledges id",
                "type": "integer",
                "required": True
              }
            ]
        },{
            "name": "self.multi_algorithm_control.set_multi_algorithm",
            "description": "Load and activate multiple algorithms on the device at the same time.You must use a real algorithm ID retrieved from self.manage_applications.application_list; do not use a fabricated or made-up algorithm ID.",
            "parameters": [
              {
                "name": "algorithms",
                "description":  "Array of algorithm IDs, e.g. [1,2,3] or [1,2]. Only 2 or 3 algorithms are supported.",
                "type": "array",
                "items": {
                  "type": "integer"
                },
                "required": True
              }
            ]
        #},{
        #    "name": "self.multi_algorithm_control.set_multi_ratios",
        #    "description": "Configure the compute resource ratios for the currently loaded multiple algorithms.",
        #    "parameters": [
        #      {
        #        "name": "ratios",
        #        "description": "Array of ratios corresponding to the running algorithms, e.g. [1,2,0] or [1,2]. The length must match the number of currently active algorithms. Higher values indicate higher compute allocation.",
        #        "type": "array",
        #        "items": {
        #          "type": "integer"
        #        },
        #        "required": True
        #      }
        #    ]
        },{
            "name": "self.algorithm_params_control.get_algorithm_params",
            "description": "Retrieve the parameter list and current values for the specified algorithm. This tool must be called before reading or modifying any algorithm parameter to ensure the parameter name, type, and current value are known.",
            "parameters": [
              {
                "name": "algorithm",
                "description": "The ID of the algorithm whose parameters should be retrieved.",
                "type": "integer",
                "required": True
              }
            ]
        },{
            "name": "self.algorithm_params_control.set_algorithm_params",
            "description": "setting parameters of a specific algorithm.",
            "parameters": [
              {
                "name": "algorithm",
                "description": "The ID of the algorithm whose parameters should be retrieved.",
                "type": "integer",
                "required": True
              },
              {
                "name": "params",
                "description": "Algorithm parameter list encoded as a JSON string, for example: [{\"show_name\": true}, {\"face_features\": true}, {\"multi_face_acceleration\": true}, {\"rec_thres\": 0.2}, {\"det_thres\": 0.4}, {\"nms_thres\": 0.5}]. Parameter names and value types must exactly match those returned by get_algorithm_params. All parameters must be provided as an array of single key-value objects.",
                "type": "string",
                "required": True
              }
            ]
        },{
          "name": "self.device_control.set_backlight",
          "description": "Set the device backlight brightness.",
          "parameters": [
              {
                "name": "backlight",
                "description": "Backlight level (0–100).",
                "type": "integer",
                "required": True
              }
            ]
        },{
          "name": "self.device_control.get_backlight",
          "description": "Get the current device backlight brightness.",
          "parameters": [
            ]
        },{
          "name": "self.device_control.set_system_volume",
          "description": "Set the system volume level.",
          "parameters": [
              {
                "name": "volume",
                "description": "System volume level (0–100). Only supports discrete values in steps of 10 (0, 10, 20, ..., 100). For `get_system_volume`, read the current value from the returned `volume` field.",
                "type": "integer",
                "required": True
              }
            ]
        },{
          "name": "self.device_control.get_system_volume",
          "description": "Get the current system volume level.",
          "parameters": [
            ]
        },{
          "name": "self.device_control.set_flashlight",
          "description": "Set the device flashlight brightness",
          "parameters": [
              {
                "name": "flashlight",
                "description": "Flashlight brightness level (0–100). For `get_flashlight`, obtain the current value from the returned `flash_light_brightness` field.",
                "type": "integer",
                "required": True
              }
            ]
        },{
          "name": "self.device_control.get_flashlight",
          "description": "Get the current flashlight brightness and switch. flash_light_brightness: Flashlight brightness level (0–100).flash_light_switch: Whether the flashlight is on (true) or off (false).",
          "parameters": [
            ]
        }
    ]
}

with open("huskylens_mcp_server.json", "w", encoding="utf-8") as f:
    json.dump(tools, f, indent=4, ensure_ascii=False)

