# Run as administrator

import winreg
import ctypes

def set_env_var_system(name, value):
    """
    Set a system environment variable.
    Requires admin privileges.
    """
    registry_path = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
    access = winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY

    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, access) as key:
        # Use REG_EXPAND_SZ to allow expanding %VAR% references
        winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)

def get_env_var_system(name):
    """
    Get a system environment variable value.
    """
    registry_path = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
    access = winreg.KEY_READ | winreg.KEY_WOW64_64KEY

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path, 0, access) as key:
            value, _ = winreg.QueryValueEx(key, name)
            return value
    except FileNotFoundError:
        return None

def append_to_system_path(paths):
    existing_path = get_env_var_system('Path')
    if existing_path is None:
        existing_path = ''
   
    existing_paths = existing_path.split(';')
    # Append only new paths (avoid duplicates)
    new_paths = [p for p in paths if p not in existing_paths]
    if not new_paths:
        print("No new paths to append to system Path.")
        return

    updated_path = existing_path.rstrip(';') + ';' + ';'.join(new_paths)
    set_env_var_system('Path', updated_path)

def broadcast_environment_change():
    HWND_BROADCAST = 0xFFFF
    WM_SETTINGCHANGE = 0x1A
    SMTO_ABORTIFHUNG = 0x0002

    result = ctypes.c_long()
    ctypes.windll.user32.SendMessageTimeoutW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", SMTO_ABORTIFHUNG, 5000, ctypes.byref(result))

def main():
    # System variables to add
    variables = {
        'JAVA_HOME': r'C:\Java\jdk1.8.0_40',
        'HADOOP_HOME': r'C:\hadoop-3.3.6',
        'HADOOP_COMMON_HOME': r'%HADOOP_HOME%',
        'HADOOP_HDFS_HOME': r'%HADOOP_HOME%',
        'HADOOP_MAPRED_HOME': r'%HADOOP_HOME%',
        'HADOOP_YARN_HOME': r'%HADOOP_HOME%',
        'HADOOP_CONF_DIR': r'%HADOOP_HOME%\etc\hadoop',
    }

    # Set system environment variables
    for var, val in variables.items():
        print(f"Setting system variable {var} = {val}")
        set_env_var_system(var, val)

    # Append to system Path
    paths_to_append = [
        r'%JAVA_HOME%\bin',
        r'%HADOOP_HOME%\bin',
        r'%HADOOP_HOME%\sbin'
    ]
    print("Appending paths to system Path variable...")
    append_to_system_path(paths_to_append)

    # Notify system about the environment change
    broadcast_environment_change()
    print("System environment variables updated. You may need to restart your console or log off/on.")

if __name__ == '__main__':
    main()

