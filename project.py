from dataclasses import dataclass
import os
import sys


@dataclass
class OS:
    rust_build: str
    copy_lib: str
    execute_python: str

    def dev_build(self):
        os.system(self.rust_build)
        os.system(self.copy_lib)
        os.system(self.execute_python)


@dataclass
class Linux(OS):
    rust_build: str = (
        "cargo build --release --manifest-path=./modules/libkayn/Cargo.toml"
    )
    copy_lib: str = "cp ./modules/libkayn/target/release/liblibkayn.so ./libkayn.so"
    execute_python: str = "python3 kayn.pyw"

    def dev_build(self):
        os.system(self.rust_build)
        os.system(self.copy_lib)
        os.system(self.execute_python)


class Windows(OS):
    rust_build: str = (
        "cargo build --release --manifest-path=./modules/libkayn/Cargo.toml"
    )
    copy_lib: str = "copy modules\\libkayn\\target\\release\\libkayn.dll libkayn.pyd"
    execute_python: str = "python kayn.pyw"


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

    system.dev_build()
