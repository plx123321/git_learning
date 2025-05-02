from tkinter import filedialog
import tkinter as tk
import shutil
import os
import hashlib
from pathlib import Path
import time


def get_file_hash(file_path):
    """计算文件的哈希值，用于判断文件是否发生变化"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except FileNotFoundError:
        return None

def get_file_info(file_path):
    """获取文件的元数据信息"""
    return {
        "size": os.path.getsize(file_path),
        "mtime": os.path.getmtime(file_path),
        "hash": get_file_hash(file_path)
    }

def get_directory_files_info(directory):
    """获取目录中所有文件的元数据信息"""
    files_info = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, directory)
            files_info[relative_path] = get_file_info(file_path)
    return files_info

def compare_directories(source_info, backup_info):
    """比较两个目录的文件信息，找出新增、修改和删除的文件"""
    added_files = {file: source_info[file] for file in source_info if file not in backup_info}
    modified_files = {file: source_info[file] for file in source_info if file in backup_info and source_info[file] != backup_info[file]}
    deleted_files = {file: backup_info[file] for file in backup_info if file not in source_info}
    return added_files, modified_files, deleted_files

def backup_files(source_dir, backup_dir):
    """执行增量备份"""
    # 获取源目录和备份目录的文件信息
    source_info = get_directory_files_info(source_dir)
    backup_info = get_directory_files_info(backup_dir)

    # 比较目录
    added_files, modified_files, deleted_files = compare_directories(source_info, backup_info)

    # 创建备份目录（如果不存在）
    Path(backup_dir).mkdir(parents=True, exist_ok=True)

    # 复制新增和修改的文件
    for file in added_files:
        source_file_path = os.path.join(source_dir, file)
        backup_file_path = os.path.join(backup_dir, file)
        shutil.copy2(source_file_path, backup_file_path)
        print(f"Added/Modified: {file}")

    # 删除备份目录中已删除的文件
    for file in deleted_files:
        backup_file_path = os.path.join(backup_dir, file)
        os.remove(backup_file_path)
        print(f"Deleted: {file}")

    # 更新备份目录的文件信息
    backup_info = get_directory_files_info(backup_dir)

    # 保存备份目录的文件信息到一个日志文件中
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    log_file = os.path.join(backup_dir, f"backup_log_{timestamp}.txt")
    with open(log_file, "w") as f:
        f.write("Added/Modified Files:\n")
        for file in added_files:
            f.write(f"{file}\n")
        for file in modified_files:
            f.write(f"{file}\n")
        f.write("\nDeleted Files:\n")
        for file in deleted_files:
            f.write(f"{file}\n")

    print(f"Backup completed. Log saved to {log_file}")

if __name__ == "__main__":

  root = tk.Tk()    
  root.withdraw()  # Hide the main window
    # Prompt user to select source and backup directories
  print("Please select the source directory:")
  print("Please select the backup directory:")
  source_directory = filedialog.askdirectory(title="Select Source Directory")
  backup_directory = filedialog.askdirectory(title="Select Backup Directory")
  backup_files(source_directory, backup_directory)


  
  
