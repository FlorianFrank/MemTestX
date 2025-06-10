^import psutil


def print_start_dialog():
    print("*******************************************************************************************")
    print("******************************* Start Test Hub Micro Service*******************************")
    print("*******************************************************************************************")


def print_network_card_selection() -> str:
    """
    Prints a list of available network interfaces currently connected, allowing the user to select one to bind
    this microservice.
    """
    network_card_list = list(psutil.net_if_addrs().keys())

    print("Select a network card to bind the micro-service:")
    for idx, card in enumerate(network_card_list):
        print(f"    {idx}: {card}")

    while True:
        selection = input("Insert selection: ").strip()
        try:
            selected_index = int(selection)
            if 0 <= selected_index < len(network_card_list):
                return network_card_list[selected_index]
            else:
                print(f"Selection out of range! Please enter a number between 0 and {len(network_card_list) - 1}")
        except ValueError:
            print(f"Invalid input! Please insert numbers between 0 and {len(network_card_list) - 1}")


def print_app_config(app_config: dict) -> None:
    print("\n**********************************")
    print("**Load app config**:")
    for key, value in app_config.items():
        print(f"{key}: {value}")
    print("**********************************\n")
