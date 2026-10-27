import os
import re
import time
import requests

PATH = "/dev/shm/xiaozhi_runtime_msgq_v1"

def read_messages():
    try:
        with open(PATH, "rb") as f:
            data = f.read()
    except OSError as e:
        print("Cannot read message queue:", e)
        return []

    # Extract readable ASCII strings of at least four characters.
    pattern = rb"[\x20-\x7e]{4,}"
    return [
        (m.start(), m.group().decode("ascii", errors="replace"))
        for m in re.finditer(pattern, data)
    ]

print("Xiaozhi text monitor started.")
print("Listening for new text. Press Ctrl+C to exit.")
print()

previous = {}
try:
    while True:
        current = dict(read_messages())

        for offset, message in current.items():
            if previous.get(offset) != message:
                # Skip the queue's recurring hexadecimal-looking identifiers.
                if re.fullmatch(r"[0-9a-fA-F]{8}", message):
                    continue

                print("\033[1;32mXiaozhi:\033[0m \033[1;35m" + message + "\033[0m", flush=True)
                word = "Open Python" in message
                if(word==True):
                    print("opening...")
                    #os.system("killall menu")
                    #os.system("~/camera_drm.py")

                 # Send text message                                                        
                token = '8700402484:AAGSrdgBw5C0GIjGyTkqciyXejsxw-mzskg'                                              
                msg_type = 'sendMessage'                                                   
                chat_id = '-1003793960466'                                            
                text = message                                                            
                msg = f'https://api.telegram.org/bot{token}/{msg_type}?chat_id={chat_id}&text={text}'
                #telegram_msg = requests.get(msg)                                           
                #print(msg)                                                                
                #print(telegram_msg)                                                       
                #print(telegram_msg.content)


        previous = current
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nMonitor stopped.")
