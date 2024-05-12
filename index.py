import psutil
import time
import subprocess
import win32gui
import win32con
import ctypes
import sys
import os
import msvcrt

# 设置服务名称和 CPU 使用率阈值
program_name = "vmnat.exe"  # 程序名
service_name = "VMware NAT Service"  # 服务名，需要与 windows 服务中所显示的服务名一致
cpu_threshold = 110  # 设置 CPU 使用率阈值（例如 100%）

# 根据进程名获取进程 PID
def get_pid_by_name(process_name):
    pid = None
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            pid = proc.info['pid']
            break
    return pid

# 判断是否以管理员权限运行
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# 运行程序以管理员权限运行
def run_as_admin():
    if is_admin():
        # 已经是管理员，可以直接运行你的程序
        pass
    else:
        print("********************************")
        print("请求用户 UAC 权限批准...")
        print("********************************")
        # 请求管理员权限
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

# 重启服务
def restart_service(service_name):
    subprocess.run(["net", "stop", service_name], check=True)
    subprocess.run(["net", "start", service_name], check=True)
    print("服务已重新启动。")

# 监控 CPU 使用率
def monitor_cpu_usage(target_pid, service_name):
    while True:
        process = psutil.Process(target_pid)
        cpu_percent = process.cpu_percent(interval=1)
        if cpu_percent > cpu_threshold:
            print(f"CPU 使用率超过 {cpu_threshold}%，正在重新启动服务...")
            restart_service(service_name)
        time.sleep(10)

def main():
    if not is_admin():
        print("********************************")
        print("注意：此脚本需要以管理员权限运行。")
        print("用途：重启 WINDOWS 服务时需要管理员权限。")
        print("********************************")
        os.system('pause')
        run_as_admin()
        sys.exit()

    win32gui.ShowWindow(win32gui.GetForegroundWindow(), win32con.SW_MINIMIZE)  # 最小化窗口
    while True:
        get_pid = get_pid_by_name(program_name)
        if get_pid is None:
            raise TypeError(f"找不到需要监控的程序 {program_name}。")

        print(f"正在监控服务 {service_name} 所对应程序 {program_name}(PID: {get_pid}) 的 CPU 占用率...")
        try:
            monitor_cpu_usage(get_pid, service_name)
        except TypeError as e:
            print(e)
        except psutil.NoSuchProcess:
            print((f"找不到进程 {get_pid}。"))
        time.sleep(10)

if __name__ == "__main__":
    try:
        print(f"服务 CPU 占用率监控自动重启脚本。by: Komori_晓椮")
        main()
    except KeyboardInterrupt as e:
        print("通过 Ctrl+C 退出脚本")
    except TypeError as e:
        print(e)
    except subprocess.CalledProcessError:
        print(f"无法重新启动服务 {service_name}。")
    except Exception as e:
        print(f"出现未知错误：{e}")
    finally:
        print("请按任意键退出~")
        ord(msvcrt.getch())