TMPFS_DIR = "/pms_tmpfs/"

def main():
    set_pmstmpfs()

def set_pmstmpfs():
    env.user = "root"
    env.password = "shroot"
    if not exists(TMPFS_DIR, use_sudo=False):
        run("mkdir "+ TMPFS_DIR)
    run("umount " + TMPFS_DIR)
    run("mount " + TMPFS_DIR)
    run("chmod 777 " + TMPFS_DIR)