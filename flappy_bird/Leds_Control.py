import subprocess
from itertools import chain


def ssh_cmd(
    host_ip: str,
    cmd: str,
    user: str = "root",
    password: str = None,
    remote_path="/root/",
    timeout_seconds=None,
):
    if timeout_seconds is not None:
        timeout = "timeout " + str(timeout_seconds) + "s "
    else:
        timeout = ""
    out = subprocess.Popen(
        f"ssh  -o StrictHostKeyChecking=no {user}@{host_ip} "
        + f'"cd {remote_path}; '
        + timeout
        + f" {cmd}"
        + '"',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).communicate()
    return out[0].decode(), out[1].decode()


def color_chooser(color: str):
    if color == "red":
        color = "ff0000"
    elif color == "green":
        color = "00ff00"
    elif color == "blue":
        color = "0000ff"
    elif color == "off":
        color = "000000"

    return color


def change_leds_color(
    leds_idx: list,
    color: str,
    timeout_sec: int = 0,
    host_ip: str = "192.168.116.171",
):
    color = color_chooser(color)

    for idx in leds_idx:
        ssh_cmd(
            host_ip=host_ip, cmd=f"opx_leds {idx} {color}", timeout_seconds=timeout_sec
        )


def flash_all_leds(
    color: str,
    time_on_ms: int = 350,
    time_off_ms: int = 200,
    host_ip: str = "192.168.116.171",
    duration_sec: int = 3,
):
    color = color_chooser(color)

    ssh_cmd(
        host_ip=host_ip,
        cmd=f"opx_leds 0x3fffff {color} {time_on_ms} 000000 {time_off_ms}",
    )


def led_progress_bar(color: str, host_ip: str = "192.168.116.171"):
    f = lambda x: x
    g = lambda x: 24 - x
    leds_idx_left_to_right = list(chain.from_iterable((f(x), g(x)) for x in range(12)))

    color = color_chooser(color)

    change_leds_color(leds_idx_left_to_right, color, host_ip=host_ip)


def kill_leds(host_ip: str = "192.168.116.171"):
    ssh_cmd(host_ip=host_ip, cmd="pkill opx_leds")


def ssh_bash(
    host_ip: str,
    bash_script: str,
    user: str = "root",
    password: str = None,
    remote_path="/root/",
    timeout_seconds=None,
):
    if timeout_seconds is not None:
        timeout = "timeout " + str(timeout_seconds) + "s "
    else:
        timeout = ""
    out = subprocess.Popen(
        f"ssh  -o StrictHostKeyChecking=no {user}@{host_ip} "
        + timeout
        + "bash -s"
        + f" < {bash_script}.sh"
        + '"',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).communicate()
    return out[0].decode(), out[1].decode()


if __name__ == "__main__":
    # leds_idx = [i for i in range(22)]
    # change_leds_color(leds_idx, "off")
    # flash_all_leds(color="red", time_on_ms=300, time_off_ms=200)
    # led_progress_bar("blue")

    ssh_bash(host_ip="192.168.116.171", bash_script="test")
