ESP1_control_signal = 0
ESP1_command_signal = 0
ESP1_level = 0

ESP2_control_signal = 0
ESP2_command_signal = 0
ESP2_level = 0

ESP3_control_signal = 0
ESP3_command_signal = 0
ESP3_level = 0


def get_signals():
    
    signal_list = []

    for number in [1,2,3]:
    
        with open(f"ESP{number}.txt") as file:
            lines = file.read()
            split = lines.split(';')
            # print(split)
            
            if split[1] != ' Transmission failed':
                signal_list.append(split[1:])
            
            else:
                signal_list.append('no data')
                
    return signal_list
        
signals = get_signals()
print(signals)
        
if isinstance(signals[0], list):
    ESP1_control_signal = signals[0][0]
    ESP1_command_signal = signals[0][1]
    ESP1_level = signals[0][2]

if isinstance(signals[1], list):
    ESP2_control_signal = signals[1][0]
    ESP2_command_signal = signals[1][1]
    ESP2_level = signals[1][2]

if isinstance(signals[2], list):
    ESP3_control_signal = signals[2][0]
    ESP3_command_signal = signals[2][1]
    ESP3_level = signals[2][2]