# fmt: off
import os
import sys

class OS:
    def __init__(self):
        self.rust_build = None
        self.copy_lib = None
        self.execute_python = None
        self.compile_python = None

    def dev_build(self):
        os.system(self.rust_build)
        os.system(self.copy_lib)
        os.system(self.execute_python)
    
    def release_build(self):
        os.system(self.rust_build)
        os.system(self.copy_lib)
        os.system(self.compile_python) # TODO: "compile" python


class Linux(OS):
    def __init__(self):
        self.rust_build = "cargo build --release --manifest-path=./modules/libkayn/Cargo.toml"
        self.copy_lib = "cp ./modules/libkayn/target/release/liblibkayn.so ./libkayn.so"
        self.execute_python = "python kayn.pyw"


class Windows(OS):
    def __init__(self):
        self.rust_build = "cargo build --release --manifest-path=./modules/libkayn/Cargo.toml"
        self.copy_lib = "copy modules\\libkayn\\target\\release\\libkayn.dll libkayn.pyd"
        self.execute_python = "python kayn.pyw"
    
class Mac(OS):
    def __init__(self):
        self.rust_build = "cargo build --release --manifest-path=./modules/libkayn/Cargo.toml"
        self.copy_lib = "cp ./modules/libkayn/target/release/liblibkayn.dylib ./libkayn.so"
        self.execute_python = "python kayn.pyw"


if __name__ == "__main__":
    # Recognize the OS
    system = sys.platform
    if sys.platform == "linux":
        system = Linux()
    elif sys.platform == "win32":
        system = Windows()
    else:
        print("Unsupported OS")
        sys.exit(1)

    if len(sys.argv) > 1:
        if sys.argv[1] == "dev" or sys.argv[1] == "run":
            system.dev_build()
        elif sys.argv[1] == "release":
            system.release_build()
        else:
            print("Unsupported argument")
            sys.exit(1)
    else:
        print("No argument given. Available arguments: dev, release")
        sys.exit(1)
